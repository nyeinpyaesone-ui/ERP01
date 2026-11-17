"""Inventory models with a transactional and immutable stock ledger."""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Q


class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Warehouses"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    reorder_level = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["sku"]), models.Index(fields=["category"])]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def total_stock(self):
        return sum(stock.quantity for stock in self.stock_levels.all())


class StockLevel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_levels")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_levels")
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    last_counted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "warehouse"]
        ordering = ["warehouse", "product"]
        constraints = [
            models.CheckConstraint(
                check=Q(quantity__gte=F("reserved_quantity")),
                name="stock_reserved_lte_on_hand",
            )
        ]

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code}: {self.quantity}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity


class StockMovement(models.Model):
    """Immutable ledger record; stock changes commit atomically with the ledger."""

    MOVEMENT_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
        ("TRANSFER_IN", "Transfer In"),
        ("TRANSFER_OUT", "Transfer Out"),
        ("ADJUSTMENT", "Adjustment"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["warehouse", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.movement_type}: {self.product.sku} ({self.quantity})"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                "Stock movements are immutable; create a compensating movement."
            )

        valid_types = {value for value, _label in self.MOVEMENT_TYPES}
        if self.movement_type not in valid_types:
            raise ValidationError({"movement_type": "Unsupported movement type."})
        if self.movement_type != "ADJUSTMENT" and self.quantity == 0:
            raise ValidationError({"quantity": "Movement quantity must be non-zero."})
        if self.movement_type == "ADJUSTMENT" and self.quantity < 0:
            raise ValidationError({"quantity": "Adjustment must be an on-hand quantity."})

        # Lock product then warehouse in stable order. This serializes creation
        # of a missing StockLevel row and prevents concurrent overselling.
        Product.objects.select_for_update().get(pk=self.product_id)
        Warehouse.objects.select_for_update().get(pk=self.warehouse_id)
        stock, _created = StockLevel.objects.get_or_create(
            product_id=self.product_id,
            warehouse_id=self.warehouse_id,
            defaults={"quantity": 0, "reserved_quantity": 0},
        )
        stock = StockLevel.objects.select_for_update().get(pk=stock.pk)

        amount = abs(self.quantity)
        if self.movement_type in {"IN", "TRANSFER_IN"}:
            new_quantity = stock.quantity + amount
        elif self.movement_type in {"OUT", "TRANSFER_OUT"}:
            if amount > stock.available_quantity:
                raise ValidationError(
                    {"quantity": f"Insufficient available stock ({stock.available_quantity})."}
                )
            new_quantity = stock.quantity - amount
        else:
            if self.quantity < stock.reserved_quantity:
                raise ValidationError(
                    {"quantity": "On-hand quantity cannot be lower than reserved stock."}
                )
            new_quantity = self.quantity

        super().save(*args, **kwargs)
        stock.quantity = new_quantity
        stock.save(update_fields=["quantity", "updated_at"])
