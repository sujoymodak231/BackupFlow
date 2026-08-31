# 💾 Backup Management System (BackupFlow)

A clean, intermediate-level **Backup Management Web Application** built with **Python, Flask, SQLite, HTML5, CSS3, and JavaScript**. 

This application is designed specifically as the foundational web project for a **Jenkins CI/CD, Backup, Verification, Retention, and Disaster Recovery Automation Pipeline** running directly on Ubuntu/Linux without containerization tools (No Docker / No Kubernetes).

---

## 🚀 Key Features

1. **📊 Interactive Dashboard**:
   - Total database records and financial asset values
   - File upload count and storage usage
   - Live status of available backup archives (`backups/`)
   - Direct database connection monitoring

2. **📁 Data Management (CRUD)**:
   - Create, View, Edit, and Delete company assets/data records
   - Search by name/description and filter by category (Server, Database, Config, Credentials)

3. **📤 File Upload Manager**:
   - Upload sample files and document assets
   - Files stored safely in dedicated `uploads/` directory
   - File browser with human-readable file sizes, download, and deletion

4. **🛡️ Backup Information Center**:
   - Scans `backups/` for generated `.tar.gz` archive files
   - Calculates total backup count, total archive size, latest backup timestamp, and system backup health

5. **⚡ Health Check Endpoint (`/health`)**:
   - JSON API endpoint for automated monitoring probes
   - Verifies SQLite connectivity and returns real-time system metrics

---

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: Flask 3.x
- **Database**: SQLite3 via Flask-SQLAlchemy 3.x
- **Environment Management**: python-dotenv
- **Testing**: pytest 8.x
- **Frontend**: HTML5, CSS3 (Custom responsive theme), Vanilla JavaScript

---

## 📂 Project Directory Structure

```text
BackupFlow/
├── app.py                  # Main Flask application entry point & routes
├── config.py               # Environment configuration settings
├── requirements.txt        # Python dependency manifest
├── README.md               # Project documentation
├── .gitignore              # Git exclusion rules (venv, app.db, uploads, env)
├── .env.example            # Environment variables template
│
├── database/
│   ├── .gitkeep
│   └── app.db              # SQLite database (Created on startup, excluded from git)
│
├── uploads/
│   ├── .gitkeep            # Uploaded files folder (Excluded from git)
│   └── ...
│
├── backups/
│   ├── .gitkeep            # Target folder for Jenkins backup archives (Excluded from git)
│   └── ...
│
├── templates/
│   ├── base.html           # Master layout with navbar & alert banners
│   ├── dashboard.html      # Analytics dashboard view
│   ├── records.html        # Records management table & add record form
│   ├── edit_record.html    # Record edit view
│   ├── uploads.html        # File upload manager & file browser
│   └── backups.html        # Backup status & archive inspector
│
├── static/
│   ├── css/
│   │   └── style.css       # Clean responsive design & metrics styles
│   └── js/
│       └── main.js         # Alert handling & file upload preview
│
├── tests/
│   ├── conftest.py         # Pytest fixtures & isolated test env
│   └── test_app.py         # Automated unit & integration tests
│
└── scripts/
    ├── start.sh            # Linux application launch script
    └── stop.sh             # Linux process termination script
```

---

## 💻 Installation & Setup (Linux / Ubuntu)

### Prerequisites
Ensure Python 3 and `pip` are installed on your Linux system:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### Local Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone <your-repository-url>
   cd BackupFlow
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup (Optional)**:
   ```bash
   cp .env.example .env
   ```

5. **Run the Web Application**:
   ```bash
   python3 app.py
   ```
   *Access the web application at:* `http://localhost:5000`

---

## 🧪 Running Automated Tests

The application includes unit and integration test coverage using `pytest`.

To run the test suite, activate your virtual environment and execute:

```bash
pytest
```

For verbose test execution details:
```bash
pytest -v
```

### Test Coverage Includes:
- Application initialization in testing context
- Database connectivity check (`SELECT 1`)
- `/health` endpoint HTTP 200 response & JSON structure
- Dashboard page loading
- Record creation, retrieval, editing, and deletion (CRUD)
- File upload, storage verification, download, and deletion
- Backup stats calculation for archives in `backups/`

---

## 🔌 API & Health Check Endpoint

### `GET /health`

**Purpose**: Used by Jenkins pipelines, load balancers, or uptime monitors to check application readiness.

**Sample Request**:
```bash
curl -X GET http://localhost:5000/health
```

**Sample Response (HTTP 200 OK)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "record_count": 5,
  "upload_count": 3,
  "backup_count": 2,
  "timestamp": "2026-08-31T16:25:00.123456Z"
}
```

---

## ⚙️ Future Jenkins Automation & Pipeline Integration

This application separates **important persistent data** into two specific locations:
1. `database/app.db` (SQLite Database containing all record data)
2. `uploads/` (User uploaded document assets)

### Planned Jenkins Pipeline & Bash Script Operations

In your future DevOps project, Jenkins will run automated Bash scripts to perform the following operations:

1. **Check Application Health**: Probe `http://localhost:5000/health`.
2. **Stop Application (if required)**: Execute `scripts/stop.sh` or terminate process cleanly.
3. **Back Up Database**: Copy `database/app.db` to a temporary backup staging directory.
4. **Back Up Uploaded Files**: Copy `uploads/` directory to backup staging.
5. **Compress the Backup**: Create a timestamped archive:
   ```bash
   tar -czvf backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz database/app.db uploads/
   ```
6. **Timestamping**: Ensure backup filename includes year, month, day, hour, minute, second.
7. **Verify Backup Integrity**: Test archive integrity via `tar -tzf backups/backup_*.tar.gz`.
8. **Retention Policy Enforcement**: Keep only the latest $N$ backups (e.g., keep latest 5, delete older archives).
9. **Restore Verification**: Extract archive to `/tmp/restore_test/` and run `sqlite3 /tmp/restore_test/database/app.db "PRAGMA quick_check;"` to confirm data validity.
10. **Start/Restart Application**: Execute `scripts/start.sh` or `python3 app.py`.

---

## 📋 Quick Reference Commands Summary

### Run Application (Linux / Ubuntu CLI):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Run Tests:
```bash
source venv/bin/activate
pytest -v
```
