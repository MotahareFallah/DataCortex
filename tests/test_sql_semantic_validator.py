import pytest

from app.database.sql_semantic_validator import (
    SemanticSQLValidationError,
    validate_sql_semantics,
)


def test_category_name_must_not_be_compared_with_product_name():
    sql = """
    SELECT c.name
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE p.name = 'Electronics'
    GROUP BY c.name
    ORDER BY SUM(oi.line_total) DESC
    LIMIT 1
    """

    with pytest.raises(SemanticSQLValidationError):
        validate_sql_semantics(
            sql=sql,
            question="Which customer spent the most on Electronics last year?",
        )


def test_category_name_filter_using_category_table_is_allowed():
    sql = """
    SELECT c.name
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    JOIN categories cat ON p.category_id = cat.id
    WHERE cat.name = 'Electronics'
    GROUP BY c.name
    ORDER BY SUM(oi.line_total) DESC
    LIMIT 1
    """

    validate_sql_semantics(
        sql=sql,
        question="Which customer spent the most on Electronics last year?",
    )


def test_product_name_filter_is_allowed_for_product_question():
    sql = """
    SELECT p.name
    FROM products p
    WHERE p.name = 'Laptop'
    """

    validate_sql_semantics(
        sql=sql,
        question="Which product is named Laptop?",
    )


def test_unrelated_question_is_not_rejected():
    sql = """
    SELECT COUNT(*)
    FROM orders
    """

    validate_sql_semantics(
        sql=sql,
        question="How many orders are there?",
    )
