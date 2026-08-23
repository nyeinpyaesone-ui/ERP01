"""
Inventory Service Layer - Encapsulates Business Logic
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone

from src.modules.inventory.models import Product, StockLevel, StockMovement
from src.core.events import event_bus

logger = logging.getLogger(__name__)


class InventoryService:
    """Service layer for inventory operations."""

    @staticmethod
    @transaction.atomic
    def adjust_stock(product_id: int, quantity_change: int, reason: str, reference: str = None) -> StockMovement:
        """
        Adjust stock level for a product.
        Triggers real-time events and creates movement records.
        """
        try:
            product = Product.objects.select_for_update().get(id=product_id)
            
            # Update stock level
            stock_level, created = StockLevel.objects.get_or_create(
                product=product,
                defaults={'quantity': 0, 'last_updated': timezone.now()}
            )
            
            old_quantity = stock_level.quantity
            new_quantity = old_quantity + quantity_change
            
            if new_quantity < 0:
                raise ValueError(f"Insufficient stock for {product.sku}. Available: {old_quantity}")
            
            stock_level.quantity = new_quantity
            stock_level.last_updated = timezone.now()
            stock_level.save()
            
            # Create movement record
            movement = StockMovement.objects.create(
                product=product,
                movement_type='ADJ' if quantity_change > 0 else 'REM',
                quantity=abs(quantity_change),
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                reason=reason,
                reference=reference
            )
            
            # Publish real-time event
            event_bus.publish('stock_adjusted', {
                'product_id': product.id,
                'sku': product.sku,
                'old_quantity': old_quantity,
                'new_quantity': new_quantity,
                'change': quantity_change,
                'movement_id': movement.id
            })
            
            # Check low stock threshold
            if new_quantity <= product.reorder_point:
                event_bus.publish('low_stock_alert', {
                    'product_id': product.id,
                    'sku': product.sku,
                    'current_quantity': new_quantity,
                    'reorder_point': product.reorder_point
                })
            
            logger.info(f"Stock adjusted for {product.sku}: {old_quantity} -> {new_quantity}")
            return movement
            
        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            raise
        except Exception as e:
            logger.error(f"Stock adjustment failed: {str(e)}")
            raise

    @staticmethod
    def get_stock_summary(product_id: int) -> Dict[str, Any]:
        """Get current stock summary for a product."""
        try:
            product = Product.objects.get(id=product_id)
            stock_level = StockLevel.objects.filter(product=product).first()
            
            return {
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'current_stock': stock_level.quantity if stock_level else 0,
                'reorder_point': product.reorder_point,
                'is_low_stock': (stock_level.quantity <= product.reorder_point) if stock_level else False
            }
        except Product.DoesNotExist:
            return {'error': 'Product not found'}
