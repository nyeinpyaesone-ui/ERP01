"""
Sales Management Module
============================
Handles customer orders, invoicing, and sales operations.
"""

__all__ = ['SalesService']


def get_sales_service():
    """Lazy loading of SalesService to avoid circular imports."""
    from src.modules.sales.services import SalesService
    return SalesService
