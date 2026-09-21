import sqlglot
from sqlglot import exp


class UnsafeSQLQueryError(ValueError):
    pass


def validate_sql(sql: str) -> None:
    sql = sql.strip()

    if not sql:
        raise UnsafeSQLQueryError("SQL query cannot be empty.")

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise UnsafeSQLQueryError("Invalid SQL query.") from exc

    if len(statements) != 1:
        raise UnsafeSQLQueryError("Multiple SQL statements are not allowed.")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise UnsafeSQLQueryError("Only SELECT queries are allowed.")
