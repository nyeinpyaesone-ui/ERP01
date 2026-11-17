"""PostgreSQL-only tests for database-enforced ledger immutability."""

import pytest
from django.db import DatabaseError, connection, transaction

from src.modules.inventory.models import Category, Product, StockMovement, Warehouse


@pytest.mark.django_db
@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Database triggers are installed on PostgreSQL deployments.",
)
def test_bulk_update_and_delete_cannot_rewrite_stock_ledger():
    warehouse = Warehouse.objects.create(name="Trigger Warehouse", code="TRG-WH")
    category = Category.objects.create(name="Trigger Category")
    product = Product.objects.create(
        sku="TRIGGER-LEDGER",
        name="Trigger Ledger Item",
        category=category,
        unit_price="10.00",
    )
    movement = StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type="IN",
        quantity=7,
        performed_by="test",
    )

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            StockMovement.objects.filter(pk=movement.pk).update(quantity=99)

    with pytest.raises(DatabaseError):
        with transaction.atomic():
            StockMovement.objects.filter(pk=movement.pk).delete()

    movement.refresh_from_db()
    assert movement.quantity == 7
