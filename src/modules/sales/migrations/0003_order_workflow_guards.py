"""Enforce legal order state transitions and draft-only line edits in PostgreSQL."""

from django.db import migrations


FORWARD_SQL = """
CREATE OR REPLACE FUNCTION sales_guard_order_status_transition()
RETURNS trigger AS $$
BEGIN
    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'DRAFT' AND NEW.status IN ('SUBMITTED', 'CANCELLED'))
        OR
        (OLD.status = 'SUBMITTED' AND NEW.status IN ('FULFILLED', 'CANCELLED'))
    ) THEN
        RAISE EXCEPTION 'Invalid sales order state transition: % -> %',
            OLD.status, NEW.status
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sales_guard_order_item_draft_only()
RETURNS trigger AS $$
DECLARE
    parent_order_id bigint;
    parent_status varchar(20);
BEGIN
    IF TG_OP = 'DELETE' THEN
        parent_order_id := OLD.order_id;
    ELSE
        IF TG_OP = 'UPDATE' AND NEW.order_id <> OLD.order_id THEN
            RAISE EXCEPTION 'Order lines cannot be moved between orders.'
                USING ERRCODE = 'integrity_constraint_violation';
        END IF;
        parent_order_id := NEW.order_id;
    END IF;

    SELECT status INTO parent_status
    FROM sales_order
    WHERE id = parent_order_id
    FOR UPDATE;

    IF parent_status IS DISTINCT FROM 'DRAFT' THEN
        RAISE EXCEPTION 'Order lines may only be changed while the order is a draft.'
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sales_order_state_transition_guard ON sales_order;
CREATE TRIGGER sales_order_state_transition_guard
BEFORE UPDATE OF status ON sales_order
FOR EACH ROW
EXECUTE FUNCTION sales_guard_order_status_transition();

DROP TRIGGER IF EXISTS sales_order_item_draft_guard ON sales_orderitem;
CREATE TRIGGER sales_order_item_draft_guard
BEFORE INSERT OR UPDATE OR DELETE ON sales_orderitem
FOR EACH ROW
EXECUTE FUNCTION sales_guard_order_item_draft_only();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS sales_order_item_draft_guard ON sales_orderitem;
DROP TRIGGER IF EXISTS sales_order_state_transition_guard ON sales_order;
DROP FUNCTION IF EXISTS sales_guard_order_item_draft_only();
DROP FUNCTION IF EXISTS sales_guard_order_status_transition();
"""


def install_triggers(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(FORWARD_SQL)


def remove_triggers(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [("sales", "0002_order_item_integrity")]

    operations = [migrations.RunPython(install_triggers, remove_triggers)]
