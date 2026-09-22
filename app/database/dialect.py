from abc import ABC, abstractmethod


class DatabaseDialect(ABC):
    @abstractmethod
    def placeholder(self) -> str:
        pass


class PostgreSQLDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "%s"


class MySQLDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "%s"


class SQLServerDialect(DatabaseDialect):
    def placeholder(self) -> str:
        return "?"
