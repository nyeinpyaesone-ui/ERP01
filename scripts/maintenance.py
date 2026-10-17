#!/usr/bin/env python3
"""Maintenance Script for ERP01.

Usage: python scripts/maintenance.py [health|backup|clear-cache|rotate-logs]
"""

import importlib.util
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEPENDENCIES = ("dotenv", "pytest", "black", "flake8")

EXCLUDED_DIRS = {".venv", "venv", ".git", "node_modules", "backups"}


def check_health() -> int:
    """Run health checks on the system."""
    print("Running health checks...")
    exit_code = 0

    # Check if virtual environment exists
    if (PROJECT_ROOT / ".venv").exists():
        print("✅ Virtual environment exists")
    else:
        print("⚠️  Virtual environment not found (run: python -m venv .venv)")

    # Check if dependencies are installed without importing them
    missing = [name for name in DEPENDENCIES if importlib.util.find_spec(name) is None]
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        exit_code = 1
    else:
        print("✅ All dependencies installed")

    # Run tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.returncode == 0:
        print("✅ All tests passing")
    else:
        print("❌ Some tests failing")
        print(result.stdout)
        print(result.stderr)
        exit_code = 1

    print("\nHealth check complete!")
    return exit_code


def create_backup() -> int:
    """Create a backup of important files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / "backups" / f"backup_{timestamp}"

    print(f"Creating backup in {backup_dir}...")
    backup_dir.mkdir(parents=True, exist_ok=True)

    dirs_to_backup = ["config", "modules", "utils", "docs"]
    for dir_name in dirs_to_backup:
        source = PROJECT_ROOT / dir_name
        if source.exists():
            shutil.copytree(
                source,
                backup_dir / dir_name,
                ignore=shutil.ignore_patterns("__pycache__"),
                dirs_exist_ok=True,
            )

    files_to_backup = ["main.py", "requirements.txt", ".env.example"]
    for file_name in files_to_backup:
        source = PROJECT_ROOT / file_name
        if source.exists():
            shutil.copy2(source, backup_dir / file_name)

    print(f"✅ Backup created successfully in {backup_dir}")
    return 0


def clear_cache() -> int:
    """Clear Python cache and pytest cache (excluding venv/build dirs)."""
    print("Clearing caches...")

    removed = 0
    for root, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Do not descend into excluded directories (e.g. .venv, .git)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        if Path(root).name == "__pycache__":
            shutil.rmtree(root, ignore_errors=True)
            removed += 1
            dirnames[:] = []
            continue
        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")):
                os.remove(os.path.join(root, filename))

    # Remove pytest cache
    pytest_cache = PROJECT_ROOT / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache, ignore_errors=True)

    # Remove coverage files
    for artifact in (".coverage", "coverage.xml"):
        path = PROJECT_ROOT / artifact
        if path.exists():
            path.unlink()

    print(f"✅ Caches cleared ({removed} __pycache__ dirs removed)")
    return 0


def rotate_logs() -> int:
    """Rotate log files with collision-safe timestamps."""
    print("Rotating logs...")

    log_dir = PROJECT_ROOT / "logs"
    if not log_dir.exists():
        print("No logs directory found")
        return 0

    base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    counter = 0
    rotated = 0
    for filepath in sorted(log_dir.glob("*.log")):
        suffix = f".{base_timestamp}"
        if counter:
            suffix += f".{counter}"
        new_filepath = filepath.with_name(filepath.name + suffix)
        while new_filepath.exists():
            counter += 1
            suffix = f".{base_timestamp}.{counter}"
            new_filepath = filepath.with_name(filepath.name + suffix)
        filepath.rename(new_filepath)
        rotated += 1
        print(f"Rotated {filepath.name} -> {new_filepath.name}")

    print(f"✅ Log rotation complete ({rotated} file(s))")
    return 0


def main() -> int:
    """Dispatch maintenance subcommands."""
    commands = {
        "health": check_health,
        "backup": create_backup,
        "clear-cache": clear_cache,
        "rotate-logs": rotate_logs,
    }

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        names = ", ".join(commands)
        print("Usage: python scripts/maintenance.py " f"[{names.replace(', ', '|')}]")
        return 1

    command = sys.argv[1].lower()
    handler = commands.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands)}")
        return 1
    return handler()


if __name__ == "__main__":
    raise SystemExit(main())
