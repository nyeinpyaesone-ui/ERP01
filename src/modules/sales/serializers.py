"""Serializers for customer, order and order-line workflows."""

from decimal import Decimal

from rest_framework import serializers

from .models import Customer, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id", "name", "customer_type", "email", "phone",
            "billing_address", "shipping_address", "is_active",
            "orders_count", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_orders_count(self, obj):
        value = getattr(obj, "orders_count", None)
        return value if value is not None else obj.orders.count()


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False
    )
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "order", "product", "product_sku", "product_name",
            "quantity", "unit_price", "discount_amount", "line_total",
        ]
        read_only_fields = ["id", "product_sku", "product_name", "line_total"]

    def validate(self, attrs):
        order = attrs.get("order")
        if order is None:
            order = self.instance.order if self.instance else self.context.get("order")
        if order is None:
            raise serializers.ValidationError({"order": "An order is required."})
        if order.status != "DRAFT":
            raise serializers.ValidationError(
                {"order": "Order lines can only change while the order is a draft."}
            )

        quantity = attrs.get("quantity", self.instance.quantity if self.instance else None)
        unit_price = attrs.get(
            "unit_price", self.instance.unit_price if self.instance else None
        )
        discount = attrs.get(
            "discount_amount",
            self.instance.discount_amount if self.instance else Decimal("0.00"),
        )
        product = attrs.get("product", self.instance.product if self.instance else None)

        if quantity is not None and quantity < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be positive."})
        if unit_price is not None and unit_price < 0:
            raise serializers.ValidationError({"unit_price": "Price cannot be negative."})
        if discount < 0:
            raise serializers.ValidationError({"discount_amount": "Discount cannot be negative."})
        if quantity is not None and unit_price is not None and discount > unit_price * quantity:
            raise serializers.ValidationError(
                {"discount_amount": "Discount cannot exceed the line subtotal."}
            )
        if product is not None and not product.is_active:
            raise serializers.ValidationError({"product": "Inactive products cannot be sold."})
        if product is not None:
            existing_lines = OrderItem.objects.filter(order=order, product=product)
            if self.instance is not None:
                existing_lines = existing_lines.exclude(pk=self.instance.pk)
            if existing_lines.exists():
                raise serializers.ValidationError(
                    {"product": "This product already exists on the order; update quantities before submission."}
                )

        attrs["order"] = order
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id", "customer", "customer_name", "order_number", "status",
            "order_date", "requested_ship_date", "notes", "created_by",
            "items", "total_amount", "created_at", "updated_at",
        ]
        read_only_fields = [
            "status", "order_date", "created_by", "created_at", "updated_at",
        ]
