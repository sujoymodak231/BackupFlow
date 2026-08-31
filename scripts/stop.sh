#!/bin/bash
# ==============================================================================
# Backup Management System - Application Stop Script (Linux / Ubuntu)
# ==============================================================================

echo "[INFO] Stopping Backup Management System..."

# Find and stop running Flask process
PID=$(pgrep -f "python3 app.py" || true)

if [ -n "$PID" ]; then
    echo "[INFO] Terminating process PID: $PID..."
    kill -15 $PID
    sleep 2
    if pgrep -f "python3 app.py" > /dev/null; then
        echo "[WARNING] Process did not terminate gracefully, force killing..."
        kill -9 $PID
    fi
    echo "[SUCCESS] Application stopped successfully."
else
    echo "[INFO] No running application process found."
fi
