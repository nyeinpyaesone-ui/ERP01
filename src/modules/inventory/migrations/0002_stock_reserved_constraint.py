"""Prevent reservations from exceeding on-hand inventory."""

from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):
    dependencies = [("inventory", "0001_initial")]

    operations = [
        migrations.AddConstraint(
            model_name="stocklevel",
            constraint=models.CheckConstraint(
                check=Q(quantity__gte=F("reserved_quantity")),
                name="stock_reserved_lte_on_hand",
            ),
        ),
    ]
