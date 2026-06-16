"""Tests for utility functions."""
import pytest
from utils import setup_logger, validate_config


class TestSetupLogger:
    """Test cases for setup_logger function."""

    def test_setup_logger_returns_logger(self):
        """Test that setup_logger returns a logger instance."""
        logger = setup_logger('test_logger')
        assert logger is not None
        assert logger.name == 'test_logger'

    def test_setup_logger_with_debug_level(self):
        """Test setup_logger with DEBUG level."""
        logger = setup_logger('debug_logger', 'DEBUG')
        assert logger.level == 10  # DEBUG level value

    def test_setup_logger_with_info_level(self):
        """Test setup_logger with INFO level."""
        logger = setup_logger('info_logger', 'INFO')
        assert logger.level == 20  # INFO level value

    def test_setup_logger_with_warning_level(self):
        """Test setup_logger with WARNING level."""
        logger = setup_logger('warning_logger', 'WARNING')
        assert logger.level == 30  # WARNING level value

    def test_setup_logger_with_error_level(self):
        """Test setup_logger with ERROR level."""
        logger = setup_logger('error_logger', 'ERROR')
        assert logger.level == 40  # ERROR level value

    def test_setup_logger_default_level(self):
        """Test setup_logger uses INFO as default."""
        logger = setup_logger('default_logger')
        assert logger.level == 20  # INFO level value


class TestValidateConfig:
    """Test cases for validate_config function."""

    def test_validate_config_all_keys_present(self):
        """Test validation passes when all required keys are present."""
        config = {'key1': 'value1', 'key2': 'value2'}
        required = ['key1', 'key2']
        assert validate_config(config, required) is True

    def test_validate_config_missing_key(self):
        """Test validation fails when a required key is missing."""
        config = {'key1': 'value1'}
        required = ['key1', 'key2']
        assert validate_config(config, required) is False

    def test_validate_config_empty_required(self):
        """Test validation passes with empty required keys list."""
        config = {'key1': 'value1'}
        required = []
        assert validate_config(config, required) is True

    def test_validate_config_empty_config(self):
        """Test validation fails when config is empty but keys required."""
        config = {}
        required = ['key1']
        assert validate_config(config, required) is False

    def test_validate_config_both_empty(self):
        """Test validation passes when both config and required are empty."""
        config = {}
        required = []
        assert validate_config(config, required) is True
