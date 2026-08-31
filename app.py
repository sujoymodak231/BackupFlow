import os
import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text
from dotenv import load_dotenv

from config import Config

# Load environment variables from .env file if available
load_dotenv()

# Initialize SQLAlchemy ORM instance
db = SQLAlchemy()


class Record(db.Model):
    """Data model for application records (e.g. system assets, data entries)."""
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active')
    value = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def format_bytes(size_in_bytes):
    """Format size in bytes into human-readable format (B, KB, MB, GB)."""
    if size_in_bytes is None or size_in_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)
    unit_index = 0
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


def get_backup_stats(backup_dir):
    """Inspect backup directory and calculate summary metrics."""
    stats = {
        "count": 0,
        "total_bytes": 0,
        "formatted_size": "0 B",
        "latest_backup_file": None,
        "latest_backup_time": None,
        "status": "No Backups Found",
        "backup_files": []
    }

    if not os.path.exists(backup_dir):
        return stats

    files = []
    for item in os.listdir(backup_dir):
        if item == '.gitkeep':
            continue
        item_path = os.path.join(backup_dir, item)
        if os.path.isfile(item_path):
            file_stat = os.stat(item_path)
            mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
            size = file_stat.st_size
            files.append({
                "filename": item,
                "size_bytes": size,
                "formatted_size": format_bytes(size),
                "modified_time": mod_time,
                "modified_str": mod_time.strftime("%Y-%m-%d %H:%M:%S")
            })

    if files:
        # Sort by modification time descending
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        total_size = sum(f["size_bytes"] for f in files)
        latest = files[0]

        stats["count"] = len(files)
        stats["total_bytes"] = total_size
        stats["formatted_size"] = format_bytes(total_size)
        stats["latest_backup_file"] = latest["filename"]
        stats["latest_backup_time"] = latest["modified_str"]
        stats["status"] = "Healthy"
        stats["backup_files"] = files

    return stats


def get_upload_stats(upload_dir):
    """Inspect uploads directory and return file list and summary stats."""
    stats = {
        "count": 0,
        "total_bytes": 0,
        "formatted_size": "0 B",
        "files": []
    }

    if not os.path.exists(upload_dir):
        return stats

    files = []
    for item in os.listdir(upload_dir):
        if item == '.gitkeep':
            continue
        item_path = os.path.join(upload_dir, item)
        if os.path.isfile(item_path):
            file_stat = os.stat(item_path)
            mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
            size = file_stat.st_size
            files.append({
                "filename": item,
                "size_bytes": size,
                "formatted_size": format_bytes(size),
                "modified_time": mod_time,
                "modified_str": mod_time.strftime("%Y-%m-%d %H:%M:%S")
            })

    if files:
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        total_size = sum(f["size_bytes"] for f in files)
        stats["count"] = len(files)
        stats["total_bytes"] = total_size
        stats["formatted_size"] = format_bytes(total_size)
        stats["files"] = files

    return stats


def seed_initial_data():
    """Seed realistic initial company records if the database is empty."""
    if Record.query.count() == 0:
        sample_records = [
            Record(
                name="Production PostgreSQL Database Dump",
                category="Database",
                description="Full nightly dump of production customer transactional database.",
                status="Active",
                value=12500.00
            ),
            Record(
                name="Nginx Web Server Configuration",
                category="Configuration",
                description="Nginx reverse proxy, load balancer, and SSL certificate config files.",
                status="Active",
                value=1500.00
            ),
            Record(
                name="AWS IAM Service Account Credentials",
                category="Credentials",
                description="Encrypted API keys and service tokens for cloud backup storage.",
                status="Active",
                value=5000.00
            ),
            Record(
                name="Employee Payroll & Tax Data Q2",
                category="General",
                description="Encrypted CSV export of quarterly payroll records.",
                status="Active",
                value=8500.00
            ),
            Record(
                name="Legacy Linux File Server Snapshot",
                category="Server",
                description="Disk snapshot of deprecated Ubuntu 20.04 internal file server.",
                status="Pending",
                value=3200.00
            ),
            Record(
                name="Wildcard SSL / TLS Certificate Bundle",
                category="Credentials",
                description="Wildcard SSL certificates and private keys for internal domain.",
                status="Active",
                value=2400.00
            ),
            Record(
                name="System Security Audit Logs Q2",
                category="General",
                description="Compliance audit trail log export for security review.",
                status="Archived",
                value=750.00
            )
        ]
        db.session.bulk_save_objects(sample_records)
        db.session.commit()


