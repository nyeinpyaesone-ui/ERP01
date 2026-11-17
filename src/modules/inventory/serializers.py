"""DRF serializers for inventory records and ledger commands."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Category, Product, StockLevel, StockMovement, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name", "code", "address", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "description", "children_count", "created_at"]
        read_only_fields = ["created_at"]

    def get_children_count(self, obj):
        annotated = getattr(obj, "children_count", None)
        return annotated if annotated is not None else obj.children.count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    total_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "description", "category", "category_name",
            "unit_price", "cost_price", "reorder_level", "is_active",
            "total_stock", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StockLevelSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = StockLevel
        fields = [
            "id", "product", "product_sku", "product_name", "warehouse",
            "warehouse_name", "quantity", "reserved_quantity",
            "available_quantity", "last_counted_at", "updated_at",
        ]
        read_only_fields = ["updated_at"]


class StockMovementSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id", "product", "product_sku", "product_name", "warehouse",
            "warehouse_name", "movement_type", "quantity", "reference",
            "notes", "performed_by", "created_at",
        ]
        read_only_fields = fields


class StockAdjustmentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    warehouse_id = serializers.IntegerField(min_value=1)
    movement_type = serializers.ChoiceField(choices=StockMovement.MOVEMENT_TYPES)
    quantity = serializers.IntegerField()
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        product_id = data["product_id"]
        warehouse_id = data["warehouse_id"]
        movement_type = data["movement_type"]
        quantity = data["quantity"]

        if not Product.objects.filter(pk=product_id, is_active=True).exists():
            raise serializers.ValidationError({"product_id": "Active product not found."})
        if not Warehouse.objects.filter(pk=warehouse_id, is_active=True).exists():
            raise serializers.ValidationError({"warehouse_id": "Active warehouse not found."})
        if movement_type != "ADJUSTMENT" and quantity == 0:
            raise serializers.ValidationError({"quantity": "Quantity must be non-zero."})
        if movement_type == "ADJUSTMENT" and quantity < 0:
            raise serializers.ValidationError({"quantity": "Adjustment quantity cannot be negative."})

        level = StockLevel.objects.filter(
            product_id=product_id, warehouse_id=warehouse_id
        ).first()
        reserved = level.reserved_quantity if level else 0
        available = level.available_quantity if level else 0

        if movement_type in {"OUT", "TRANSFER_OUT"} and abs(quantity) > available:
            raise serializers.ValidationError({"quantity": "Insufficient available stock."})
        if movement_type == "ADJUSTMENT" and quantity < reserved:
            raise serializers.ValidationError(
                {"quantity": "Adjustment cannot reduce stock below reserved quantity."}
            )
        return data

    def create(self, validated_data):
        try:
            return StockMovement.objects.create(**validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"quantity": exc.messages}) from exc
