"""Regression tests for inventory ledger integrity."""

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from src.modules.inventory.models import (
    Category,
    Product,
    StockLevel,
    StockMovement,
    Warehouse,
)


@pytest.mark.django_db
def test_outbound_movement_cannot_consume_reserved_or_overdraw_stock():
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    category = Category.objects.create(name="Goods")
    product = Product.objects.create(
        sku="LEDGER-001", name="Ledger Item", category=category, unit_price="10.00"
    )
    StockLevel.objects.create(
        product=product, warehouse=warehouse, quantity=10, reserved_quantity=4
    )

    with pytest.raises(ValidationError):
        StockMovement.objects.create(
            product=product, warehouse=warehouse, movement_type="OUT",
            quantity=7, performed_by="tester",
        )

    level = StockLevel.objects.get(product=product, warehouse=warehouse)
    assert level.quantity == 10
    assert level.available_quantity == 6
    assert StockMovement.objects.count() == 0


@pytest.mark.django_db
def test_stock_movement_is_immutable_and_cannot_be_replayed():
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    category = Category.objects.create(name="Goods")
    product = Product.objects.create(
        sku="LEDGER-002", name="Ledger Item", category=category, unit_price="10.00"
    )
    movement = StockMovement.objects.create(
        product=product, warehouse=warehouse, movement_type="IN",
        quantity=12, performed_by="tester",
    )

    with pytest.raises(ValidationError):
        movement.save()

    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 12
    assert StockMovement.objects.count() == 1


@pytest.mark.django_db
def test_adjustment_cannot_reduce_on_hand_below_reservations():
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    category = Category.objects.create(name="Goods")
    product = Product.objects.create(
        sku="LEDGER-003", name="Ledger Item", category=category, unit_price="10.00"
    )
    StockLevel.objects.create(
        product=product, warehouse=warehouse, quantity=20, reserved_quantity=8
    )

    with pytest.raises(ValidationError):
        StockMovement.objects.create(
            product=product, warehouse=warehouse, movement_type="ADJUSTMENT",
            quantity=5, performed_by="tester",
        )

    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 20


@pytest.mark.django_db
def test_stock_ledger_api_does_not_allow_update_or_delete():
    user = get_user_model().objects.create_user("ledger-api-user", password="test")
    category = Category.objects.create(name="API Goods")
    product = Product.objects.create(
        sku="LEDGER-API", name="API Item", category=category, unit_price="10.00"
    )
    warehouse = Warehouse.objects.create(name="API Warehouse", code="API-WH")
    movement = StockMovement.objects.create(
        product=product, warehouse=warehouse, movement_type="IN",
        quantity=4, performed_by="tester",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/stock-movements/{movement.pk}/",
        {"quantity": 99},
        format="json",
    )
    assert response.status_code == 405
    response = client.delete(f"/api/stock-movements/{movement.pk}/")
    assert response.status_code == 405
    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 4
