"""Utility functions for ERP01."""

import logging
from typing import Any, Dict


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up and return a logger instance.

    Args:
        name: Logger name.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
    """Validate that all required configuration keys are present.

    Args:
        config: Configuration dictionary to validate.
        required_keys: List of required keys.

    Returns:
        True if all required keys are present, False otherwise.
    """
    return all(key in config for key in required_keys)
