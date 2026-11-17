"""API viewsets for warehouse, product, stock position and stock ledger."""

from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser

from src.api.permissions import StaffOrReadOnly
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .models import Category, Product, StockLevel, StockMovement, Warehouse
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockAdjustmentSerializer,
    StockLevelSerializer,
    StockMovementSerializer,
    WarehouseSerializer,
)


class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = [StaffOrReadOnly]
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "address"]
    ordering_fields = ["name", "code", "created_at"]

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "DELETE",
            detail="Warehouses are retained for stock and movement history; deactivate instead.",
        )


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [StaffOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return super().get_queryset().annotate(children_count=Count("children"))


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [StaffOrReadOnly]
    queryset = Product.objects.select_related("category").prefetch_related("stock_levels").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["sku", "name", "description"]
    ordering_fields = ["name", "sku", "unit_price", "created_at"]

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "DELETE",
            detail="Products are retained for order and stock history; deactivate instead.",
        )

    @action(detail=True, methods=["get"])
    def stock_summary(self, request, pk=None):
        product = self.get_object()
        levels = StockLevel.objects.filter(product=product).select_related("warehouse")
        return Response({
            "product": ProductSerializer(product).data,
            "total_stock": sum(level.quantity for level in levels),
            "total_reserved": sum(level.reserved_quantity for level in levels),
            "warehouses": StockLevelSerializer(levels, many=True).data,
        })


class StockLevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockLevel.objects.select_related("product", "warehouse").all()
    serializer_class = StockLevelSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product", "warehouse"]
    ordering_fields = ["quantity", "updated_at"]

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        levels = StockLevel.objects.filter(
            quantity__lte=F("product__reorder_level")
        ).select_related("product", "warehouse")
        return Response(self.get_serializer(levels, many=True).data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Ledger is read-only; changes are only made through the command endpoint."""

    queryset = StockMovement.objects.select_related(
        "product", "warehouse"
    ).all().order_by("-created_at")
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product", "warehouse", "movement_type"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "adjust_stock":
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=["post"])
    def adjust_stock(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movement = serializer.save(performed_by=request.user.get_username())
        return Response(
            StockMovementSerializer(movement).data,
            status=status.HTTP_201_CREATED,
        )
