"""Tests for sales API views."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.modules.sales.models import Customer, Order


@pytest.mark.django_db
def test_customer_api_creates_customer():
    user = get_user_model().objects.create_user("api-user", password="secret")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/sales/customers/",
        {
            "name": "Acme Corporation",
            "customer_type": "BUSINESS",
            "email": "buyer@acme.example",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Customer.objects.filter(email="buyer@acme.example").exists()


@pytest.mark.django_db
def test_order_api_records_authenticated_creator():
    user = get_user_model().objects.create_user("sales-user", password="secret")
    customer = Customer.objects.create(
        name="Acme Corporation",
        email="buyer@acme.example",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/sales/orders/",
        {
            "customer": customer.id,
            "order_number": "SO-1001",
            "status": "DRAFT",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Order.objects.get(order_number="SO-1001").created_by == "sales-user"
