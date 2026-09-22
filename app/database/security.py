from app.database.database import DatabaseAdapter


class DatabaseSecurityPolicy:
    MAX_ROWS = 1000

    def validate_row_limit(self, row_count: int) -> None:
        if row_count > self.MAX_ROWS:
            raise ValueError(
                f"Query returned too many rows: {row_count}. "
                f"Maximum allowed is {self.MAX_ROWS}."
            )

    def has_row_limit(self, sql: str, adapter: DatabaseAdapter) -> bool:
        return adapter.has_limit(sql)

    def apply_row_limit(
        self,
        sql: str,
        adapter: DatabaseAdapter,
    ) -> str:
        if self.has_row_limit(sql, adapter):
            return sql

        return adapter.apply_limit(sql, self.MAX_ROWS)
