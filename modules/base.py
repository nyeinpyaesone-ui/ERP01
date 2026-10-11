"""Base module for ERP01 components."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseModule(ABC):
    """Abstract base class for all ERP modules."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._initialized = False
        self.logger = logging.getLogger(f"erp01.modules.{name}")

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the module."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the main functionality of the module."""
        pass

    def validate(self) -> bool:
        """Validate module configuration."""
        return True

    def shutdown(self) -> None:
        """Clean up resources."""
        self._initialized = False
