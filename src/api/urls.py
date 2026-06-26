"""
API URL Configuration
"""

from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

app_name = "api"

urlpatterns = [
    # Authentication endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Backward-compatible inventory endpoints
    path(
        "",
        include(
            ("src.modules.inventory.urls", "inventory_legacy"),
            namespace="inventory-legacy",
        ),
    ),
    # Module API endpoints
    path("inventory/", include("src.modules.inventory.urls")),
    # path('hr/', include('src.modules.hr.api.urls')),
    # path('finance/', include('src.modules.finance.api.urls')),
    path("sales/", include("src.modules.sales.urls")),
    # path('procurement/', include('src.modules.procurement.api.urls')),
    # path('manufacturing/', include('src.modules.manufacturing.api.urls')),
]
