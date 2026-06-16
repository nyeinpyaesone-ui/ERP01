"""Tests for configuration management."""
import os
import pytest
from config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self):
        """Test that Config initializes correctly."""
        config = Config()
        assert config is not None

    def test_get_app_name(self):
        """Test getting application name."""
        config = Config()
        app_name = config.get('APP_NAME')
        assert app_name is not None
        assert isinstance(app_name, str)

    def test_get_debug_mode(self):
        """Test getting debug mode setting."""
        config = Config()
        debug = config.get('DEBUG')
        assert debug is not None
        # Should be a boolean
        assert isinstance(debug, bool)

    def test_get_log_level(self):
        """Test getting log level."""
        config = Config()
        log_level = config.get('LOG_LEVEL')
        assert log_level is not None
        assert isinstance(log_level, str)
        assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def test_get_database_url(self):
        """Test getting database URL."""
        config = Config()
        db_url = config.get('DATABASE_URL')
        assert db_url is not None
        assert isinstance(db_url, str)
        assert '://' in db_url

    def test_get_secret_key(self):
        """Test getting secret key."""
        config = Config()
        secret_key = config.get('SECRET_KEY')
        assert secret_key is not None
        assert isinstance(secret_key, str)

    def test_get_optional_config_with_default(self):
        """Test getting optional config with default value."""
        config = Config()
        value = config.get('NON_EXISTENT_KEY', default='default_value')
        assert value == 'default_value'

    def test_set_config_value(self):
        """Test setting a configuration value."""
        config = Config()
        config.set('TEST_KEY', 'test_value')
        assert config.get('TEST_KEY') == 'test_value'

    def test_all_config_values(self):
        """Test getting all configuration values."""
        config = Config()
        all_values = config.all()
        assert all_values is not None
        assert isinstance(all_values, dict)
        assert 'APP_NAME' in all_values
        assert 'DEBUG' in all_values
        assert 'DATABASE_URL' in all_values
