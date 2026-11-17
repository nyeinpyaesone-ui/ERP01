"""Django admin registration for core ERP configuration."""

from django.contrib import admin

from .models import BusinessProfile


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "currency", "timezone", "updated_at")
    readonly_fields = ("singleton_key", "created_at", "updated_at")
