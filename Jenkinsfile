pipeline {
    agent {
        label 'backupflow'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        // Prevents Jenkins ProcessTreeKiller from terminating background Flask process
        JENKINS_NODE_COOKIE = 'dontKillMe'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo '==================================================='
                echo 'STAGE: Checkout Source Code'
                echo '==================================================='
                checkout scm
                sh '''
                    echo "Current Commit Information:"
                    git log -1 --oneline
                    echo "Workspace Directory Contents:"
                    ls -la
                '''
            }
        }

        stage('Environment & Dependencies') {
            steps {
                echo '==================================================='
                echo 'STAGE: Environment & Dependencies'
                echo '==================================================='
                sh '''
                    echo "Checking Python environment..."
                    python3 --version

                    if [ ! -d "venv" ]; then
                        echo "Creating virtual environment..."
                        python3 -m venv venv
                    fi

                    echo "Activating virtualenv & installing dependencies..."
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Automated Testing') {
            steps {
                echo '==================================================='
                echo 'STAGE: Automated Testing (pytest)'
                echo '==================================================='
                sh '''
                    . venv/bin/activate
                    echo "Executing pytest suite..."
                    pytest -v
                '''
            }
        }

        stage('Start Application') {
            steps {
                echo '==================================================='
                echo 'STAGE: Start Application'
                echo '==================================================='
                sh '''
                    echo "Ensuring scripts are executable..."
                    chmod +x scripts/start.sh scripts/stop.sh

                    echo "Stopping any existing Flask process..."
                    ./scripts/stop.sh || true

                    echo "Starting Flask web application..."
                    ./scripts/start.sh

                    echo "Waiting 5 seconds for application startup..."
                    sleep 5
                '''
            }
        }

        stage('Initial Health Check') {
            steps {
                echo '==================================================='
                echo 'STAGE: Initial Health Check'
                echo '==================================================='
                sh '''
                    echo "Probing http://127.0.0.1:5000/health..."
                    curl --retry 5 --retry-connrefused --retry-delay 2 --fail http://127.0.0.1:5000/health
                    echo ""
                    echo "Application is HEALTHY."
                '''
            }
        }

        stage('Stop Application for Backup') {
            steps {
                echo '==================================================='
                echo 'STAGE: Stop Application for Backup'
                echo '==================================================='
                sh '''
                    echo "Stopping application cleanly before data archive..."
                    ./scripts/stop.sh || true
                    sleep 2
                '''
            }
        }

        stage('Create Backup Archive') {
            steps {
                echo '==================================================='
                echo 'STAGE: Create Backup Archive'
                echo '==================================================='
                sh '''
                    mkdir -p backups

                    echo "Verifying persistent data targets exist..."
                    if [ ! -f "database/app.db" ]; then
                        echo "ERROR: database/app.db file does not exist!"
                        exit 1
                    fi

                    if [ ! -d "uploads" ]; then
                        echo "ERROR: uploads/ directory does not exist!"
                        exit 1
                    fi

                    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
                    BACKUP_FILE="backups/backup_${TIMESTAMP}.tar.gz"

                    echo "Creating timestamped backup archive: $BACKUP_FILE..."
                    tar -czf "$BACKUP_FILE" database/app.db uploads/

                    echo "Backup archive successfully created:"
                    ls -lh "$BACKUP_FILE"
                '''
            }
        }

        stage('Verify Backup Archive') {
            steps {
                echo '==================================================='
                echo 'STAGE: Verify Backup Archive'
                echo '==================================================='
                sh '''
                    echo "Verifying backup existence..."
                    BACKUP_COUNT=$(ls -1 backups/backup_*.tar.gz 2>/dev/null | wc -l)
                    if [ "$BACKUP_COUNT" -eq 0 ]; then
                        echo "ERROR: No backup files found in backups/ directory!"
                        exit 1
                    fi
                    echo "Total backups found: $BACKUP_COUNT"

                    LATEST_BACKUP=$(ls -1t backups/backup_*.tar.gz | head -1)
                    echo "Verifying latest archive integrity: $LATEST_BACKUP..."
                    tar -tzf "$LATEST_BACKUP" > /dev/null

                    echo "SUCCESS: Archive integrity verified."
                    echo "Archive Table of Contents:"
                    tar -tzf "$LATEST_BACKUP"
                '''
            }
        }

        stage('Enforce Retention Policy') {
            steps {
                echo '==================================================='
                echo 'STAGE: Enforce Retention Policy'
                echo '==================================================='
                sh '''
                    echo "Applying retention rule: Keep latest 5 backups..."
                    ls -1t backups/backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f

                    REMAINING=$(ls -1 backups/backup_*.tar.gz 2>/dev/null | wc -l)
                    echo "Remaining backups count: $REMAINING"

                    if [ "$REMAINING" -gt 5 ]; then
                        echo "ERROR: Retention policy failed! Found $REMAINING backups (expected max 5)."
                        exit 1
                    fi

                    echo "Current active backups in storage:"
                    ls -lh backups/
                '''
            }
        }

        stage('Disaster Recovery Restore Test') {
            steps {
                echo '==================================================='
                echo 'STAGE: Disaster Recovery Restore Test'
                echo '==================================================='
                sh '''
                    RESTORE_DIR="restore_test_${BUILD_NUMBER}"
                    echo "Setting up temporary restore directory: $RESTORE_DIR..."

                    # Ensure cleanup runs even if test steps fail
                    trap 'echo "Cleaning up temporary restore directory..."; rm -rf "$RESTORE_DIR"' EXIT

                    mkdir -p "$RESTORE_DIR"

                    LATEST_BACKUP=$(ls -1t backups/backup_*.tar.gz | head -1)
                    echo "Extracting backup $LATEST_BACKUP into $RESTORE_DIR..."
                    tar -xzf "$LATEST_BACKUP" -C "$RESTORE_DIR"

                    echo "Verifying restored database file..."
                    if [ ! -f "$RESTORE_DIR/database/app.db" ]; then
                        echo "ERROR: Restored database/app.db missing!"
                        exit 1
                    fi
                    echo "✓ Restored database/app.db exists."

                    echo "Verifying restored uploads directory..."
                    if [ ! -d "$RESTORE_DIR/uploads" ]; then
                        echo "ERROR: Restored uploads/ directory missing!"
                        exit 1
                    fi
                    echo "✓ Restored uploads/ directory exists."

                    echo "Checking SQLite database integrity..."
                    if command -v sqlite3 > /dev/null 2>&1; then
                        INTEGRITY_CHECK=$(sqlite3 "$RESTORE_DIR/database/app.db" "PRAGMA quick_check;")
                        echo "SQLite PRAGMA quick_check result: $INTEGRITY_CHECK"
                        if [ "$INTEGRITY_CHECK" != "ok" ]; then
                            echo "ERROR: SQLite database integrity check failed!"
                            exit 1
                        fi
                        echo "✓ SQLite database integrity verified OK."
                    else
                        echo "NOTICE: sqlite3 CLI tool not installed on host, skipping PRAGMA check."
                    fi

                    echo "Restore verification test completed successfully!"
                '''
            }
        }

        stage('Restart & Validate Application') {
            steps {
                echo '==================================================='
                echo 'STAGE: Restart & Validate Application'
                echo '==================================================='
                sh '''
                    echo "Restarting application..."
                    ./scripts/start.sh

                    echo "Waiting 5 seconds for application startup..."
                    sleep 5

                    echo "Probing final health check at http://127.0.0.1:5000/health..."
                    curl --retry 5 --retry-connrefused --retry-delay 2 --fail http://127.0.0.1:5000/health
                    echo ""
                    echo "Final Health Check Passed. Application is ONLINE."
                '''
            }
        }
    }

    post {
        success {
            echo '==================================================='
            echo '   SUCCESS: BACKUPFLOW PIPELINE COMPLETED CLEANLY'
            echo '==================================================='
        }

        failure {
            echo '==================================================='
            echo '   FAILURE: BACKUPFLOW PIPELINE FAILED'
            echo '==================================================='
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
