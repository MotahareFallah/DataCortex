from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database.query import SQLExecutionError
from app.database.sql_validator import UnsafeSQLQueryError
from app.main import app
from app.schemas.ai_query import AIQueryResponse
from app.services.exceptions import (
    QuestionNotAnswerableError,
    WriteRequestError,
)

client = TestClient(app)


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_response(mock_service):
    mock_service.return_value.query.return_value = AIQueryResponse(
        question="What are the total sales?",
        sql="SELECT SUM(total_amount) AS total_sales FROM orders;",
        columns=["total_sales"],
        rows=[{"total_sales": "1022033.54"}],
        row_count=1,
        answer="The total sales are 1,022,033.54.",
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
    assert response.json()["answer"] == ("The total sales are 1,022,033.54.")


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_passes_question_to_service(mock_service):
    mock_service.return_value.query.return_value = AIQueryResponse(
        question="How many customers are there?",
        sql="SELECT COUNT(*) FROM customers;",
        columns=["count"],
        rows=[{"count": 50}],
        row_count=1,
        answer="There are 50 customers.",
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


def test_ai_query_endpoint_returns_answer():
    with patch("app.api.routes.ai_query.AIQueryService") as mock_service:
        mock_service.return_value.query.return_value = AIQueryResponse(
            question="What are the total sales?",
            sql="SELECT SUM(total_amount) AS total_sales FROM orders",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
            row_count=1,
            answer="The total sales are 1,022,033.54.",
        )

        response = client.post(
            "/ai/query",
            json={"question": "What are the total sales?"},
        )

        assert response.status_code == 200
        assert response.json()["answer"] == ("The total sales are 1,022,033.54.")


def test_ai_query_endpoint_includes_answer_in_response():
    with patch("app.api.routes.ai_query.AIQueryService") as mock_service:
        mock_service.return_value.query.return_value = AIQueryResponse(
            question="What are the total sales?",
            sql="SELECT SUM(total_amount) AS total_sales FROM orders",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
            row_count=1,
            answer="The total sales are 1,022,033.54.",
        )

        response = client.post(
            "/ai/query",
            json={"question": "What are the total sales?"},
        )

        data = response.json()

        assert "answer" in data
        assert isinstance(data["answer"], str)


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_422_when_sql_cannot_be_validated(
    mock_service,
):
    mock_service.return_value.query.side_effect = UnsafeSQLQueryError(
        "Invalid SQL query."
    )

    response = client.post(
        "/ai/query",
        json={"question": "How are we doing?"},
    )

    assert response.status_code == 422
    assert "couldn't turn" in response.json()["detail"]
    # Technical details must not leak to the user.
    assert "Invalid SQL query" not in response.json()["detail"]


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_422_when_question_not_answerable(mock_service):
    mock_service.return_value.query.side_effect = QuestionNotAnswerableError("x")

    response = client.post(
        "/ai/query",
        json={"question": "Show customer birthdays"},
    )

    assert response.status_code == 422
    assert "can't answer" in response.json()["detail"]


@patch("app.api.routes.ai_query.AIQueryService")
def test_ai_query_endpoint_returns_422_for_write_requests(mock_service):
    mock_service.return_value.query.side_effect = WriteRequestError("x")

    response = client.post(
        "/ai/query",
        json={"question": "Delete all orders"},
    )

    assert response.status_code == 422
    assert "read-only" in response.json()["detail"]
