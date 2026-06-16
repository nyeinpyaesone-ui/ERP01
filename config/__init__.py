"""Configuration module for ERP01."""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Application configuration manager."""

    def __init__(self, env_file: Optional[str] = None):
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self._settings: Dict[str, Any] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._settings = {
            'APP_NAME': os.getenv('APP_NAME', 'ERP01'),
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
            'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///erp01.db'),
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._settings[key] = value

    def all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._settings.copy()
