"""PostgreSQL-only tests for order and order-item database guards."""

import pytest
from django.db import DatabaseError, connection, transaction

from src.modules.inventory.models import Category, Product
from src.modules.sales.models import Customer, Order, OrderItem


@pytest.mark.django_db
@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Database triggers are installed on PostgreSQL deployments.",
)
def test_order_status_cannot_skip_lifecycle_states():
    customer = Customer.objects.create(
        name="Workflow Guard Customer",
        email="workflow-guard@example.test",
    )
    order = Order.objects.create(
        customer=customer,
        order_number="SO-DB-GUARD",
    )

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            Order.objects.filter(pk=order.pk).update(status="FULFILLED")

    order.refresh_from_db()
    assert order.status == "DRAFT"


@pytest.mark.django_db
@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Database triggers are installed on PostgreSQL deployments.",
)
def test_order_lines_cannot_be_changed_after_submission():
    category = Category.objects.create(name="Guard Goods")
    product = Product.objects.create(
        sku="GUARD-ITEM",
        name="Guard Item",
        category=category,
        unit_price="5.00",
    )
    customer = Customer.objects.create(
        name="Order Guard Customer",
        email="order-guard@example.test",
    )
    order = Order.objects.create(
        customer=customer,
        order_number="SO-LINE-GUARD",
    )
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price="5.00",
    )
    order.status = "SUBMITTED"
    order.save(update_fields=["status", "updated_at"])

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            OrderItem.objects.filter(pk=item.pk).update(quantity=2)

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            OrderItem.objects.filter(pk=item.pk).delete()

    item.refresh_from_db()
    assert item.quantity == 1
