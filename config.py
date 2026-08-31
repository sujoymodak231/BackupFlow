import os
from pathlib import Path

# Define base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-backup-management-system')
    
    # Path configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'database' / 'app.db'))
    
    # Ensure relative paths resolve correctly from BASE_DIR if relative
    if not os.path.isabs(DATABASE_PATH):
        DATABASE_PATH = str(BASE_DIR / DATABASE_PATH)
        
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', str(BASE_DIR / 'uploads'))
    if not os.path.isabs(UPLOAD_DIR):
        UPLOAD_DIR = str(BASE_DIR / UPLOAD_DIR)
        
    BACKUP_DIR = os.environ.get('BACKUP_DIR', str(BASE_DIR / 'backups'))
    if not os.path.isabs(BACKUP_DIR):
        BACKUP_DIR = str(BASE_DIR / BACKUP_DIR)

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
