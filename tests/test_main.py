"""Tests for the application entry point (main.py)."""

import pytest

import main


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    """Isolate main() from ambient env and repo .env file."""
    for key in (
        "APP_NAME",
        "APP_ENV",
        "DEBUG",
        "DATABASE_URL",
        "SECRET_KEY",
        "LOG_LEVEL",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)


def test_core_module_lifecycle():
    """Test CoreModule initialize/execute wiring."""
    module = main.CoreModule("core")
    assert module.initialize() is True
    result = module.execute()
    assert result["status"] == "success"
    assert result["module"] == "core"


def test_main_runs_successfully(tmp_path, monkeypatch):
    """Test the entry point completes and returns 0."""
    monkeypatch.chdir(tmp_path)
    assert main.main() == 0
