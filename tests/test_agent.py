from unittest.mock import patch

import pytest

from app.services.agent import AIAgent


def test_agent_extracts_standard_tool_call():
    agent = AIAgent()

    response = {
        "message": {
            "tool_calls": [
                {
                    "function": {
                        "name": "execute_sql",
                        "arguments": {
                            "sql": "SELECT * FROM orders",
                        },
                    }
                }
            ]
        }
    }

    with patch.object(
        agent.llm,
        "generate_with_tools",
        return_value=response,
    ):
        result = agent.run("Show me orders.")

    assert result == "SELECT * FROM orders"


def test_agent_extracts_json_content_tool_call():
    agent = AIAgent()

    response = {
        "message": {
            "content": """```json
{
  "name": "execute_sql",
  "arguments": {
    "sql": "SELECT * FROM orders"
  }
}
```"""
        }
    }

    with patch.object(
        agent.llm,
        "generate_with_tools",
        return_value=response,
    ):
        result = agent.run("Show me orders.")

    assert result == "SELECT * FROM orders"


def test_agent_raises_when_no_tool_call_is_returned():
    agent = AIAgent()

    response = {
        "message": {
            "content": "",
            "tool_calls": [],
        }
    }

    with patch.object(
        agent.llm,
        "generate_with_tools",
        return_value=response,
    ):
        with pytest.raises(
            ValueError,
            match="LLM did not return a tool call.",
        ):
            agent.run("Show me orders.")


def test_agent_raises_for_invalid_tool():
    agent = AIAgent()

    response = {
        "message": {
            "content": """{
                "name": "unknown_tool",
                "arguments": {
                    "sql": "SELECT * FROM orders"
                }
            }"""
        }
    }

    with patch.object(
        agent.llm,
        "generate_with_tools",
        return_value=response,
    ):
        with pytest.raises(
            ValueError,
            match="LLM did not return the execute_sql tool.",
        ):
            agent.run("Show me orders.")
