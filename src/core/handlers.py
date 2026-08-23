"""
Real-time Event Handlers - Connect Events to Actions
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def handle_stock_adjusted(payload: Dict[str, Any]):
    """Handle stock adjustment events."""
    logger.info(
        f"STOCK UPDATE: {payload['sku']} | "
        f"Qty: {payload['old_quantity']} -> {payload['new_quantity']} "
        f"({payload['change']:+d})"
    )
    # Could trigger: cache invalidation, analytics, notifications


def handle_low_stock_alert(payload: Dict[str, Any]):
    """Handle low stock alerts."""
    logger.warning(
        f"LOW STOCK ALERT: {payload['sku']} | "
        f"Current: {payload['current_quantity']} | "
        f"Reorder Point: {payload['reorder_point']}"
    )
    # Could trigger: email to procurement, auto-purchase order creation


def handle_order_created(payload: Dict[str, Any]):
    """Handle new order events."""
    logger.info(
        f"NEW ORDER: {payload['order_reference']} | "
        f"Customer: {payload['customer_id']} | "
        f"Total: ${payload['total_amount']} | "
        f"Items: {payload['items_count']}"
    )
    # Could trigger: warehouse notification, invoice generation


def handle_order_confirmed(payload: Dict[str, Any]):
    """Handle order confirmation events."""
    logger.info(
        f"ORDER CONFIRMED: {payload['order_reference']} | "
        f"Time: {payload['confirmed_at']}"
    )
    # Could trigger: shipping label generation, customer email


def handle_order_shipped(payload: Dict[str, Any]):
    """Handle order shipped events."""
    logger.info(
        f"ORDER SHIPPED: {payload['order_reference']} | "
        f"Time: {payload['shipped_at']}"
    )
    # Could trigger: tracking email to customer, delivery notification


# Register all handlers
def register_handlers():
    """Register event handlers with the event bus."""
    from src.core.events import event_bus
    
    event_bus.subscribe('stock_adjusted', handle_stock_adjusted)
    event_bus.subscribe('low_stock_alert', handle_low_stock_alert)
    event_bus.subscribe('order_created', handle_order_created)
    event_bus.subscribe('order_confirmed', handle_order_confirmed)
    event_bus.subscribe('order_shipped', handle_order_shipped)
    
    logger.info("All event handlers registered")
