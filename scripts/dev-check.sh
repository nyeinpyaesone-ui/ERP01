#!/bin/bash

# Development Check Script
# Runs all quality checks before committing/pushing

set -e

echo "=========================================="
echo "Running Development Quality Checks"
echo "=========================================="

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# 1. Check code formatting with black
echo ""
echo "[1/3] Checking code formatting (black)..."
if black --check . ; then
    echo "[OK] Formatting check passed"
else
    echo "[ERROR] Formatting check failed. Run 'black .' to fix."
    exit 1
fi

# 2. Run linter with flake8
echo ""
echo "[2/3] Running linter (flake8)..."
if flake8 . ; then
    echo "[OK] Linting passed"
else
    echo "[ERROR] Linting failed. Please fix the issues above."
    exit 1
fi

# 3. Run tests with coverage
echo ""
echo "[3/3] Running tests with coverage (pytest)..."
if pytest --cov=. --cov-fail-under=80 ; then
    echo "[OK] Tests passed with sufficient coverage"
else
    echo "[ERROR] Tests failed or coverage below 80%"
    exit 1
fi

echo ""
echo "=========================================="
echo "[OK] All quality checks passed!"
echo "=========================================="
