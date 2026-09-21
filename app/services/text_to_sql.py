from app.services.llm import LLMService
from app.services.sql_prompt import build_sql_prompt


class TextToSQLService:
    def __init__(self) -> None:
        self.llm = LLMService()

    def generate_sql(self, question: str, schema: str) -> str:
        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        return self.llm.generate(prompt).strip()
