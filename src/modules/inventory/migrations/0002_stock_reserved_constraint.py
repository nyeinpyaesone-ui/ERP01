"""Add the stock reservation invariant without silently repairing existing data."""

from django.db import migrations, models
from django.db.models import F, Q


def verify_existing_stock(apps, schema_editor):
    StockLevel = apps.get_model("inventory", "StockLevel")
    invalid_count = StockLevel.objects.filter(
        quantity__lt=F("reserved_quantity")
    ).count()
    if invalid_count:
        raise RuntimeError(
            "Cannot add stock_reserved_lte_on_hand: "
            f"{invalid_count} stock rows have reserved_quantity greater than quantity. "
            "Review and reconcile those rows before retrying this migration."
        )


class Migration(migrations.Migration):
    dependencies = [("inventory", "0001_initial")]

    operations = [
        migrations.RunPython(verify_existing_stock, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="stocklevel",
            constraint=models.CheckConstraint(
                check=Q(quantity__gte=F("reserved_quantity")),
                name="stock_reserved_lte_on_hand",
            ),
        ),
    ]
