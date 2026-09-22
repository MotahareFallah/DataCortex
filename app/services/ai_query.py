from app.database.query import SQLExecutionError, execute_query
from app.database.schema import discover_schema
from app.database.sql_validator import UnsafeSQLQueryError, validate_sql
from app.schemas.ai_query import AIQueryResponse
from app.services.agent import AIAgent
from app.services.answer import AnswerService
from app.services.sql_cleaner import clean_sql
from app.services.sql_prompt import build_sql_prompt
from app.services.sql_repair_prompt import build_sql_repair_prompt


class AIQueryService:
    def __init__(self) -> None:
        self.agent = AIAgent()
        self.answer = AnswerService()

    def _validate_and_repair_sql(
        self,
        sql: str,
        schema: str,
    ) -> str:
        database_schema = discover_schema()

        validation_schema = {
            table_name: {column.name for column in table_schema.columns}
            for table_name, table_schema in database_schema.tables.items()
        }

        try:
            validate_sql(sql, validation_schema)
            return sql

        except UnsafeSQLQueryError as exc:
            repair_prompt = build_sql_repair_prompt(
                sql=sql,
                error=str(exc),
                schema=schema,
            )

            repaired_sql = self.agent.repair_sql(repair_prompt)
            repaired_sql = clean_sql(repaired_sql)

            validate_sql(repaired_sql, validation_schema)

            return repaired_sql

    def query(self, question: str) -> AIQueryResponse:
        schema = discover_schema().model_dump_json(indent=2)

        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        sql = self.agent.run(prompt)
        sql = clean_sql(sql)

        sql = self._validate_and_repair_sql(
            sql=sql,
            schema=schema,
        )

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
