"""Tests for shared authenticated ERP endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.core.models import BusinessProfile


@pytest.mark.django_db
def test_health_endpoint_is_public_and_reports_database():
    response = APIClient().get("/api/health/")
    assert response.status_code == 200
    assert response.data == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_business_profile_can_be_read_by_authenticated_user():
    user = get_user_model().objects.create_user("profile-reader", password="not-used")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/business-profile/")
    assert response.status_code == 200
    assert response.data["currency"] == "MMK"
    assert response.data["timezone"] == "Asia/Yangon"


@pytest.mark.django_db
def test_business_profile_update_requires_staff():
    user = get_user_model().objects.create_user("profile-writer", password="not-used")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/business-profile/",
        {"business_name": "Unauthorized Edit"},
        format="json",
    )
    assert response.status_code == 403
    assert not BusinessProfile.objects.filter(singleton_key=1).exists()


@pytest.mark.django_db
def test_staff_can_update_business_profile_and_audit_username():
    user = get_user_model().objects.create_user(
        "profile-admin", password="not-used", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/business-profile/",
        {"business_name": "Yangon Trading", "currency": "MMK"},
        format="json",
    )
    assert response.status_code == 200
    profile = BusinessProfile.objects.get(singleton_key=1)
    assert profile.business_name == "Yangon Trading"
    assert profile.updated_by == "profile-admin"
