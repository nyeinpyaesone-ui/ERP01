"""Customer and sales-order endpoints with explicit transactional workflows."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.modules.inventory.models import Product, StockMovement, Warehouse

from .models import Customer, Order, OrderItem
from .serializers import CustomerSerializer, OrderItemSerializer, OrderSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["customer_type", "is_active"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return super().get_queryset().annotate(orders_count=Count("orders"))


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("customer").prefetch_related("items__product")
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["customer", "status"]
    search_fields = ["order_number", "customer__name", "customer__email"]
    ordering_fields = ["order_date", "created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.get_username())

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), pk=pk)
            if order.status != "DRAFT":
                raise serializers.ValidationError(
                    {"status": "Items can only be added to draft orders."}
                )
            serializer = OrderItemSerializer(
                data=request.data,
                context={**self.get_serializer_context(), "order": order},
            )
            serializer.is_valid(raise_exception=True)
            item = serializer.save(order=order)
        return Response(OrderItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update().prefetch_related("items"), pk=pk
            )
            if order.status != "DRAFT":
                raise serializers.ValidationError(
                    {"status": "Only draft orders can be submitted."}
                )
            if not order.items.exists():
                raise serializers.ValidationError(
                    {"items": "Add at least one item before submitting."}
                )
            order.status = "SUBMITTED"
            order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def fulfill(self, request, pk=None):
        warehouse_id = request.data.get("warehouse_id")
        if not warehouse_id:
            raise serializers.ValidationError(
                {"warehouse_id": "A warehouse is required for fulfilment."}
            )

        try:
            with transaction.atomic():
                order = get_object_or_404(
                    Order.objects.select_for_update().prefetch_related("items"), pk=pk
                )
                if order.status != "SUBMITTED":
                    raise serializers.ValidationError(
                        {"status": "Only submitted orders can be fulfilled."}
                    )
                items = list(order.items.all().order_by("product_id"))
                if not items:
                    raise serializers.ValidationError({"items": "Order has no items."})

                product_ids = sorted({item.product_id for item in items})
                list(
                    Product.objects.select_for_update()
                    .filter(pk__in=product_ids)
                    .order_by("pk")
                )
                warehouse = get_object_or_404(
                    Warehouse.objects.select_for_update(), pk=warehouse_id, is_active=True
                )
                for item in items:
                    StockMovement.objects.create(
                        product_id=item.product_id,
                        warehouse=warehouse,
                        movement_type="OUT",
                        quantity=item.quantity,
                        reference=order.order_number,
                        notes="Sales order fulfilment",
                        performed_by=request.user.get_username(),
                    )
                order.status = "FULFILLED"
                order.save(update_fields=["status", "updated_at"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"stock": exc.messages}) from exc

        order.refresh_from_db()
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), pk=pk)
            if order.status not in {"DRAFT", "SUBMITTED"}:
                raise serializers.ValidationError(
                    {"status": "Only draft or submitted orders can be cancelled."}
                )
            order.status = "CANCELLED"
            order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product").all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["order", "product"]
    ordering_fields = ["id", "quantity", "unit_price"]
