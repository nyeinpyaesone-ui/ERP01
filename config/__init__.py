"""Configuration module for ERP01."""

import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"


class Config:
    """Application configuration manager.

    Loads values from a ``.env`` file (via python-dotenv) and process
    environment variables.  Values already present in the environment take
    precedence over the ``.env`` file unless ``override=True`` is passed.
    """

    def __init__(self, env_file: Optional[str] = None, override: bool = False):
        load_dotenv(env_file, override=override)

        self._settings: Dict[str, Any] = {}
        self._load_defaults()
        self._check_security()

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._settings = {
            "APP_NAME": os.getenv("APP_NAME", "ERP01"),
            "APP_ENV": os.getenv("APP_ENV", "development"),
            "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
            "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///erp01.db"),
            "SECRET_KEY": os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        }

    def _check_security(self) -> None:
        """Fail fast when unsafe defaults are used in production."""
        if (
            self._settings["APP_ENV"].lower() == "production"
            and self._settings["SECRET_KEY"] == DEFAULT_SECRET_KEY
        ):
            raise RuntimeError(
                "SECRET_KEY is using the insecure development default "
                "while APP_ENV=production. Set SECRET_KEY in your "
                "environment or .env file."
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value on this instance only.

        This does not modify ``os.environ`` or the ``.env`` file, so other
        ``Config`` instances created later will not see this change.
        """
        self._settings[key] = value

    def all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._settings.copy()

    def validate_required(self, keys) -> None:
        """Raise ValueError if any required key is missing or empty."""
        missing = [key for key in keys if not str(self._settings.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return a logger configured from environment settings."""
    resolved_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, str(resolved_level).upper(), logging.INFO))
    return logger
