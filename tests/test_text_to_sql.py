from unittest.mock import patch

import pytest

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


@patch("app.services.text_to_sql.LLMService")
def test_generate_sql_with_tool_returns_sql_from_tool_call(mock_llm):
    mock_llm.return_value.generate_with_tools.return_value = {
        "message": {
            "tool_calls": [
                {
                    "function": {
                        "name": "execute_sql",
                        "arguments": {"sql": "SELECT COUNT(*) FROM customers"},
                    }
                }
            ]
        }
    }

    service = TextToSQLService()

    result = service.generate_sql_with_tool(
        question="How many customers are there?",
        schema="customers(id)",
    )

    assert result == "SELECT COUNT(*) FROM customers"


@patch("app.services.text_to_sql.LLMService")
def test_generate_sql_with_tool_raises_without_tool_call(mock_llm):
    mock_llm.return_value.generate_with_tools.return_value = {
        "message": {"tool_calls": []}
    }

    service = TextToSQLService()

    with pytest.raises(
        ValueError,
        match="LLM did not return a tool call.",
    ):
        service.generate_sql_with_tool(
            question="How many customers are there?",
            schema="customers(id)",
        )


def test_generate_sql_with_tool_parses_standard_tool_call():
    service = TextToSQLService()

    response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "execute_sql",
                        "arguments": {"sql": "SELECT SUM(total_amount) FROM orders"},
                    }
                }
            ],
        }
    }

    with patch.object(
        service.llm,
        "generate_with_tools",
        return_value=response,
    ):
        result = service.generate_sql_with_tool(
            question="What are the total sales?",
            schema="{}",
        )

    assert result == "SELECT SUM(total_amount) FROM orders"


def test_generate_sql_with_tool_parses_json_content():
    service = TextToSQLService()

    response = {
        "message": {
            "role": "assistant",
            "content": """```json
{
  "name": "execute_sql",
  "arguments": {
    "sql": "SELECT SUM(total_amount) FROM orders"
  }
}
```""",
        }
    }

    with patch.object(
        service.llm,
        "generate_with_tools",
        return_value=response,
    ):
        result = service.generate_sql_with_tool(
            question="What are the total sales?",
            schema="{}",
        )

    assert result == "SELECT SUM(total_amount) FROM orders"
