"""Tests for the gateway's static service registry and URL allowlist."""

import pytest

from gateway.core.discovery import ServiceRegistry


def test_registry_only_exposes_configured_module_names(monkeypatch):
    monkeypatch.setenv("SERVICE_INVENTORY_URL", "http://web:8000/api/inventory")
    monkeypatch.setenv(
        "SERVICE_INVENTORY_HEALTH_URL",
        "http://web:8000/api/health/",
    )
    registry = ServiceRegistry(["inventory"])
    registry.load_from_environment()

    endpoint = registry.get("INVENTORY")
    assert endpoint is not None
    assert endpoint.base_url == "http://web:8000/api/inventory"
    assert registry.public_status() == [{"name": "inventory", "configured": "true"}]


@pytest.mark.parametrize(
    "value",
    [
        "ftp://internal.example",
        "file:///etc/passwd",
        "http://user:password@service:8000",
        "http://service:8000/path?redirect=evil",
        "//evil.example",
    ],
)
def test_registry_rejects_unsafe_or_ambiguous_service_urls(monkeypatch, value):
    monkeypatch.setenv("SERVICE_FINANCE_URL", value)
    registry = ServiceRegistry(["finance"])
    with pytest.raises(ValueError):
        registry.load_from_environment()


def test_registry_does_not_allow_unconfigured_module(monkeypatch):
    monkeypatch.delenv("SERVICE_UNKNOWN_URL", raising=False)
    registry = ServiceRegistry(["unknown"])
    registry.load_from_environment()
    assert registry.get("unknown") is None
    assert registry.public_status() == []
