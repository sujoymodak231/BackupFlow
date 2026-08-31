import io
import os
from sqlalchemy import text
from app import db, Record, get_backup_stats, format_bytes

def test_app_starts(app):
    """Test 1: Verify application initializes correctly in testing mode."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_health_endpoint(client):
    """Test 2: Verify /health endpoint returns HTTP 200 and healthy JSON payload."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'timestamp' in data
    assert 'record_count' in data
    assert 'upload_count' in data
    assert 'backup_count' in data

def test_dashboard_loads(client):
    """Test 3: Verify dashboard page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'System Overview' in response.data
    assert b'Backup Management System' in response.data

def test_database_connection(app):
    """Test 4: Verify direct SQLite database connection and table creation."""
    with app.app_context():
        result = db.session.execute(text('SELECT 1')).scalar()
        assert result == 1

def test_create_and_retrieve_record(client, app):
    """Test 5 & 6: Verify a record can be created and retrieved from database."""
    # Create record via POST request
    post_data = {
        'name': 'Production Server Config',
        'category': 'Server',
        'description': 'Main web server configuration file backup',
        'status': 'Active',
        'value': '150.50'
    }
    response = client.post('/records/add', data=post_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Production Server Config' in response.data

    # Retrieve from database directly
    with app.app_context():
        record = Record.query.filter_by(name='Production Server Config').first()
        assert record is not None
        assert record.category == 'Server'
        assert record.value == 150.50
        assert record.status == 'Active'

    # Retrieve via records list endpoint
    list_response = client.get('/records')
    assert list_response.status_code == 200
    assert b'Production Server Config' in list_response.data

def test_edit_record(client, app):
    """Test editing an existing record."""
    # Create initial record
    with app.app_context():
        rec = Record(name='Initial Name', category='General', value=10.0)
        db.session.add(rec)
        db.session.commit()
        rec_id = rec.id

    # Edit record
    update_data = {
        'name': 'Updated Record Name',
        'category': 'Configuration',
        'description': 'Updated description',
        'status': 'Pending',
        'value': '250.00'
    }
    response = client.post(f'/records/edit/{rec_id}', data=update_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Updated Record Name' in response.data

    with app.app_context():
        updated_rec = db.session.get(Record, rec_id)
        assert updated_rec.name == 'Updated Record Name'
        assert updated_rec.category == 'Configuration'
        assert updated_rec.value == 250.00

def test_delete_record(client, app):
    """Test deleting a record."""
    with app.app_context():
        rec = Record(name='To Be Deleted', category='General')
        db.session.add(rec)
        db.session.commit()
        rec_id = rec.id

    response = client.post(f'/records/delete/{rec_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        deleted = db.session.get(Record, rec_id)
        assert deleted is None

def test_file_upload(client, app):
    """Test 7: Verify file upload functionality."""
    upload_dir = app.config['UPLOAD_DIR']
    file_content = b"Sample configuration data for backup test"
    data = {
        'file': (io.BytesIO(file_content), 'test_sample.txt')
    }

    response = client.post('/uploads', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'test_sample.txt' in response.data

    # Verify file saved on disk
    saved_file_path = os.path.join(upload_dir, 'test_sample.txt')
    assert os.path.exists(saved_file_path)
    with open(saved_file_path, 'rb') as f:
        assert f.read() == file_content

def test_file_download_and_delete(client, app):
    """Test downloading and deleting an uploaded file."""
    upload_dir = app.config['UPLOAD_DIR']
    file_path = os.path.join(upload_dir, 'download_test.txt')
    with open(file_path, 'w') as f:
        f.write("Test content for download and delete")

    # Download file
    dl_response = client.get('/uploads/download/download_test.txt')
    assert dl_response.status_code == 200
    assert dl_response.data == b"Test content for download and delete"
    dl_response.close()

    # Delete file
    del_response = client.post('/uploads/delete/download_test.txt', follow_redirects=True)
    assert del_response.status_code == 200
    assert not os.path.exists(file_path)

def test_backup_stats(app):
    """Test inspection and metric calculation for backup archives."""
    backup_dir = app.config['BACKUP_DIR']
    
    # Initially no backups
    stats = get_backup_stats(backup_dir)
    assert stats['count'] == 0
    assert stats['status'] == 'No Backups Found'

    # Create dummy backup file
    dummy_backup = os.path.join(backup_dir, 'backup_20260831_120000.tar.gz')
    with open(dummy_backup, 'wb') as f:
        f.write(b'x' * 2048)  # 2 KB dummy archive

    stats_after = get_backup_stats(backup_dir)
    assert stats_after['count'] == 1
    assert stats_after['status'] == 'Healthy'
    assert stats_after['latest_backup_file'] == 'backup_20260831_120000.tar.gz'
    assert stats_after['formatted_size'] == '2.00 KB'

def test_format_bytes_utility():
    """Test human readable bytes formatter function."""
    assert format_bytes(0) == "0 B"
    assert format_bytes(500) == "500.00 B"
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1048576) == "1.00 MB"
    assert format_bytes(1073741824) == "1.00 GB"
