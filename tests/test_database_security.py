import pytest

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

    assert policy.has_row_limit(
        "SELECT * FROM products LIMIT 10",
        "postgresql",
    )


def test_has_row_limit_detects_mysql_limit():
    policy = DatabaseSecurityPolicy()

    assert policy.has_row_limit(
        "SELECT * FROM products LIMIT 10",
        "mysql",
    )


def test_has_row_limit_detects_sqlserver_top():
    policy = DatabaseSecurityPolicy()

    assert policy.has_row_limit(
        "SELECT TOP 10 * FROM products",
        "sqlserver",
    )
