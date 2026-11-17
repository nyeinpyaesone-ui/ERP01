"""Shared authenticated API endpoints for the ERP application."""

from decimal import Decimal

from django.db import DatabaseError, connection
from django.db.models import DecimalField, ExpressionWrapper, F, IntegerField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from src.core.models import BusinessProfile
from src.modules.inventory.models import Product
from src.modules.sales.models import Customer, Order, OrderItem
from src.modules.sales.serializers import OrderSerializer

from .serializers import BusinessProfileSerializer


class HealthCheckAPIView(APIView):
    """Database-backed liveness/readiness endpoint."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            connection.ensure_connection()
        except DatabaseError:
            return Response(
                {"status": "unavailable", "database": "unavailable"},
                status=503,
            )
        return Response({"status": "ok", "database": "ok"})


class CurrentUserAPIView(APIView):
    """Return the authenticated user and Django group memberships."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.pk,
                "username": user.get_username(),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "groups": list(
                    user.groups.order_by("name").values_list("name", flat=True)
                ),
            }
        )


class BusinessProfileAPIView(generics.RetrieveUpdateAPIView):
    """All authenticated users may read; only staff may update the profile."""

    serializer_class = BusinessProfileSerializer
    queryset = BusinessProfile.objects.all()

    def get_permissions(self):
        permission = (
            permissions.IsAdminUser
            if self.request.method not in permissions.SAFE_METHODS
            else permissions.IsAuthenticated
        )
        return [permission()]

    def get_object(self):
        profile, _created = BusinessProfile.objects.get_or_create(
            singleton_key=1,
            defaults={"business_name": "My Business"},
        )
        return profile

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.get_username())


class DashboardSummaryAPIView(APIView):
    """Metrics derived from live committed ERP records, not demo constants."""

    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def sales_total(queryset):
        line_total = ExpressionWrapper(
            (F("unit_price") * F("quantity")) - F("discount_amount"),
            output_field=DecimalField(max_digits=22, decimal_places=2),
        )
        return queryset.aggregate(
            total=Coalesce(
                Sum(line_total),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=22, decimal_places=2),
            )
        )["total"]

    def get(self, request):
        today = timezone.localdate()
        month_start = today.replace(day=1)
        # This is fulfilled sales value, not cash received: ERP01 does not yet
        # implement customer payment allocation or a cashbook.
        fulfilled_lines = OrderItem.objects.filter(order__status="FULFILLED")

        low_stock_count = (
            Product.objects.filter(is_active=True)
            .annotate(
                stock_total=Coalesce(
                    Sum("stock_levels__quantity"),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
            .filter(stock_total__lte=F("reorder_level"))
            .count()
        )

        profile = BusinessProfile.objects.filter(singleton_key=1).first()
        recent_orders = (
            Order.objects.select_related("customer")
            .prefetch_related("items__product")
            .order_by("-created_at")[:5]
        )

        return Response(
            {
                "as_of": timezone.now(),
                "currency": profile.currency if profile else "MMK",
                "fulfilled_sales_today": self.sales_total(
                    fulfilled_lines.filter(order__order_date=today)
                ),
                "fulfilled_sales_this_month": self.sales_total(
                    fulfilled_lines.filter(order__order_date__gte=month_start)
                ),
                "orders_today": Order.objects.filter(order_date=today).count(),
                "open_orders": Order.objects.filter(
                    status__in=("DRAFT", "SUBMITTED")
                ).count(),
                "customers": Customer.objects.filter(is_active=True).count(),
                "active_products": Product.objects.filter(is_active=True).count(),
                "low_stock_products": low_stock_count,
                "recent_orders": OrderSerializer(recent_orders, many=True).data,
            }
        )
