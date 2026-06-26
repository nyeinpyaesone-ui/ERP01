"""
Sales and Customer Models
=========================
Core sales models for customers, orders, and order line items.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from src.modules.inventory.models import Product


class Customer(models.Model):
    """Represents a customer account for sales and CRM workflows."""

    CUSTOMER_TYPES = [
        ("INDIVIDUAL", "Individual"),
        ("BUSINESS", "Business"),
    ]

    name = models.CharField(max_length=200)
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default="BUSINESS",
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["customer_type"]),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Order(models.Model):
    """Customer order header with lifecycle status and totals."""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("FULFILLED", "Fulfilled"),
        ("CANCELLED", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )
    order_date = models.DateField(auto_now_add=True)
    requested_ship_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer", "-created_at"]),
        ]

    def __str__(self):
        return self.order_number

    @property
    def total_amount(self):
        """Calculate the current order total from all line items."""
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class OrderItem(models.Model):
    """Line item for a customer order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    class Meta:
        ordering = ["id"]
        unique_together = ["order", "product"]

    def __str__(self):
        return f"{self.order.order_number}: {self.product.sku} x {self.quantity}"

    @property
    def line_total(self):
        """Calculate the extended amount after line-level discount."""
        return (self.unit_price * self.quantity) - self.discount_amount
