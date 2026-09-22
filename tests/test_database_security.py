import pytest

from app.database.database import get_database_adapter
from app.database.security import DatabaseSecurityPolicy


def test_max_rows_is_1000():
    policy = DatabaseSecurityPolicy()

    assert policy.MAX_ROWS == 1000


def test_validate_row_limit_accepts_allowed_rows():
    policy = DatabaseSecurityPolicy()

    policy.validate_row_limit(1000)


def test_validate_row_limit_rejects_too_many_rows():
    policy = DatabaseSecurityPolicy()

    with pytest.raises(ValueError, match="Query returned too many rows"):
        policy.validate_row_limit(1001)


def test_has_row_limit_detects_postgresql_limit():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("postgresql")

    assert policy.has_row_limit(
        "SELECT * FROM products LIMIT 10",
        adapter,
    )


def test_has_row_limit_detects_mysql_limit():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("mysql")

    assert policy.has_row_limit(
        "SELECT * FROM products LIMIT 10",
        adapter,
    )


def test_has_row_limit_detects_sqlserver_top():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("sqlserver")

    assert policy.has_row_limit(
        "SELECT TOP 10 * FROM products",
        adapter,
    )


def test_apply_row_limit_adds_postgresql_limit():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("postgresql")

    result = policy.apply_row_limit(
        "SELECT * FROM products",
        adapter,
    )

    assert result == "SELECT * FROM products LIMIT 1000"


def test_apply_row_limit_preserves_existing_limit():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("postgresql")

    result = policy.apply_row_limit(
        "SELECT * FROM products LIMIT 10",
        adapter,
    )

    assert result == "SELECT * FROM products LIMIT 10"


def test_apply_row_limit_adds_sqlserver_top():
    policy = DatabaseSecurityPolicy()
    adapter = get_database_adapter("sqlserver")

    result = policy.apply_row_limit(
        "SELECT * FROM products",
        adapter,
    )

    assert result == "SELECT TOP 1000 * FROM products"
