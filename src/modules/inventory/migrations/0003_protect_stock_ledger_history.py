"""Protect ledger history from product or warehouse deletion."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0002_stock_reserved_constraint")]

    operations = [
        migrations.AlterField(
            model_name="stockmovement",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="movements",
                to="inventory.product",
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="movements",
                to="inventory.warehouse",
            ),
        ),
    ]
