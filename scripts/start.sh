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

# Run application
echo "[INFO] Application starting on http://0.0.0.0:5000..."
python3 app.py
