from sqlalchemy import inspect, text

from app.database.connection import engine


def test_database_tables():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    expected_tables = {
        "departments",
        "employees",
        "customers",
        "categories",
        "products",
        "orders",
        "order_items",
        "payments",
    }

    assert set(tables) == expected_tables


def get_table_count(table_name: str) -> int:
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar_one()


def test_departments_count():
    assert get_table_count("departments") == 10


def test_employees_count():
    assert get_table_count("employees") == 20


def test_customers_count():
    assert get_table_count("customers") == 50


def test_categories_count():
    assert get_table_count("categories") == 20


def test_products_count():
    assert get_table_count("products") == 100


def test_orders_count():
    assert get_table_count("orders") == 200


def test_order_items_count():
    assert get_table_count("order_items") == 400


def test_payments_count():
    assert get_table_count("payments") == 200


def test_foreign_key_integrity():
    queries = [
        """
        SELECT COUNT(*)
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE d.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM employees e
        LEFT JOIN employees m ON e.manager_id = m.id
        WHERE e.manager_id IS NOT NULL
          AND m.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE c.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        WHERE c.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN employees e ON o.employee_id = e.id
        WHERE e.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.id
        WHERE o.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE p.id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM payments p
        LEFT JOIN orders o ON p.order_id = o.id
        WHERE o.id IS NULL
        """,
    ]

    with engine.connect() as connection:
        for query in queries:
            result = connection.execute(text(query))
            assert result.scalar_one() == 0


def test_order_subtotal_matches_order_items():
    query = """
        SELECT
            o.id,
            o.subtotal,
            COALESCE(SUM(oi.line_total), 0) AS items_total
        FROM orders o
        LEFT JOIN order_items oi
            ON oi.order_id = o.id
        GROUP BY o.id, o.subtotal
        HAVING o.subtotal != COALESCE(SUM(oi.line_total), 0)
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        inconsistent_orders = result.fetchall()

    assert inconsistent_orders == []


def test_order_item_amount_consistency():
    query = """
        SELECT id
        FROM order_items
        WHERE line_total != (
            quantity * unit_price - discount_amount
        )
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        inconsistent_items = result.fetchall()

    assert inconsistent_items == []
