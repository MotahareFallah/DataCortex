import pytest

from app.database.database import (
    DatabaseAdapter,
    get_database_adapter,
)
from app.database.dialect import (
    MySQLDialect,
    PostgreSQLDialect,
    SQLServerDialect,
)


def test_postgresql_dialect_placeholder():
    dialect = PostgreSQLDialect()

    assert dialect.placeholder() == "%s"


def test_mysql_dialect_placeholder():
    dialect = MySQLDialect()

    assert dialect.placeholder() == "%s"


def test_sqlserver_dialect_placeholder():
    dialect = SQLServerDialect()

    assert dialect.placeholder() == "?"


def test_database_adapter_uses_postgresql_dialect():
    adapter = DatabaseAdapter(PostgreSQLDialect())

    assert adapter.placeholder() == "%s"


def test_database_adapter_uses_mysql_dialect():
    adapter = DatabaseAdapter(MySQLDialect())

    assert adapter.placeholder() == "%s"


def test_database_adapter_uses_sqlserver_dialect():
    adapter = DatabaseAdapter(SQLServerDialect())

    assert adapter.placeholder() == "?"


def test_get_database_adapter_returns_adapter():
    adapter = get_database_adapter("postgresql")

    assert isinstance(adapter, DatabaseAdapter)


def test_get_database_adapter_rejects_unsupported_database():
    with pytest.raises(ValueError, match="Unsupported database type"):
        get_database_adapter("oracle")
