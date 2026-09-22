import re


class DatabaseSecurityPolicy:
    MAX_ROWS = 1000

    def validate_row_limit(self, row_count: int) -> None:
        if row_count > self.MAX_ROWS:
            raise ValueError(
                f"Query returned too many rows: {row_count}. "
                f"Maximum allowed is {self.MAX_ROWS}."
            )

    def has_row_limit(self, sql: str, database_type: str) -> bool:
        normalized_sql = sql.strip().lower()

        if database_type in {"postgresql", "mysql"}:
            return bool(re.search(r"\blimit\s+\d+", normalized_sql))

        if database_type == "sqlserver":
            return bool(re.match(r"^select\s+(distinct\s+)?top\s+\d+", normalized_sql))

        return False
