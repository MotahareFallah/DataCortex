from unittest.mock import patch

import pytest

from app.services.agent import AIAgent


def test_agent_returns_generated_sql():
    agent = AIAgent()

    with patch.object(
        agent.llm,
        "generate",
        return_value="SELECT * FROM orders",
    ):
        result = agent.run("Show me orders.")

    assert result == "SELECT * FROM orders"


def test_agent_strips_generated_sql():
    agent = AIAgent()

    with patch.object(
        agent.llm,
        "generate",
        return_value="  SELECT * FROM orders  ",
    ):
        result = agent.run("Show me orders.")

    assert result == "SELECT * FROM orders"


def test_agent_raises_when_llm_returns_empty_sql():
    agent = AIAgent()

    with patch.object(
        agent.llm,
        "generate",
        return_value="",
    ):
        with pytest.raises(
            ValueError,
            match="LLM returned an empty SQL query.",
        ):
            agent.run("Show me orders.")


def test_agent_repairs_sql():
    agent = AIAgent()

    with patch.object(
        agent.llm,
        "generate",
        return_value="SELECT * FROM orders",
    ):
        result = agent.repair_sql("Repair this SQL.")

    assert result == "SELECT * FROM orders"


def test_agent_raises_when_repair_returns_empty_sql():
    agent = AIAgent()

    with patch.object(
        agent.llm,
        "generate",
        return_value="",
    ):
        with pytest.raises(
            ValueError,
            match="LLM returned an empty SQL query.",
        ):
            agent.repair_sql("Repair this SQL.")
