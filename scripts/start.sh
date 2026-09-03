#!/bin/bash
# ==============================================================================
# Backup Management System - Application Startup Script (Linux / Ubuntu)
# ==============================================================================

set -e

# Base directory navigation
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

echo "[INFO] Starting Backup Management System in $PROJECT_DIR..."

# Check Python3 availability
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment (venv)..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install / verify requirements
echo "[INFO] Installing dependencies from requirements.txt..."
pip install --quiet -r requirements.txt

# Create required data directories
mkdir -p database uploads backups

# Stop existing running instance if any
if [ -f "scripts/stop.sh" ]; then
    bash scripts/stop.sh > /dev/null 2>&1 || true
fi

# Run application in background for Jenkins compatibility
echo "[INFO] Application starting on http://0.0.0.0:5000 in background..."
nohup python3 app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

echo "[SUCCESS] Application started with PID: $APP_PID (Logs: app.log)"
