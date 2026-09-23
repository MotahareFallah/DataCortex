import sqlglot
from sqlglot import exp


class UnsafeSQLQueryError(ValueError):
    pass


def validate_sql(
    sql: str,
    schema: dict[str, set[str]] | None = None,
) -> None:
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

    if schema is not None:
        for table in statement.find_all(exp.Table):
            table_name = table.name

            if table_name not in schema:
                raise UnsafeSQLQueryError(
                    f"Table '{table_name}' does not exist in the schema."
                )

        for column in statement.find_all(exp.Column):
            column_name = column.name

            if column.table:
                table_name = column.table

                if table_name not in schema:
                    raise UnsafeSQLQueryError(
                        f"Table '{table_name}' does not exist in the schema."
                    )

                if column_name not in schema[table_name]:
                    raise UnsafeSQLQueryError(
                        f"Column '{column_name}' does not exist in table "
                        f"'{table_name}'."
                    )

                continue

            matching_tables = [
                table_name
                for table_name, columns in schema.items()
                if column_name in columns
            ]

            if not matching_tables:
                raise UnsafeSQLQueryError(
                    f"Column '{column_name}' does not exist in the schema."
                )
