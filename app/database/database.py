from app.database.dialect import (
    DatabaseDialect,
    MySQLDialect,
    PostgreSQLDialect,
    SQLServerDialect,
)


class DatabaseAdapter:
    def __init__(self, dialect: DatabaseDialect) -> None:
        self.dialect = dialect

    def placeholder(self) -> str:
        return self.dialect.placeholder()

    def apply_limit(self, sql: str, limit: int) -> str:
        return self.dialect.apply_limit(sql, limit)


def get_database_adapter(database_type: str) -> DatabaseAdapter:
    dialects = {
        "postgresql": PostgreSQLDialect(),
        "mysql": MySQLDialect(),
        "sqlserver": SQLServerDialect(),
    }

    try:
        dialect = dialects[database_type.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported database type: {database_type}") from exc

    return DatabaseAdapter(dialect)
