from abc import ABC, abstractmethod


class DatabaseDialect(ABC):
    @abstractmethod
    def placeholder(self) -> str:
        pass

    @abstractmethod
    def has_limit(self, sql: str) -> bool:
        pass

    @abstractmethod
    def apply_limit(self, sql: str, limit: int) -> str:
        pass


class PostgreSQLDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "%s"

    def has_limit(self, sql: str) -> bool:
        return "limit" in sql.lower()

    def apply_limit(self, sql: str, limit: int) -> str:
        return f"{sql.rstrip().rstrip(';')} LIMIT {limit}"


class MySQLDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "%s"

    def has_limit(self, sql: str) -> bool:
        return "limit" in sql.lower()

    def apply_limit(self, sql: str, limit: int) -> str:
        return f"{sql.rstrip().rstrip(';')} LIMIT {limit}"


class SQLServerDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "?"

    def has_limit(self, sql: str) -> bool:
        normalized_sql = sql.strip().lower()

        return normalized_sql.startswith(("select top ", "select distinct top "))

    def apply_limit(self, sql: str, limit: int) -> str:
        sql = sql.strip()

        if sql.lower().startswith("select "):
            return f"SELECT TOP {limit} {sql[7:]}"

        return sql
