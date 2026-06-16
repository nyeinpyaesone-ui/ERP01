#!/bin/bash

# Maintenance Script for ERP01
# Usage: python scripts/maintenance.py [health|backup|clear-cache|rotate-logs]

import sys
import os
import subprocess
from datetime import datetime

def check_health():
    """Run health checks on the system."""
    print("Running health checks...")
    
    # Check if virtual environment exists
    if os.path.exists('.venv'):
        print("✅ Virtual environment exists")
    else:
        print("❌ Virtual environment not found")
    
    # Check if dependencies are installed
    try:
        import dotenv
        import pytest
        import black
        import flake8
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
    
    # Run tests
    result = subprocess.run(['pytest', '--tb=short'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ All tests passing")
    else:
        print("❌ Some tests failing")
        print(result.stdout)
        print(result.stderr)
    
    print("\nHealth check complete!")

def create_backup():
    """Create a backup of important files."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/backup_{timestamp}'
    
    print(f"Creating backup in {backup_dir}...")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup key directories
    dirs_to_backup = ['config', 'modules', 'utils', 'sprint_planning']
    for dir_name in dirs_to_backup:
        if os.path.exists(dir_name):
            subprocess.run(['cp', '-r', dir_name, backup_dir])
    
    # Backup key files
    files_to_backup = ['main.py', 'requirements.txt', '.env.example']
    for file_name in files_to_backup:
        if os.path.exists(file_name):
            subprocess.run(['cp', file_name, backup_dir])
    
    print(f"✅ Backup created successfully in {backup_dir}")

def clear_cache():
    """Clear Python cache and pytest cache."""
    print("Clearing caches...")
    
    # Remove Python cache
    subprocess.run(['find', '.', '-type', 'd', '-name', '__pycache__', '-exec', 'rm', '-rf', '{}', '+'])
    subprocess.run(['find', '.', '-type', 'f', '-name', '*.pyc', '-delete'])
    
    # Remove pytest cache
    if os.path.exists('.pytest_cache'):
        subprocess.run(['rm', '-rf', '.pytest_cache'])
    
    # Remove coverage files
    subprocess.run(['rm', '-f', '.coverage', 'coverage.xml'])
    
    print("✅ Caches cleared")

def rotate_logs():
    """Rotate log files if they exist."""
    print("Rotating logs...")
    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("No logs directory found")
        return
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filepath = f"{filepath}.{timestamp}"
            os.rename(filepath, new_filepath)
            print(f"Rotated {filename}")
    
    print("✅ Log rotation complete")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/maintenance.py [health|backup|clear-cache|rotate-logs]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'health':
        check_health()
    elif command == 'backup':
        create_backup()
    elif command == 'clear-cache':
        clear_cache()
    elif command == 'rotate-logs':
        rotate_logs()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: health, backup, clear-cache, rotate-logs")
        sys.exit(1)

if __name__ == '__main__':
    main()
