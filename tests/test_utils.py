"""Tests for utility functions.

Hermetic: loggers are reset between tests and file handlers write only
into pytest's ``tmp_path``.
"""

import logging

import pytest
from utils import get_log_level, setup_logger, validate_config


@pytest.fixture(autouse=True)
def reset_loggers():
    """Ensure each test starts with clean logger state."""
    names = []
    for record in list(logging.root.manager.loggerDict.items()):
        name, obj = record
        if isinstance(obj, logging.Logger) and name.startswith("testu_"):
            names.append(name)
    yield
    for name in names:
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)


class TestSetupLogger:
    """Test cases for setup_logger function."""

    def test_setup_logger_returns_logger(self):
        """Test that setup_logger returns a logger instance."""
        logger = setup_logger("testu_basic")
        assert logger is not None
        assert logger.name == "testu_basic"

    @pytest.mark.parametrize(
        "level,expected",
        [("DEBUG", 10), ("INFO", 20), ("WARNING", 30), ("ERROR", 40)],
    )
    def test_setup_logger_levels(self, level, expected):
        """Test setup_logger maps level names correctly."""
        logger = setup_logger(f"testu_{level}", level)
        assert logger.level == expected

    def test_setup_logger_default_level(self):
        """Test setup_logger uses INFO as default."""
        logger = setup_logger("testu_default")
        assert logger.level == 20

    def test_setup_logger_case_insensitive(self):
        """Test level names are case insensitive."""
        logger = setup_logger("testu_lower", "debug")
        assert logger.level == 10

    def test_setup_logger_invalid_level(self):
        """Test invalid levels raise ValueError."""
        with pytest.raises(ValueError):
            setup_logger("testu_bad", "VERBOSE")

    def test_setup_logger_no_duplicate_handlers(self):
        """Test repeated calls do not stack duplicate handlers."""
        first = setup_logger("testu_dup")
        count = len(first.handlers)
        second = setup_logger("testu_dup")
        assert second is first
        assert len(second.handlers) == count

    def test_setup_logger_adds_file_handler(self, tmp_path):
        """Test log_file creates a file handler writing to it."""
        logfile = tmp_path / "sub" / "app.log"
        logger = setup_logger("testu_file", "INFO", str(logfile))
        logger.info("hello file")
        assert logfile.exists()
        assert "hello file" in logfile.read_text()

    def test_setup_logger_file_not_duplicated(self, tmp_path):
        """Test repeated calls with same file add one file handler."""
        logfile = tmp_path / "app.log"
        setup_logger("testu_file2", "INFO", str(logfile))
        logger = setup_logger("testu_file2", "INFO", str(logfile))
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1


class TestValidateConfig:
    """Test cases for validate_config function."""

    def test_all_keys_present(self):
        """Test validation passes when all required keys are present."""
        config = {"key1": "value1", "key2": "value2"}
        assert validate_config(config, ["key1", "key2"]) is True

    def test_missing_key(self):
        """Test validation fails when a required key is missing."""
        assert validate_config({"key1": "value1"}, ["key1", "key2"]) is False

    def test_empty_required(self):
        """Test validation passes with empty required keys list."""
        assert validate_config({"key1": "value1"}, []) is True

    def test_empty_config(self):
        """Test validation fails when config is empty but keys required."""
        assert validate_config({}, ["key1"]) is False

    def test_both_empty(self):
        """Test validation passes when both config and required are empty."""
        assert validate_config({}, []) is True

    def test_none_value_fails(self):
        """Test a present-but-None value is rejected."""
        assert validate_config({"key1": None}, ["key1"]) is False

    def test_blank_string_fails(self):
        """Test whitespace-only string values are rejected."""
        assert validate_config({"key1": "   "}, ["key1"]) is False

    def test_non_string_values_ok(self):
        """Test falsy non-string values (0, False) are accepted."""
        assert validate_config({"count": 0, "flag": False}, ["count"]) is True


class TestGetLogLevel:
    """Test cases for get_log_level helper."""

    def test_default_when_unset(self, monkeypatch):
        """Test INFO is returned when LOG_LEVEL is unset."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        assert get_log_level() == "INFO"

    def test_reads_env(self, monkeypatch):
        """Test valid LOG_LEVEL from environment is used."""
        monkeypatch.setenv("LOG_LEVEL", "debug")
        assert get_log_level() == "DEBUG"

    def test_invalid_falls_back(self, monkeypatch):
        """Test invalid LOG_LEVEL falls back to the default."""
        monkeypatch.setenv("LOG_LEVEL", "LOUD")
        assert get_log_level(default="WARNING") == "WARNING"
