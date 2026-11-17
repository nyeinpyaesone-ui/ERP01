"""Enforce positive quantities and bounded discounts in order items."""

from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):
    dependencies = [("sales", "0001_initial")]

    operations = [
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
