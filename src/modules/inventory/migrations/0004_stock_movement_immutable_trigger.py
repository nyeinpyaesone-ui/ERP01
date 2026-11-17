"""Enforce inventory-ledger immutability in PostgreSQL, including bulk SQL writes."""

from django.db import migrations


FORWARD_SQL = """
CREATE OR REPLACE FUNCTION inventory_reject_stock_movement_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'Stock movement history is immutable; create a compensating movement.'
        USING ERRCODE = 'integrity_constraint_violation';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS inventory_stock_movement_immutable
    ON inventory_stockmovement;

CREATE TRIGGER inventory_stock_movement_immutable
BEFORE UPDATE OR DELETE ON inventory_stockmovement
FOR EACH ROW
EXECUTE FUNCTION inventory_reject_stock_movement_mutation();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS inventory_stock_movement_immutable
    ON inventory_stockmovement;
DROP FUNCTION IF EXISTS inventory_reject_stock_movement_mutation();
"""


def install_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(FORWARD_SQL)


def remove_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [("inventory", "0003_protect_stock_ledger_history")]

    operations = [migrations.RunPython(install_trigger, remove_trigger)]
