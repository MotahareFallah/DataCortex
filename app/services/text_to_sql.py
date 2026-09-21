import json

from pydantic import BaseModel

from app.services.llm import LLMService
from app.services.sql_prompt import build_sql_prompt
from app.services.tools import EXECUTE_SQL_TOOL


class SQLGenerationResult(BaseModel):
    sql: str


class TextToSQLService:
    def __init__(self) -> None:
        self.llm = LLMService()

    def generate_sql(self, question: str, schema: str) -> str:
        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        result = self.llm.generate_json(prompt)

        structured_result = SQLGenerationResult.model_validate(result)

        return structured_result.sql.strip()

    def generate_sql_with_tool(
        self,
        question: str,
        schema: str,
    ) -> str:
        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        response = self.llm.generate_with_tools(
            prompt=prompt,
            tools=[EXECUTE_SQL_TOOL],
        )

        message = response["message"]

        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            arguments = tool_calls[0]["function"]["arguments"]
            return arguments["sql"].strip()

        content = message.get("content", "").strip()

        if not content:
            raise ValueError("LLM did not return a tool call.")

        if content.startswith("```json"):
            content = content[len("```json") :].strip()

        elif content.startswith("```"):
            content = content[3:].strip()

        if content.endswith("```"):
            content = content[:-3].strip()

        try:
            tool_call = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM did not return a valid tool call.") from exc

        if tool_call.get("name") != "execute_sql":
            raise ValueError("LLM did not return the execute_sql tool.")

        arguments = tool_call.get("arguments", {})

        if "sql" not in arguments:
            raise ValueError("Tool call does not contain SQL.")

        return arguments["sql"].strip()
