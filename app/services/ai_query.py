from app.database.query import SQLExecutionError, execute_query
from app.database.schema import discover_schema
from app.schemas.ai_query import AIQueryResponse
from app.services.answer import AnswerService
from app.services.sql_cleaner import clean_sql
from app.services.text_to_sql import TextToSQLService


class AIQueryService:
    def __init__(self) -> None:
        self.text_to_sql = TextToSQLService()
        self.answer = AnswerService()

    def query(self, question: str) -> AIQueryResponse:
        schema = discover_schema().model_dump_json(indent=2)

        sql = self.text_to_sql.generate_sql(
            question=question,
            schema=schema,
        )

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
