#!/bin/bash
# ==============================================================================
# Backup Management System - Application Stop Script (Linux / Ubuntu)
# ==============================================================================

echo "[INFO] Stopping Backup Management System..."

# Base directory navigation
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

# Stop process via PID file if present
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
        echo "[INFO] Terminating process PID $PID from app.pid..."
        kill -15 $PID 2>/dev/null || true
        sleep 2
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null || true
        fi
    fi
    rm -f app.pid
fi

# Fallback check for any process running python3 app.py
PIDS=$(pgrep -f "python3 app.py" || true)
if [ -n "$PIDS" ]; then
    echo "[INFO] Terminating remaining process(es) PID(s): $PIDS..."
    kill -15 $PIDS 2>/dev/null || true
    sleep 2
    kill -9 $PIDS 2>/dev/null || true
fi

echo "[SUCCESS] Application stopped successfully."
