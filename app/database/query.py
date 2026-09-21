from sqlalchemy import text

from app.database.connection import engine
from app.database.sql_validator import validate_sql
from app.schemas.query import QueryResult


def execute_query(sql: str) -> QueryResult:
    validate_sql(sql)

    with engine.connect() as connection:
        result = connection.execute(text(sql))

        columns = list(result.keys())
        rows = [dict(row) for row in result.mappings().all()]

    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
