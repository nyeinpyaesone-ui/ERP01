"""Tests for base module functionality."""

import pytest

from modules import BaseModule as ReExportedBaseModule
from modules.base import BaseModule


class ConcreteTestModule(BaseModule):
    """Concrete implementation of BaseModule for testing."""

    def initialize(self) -> bool:
        """Initialize the test module."""
        self._initialized = True
        return True

    def execute(self, *args, **kwargs):
        """Execute the test module functionality."""
        if not self._initialized:
            self.initialize()
        return {"status": "success", "result": "executed", "module": self.name}


class TestBaseModule:
    """Test cases for BaseModule class."""

    def test_base_module_initialization(self):
        """Test that BaseModule initializes correctly."""
        module = ConcreteTestModule("test_module")
        assert module is not None
        assert module.name == "test_module"

    def test_package_reexports_base_module(self):
        """Test modules package re-exports the same class."""
        assert ReExportedBaseModule is BaseModule

    def test_abstract_cannot_be_instantiated(self):
        """Test BaseModule itself cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseModule("nope")

    def test_has_logger(self):
        """Test every module gets a usable logger (scaffold templates
        rely on self.logger)."""
        module = ConcreteTestModule("logged")
        assert module.logger is not None
        assert module.logger.name.endswith("logged")
        # Logging must not raise.
        module.logger.info("ok")

    def test_base_module_initialize(self):
        """Test module initialization."""
        module = ConcreteTestModule("hr")
        assert module.initialize() is True
        assert module._initialized is True

    def test_base_module_execute_success(self):
        """Test successful module execution."""
        module = ConcreteTestModule("finance")
        module.initialize()
        result = module.execute()
        assert result["status"] == "success"
        assert "result" in result
        assert result["module"] == "finance"

    def test_base_module_execute_without_init(self):
        """Test module execution auto-initializes."""
        result = ConcreteTestModule("procurement").execute()
        assert result is not None
        assert result["status"] == "success"

    def test_base_module_shutdown(self):
        """Test module shutdown."""
        module = ConcreteTestModule("warehouse")
        module.initialize()
        assert module._initialized is True
        module.shutdown()
        assert module._initialized is False

    def test_base_module_multiple_instances(self):
        """Test creating multiple module instances."""
        module1 = ConcreteTestModule("module1")
        module2 = ConcreteTestModule("module2")
        assert module1.name != module2.name

    def test_base_module_validate(self):
        """Test configuration validation default."""
        assert ConcreteTestModule("config_test").validate() is True

    def test_base_module_with_config(self):
        """Test module with custom config."""
        config = {"key1": "value1", "key2": "value2"}
        module = ConcreteTestModule("custom_config", config=config)
        assert module.config == config
        assert module.config["key1"] == "value1"

    def test_base_module_default_config(self):
        """Test module without config gets an empty dict."""
        assert ConcreteTestModule("nocfg").config == {}
