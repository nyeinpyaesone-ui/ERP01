"""Regression tests for transactional sales order workflow."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.modules.inventory.models import Category, Product, StockLevel, Warehouse
from src.modules.sales.models import Customer, Order, OrderItem


@pytest.mark.django_db
def test_fulfilment_deducts_stock_once_and_rejects_replay():
    user = get_user_model().objects.create_user("warehouse-user", password="not-used", is_staff=True)
    category = Category.objects.create(name="Goods")
    product = Product.objects.create(
        sku="SO-ITEM-001", name="Order Item", category=category, unit_price="25.00"
    )
    customer = Customer.objects.create(name="Customer One", email="one@example.test")
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    StockLevel.objects.create(product=product, warehouse=warehouse, quantity=9)
    order = Order.objects.create(customer=customer, order_number="SO-WORKFLOW-001")
    OrderItem.objects.create(
        order=order, product=product, quantity=3, unit_price="25.00"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/sales/orders/{order.pk}/submit/", {}, format="json"
    )
    assert response.status_code == 200

    response = client.post(
        f"/api/sales/orders/{order.pk}/fulfill/",
        {"warehouse_id": warehouse.pk},
        format="json",
    )
    assert response.status_code == 200

    level = StockLevel.objects.get(product=product, warehouse=warehouse)
    order.refresh_from_db()
    assert level.quantity == 6
    assert order.status == "FULFILLED"

    response = client.post(
        f"/api/sales/orders/{order.pk}/fulfill/",
        {"warehouse_id": warehouse.pk},
        format="json",
    )
    assert response.status_code == 400
    level.refresh_from_db()
    assert level.quantity == 6


@pytest.mark.django_db
def test_fulfilment_rolls_back_all_lines_when_stock_is_short():
    user = get_user_model().objects.create_user("short-stock-user", password="not-used", is_staff=True)
    category = Category.objects.create(name="Goods")
    first = Product.objects.create(
        sku="SO-ROLLBACK-1", name="First", category=category, unit_price="10.00"
    )
    second = Product.objects.create(
        sku="SO-ROLLBACK-2", name="Second", category=category, unit_price="20.00"
    )
    customer = Customer.objects.create(name="Customer Two", email="two@example.test")
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    StockLevel.objects.create(product=first, warehouse=warehouse, quantity=10)
    StockLevel.objects.create(product=second, warehouse=warehouse, quantity=1)
    order = Order.objects.create(customer=customer, order_number="SO-WORKFLOW-ROLLBACK")
    OrderItem.objects.create(order=order, product=first, quantity=2, unit_price="10.00")
    OrderItem.objects.create(order=order, product=second, quantity=5, unit_price="20.00")

    client = APIClient()
    client.force_authenticate(user=user)
    assert client.post(f"/api/sales/orders/{order.pk}/submit/", {}, format="json").status_code == 200

    response = client.post(
        f"/api/sales/orders/{order.pk}/fulfill/",
        {"warehouse_id": warehouse.pk},
        format="json",
    )
    assert response.status_code == 400
    assert StockLevel.objects.get(product=first, warehouse=warehouse).quantity == 10
    assert StockLevel.objects.get(product=second, warehouse=warehouse).quantity == 1
    order.refresh_from_db()
    assert order.status == "SUBMITTED"


@pytest.mark.django_db
def test_dashboard_returns_database_backed_metrics():
    user = get_user_model().objects.create_user("dashboard-user", password="not-used", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/dashboard/")
    assert response.status_code == 200
    assert response.data["currency"] == "MMK"
    assert response.data["customers"] == 0
    assert response.data["active_products"] == 0
    assert response.data["low_stock_products"] == 0
    assert "fulfilled_sales_this_month" in response.data


@pytest.mark.django_db
def test_order_status_cannot_be_patched_directly():
    user = get_user_model().objects.create_user("order-patch-user", password="not-used", is_staff=True)
    customer = Customer.objects.create(name="Patch Test", email="patch@example.test")
    order = Order.objects.create(customer=customer, order_number="SO-NO-PATCH")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/sales/orders/{order.pk}/",
        {"status": "FULFILLED"},
        format="json",
    )
    order.refresh_from_db()
    assert response.status_code == 200
    assert order.status == "DRAFT"
