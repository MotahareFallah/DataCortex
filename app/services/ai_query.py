from app.database.query import SQLExecutionError, execute_query
from app.database.schema import discover_schema
from app.schemas.ai_query import AIQueryResponse
from app.services.agent import AIAgent
from app.services.answer import AnswerService
from app.services.sql_cleaner import clean_sql
from app.services.sql_prompt import build_sql_prompt


class AIQueryService:
    def __init__(self) -> None:
        self.agent = AIAgent()
        self.answer = AnswerService()

    def query(self, question: str) -> AIQueryResponse:
        schema = discover_schema().model_dump_json(indent=2)

        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        sql = self.agent.run(prompt)

        sql = clean_sql(sql)

        try:
            result = execute_query(sql)
        except SQLExecutionError as exc:
            raise SQLExecutionError(
                "AI-generated SQL query failed to execute."
            ) from exc

        answer = self.answer.generate_answer(
            question=question,
            columns=result.columns,
            rows=result.rows,
        )

        return AIQueryResponse(
            question=question,
            sql=sql,
            columns=result.columns,
            rows=result.rows,
            row_count=result.row_count,
            answer=answer,
        )
