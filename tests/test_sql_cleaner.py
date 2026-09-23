from app.services.sql_cleaner import clean_sql


def test_clean_sql_removes_sql_code_fence():
    sql = """```sql
SELECT SUM(total_amount) FROM orders;
```"""

    result = clean_sql(sql)

    assert result == "SELECT SUM(total_amount) FROM orders;"


def test_clean_sql_removes_plain_code_fence():
    sql = """```
SELECT COUNT(*) FROM customers;
```"""

    result = clean_sql(sql)

    assert result == "SELECT COUNT(*) FROM customers;"
