from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.database.query import SQLExecutionError, execute_query


class FakeColumn:
    def __init__(self, name: str):
        self.name = name


def test_execute_query_returns_result():
    result = execute_query("SELECT id, name FROM products LIMIT 1")

    assert result.columns == ["id", "name"]
    assert result.row_count == 1
    assert len(result.rows) == 1


def test_execute_query_returns_multiple_rows():
    result = execute_query("SELECT id, name FROM products LIMIT 3")

    assert result.columns == ["id", "name"]
    assert result.row_count == 3
    assert len(result.rows) == 3


def test_execute_query_returns_expected_columns():
    result = execute_query("SELECT id, name, price FROM products LIMIT 1")

    assert result.columns == ["id", "name", "price"]


def test_execute_query_with_where_clause():
    result = execute_query("SELECT id, name FROM products WHERE price > 0 LIMIT 1")

    assert result.columns == ["id", "name"]
    assert result.row_count == 1


def test_execute_query_returns_dict_rows():
    result = execute_query("SELECT id, name FROM products LIMIT 1")

    assert isinstance(result.rows[0], dict)
    assert "id" in result.rows[0]
    assert "name" in result.rows[0]


def test_execute_query_with_valid_schema_query():
    result = execute_query("SELECT id, name FROM products LIMIT 1")

    assert result.columns == ["id", "name"]
    assert result.row_count == 1


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_uses_database_connection(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
                FakeColumn("total_amount"),
            ]
        )
    }

    mock_connection = Mock()
    mock_result = Mock()

    mock_result.keys.return_value = ["id"]
    mock_result.mappings.return_value.all.return_value = [
        {"id": 1},
    ]

    mock_connection.execute.return_value = mock_result
    mock_connect.return_value.__enter__.return_value = mock_connection

    result = execute_query("SELECT id FROM orders")

    mock_connect.assert_called_once()
    mock_connection.execute.assert_called_once()

    assert result.columns == ["id"]
    assert result.rows == [{"id": 1}]
    assert result.row_count == 1


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_uses_sql_text(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
                FakeColumn("total_amount"),
            ]
        )
    }

    mock_connection = Mock()
    mock_result = Mock()

    mock_result.keys.return_value = ["id"]
    mock_result.mappings.return_value.all.return_value = []

    mock_connection.execute.return_value = mock_result
    mock_connect.return_value.__enter__.return_value = mock_connection

    execute_query("SELECT id FROM orders")

    executed_argument = mock_connection.execute.call_args.args[0]

    assert str(executed_argument) == "SELECT id FROM orders"


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_raises_execution_error(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
                FakeColumn("total_amount"),
            ]
        )
    }

    mock_connection = Mock()
    mock_connection.execute.side_effect = SQLAlchemyError("database error")
    mock_connect.return_value.__enter__.return_value = mock_connection

    with pytest.raises(
        SQLExecutionError,
        match="Failed to execute SQL query.",
    ):
        execute_query("SELECT * FROM orders")


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_preserves_original_database_error(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
                FakeColumn("total_amount"),
            ]
        )
    }

    original_error = SQLAlchemyError("database error")

    mock_connection = Mock()
    mock_connection.execute.side_effect = original_error
    mock_connect.return_value.__enter__.return_value = mock_connection

    with pytest.raises(SQLExecutionError) as exc_info:
        execute_query("SELECT * FROM orders")

    assert exc_info.value.__cause__ is original_error


def test_execute_query_rejects_unknown_table():
    with pytest.raises(
        ValueError,
        match="Table 'unknown_table' does not exist in the schema.",
    ):
        execute_query("SELECT id FROM unknown_table")


def test_execute_query_rejects_unknown_column():
    with pytest.raises(
        ValueError,
        match="Column 'unknown_column' does not exist in the schema.",
    ):
        execute_query("SELECT unknown_column FROM products")


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_accepts_maximum_allowed_rows(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
            ]
        )
    }

    mock_connection = Mock()
    mock_result = Mock()

    mock_result.keys.return_value = ["id"]
    mock_result.mappings.return_value.all.return_value = [
        {"id": index} for index in range(1000)
    ]

    mock_connection.execute.return_value = mock_result
    mock_connect.return_value.__enter__.return_value = mock_connection

    result = execute_query("SELECT id FROM orders")

    assert result.row_count == 1000


@patch("app.database.query.engine.connect")
@patch("app.database.query.discover_schema")
def test_execute_query_rejects_too_many_rows(
    mock_discover_schema,
    mock_connect,
):
    mock_discover_schema.return_value.tables = {
        "orders": Mock(
            columns=[
                FakeColumn("id"),
            ]
        )
    }

    mock_connection = Mock()
    mock_result = Mock()

    mock_result.keys.return_value = ["id"]
    mock_result.mappings.return_value.all.return_value = [
        {"id": index} for index in range(1001)
    ]

    mock_connection.execute.return_value = mock_result
    mock_connect.return_value.__enter__.return_value = mock_connection

    with pytest.raises(
        ValueError,
        match="Query returned too many rows",
    ):
        execute_query("SELECT id FROM orders")
