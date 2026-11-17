"""
Sales Module Views
==================
API views for customers and customer order workflows.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Customer, Order, OrderItem
from .serializers import (CustomerSerializer, OrderItemSerializer,
                          OrderSerializer)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for customer account management."""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["customer_type", "is_active"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["name", "created_at"]


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for sales order management."""

    queryset = Order.objects.select_related("customer").prefetch_related(
        "items__product"
    )
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["customer", "status"]
    search_fields = ["order_number", "customer__name", "customer__email"]
    ordering_fields = ["order_date", "created_at", "updated_at"]

    def perform_create(self, serializer):
        """Persist the username that created the order when authenticated."""
        username = getattr(self.request.user, "username", "") or ""
        serializer.save(created_by=username)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        """Add a product line to an order."""
        order = self.get_object()
        serializer = OrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(order=order)
        return Response(OrderItemSerializer(item).data, status=status.HTTP_201_CREATED)


class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing order line items directly."""

    queryset = OrderItem.objects.select_related("order", "product").all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["order", "product"]
    ordering_fields = ["id", "quantity", "unit_price"]
