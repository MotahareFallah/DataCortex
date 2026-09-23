from app.services.llm import LLMService


class AIAgent:
    def __init__(self) -> None:
        self.llm = LLMService()

    def run(self, prompt: str) -> str:
        sql = self.llm.generate(prompt).strip()

        if not sql:
            raise ValueError("LLM returned an empty SQL query.")

        return sql

    def repair_sql(self, prompt: str) -> str:
        sql = self.llm.generate(prompt).strip()

        if not sql:
            raise ValueError("LLM returned an empty SQL query.")

        return sql
