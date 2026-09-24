import logging

from app.database.query import SQLExecutionError, execute_query
from app.database.schema import discover_schema
from app.database.sql_repair import repair_column_table_reference
from app.database.sql_semantic_validator import (
    SemanticSQLValidationError,
    validate_sql_semantics,
)
from app.database.sql_validator import UnsafeSQLQueryError, validate_sql
from app.schemas.ai_query import AIQueryResponse
from app.services.agent import AIAgent
from app.services.answer import AnswerService
from app.services.exceptions import (
    QuestionNotAnswerableError,
    WriteRequestError,
)
from app.services.question_guard import is_write_request
from app.services.sql_cleaner import clean_sql, is_cannot_answer
from app.services.sql_prompt import build_sql_prompt
from app.services.sql_repair_prompt import build_sql_repair_prompt

MAX_RESPONSE_ROWS = 100


class AIQueryService:
    def __init__(self) -> None:
        self.agent = AIAgent()
        self.answer = AnswerService()

    def _build_validation_schema(self) -> dict[str, set[str]]:
        database_schema = discover_schema()

        return {
            table_name: {column.name for column in table_schema.columns}
            for table_name, table_schema in database_schema.tables.items()
        }

    def _validate_sql(
        self,
        sql: str,
        question: str,
        validation_schema: dict[str, set[str]],
    ) -> None:
        validate_sql(sql, validation_schema)

        validate_sql_semantics(
            sql=sql,
            question=question,
        )

    def _repair_sql_deterministically(
        self,
        sql: str,
        validation_schema: dict[str, set[str]],
    ) -> str:
        repaired_sql = repair_column_table_reference(
            sql=sql,
            schema=validation_schema,
        )

        return clean_sql(repaired_sql)

    def _validate_and_repair_sql(
        self,
        sql: str,
        question: str,
        schema: str,
    ) -> str:
        validation_schema = self._build_validation_schema()

        try:
            self._validate_sql(
                sql=sql,
                question=question,
                validation_schema=validation_schema,
            )

            return sql

        except (
            UnsafeSQLQueryError,
            SemanticSQLValidationError,
        ) as exc:
            validation_error = str(exc)

            logging.warning(
                "Initial SQL rejected (%s): %s",
                exc,
                sql,
            )

        try:
            repaired_sql = self._repair_sql_deterministically(
                sql=sql,
                validation_schema=validation_schema,
            )

            logging.warning(
                "Deterministically repaired SQL: %s",
                repaired_sql,
            )

            self._validate_sql(
                sql=repaired_sql,
                question=question,
                validation_schema=validation_schema,
            )

            return repaired_sql

        except (
            UnsafeSQLQueryError,
            SemanticSQLValidationError,
            ValueError,
        ) as deterministic_exc:
            logging.warning(
                "Deterministic SQL repair failed (%s). Falling back to LLM repair.",
                deterministic_exc,
            )

        repair_prompt = build_sql_repair_prompt(
            sql=sql,
            error=validation_error,
            schema=schema,
            question=question,
        )

        repaired_sql = self.agent.repair_sql(repair_prompt)
        repaired_sql = clean_sql(repaired_sql)

        logging.warning(
            "LLM repaired SQL: %s",
            repaired_sql,
        )

        if is_cannot_answer(repaired_sql):
            raise QuestionNotAnswerableError(
                "The model reported that the data is not available."
            )

        self._validate_sql(
            sql=repaired_sql,
            question=question,
            validation_schema=validation_schema,
        )

        return repaired_sql

    def query(self, question: str) -> AIQueryResponse:
        if is_write_request(question):
            raise WriteRequestError("Write operations are not supported.")

        schema = discover_schema().model_dump_json(indent=2)

        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        sql = self.agent.run(prompt)
        sql = clean_sql(sql)

        logging.warning(
            "Initial generated SQL: %s",
            sql,
        )

        if is_cannot_answer(sql):
            raise QuestionNotAnswerableError(
                "The model reported that the data is not available."
            )

        sql = self._validate_and_repair_sql(
            sql=sql,
            question=question,
            schema=schema,
        )

        try:
            result = execute_query(sql)

        except SQLExecutionError as exc:
            raise SQLExecutionError(
                "AI-generated SQL query failed to execute."
            ) from exc

        truncated = len(result.rows) > MAX_RESPONSE_ROWS
        rows = result.rows[:MAX_RESPONSE_ROWS]

        answer = self.answer.generate_answer(
            question=question,
            columns=result.columns,
            rows=rows,
        )

        return AIQueryResponse(
            question=question,
            sql=sql,
            columns=result.columns,
            rows=rows,
            row_count=result.row_count,
            answer=answer,
            truncated=truncated,
        )
