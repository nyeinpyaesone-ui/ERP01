"""
ERP01 - Enterprise Resource Planning System

Main entry point for the application.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import Config
from utils import setup_logger


def main():
    """Main application entry point."""
    # Initialize configuration
    config = Config()

    # Setup logging
    logger = setup_logger(__name__, config.get("LOG_LEVEL"))

    app_name = config.get("APP_NAME")
    app_env = os.getenv("APP_ENV", "development")
    use_web = os.getenv("USE_WEB", "False").lower() == "true"

    # Allow port override via environment
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))

    logger.info(f"Starting {app_name} in {app_env} mode...")

    if use_web:
        # Start web interface
        from web import create_app

        app = create_app(config)
        logger.info(f"Starting web interface on http://localhost:{port}")
        app.run(host="0.0.0.0", port=port, debug=config.get("DEBUG"))
    else:
        # Run in CLI mode
        logger.info("Application initialized successfully in CLI mode!")
        print(f"\n{app_name} - Enterprise Resource Planning System")
        print("=" * 50)
        print(f"Environment: {app_env}")
        print(f"Debug Mode: {config.get('DEBUG')}")
        print(f"Database: {config.get('DATABASE_URL')}")
        print("\nTo start the web interface, set USE_WEB=true in your .env file")
        print("Then run: python main.py\n")


if __name__ == "__main__":
    main()
