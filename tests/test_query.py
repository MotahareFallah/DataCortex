from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.database.query import SQLExecutionError, execute_query
from app.database.sql_validator import UnsafeSQLQueryError


def test_execute_query_returns_columns():
    result = execute_query(
        """
        SELECT id, name
        FROM products
        ORDER BY id
        LIMIT 3
        """
    )

    assert result.columns == ["id", "name"]


def test_execute_query_returns_rows():
    result = execute_query(
        """
        SELECT id, name
        FROM products
        ORDER BY id
        LIMIT 3
        """
    )

    assert len(result.rows) == 3
    assert result.rows[0]["id"] == 1


def test_execute_query_respects_limit():
    result = execute_query(
        """
        SELECT id
        FROM products
        LIMIT 5
        """
    )

    assert result.row_count == 5


def test_execute_query_empty_result():
    result = execute_query(
        """
        SELECT id, name
        FROM products
        WHERE id = -1
        """
    )

    assert result.columns == ["id", "name"]
    assert result.rows == []
    assert result.row_count == 0


def test_execute_query_returns_multiple_columns():
    result = execute_query(
        """
        SELECT id, name, price
        FROM products
        ORDER BY id
        LIMIT 1
        """
    )

    assert result.columns == ["id", "name", "price"]
    assert set(result.rows[0]) == {"id", "name", "price"}


def test_execute_query_allows_select():
    result = execute_query(
        """
        SELECT id
        FROM products
        LIMIT 1
        """
    )

    assert result.row_count == 1


def test_execute_query_rejects_unsafe_sql():
    with pytest.raises(UnsafeSQLQueryError):
        execute_query("DROP TABLE products")


@patch("app.database.query.engine.connect")
def test_execute_query_raises_execution_error(mock_connect):
    mock_connection = Mock()
    mock_connection.execute.side_effect = SQLAlchemyError("database error")
    mock_connect.return_value.__enter__.return_value = mock_connection

    with pytest.raises(SQLExecutionError, match="Failed to execute SQL query."):
        execute_query("SELECT * FROM orders")


@patch("app.database.query.engine.connect")
def test_execute_query_preserves_original_database_error(mock_connect):
    original_error = SQLAlchemyError("database error")

    mock_connection = Mock()
    mock_connection.execute.side_effect = original_error
    mock_connect.return_value.__enter__.return_value = mock_connection

    with pytest.raises(SQLExecutionError) as exc_info:
        execute_query("SELECT * FROM orders")

    assert exc_info.value.__cause__ is original_error
