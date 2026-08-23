"""
Inventory Management Module
============================
Handles stock tracking, warehouse management, and inventory operations.
"""

__all__ = ['InventoryService']


def get_inventory_service():
    """Lazy loading of InventoryService to avoid circular imports."""
    from src.modules.inventory.services import InventoryService
    return InventoryService
