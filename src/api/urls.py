"""Versionless API routing for ERP01."""

from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    BusinessProfileAPIView,
    CurrentUserAPIView,
    DashboardSummaryAPIView,
    HealthCheckAPIView,
)

app_name = "api"

urlpatterns = [
    path("health/", HealthCheckAPIView.as_view(), name="health"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="current_user"),
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard"),
    path(
        "business-profile/",
        BusinessProfileAPIView.as_view(),
        name="business_profile",
    ),
    path(
        "",
        include(
            ("src.modules.inventory.urls", "inventory_legacy"),
            namespace="inventory-legacy",
        ),
    ),
    path("inventory/", include("src.modules.inventory.urls")),
    path("sales/", include("src.modules.sales.urls")),
]
