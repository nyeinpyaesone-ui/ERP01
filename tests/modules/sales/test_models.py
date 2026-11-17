"""Tests for sales and customer models."""

import pytest

from src.modules.inventory.models import Category, Product
from src.modules.sales.models import Customer, Order, OrderItem


@pytest.mark.django_db
def test_order_total_amount_sums_line_totals():
    category = Category.objects.create(name="Finished Goods")
    product = Product.objects.create(
        sku="FG-001",
        name="Finished Good",
        category=category,
        unit_price="12.50",
        cost_price="7.00",
    )
    customer = Customer.objects.create(
        name="Acme Corporation",
        email="buyer@acme.example",
    )
    order = Order.objects.create(customer=customer, order_number="SO-1001")
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price="12.50",
        discount_amount="5.00",
    )

    assert order.total_amount == 20
