import re


class UnsafeSQLQueryError(ValueError):
    pass


def validate_sql(sql: str) -> None:
    normalized_sql = sql.strip().lower()

    if not normalized_sql:
        raise UnsafeSQLQueryError("SQL query cannot be empty.")

    if not normalized_sql.startswith("select"):
        raise UnsafeSQLQueryError("Only SELECT queries are allowed.")

    if ";" in normalized_sql.rstrip(";"):
        raise UnsafeSQLQueryError("Multiple SQL statements are not allowed.")

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
    ]

    for keyword in forbidden_keywords:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, normalized_sql):
            raise UnsafeSQLQueryError(f"SQL keyword '{keyword}' is not allowed.")
