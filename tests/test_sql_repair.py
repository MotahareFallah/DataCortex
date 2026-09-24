from app.database.sql_repair import repair_column_table_reference

SCHEMA = {
    "orders": {
        "id",
        "customer_id",
        "ordered_at",
        "subtotal",
        "total_amount",
    },
    "order_items": {
        "id",
        "order_id",
        "product_id",
        "line_total",
    },
    "products": {
        "id",
        "name",
        "category_id",
    },
}


def test_repair_column_with_wrong_table_alias():
    sql = """
    SELECT c.name, SUM(o.line_total) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    GROUP BY c.name
    ORDER BY total_spent DESC
    LIMIT 1
    """

    repaired_sql = repair_column_table_reference(
        sql=sql,
        schema=SCHEMA,
    )

    assert "SUM(oi.line_total)" in repaired_sql
    assert "SUM(o.line_total)" not in repaired_sql


def test_valid_column_reference_is_not_changed():
    sql = """
    SELECT SUM(oi.line_total) AS total_spent
    FROM order_items oi
    """

    repaired_sql = repair_column_table_reference(
        sql=sql,
        schema=SCHEMA,
    )

    assert "SUM(oi.line_total)" in repaired_sql


def test_ambiguous_column_is_not_changed():
    schema = {
        "orders": {"id", "customer_id"},
        "order_items": {"id", "order_id"},
    }

    sql = """
    SELECT o.id
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    """

    repaired_sql = repair_column_table_reference(
        sql=sql,
        schema=schema,
    )

    assert "o.id" in repaired_sql
