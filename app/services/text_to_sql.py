from pydantic import BaseModel

from app.services.llm import LLMService
from app.services.sql_prompt import build_sql_prompt


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
