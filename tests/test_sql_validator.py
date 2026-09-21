import pytest

from app.database.sql_validator import (
    UnsafeSQLQueryError,
    validate_sql,
)


def test_select_query_is_allowed():
    validate_sql("SELECT * FROM products")


def test_select_with_where_is_allowed():
    validate_sql("SELECT id, name FROM products WHERE id = 1")


def test_insert_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("INSERT INTO products (name) VALUES ('test')")


def test_update_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("UPDATE products SET name = 'test'")


def test_delete_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("DELETE FROM products")


def test_drop_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("DROP TABLE products")


def test_alter_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("ALTER TABLE products ADD COLUMN test TEXT")


def test_truncate_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("TRUNCATE TABLE products")


def test_empty_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("")


def test_multiple_statements_are_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("SELECT * FROM products; DROP TABLE products")


def test_invalid_sql_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("SELECT FROM")


def test_forbidden_keyword_inside_string_is_allowed():
    validate_sql("SELECT 'DROP TABLE products' AS message")


def test_select_with_comment_is_allowed():
    validate_sql("SELECT id, name FROM products -- get product data")


def test_multiple_select_statements_are_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("SELECT * FROM products; SELECT * FROM customers")


def test_grant_query_is_rejected():
    with pytest.raises(UnsafeSQLQueryError):
        validate_sql("GRANT SELECT ON products TO public")


def test_select_with_cte_is_allowed():
    validate_sql(
        "WITH product_data AS ("
        "SELECT id, name FROM products"
        ") "
        "SELECT * FROM product_data"
    )
