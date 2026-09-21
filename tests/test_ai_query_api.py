from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database.query import SQLExecutionError
from app.main import app
from app.schemas.ai_query import AIQueryResponse

client = TestClient(app)


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_response(mock_service):
    mock_service.return_value.query.return_value = AIQueryResponse(
        question="What are the total sales?",
        sql="SELECT SUM(total_amount) AS total_sales FROM orders;",
        columns=["total_sales"],
        rows=[{"total_sales": "1022033.54"}],
        row_count=1,
    )

    response = client.post(
        "/ai/query",
        json={"question": "What are the total sales?"},
    )

    assert response.status_code == 200
    assert response.json()["question"] == "What are the total sales?"
    assert response.json()["sql"] == (
        "SELECT SUM(total_amount) AS total_sales FROM orders;"
    )
    assert response.json()["row_count"] == 1


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_passes_question_to_service(mock_service):
    mock_service.return_value.query.return_value = AIQueryResponse(
        question="How many customers are there?",
        sql="SELECT COUNT(*) FROM customers;",
        columns=["count"],
        rows=[{"count": 50}],
        row_count=1,
    )

    client.post(
        "/ai/query",
        json={"question": "How many customers are there?"},
    )

    mock_service.return_value.query.assert_called_once_with(
        "How many customers are there?"
    )


def test_ai_query_endpoint_rejects_missing_question():
    response = client.post(
        "/ai/query",
        json={},
    )

    assert response.status_code == 422


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_400_for_sql_execution_error(
    mock_service,
):
    mock_service.return_value.query.side_effect = SQLExecutionError(
        "AI-generated SQL query failed to execute."
    )

    response = client.post(
        "/ai/query",
        json={"question": "What are the total sales?"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("AI-generated SQL query failed to execute.")


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_does_not_return_sql_error_as_500(
    mock_service,
):
    mock_service.return_value.query.side_effect = SQLExecutionError(
        "AI-generated SQL query failed to execute."
    )

    response = client.post(
        "/ai/query",
        json={"question": "What are the total sales?"},
    )

    assert response.status_code != 500
