"""Company-level configuration shared by ERP modules."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class BusinessProfile(models.Model):
    """Single-company identity and localization settings for this deployment."""

    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    business_name = models.CharField(max_length=200, default="My Business")
    legal_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=80, blank=True)
    currency = models.CharField(max_length=3, default="MMK")
    timezone = models.CharField(max_length=64, default="Asia/Yangon")
    locale = models.CharField(max_length=10, default="my-MM")
    updated_by = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                check=Q(singleton_key=1),
                name="business_profile_is_singleton",
            )
        ]

    def save(self, *args, **kwargs):
        if self.singleton_key != 1:
            raise ValidationError("Only one business profile is supported.")
        self.singleton_key = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name
