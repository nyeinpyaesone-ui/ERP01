"""Tests for main application entry point."""

from unittest.mock import patch
from main import main


class TestMain:
    """Test cases for main function."""

    @patch("main.os.getenv")
    def test_main_default_values(self, mock_getenv):
        """Test main with default environment values."""
        mock_getenv.side_effect = lambda key, default=None: default
        with patch("builtins.print") as mock_print:
            main()
            assert mock_print.call_count == 2

    @patch("main.os.getenv")
    def test_main_custom_app_name(self, mock_getenv):
        """Test main with custom app name."""
        mock_getenv.side_effect = lambda key, default=None: (
            "CustomApp" if key == "APP_NAME" else default
        )
        with patch("builtins.print") as mock_print:
            main()
            calls = [
                call for call in mock_print.call_args_list
                if "Starting CustomApp" in str(call)
            ]
            assert len(calls) > 0

    @patch("main.os.getenv")
    def test_main_production_mode(self, mock_getenv):
        """Test main in production mode."""
        mock_getenv.side_effect = lambda key, default=None: (
            "production" if key == "APP_ENV" else default
        )
        with patch("builtins.print") as mock_print:
            main()
            calls = [
                call for call in mock_print.call_args_list
                if "production mode" in str(call)
            ]
            assert len(calls) > 0
