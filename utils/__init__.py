"""Utility functions for ERP01."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up and return a logger instance.

    The logger is idempotent: repeated calls with the same ``name`` will
    not attach duplicate handlers.  When ``log_file`` is given (and its
    parent directory exists or can be created), a file handler is added in
    addition to the stream handler, matching the ``logs/`` layout
    documented in ``docs/MAINTENANCE.md``.
    """
    normalized_level = str(level).upper()
    if normalized_level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid log level {level!r}; expected one of "
            f"{', '.join(VALID_LOG_LEVELS)}."
        )

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, normalized_level))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in logger.handlers
    ):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if log_file:
        target = Path(log_file)
        target.parent.mkdir(parents=True, exist_ok=True)
        already_open = any(
            isinstance(h, logging.FileHandler)
            and Path(h.baseFilename).resolve() == target.resolve()
            for h in logger.handlers
        )
        if not already_open:
            file_handler = logging.FileHandler(target)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def validate_config(config: Dict[str, Any], required_keys: Sequence[str]) -> bool:
    """Validate that all required keys are present and non-empty.

    A key counts as valid only when it exists and its value is neither
    ``None`` nor an empty/whitespace-only string.
    """
    for key in required_keys:
        if key not in config:
            return False
        value = config[key]
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
    return True


def get_log_level(default: str = "INFO") -> str:
    """Return the LOG_LEVEL from the environment, validated."""
    level = os.getenv("LOG_LEVEL", default).upper()
    return level if level in VALID_LOG_LEVELS else default
