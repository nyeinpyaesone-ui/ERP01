"""
Sales Service Layer - Encapsulates Order Business Logic
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone

from src.modules.sales.models import Customer, Order, OrderItem
from src.modules.inventory.models import Product
from src.modules.inventory.services import InventoryService
from src.core.events import event_bus

logger = logging.getLogger(__name__)


class SalesService:
    """Service layer for sales operations."""

    @staticmethod
    @transaction.atomic
    def create_order(customer_id: int, items: List[Dict[str, Any]], reference: str = None) -> Order:
        """
        Create a new order with inventory reservation.
        items: [{'product_id': 1, 'quantity': 5, 'unit_price': 10.00}, ...]
        """
        try:
            customer = Customer.objects.get(id=customer_id)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                status='PENDING',
                reference=reference or f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            total_amount = Decimal('0.00')
            
            # Process each line item
            for item_data in items:
                product = Product.objects.select_for_update().get(id=item_data['product_id'])
                quantity = item_data['quantity']
                unit_price = Decimal(str(item_data.get('unit_price', product.price)))
                
                # Check stock availability
                stock_summary = InventoryService.get_stock_summary(product.id)
                if stock_summary['current_stock'] < quantity:
                    raise ValueError(f"Insufficient stock for {product.sku}. Required: {quantity}, Available: {stock_summary['current_stock']}")
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=quantity * unit_price
                )
                
                total_amount += order_item.subtotal
                
                # Reserve inventory (adjust stock)
                InventoryService.adjust_stock(
                    product_id=product.id,
                    quantity_change=-quantity,
                    reason=f"Order {order.reference} - Item {order_item.id}",
                    reference=order.reference
                )
            
            # Update order totals
            order.total_amount = total_amount
            order.status = 'CONFIRMED'
            order.save()
            
            # Publish order created event
            event_bus.publish('order_created', {
                'order_id': order.id,
                'order_reference': order.reference,
                'customer_id': customer.id,
                'total_amount': str(total_amount),
                'items_count': len(items)
            })
            
            logger.info(f"Order {order.reference} created successfully. Total: {total_amount}")
            return order
            
        except Customer.DoesNotExist:
            logger.error(f"Customer {customer_id} not found")
            raise
        except Product.DoesNotExist as e:
            logger.error(f"Product not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            raise

    @staticmethod
    @transaction.atomic
    def confirm_order(order_id: int) -> Order:
        """Confirm a pending order."""
        try:
            order = Order.objects.select_for_update().get(id=order_id)
            
            if order.status != 'PENDING':
                raise ValueError(f"Order {order.reference} is not in PENDING status")
            
            order.status = 'CONFIRMED'
            order.confirmed_at = timezone.now()
            order.save()
            
            event_bus.publish('order_confirmed', {
                'order_id': order.id,
                'order_reference': order.reference,
                'confirmed_at': order.confirmed_at.isoformat()
            })
            
            logger.info(f"Order {order.reference} confirmed")
            return order
            
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found")
            raise
        except Exception as e:
            logger.error(f"Order confirmation failed: {str(e)}")
            raise

    @staticmethod
    @transaction.atomic
    def ship_order(order_id: int) -> Order:
        """Mark order as shipped."""
        try:
            order = Order.objects.get(id=order_id)
            
            if order.status != 'CONFIRMED':
                raise ValueError(f"Order {order.reference} must be CONFIRMED before shipping")
            
            order.status = 'SHIPPED'
            order.shipped_at = timezone.now()
            order.save()
            
            event_bus.publish('order_shipped', {
                'order_id': order.id,
                'order_reference': order.reference,
                'shipped_at': order.shipped_at.isoformat()
            })
            
            logger.info(f"Order {order.reference} shipped")
            return order
            
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found")
            raise
        except Exception as e:
            logger.error(f"Order shipping failed: {str(e)}")
            raise

    @staticmethod
    def get_order_summary(order_id: int) -> Dict[str, Any]:
        """Get detailed order summary."""
        try:
            order = Order.objects.prefetch_related('items__product').get(id=order_id)
            
            items_summary = [
                {
                    'product_sku': item.product.sku,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'subtotal': str(item.subtotal)
                }
                for item in order.items.all()
            ]
            
            return {
                'order_id': order.id,
                'reference': order.reference,
                'customer_name': order.customer.name,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'items': items_summary,
                'created_at': order.created_at.isoformat(),
                'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
                'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None
            }
        except Order.DoesNotExist:
            return {'error': 'Order not found'}
