from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine
from app.database.sql_validator import validate_sql
from app.schemas.query import QueryResult


class SQLExecutionError(RuntimeError):
    pass


def execute_query(sql: str) -> QueryResult:
    validate_sql(sql)

    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql))

            columns = list(result.keys())
            rows = [dict(row) for row in result.mappings().all()]

    except SQLAlchemyError as exc:
        raise SQLExecutionError("Failed to execute SQL query.") from exc

    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
