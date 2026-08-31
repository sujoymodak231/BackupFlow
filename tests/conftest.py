import os
import sys
import tempfile
import pytest

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db as _db

class TestConfig:
    """Configuration for running automated pytest suite."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def temp_workspace():
    """Create temporary directory isolated for test environment."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        db_path = os.path.join(temp_dir, 'test_app.db')
        upload_dir = os.path.join(temp_dir, 'uploads')
        backup_dir = os.path.join(temp_dir, 'backups')
        
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)

        yield {
            'db_path': db_path,
            'upload_dir': upload_dir,
            'backup_dir': backup_dir
        }

@pytest.fixture
def app(temp_workspace):
    """Fixture to instantiate Flask application for testing."""
    config = TestConfig()
    config.DATABASE_PATH = temp_workspace['db_path']
    config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{temp_workspace['db_path']}"
    config.SQLALCHEMY_TRACK_MODIFICATIONS = False
    config.UPLOAD_DIR = temp_workspace['upload_dir']
    config.BACKUP_DIR = temp_workspace['backup_dir']

    _app = create_app(config)

    with _app.app_context():
        _db.create_all()
        yield _app
        _db.session.remove()
        _db.drop_all()
        _db.engine.dispose()

@pytest.fixture
def client(app):
    """Fixture providing Flask test client."""
    return app.test_client()
