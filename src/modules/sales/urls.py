"""
Sales Module URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, OrderItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemViewSet)

app_name = "sales"

urlpatterns = [
    path("", include(router.urls)),
]
