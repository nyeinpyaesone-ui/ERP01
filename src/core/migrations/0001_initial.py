"""Create the singleton business profile."""

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BusinessProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "singleton_key",
                    models.PositiveSmallIntegerField(
                        default=1, editable=False, unique=True
                    ),
                ),
                ("business_name", models.CharField(default="My Business", max_length=200)),
                ("legal_name", models.CharField(blank=True, max_length=200)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                ("tax_number", models.CharField(blank=True, max_length=80)),
                ("currency", models.CharField(default="MMK", max_length=3)),
                ("timezone", models.CharField(default="Asia/Yangon", max_length=64)),
                ("locale", models.CharField(default="my-MM", max_length=10)),
                ("updated_by", models.CharField(blank=True, max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AddConstraint(
            model_name="businessprofile",
            constraint=models.CheckConstraint(
                check=Q(singleton_key=1),
                name="business_profile_is_singleton",
            ),
        ),
    ]
