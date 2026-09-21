from unittest.mock import patch

from app.services.text_to_sql import TextToSQLService


@patch("app.services.text_to_sql.LLMService")
def test_generate_sql_returns_structured_llm_response(mock_llm):
    mock_llm.return_value.generate_json.return_value = {
        "sql": "SELECT SUM(total_amount) FROM orders"
    }

    service = TextToSQLService()

    result = service.generate_sql(
        question="What are the total sales?",
        schema="orders(id, total_amount)",
    )

    assert result == "SELECT SUM(total_amount) FROM orders"


@patch("app.services.text_to_sql.LLMService")
def test_generate_sql_sends_prompt_to_llm(mock_llm):
    mock_llm.return_value.generate_json.return_value = {
        "sql": "SELECT COUNT(*) FROM customers"
    }

    service = TextToSQLService()

    service.generate_sql(
        question="How many customers are there?",
        schema="customers(id)",
    )

    mock_llm.return_value.generate_json.assert_called_once()

    prompt = mock_llm.return_value.generate_json.call_args.args[0]

    assert "How many customers are there?" in prompt
    assert "customers(id)" in prompt
