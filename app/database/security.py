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
            return bool(
                re.match(
                    r"^select\s+(distinct\s+)?top\s+\d+",
                    normalized_sql,
                )
            )

        return False

    def apply_row_limit(self, sql: str, database_type: str) -> str:
        if self.has_row_limit(sql, database_type):
            return sql

        normalized_sql = sql.strip()

        if database_type in {"postgresql", "mysql"}:
            return f"{normalized_sql.rstrip(';')} LIMIT {self.MAX_ROWS}"

        if database_type == "sqlserver":
            if normalized_sql.lower().startswith("select "):
                return f"SELECT TOP {self.MAX_ROWS} {normalized_sql[7:]}"

        return sql
