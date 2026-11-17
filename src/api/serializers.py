"""Serializers for shared ERP API resources."""

from rest_framework import serializers

from src.core.models import BusinessProfile


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = [
            "id", "business_name", "legal_name", "email", "phone", "address",
            "tax_number", "currency", "timezone", "locale", "updated_by",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "updated_by", "created_at", "updated_at"]