def create_app(config_class=Config):
    """Flask Application Factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure required application directories exist
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)
    os.makedirs(app.config['BACKUP_DIR'], exist_ok=True)

    # Context processor to make helper functions available in templates
    @app.context_processor
    def utility_processor():
        return dict(format_bytes=format_bytes)

    # Create tables automatically inside app context
    with app.app_context():
        db.create_all()
        # Seed realistic initial data if database is empty (except in testing mode)
        if not app.config.get('TESTING'):
            seed_initial_data()

    # -------------------------------------------------------------------------
    # Routes
    # -------------------------------------------------------------------------

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint used by monitoring & Jenkins automation."""
        try:
            # Check database connection
            db.session.execute(text('SELECT 1'))
            record_count = Record.query.count()
            upload_stats = get_upload_stats(app.config['UPLOAD_DIR'])
            backup_stats = get_backup_stats(app.config['BACKUP_DIR'])

            return jsonify({
                "status": "healthy",
                "database": "connected",
                "record_count": record_count,
                "upload_count": upload_stats["count"],
                "backup_count": backup_stats["count"],
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }), 500

    @app.route('/')
    def dashboard():
        """Dashboard view displaying system overview and metrics."""
        record_count = Record.query.count()
        recent_records = Record.query.order_by(Record.updated_at.desc()).limit(5).all()
        upload_stats = get_upload_stats(app.config['UPLOAD_DIR'])
        backup_stats = get_backup_stats(app.config['BACKUP_DIR'])

        # Compute total records value sum
        total_value = db.session.query(db.func.sum(Record.value)).scalar() or 0.0

        return render_template(
            'dashboard.html',
            record_count=record_count,
            recent_records=recent_records,
            upload_stats=upload_stats,
            backup_stats=backup_stats,
            total_value=total_value
        )

    @app.route('/records', methods=['GET'])
    def list_records():
        """View list of all database records."""
        category_filter = request.args.get('category', '')
        search_query = request.args.get('q', '')

        query = Record.query

        if category_filter:
            query = query.filter_by(category=category_filter)
        if search_query:
            query = query.filter(
                (Record.name.contains(search_query)) | 
                (Record.description.contains(search_query))
            )

        records = query.order_by(Record.created_at.desc()).all()
        categories = db.session.query(Record.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]

        return render_template(
            'records.html',
            records=records,
            categories=categories,
            selected_category=category_filter,
            search_query=search_query
        )

    @app.route('/records/add', methods=['POST'])
    def add_record():
        """Create a new database record."""
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Active').strip()
        value_str = request.form.get('value', '0.0').strip()

        if not name:
            flash('Record name is required!', 'danger')
            return redirect(url_for('list_records'))

        try:
            value = float(value_str) if value_str else 0.0
        except ValueError:
            value = 0.0

        new_record = Record(
            name=name,
            category=category or 'General',
            description=description,
            status=status or 'Active',
            value=value
        )

        db.session.add(new_record)
        db.session.commit()
        flash(f'Record "{name}" created successfully!', 'success')
        return redirect(url_for('list_records'))

    @app.route('/records/edit/<int:record_id>', methods=['GET', 'POST'])
    def edit_record(record_id):
        """Edit an existing database record."""
        record = db.get_or_404(Record, record_id)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            category = request.form.get('category', 'General').strip()
            description = request.form.get('description', '').strip()
            status = request.form.get('status', 'Active').strip()
            value_str = request.form.get('value', '0.0').strip()

            if not name:
                flash('Record name is required!', 'danger')
                return render_template('edit_record.html', record=record)

            try:
                record.value = float(value_str) if value_str else 0.0
            except ValueError:
                pass

            record.name = name
            record.category = category
            record.description = description
            record.status = status
            record.updated_at = datetime.datetime.utcnow()

            db.session.commit()
            flash(f'Record "{name}" updated successfully!', 'success')
            return redirect(url_for('list_records'))

        return render_template('edit_record.html', record=record)

    @app.route('/records/delete/<int:record_id>', methods=['POST'])
    def delete_record(record_id):
        """Delete a record from the database."""
        record = db.get_or_404(Record, record_id)
        name = record.name
        db.session.delete(record)
        db.session.commit()
        flash(f'Record "{name}" deleted successfully!', 'info')
        return redirect(url_for('list_records'))

    @app.route('/uploads', methods=['GET', 'POST'])
    def manage_uploads():
        """Handle file uploads and file listing."""
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file selected!', 'warning')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No file selected!', 'warning')
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_DIR'], filename)
                file.save(save_path)
                flash(f'File "{filename}" uploaded successfully!', 'success')
                return redirect(url_for('manage_uploads'))

        upload_stats = get_upload_stats(app.config['UPLOAD_DIR'])
        return render_template('uploads.html', upload_stats=upload_stats)

    @app.route('/uploads/download/<filename>')
    def download_file(filename):
        """Download an uploaded file."""
        return send_from_directory(app.config['UPLOAD_DIR'], filename, as_attachment=True)

    @app.route('/uploads/delete/<filename>', methods=['POST'])
    def delete_file(filename):
        """Delete an uploaded file."""
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_DIR'], safe_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{safe_filename}" removed!', 'info')
        else:
            flash(f'File "{safe_filename}" not found!', 'danger')
        return redirect(url_for('manage_uploads'))

    @app.route('/backups')
    def view_backups():
        """View backup status and list existing backups."""
        backup_stats = get_backup_stats(app.config['BACKUP_DIR'])
        return render_template('backups.html', backup_stats=backup_stats)

    return app


app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)
