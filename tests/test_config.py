"""Tests for configuration management.

These tests are hermetic: they never depend on a local ``.env`` file or
on ambient environment variables, only on values set explicitly via
``monkeypatch`` / temporary env files.
"""

import pytest
from config import DEFAULT_SECRET_KEY, Config


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    """Isolate tests from ambient env vars and any local .env file."""
    monkeypatch.chdir(tmp_path)
    for key in (
        "APP_NAME",
        "APP_ENV",
        "DEBUG",
        "DATABASE_URL",
        "SECRET_KEY",
        "LOG_LEVEL",
    ):
        monkeypatch.delenv(key, raising=False)


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self):
        """Test that Config initializes correctly."""
        config = Config()
        assert config is not None

    def test_defaults_when_no_env(self, tmp_path, monkeypatch):
        """Test built-in defaults apply when nothing is configured."""
        # Process environment must not leak into the assertion: dotenv's
        # load_dotenv() does not override existing variables, so we clear
        # every key Config reads.  We also point at an explicit (missing)
        # env file because python-dotenv's default search walks *up* from
        # the original working directory and would otherwise pick up a
        # developer's local /workspace/.env during pytest collection.
        for key in (
            "APP_NAME",
            "APP_ENV",
            "DEBUG",
            "DATABASE_URL",
            "SECRET_KEY",
            "LOG_LEVEL",
        ):
            monkeypatch.delenv(key, raising=False)
        missing_env = tmp_path / "no-such.env"
        config = Config(env_file=str(missing_env))
        assert config.get("APP_NAME") == "ERP01"
        assert config.get("APP_ENV") == "development"
        assert config.get("DEBUG") is False
        assert config.get("DATABASE_URL") == "sqlite:///erp01.db"
        assert config.get("SECRET_KEY") == DEFAULT_SECRET_KEY
        assert config.get("LOG_LEVEL") == "INFO"

    def test_reads_environment_variables(self, monkeypatch):
        """Test values come from process environment."""
        monkeypatch.setenv("APP_NAME", "CustomApp")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        config = Config()
        assert config.get("APP_NAME") == "CustomApp"
        assert config.get("LOG_LEVEL") == "DEBUG"

    def test_debug_parsed_as_boolean(self, monkeypatch):
        """Test DEBUG string is parsed into a boolean."""
        monkeypatch.setenv("DEBUG", "True")
        assert Config().get("DEBUG") is True
        monkeypatch.setenv("DEBUG", "false")
        assert Config().get("DEBUG") is False

    def test_reads_env_file(self, tmp_path):
        """Test values can be loaded from an explicit env file."""
        env_file = tmp_path / "test.env"
        env_file.write_text("APP_NAME=FileApp\nLOG_LEVEL=WARNING\n")
        config = Config(env_file=str(env_file))
        assert config.get("APP_NAME") == "FileApp"
        assert config.get("LOG_LEVEL") == "WARNING"

    def test_env_wins_over_file_by_default(self, tmp_path, monkeypatch):
        """Test process environment takes precedence over .env file."""
        env_file = tmp_path / "test.env"
        env_file.write_text("APP_NAME=FileApp\n")
        monkeypatch.setenv("APP_NAME", "EnvApp")
        config = Config(env_file=str(env_file))
        assert config.get("APP_NAME") == "EnvApp"

    def test_override_flag_lets_file_win(self, tmp_path, monkeypatch):
        """Test override=True makes the .env file take precedence."""
        env_file = tmp_path / "test.env"
        env_file.write_text("APP_NAME=FileApp\n")
        monkeypatch.setenv("APP_NAME", "EnvApp")
        config = Config(env_file=str(env_file), override=True)
        assert config.get("APP_NAME") == "FileApp"

    def test_get_optional_config_with_default(self):
        """Test getting optional config with default value."""
        config = Config()
        value = config.get("NON_EXISTENT_KEY", default="default_value")
        assert value == "default_value"

    def test_set_config_value_is_instance_local(self):
        """Test set() changes only this instance, not new instances."""
        config = Config()
        config.set("TEST_KEY", "test_value")
        assert config.get("TEST_KEY") == "test_value"
        # A separate instance must not see the change.
        assert Config().get("TEST_KEY") is None

    def test_all_config_values(self):
        """Test getting all configuration values."""
        all_values = Config().all()
        assert isinstance(all_values, dict)
        for key in ("APP_NAME", "DEBUG", "DATABASE_URL", "SECRET_KEY"):
            assert key in all_values

    def test_all_returns_copy(self):
        """Test all() returns a defensive copy."""
        config = Config()
        snapshot = config.all()
        snapshot["APP_NAME"] = "Mutated"
        assert config.get("APP_NAME") != "Mutated"

    def test_validate_required_passes(self):
        """Test validate_required accepts populated keys."""
        Config().validate_required(["APP_NAME", "DATABASE_URL"])

    def test_validate_required_fails_on_empty(self, monkeypatch):
        """Test validate_required rejects empty values."""
        monkeypatch.setenv("APP_NAME", "")
        with pytest.raises(ValueError):
            Config().validate_required(["APP_NAME"])

    def test_production_requires_real_secret_key(self, monkeypatch):
        """Test production mode refuses the insecure default key."""
        monkeypatch.setenv("APP_ENV", "production")
        with pytest.raises(RuntimeError):
            Config()

    def test_production_ok_with_custom_secret(self, monkeypatch):
        """Test production mode passes with a real secret key."""
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("SECRET_KEY", "a-real-secret")
        config = Config()
        assert config.get("SECRET_KEY") == "a-real-secret"
