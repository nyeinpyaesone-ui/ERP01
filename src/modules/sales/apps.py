"""
Sales Module Configuration
==========================
"""

from django.apps import AppConfig


class SalesConfig(AppConfig):
    """Configuration for the sales module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.modules.sales"
    verbose_name = "Sales and Customer Management"
