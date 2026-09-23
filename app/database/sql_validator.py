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

    if schema is None:
        return

    # Map table aliases to their real table names.
    table_aliases: dict[str, str] = {}

    for table in statement.find_all(exp.Table):
        table_name = table.name

        if table_name not in schema:
            raise UnsafeSQLQueryError(
                f"Table '{table_name}' does not exist in the schema."
            )

        alias = table.alias

        if alias:
            table_aliases[alias] = table_name

    # Collect aliases defined in SELECT expressions.
    # Example:
    #   SUM(oi.line_total) AS total_sales
    #
    # "total_sales" is an SQL alias, not a database column.
    select_aliases: set[str] = set()

    for expression in statement.expressions:
        if isinstance(expression, exp.Alias):
            select_aliases.add(expression.alias)

    for column in statement.find_all(exp.Column):
        column_name = column.name

        # SELECT aliases such as "total_sales" are valid references
        # in clauses like ORDER BY.
        if not column.table and column_name in select_aliases:
            continue

        if column.table:
            table_reference = column.table

            # Resolve alias to the real table name.
            table_name = table_aliases.get(
                table_reference,
                table_reference,
            )

            if table_name not in schema:
                raise UnsafeSQLQueryError(
                    f"Table '{table_reference}' does not exist in the schema."
                )

            if column_name not in schema[table_name]:
                raise UnsafeSQLQueryError(
                    f"Column '{column_name}' does not exist in table '{table_name}'."
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
