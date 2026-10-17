"""
ERP01 - Enterprise Resource Planning System

Main entry point for the application.
"""

from config import Config
from modules.base import BaseModule
from utils import setup_logger


class CoreModule(BaseModule):
    """Minimal built-in module proving the BaseModule wiring works."""

    def initialize(self) -> bool:
        """Mark the core module as initialized."""
        self.logger.info("Initializing %s module", self.name)
        self._initialized = True
        return True

    def execute(self, *args, **kwargs):
        """Run the core module bootstrap logic."""
        if not self._initialized:
            self.initialize()
        return {"status": "success", "module": self.name}


def main() -> int:
    """Main application entry point."""
    config = Config()
    logger = setup_logger(
        "erp01",
        level=config.get("LOG_LEVEL", "INFO"),
        log_file="logs/app.log",
    )

    app_name = config.get("APP_NAME", "ERP01")
    app_env = config.get("APP_ENV", "development")

    logger.info("Starting %s in %s mode...", app_name, app_env)
    core = CoreModule("core", config=config.all())
    core.execute()
    logger.info("Application initialized successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
