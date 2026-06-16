"""
ERP01 - Enterprise Resource Planning System

Main entry point for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main application entry point."""
    app_name = os.getenv("APP_NAME", "ERP01")
    app_env = os.getenv("APP_ENV", "development")
    
    print(f"Starting {app_name} in {app_env} mode...")
    print("Application initialized successfully!")


if __name__ == "__main__":
    main()
