from unittest.mock import patch

import pytest

from app.database.query import SQLExecutionError
from app.schemas.query import QueryResult
from app.services.ai_query import AIQueryService


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.discover_schema")
@patch("app.services.ai_query.TextToSQLService")
def test_ai_query_builds_and_executes_sql(
    mock_text_to_sql,
    mock_discover_schema,
    mock_execute_query,
):
    mock_discover_schema.return_value.model_dump_json.return_value = (
        '{"tables": {"orders": {"columns": ["total_amount"]}}}'
    )

    mock_text_to_sql.return_value.generate_sql.return_value = (
        "SELECT SUM(total_amount) AS total_sales FROM orders"
    )

    mock_execute_query.return_value = QueryResult(
        columns=["total_sales"],
        rows=[{"total_sales": 12345}],
        row_count=1,
    )

    service = AIQueryService()

    result = service.query("What are the total sales?")

    mock_text_to_sql.return_value.generate_sql.assert_called_once()

    mock_execute_query.assert_called_once_with(
        "SELECT SUM(total_amount) AS total_sales FROM orders"
    )

    assert result.question == "What are the total sales?"
    assert result.sql == ("SELECT SUM(total_amount) AS total_sales FROM orders")
    assert result.columns == ["total_sales"]
    assert result.rows == [{"total_sales": 12345}]
    assert result.row_count == 1


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.discover_schema")
@patch("app.services.ai_query.TextToSQLService")
def test_ai_query_passes_schema_to_text_to_sql(
    mock_text_to_sql,
    mock_discover_schema,
    mock_execute_query,
):
    schema = '{"tables": {"customers": {"columns": ["id", "name"]}}}'

    mock_discover_schema.return_value.model_dump_json.return_value = schema

    mock_text_to_sql.return_value.generate_sql.return_value = (
        "SELECT COUNT(*) FROM customers"
    )

    mock_execute_query.return_value = QueryResult(
        columns=["count"],
        rows=[{"count": 50}],
        row_count=1,
    )

    service = AIQueryService()

    service.query("How many customers are there?")

    mock_text_to_sql.return_value.generate_sql.assert_called_once_with(
        question="How many customers are there?",
        schema=schema,
    )


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.TextToSQLService")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_raises_error_when_generated_sql_fails(
    mock_schema,
    mock_text_to_sql,
    mock_execute_query,
):
    mock_schema.return_value.model_dump_json.return_value = (
        '{"orders": {"columns": ["total_amount"]}}'
    )

    mock_text_to_sql.return_value.generate_sql.return_value = (
        "SELECT invalid_column FROM orders"
    )

    mock_execute_query.side_effect = SQLExecutionError("Failed to execute SQL query.")

    service = AIQueryService()

    with pytest.raises(
        SQLExecutionError,
        match="AI-generated SQL query failed to execute.",
    ):
        service.query("What are the total sales?")


@patch("app.services.ai_query.execute_query")
@patch("app.services.ai_query.TextToSQLService")
@patch("app.services.ai_query.discover_schema")
def test_ai_query_preserves_original_execution_error(
    mock_schema,
    mock_text_to_sql,
    mock_execute_query,
):
    mock_schema.return_value.model_dump_json.return_value = (
        '{"orders": {"columns": ["total_amount"]}}'
    )

    mock_text_to_sql.return_value.generate_sql.return_value = (
        "SELECT invalid_column FROM orders"
    )

    original_error = SQLExecutionError("Failed to execute SQL query.")
    mock_execute_query.side_effect = original_error

    service = AIQueryService()

    with pytest.raises(SQLExecutionError) as exc_info:
        service.query("What are the total sales?")

    assert exc_info.value.__cause__ is original_error


def test_ai_query_service_generates_answer():
    with (
        patch("app.services.ai_query.discover_schema") as mock_schema,
        patch("app.services.ai_query.TextToSQLService") as mock_text_to_sql,
        patch("app.services.ai_query.AnswerService") as mock_answer_service,
        patch("app.services.ai_query.execute_query") as mock_execute,
    ):
        mock_schema.return_value.model_dump_json.return_value = "{}"

        mock_text_to_sql.return_value.generate_sql.return_value = (
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
        patch("app.services.ai_query.TextToSQLService") as mock_text_to_sql,
        patch("app.services.ai_query.AnswerService") as mock_answer_service,
        patch("app.services.ai_query.execute_query") as mock_execute,
    ):
        mock_schema.return_value.model_dump_json.return_value = "{}"

        mock_text_to_sql.return_value.generate_sql.return_value = (
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
