from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import engine
from app.database.database import get_database_adapter
from app.database.schema import discover_schema
from app.database.security import DatabaseSecurityPolicy
from app.database.sql_validator import validate_sql
from app.schemas.query import QueryResult


class SQLExecutionError(RuntimeError):
    pass


def execute_query(sql: str) -> QueryResult:
    database_schema = discover_schema()

    schema = {
        table_name: {column.name for column in table_schema.columns}
        for table_name, table_schema in database_schema.tables.items()
    }

    validate_sql(sql, schema)

    database_adapter = get_database_adapter(settings.database_type)
    security_policy = DatabaseSecurityPolicy()

    sql = security_policy.apply_row_limit(
        sql,
        database_adapter,
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql))

            columns = list(result.keys())
            rows = [dict(row) for row in result.mappings().all()]

            security_policy.validate_row_limit(len(rows))

    except SQLAlchemyError as exc:
        raise SQLExecutionError("Failed to execute SQL query.") from exc

    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
