from app.services.answer_prompt import build_answer_prompt
from app.services.llm import LLMService


class AnswerService:
    def __init__(self) -> None:
        self.llm = LLMService()

    def generate_answer(
        self,
        question: str,
        columns: list[str],
        rows: list[dict],
    ) -> str:
        prompt = build_answer_prompt(
            question=question,
            columns=columns,
            rows=rows,
        )

        return self.llm.generate(prompt).strip()
