from unittest.mock import patch

import pytest

from app.database.query import SQLExecutionError
from app.database.sql_validator import UnsafeSQLQueryError
from app.schemas.database import (
    ColumnSchema,
    DatabaseSchema,
    TableSchema,
)
from app.schemas.query import QueryResult
from app.services.ai_query import AIQueryService


def make_schema(*tables: tuple[str, list[str]]) -> DatabaseSchema:
    return DatabaseSchema(
        database="test_db",
        tables={
            table_name: TableSchema(
                columns=[
                    ColumnSchema(
                        name=column_name,
                        type="INTEGER",
                        nullable=True,
                        default=None,
                    )
                    for column_name in columns
                ],
                primary_key=[],
                foreign_keys=[],
            )
            for table_name, columns in tables
        },
    )


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_builds_and_executes_sql(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    mock_agent.return_value.run.return_value = (
        "SELECT SUM(total_amount) AS total_sales FROM orders"
    )

    mock_execute_query.return_value = QueryResult(
        columns=["total_sales"],
        rows=[{"total_sales": 12345}],
        row_count=1,
    )

    service = AIQueryService()

    result = service.query("What are the total sales?")

    mock_agent.return_value.run.assert_called_once()

    mock_execute_query.assert_called_once_with(
        "SELECT SUM(total_amount) AS total_sales FROM orders"
    )

    assert result.question == "What are the total sales?"
    assert result.sql == "SELECT SUM(total_amount) AS total_sales FROM orders"
    assert result.columns == ["total_sales"]
    assert result.rows == [{"total_sales": 12345}]
    assert result.row_count == 1


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_passes_schema_to_agent(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("customers", ["id", "name"]),
    )

    mock_agent.return_value.run.return_value = "SELECT COUNT(*) FROM customers"

    mock_execute_query.return_value = QueryResult(
        columns=["count"],
        rows=[{"count": 50}],
        row_count=1,
    )

    service = AIQueryService()

    service.query("How many customers are there?")

    prompt = mock_agent.return_value.run.call_args.args[0]
    schema = mock_discover_schema.return_value.model_dump_json(
        indent=2,
    )

    assert schema in prompt
    assert "How many customers are there?" in prompt


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_raises_error_when_generated_sql_fails(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    mock_agent.return_value.run.return_value = "SELECT total_amount FROM orders"

    mock_execute_query.side_effect = SQLExecutionError("Failed to execute SQL query.")

    service = AIQueryService()

    with pytest.raises(
        SQLExecutionError,
        match="AI-generated SQL query failed to execute.",
    ):
        service.query("What are the total sales?")


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_preserves_original_execution_error(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    mock_agent.return_value.run.return_value = "SELECT total_amount FROM orders"

    original_error = SQLExecutionError("Failed to execute SQL query.")
    mock_execute_query.side_effect = original_error

    service = AIQueryService()

    with pytest.raises(SQLExecutionError) as exc_info:
        service.query("What are the total sales?")

    assert exc_info.value.__cause__ is original_error


def test_ai_query_service_generates_answer():
    with (
        patch("app.services.ai_query.discover_schema") as mock_schema,
        patch("app.services.ai_query.AIAgent") as mock_agent,
        patch("app.services.ai_query.AnswerService") as mock_answer_service,
        patch("app.services.ai_query.execute_query") as mock_execute,
    ):
        mock_schema.return_value = make_schema(
            ("orders", ["total_amount"]),
        )

        mock_agent.return_value.run.return_value = (
            "SELECT SUM(total_amount) AS total_sales FROM orders"
        )

        mock_execute.return_value.columns = ["total_sales"]
        mock_execute.return_value.rows = [{"total_sales": "1022033.54"}]
        mock_execute.return_value.row_count = 1

        mock_answer_service.return_value.generate_answer.return_value = (
            "The total sales are 1,022,033.54."
        )

        service = AIQueryService()

        result = service.query("What are the total sales?")

        assert result.answer == "The total sales are 1,022,033.54."


def test_ai_query_service_passes_query_result_to_answer_service():
    with (
        patch("app.services.ai_query.discover_schema") as mock_schema,
        patch("app.services.ai_query.AIAgent") as mock_agent,
        patch("app.services.ai_query.AnswerService") as mock_answer_service,
        patch("app.services.ai_query.execute_query") as mock_execute,
    ):
        mock_schema.return_value = make_schema(
            ("orders", ["total_amount"]),
        )

        mock_agent.return_value.run.return_value = (
            "SELECT SUM(total_amount) AS total_sales FROM orders"
        )

        mock_execute.return_value.columns = ["total_sales"]
        mock_execute.return_value.rows = [{"total_sales": "1022033.54"}]
        mock_execute.return_value.row_count = 1

        mock_answer_service.return_value.generate_answer.return_value = (
            "The total sales are 1,022,033.54."
        )

        service = AIQueryService()

        service.query("What are the total sales?")

        mock_answer_service.return_value.generate_answer.assert_called_once_with(
            question="What are the total sales?",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
        )


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_repairs_invalid_sql_and_executes_repaired_query(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    # The first query uses a column that does not exist, so validation fails.
    mock_agent.return_value.run.return_value = "SELECT missing_column FROM orders"
    mock_agent.return_value.repair_sql.return_value = "SELECT total_amount FROM orders"

    mock_execute_query.return_value = QueryResult(
        columns=["total_amount"],
        rows=[{"total_amount": 100}],
        row_count=1,
    )

    service = AIQueryService()

    result = service.query("Show order totals")

    mock_agent.return_value.repair_sql.assert_called_once()
    mock_execute_query.assert_called_once_with("SELECT total_amount FROM orders")
    assert result.sql == "SELECT total_amount FROM orders"


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_raises_unsafe_error_when_repair_also_fails(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    mock_agent.return_value.run.return_value = "SELECT missing_column FROM orders"
    mock_agent.return_value.repair_sql.return_value = "SELECT other_missing FROM orders"

    service = AIQueryService()

    with pytest.raises(UnsafeSQLQueryError):
        service.query("How are we doing?")

    # Invalid SQL must never reach the database.
    mock_execute_query.assert_not_called()


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.AIAgent")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_attempts_repair_only_once(
    mock_discover_schema,
    mock_agent,
    mock_execute_query,
):
    mock_discover_schema.return_value = make_schema(
        ("orders", ["total_amount"]),
    )

    mock_agent.return_value.run.return_value = "SELECT missing_column FROM orders"
    mock_agent.return_value.repair_sql.return_value = "SELECT other_missing FROM orders"

    service = AIQueryService()

    with pytest.raises(UnsafeSQLQueryError):
        service.query("How are we doing?")

    mock_agent.return_value.repair_sql.assert_called_once()
