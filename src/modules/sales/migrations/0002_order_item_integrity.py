"""Add order-item invariants after a non-destructive legacy-data preflight."""

from django.db import migrations, models
from django.db.models import F, Q


def verify_existing_order_items(apps, schema_editor):
    OrderItem = apps.get_model("sales", "OrderItem")
    invalid_count = OrderItem.objects.filter(
        Q(quantity__lt=1) | Q(discount_amount__gt=F("unit_price") * F("quantity"))
    ).count()
    if invalid_count:
        raise RuntimeError(
            "Cannot add sales order-item constraints: "
            f"{invalid_count} order lines have invalid quantities or discounts. "
            "Review and reconcile those rows before retrying this migration."
        )


class Migration(migrations.Migration):
    dependencies = [("sales", "0001_initial")]

    operations = [
        migrations.RunPython(verify_existing_order_items, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                check=Q(quantity__gte=1),
                name="sales_order_item_quantity_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                check=Q(discount_amount__lte=F("unit_price") * F("quantity")),
                name="sales_order_item_discount_lte_subtotal",
            ),
        ),
    ]
