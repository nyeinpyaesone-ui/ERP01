"""
Sales Module Serializers
========================
DRF serializers for customers, orders, and order line items.
"""

from rest_framework import serializers

from .models import Customer, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer account records."""

    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "customer_type",
            "email",
            "phone",
            "billing_address",
            "shipping_address",
            "is_active",
            "orders_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_orders_count(self, obj):
        return obj.orders.count() if hasattr(obj, "orders") else 0


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order line items."""

    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_sku",
            "product_name",
            "quantity",
            "unit_price",
            "discount_amount",
            "line_total",
        ]
        read_only_fields = ["order"]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for customer orders with nested read-only line items."""

    customer_name = serializers.CharField(source="customer.name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "order_number",
            "status",
            "order_date",
            "requested_ship_date",
            "notes",
            "created_by",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["order_date", "created_by", "created_at", "updated_at"]
