from app.services.sql_cleaner import clean_sql, is_cannot_answer

# Built programmatically so the file never contains literal triple backticks.
FENCE = "`" * 3


def test_clean_sql_removes_sql_code_fence():
    sql = f"{FENCE}sql\nSELECT SUM(total_amount) FROM orders;\n{FENCE}"

    result = clean_sql(sql)

    assert result == "SELECT SUM(total_amount) FROM orders;"


def test_clean_sql_removes_plain_code_fence():
    sql = f"{FENCE}\nSELECT COUNT(*) FROM customers;\n{FENCE}"

    result = clean_sql(sql)

    assert result == "SELECT COUNT(*) FROM customers;"


def test_is_cannot_answer_detects_marker():
    assert is_cannot_answer("CANNOT_ANSWER") is True
    assert is_cannot_answer("  cannot_answer.  ") is True


def test_is_cannot_answer_ignores_normal_sql():
    assert is_cannot_answer("SELECT 1") is False
    assert is_cannot_answer("SELECT COUNT(*) FROM customers;") is False
