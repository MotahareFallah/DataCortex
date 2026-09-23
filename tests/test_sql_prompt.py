from app.services.sql_prompt import build_sql_prompt


def test_sql_prompt_requires_minimum_number_of_tables():
    prompt = build_sql_prompt(
        question="What are the total sales?",
        schema="""
        orders(id, total_amount)
        order_items(id, order_id, product_id)
        products(id, name)
        """,
    )

    assert "Use the minimum number of tables required" in prompt
    assert "Do not add JOINs unless they are necessary" in prompt


def test_sql_prompt_requires_valid_table_column_relationship():
    prompt = build_sql_prompt(
        question="What are the total sales?",
        schema="orders(id, total_amount)",
    )

    assert (
        "Carefully verify that every column belongs to the table or alias used"
        in prompt
    )
    assert "orders(id, total_amount)" in prompt


def test_build_sql_prompt_for_postgresql():
    prompt = build_sql_prompt(
        question="Show total sales",
        schema="orders(id, total)",
        database_type="postgresql",
    )

    assert "postgresql" in prompt
    assert "%s" in prompt


def test_build_sql_prompt_for_mysql():
    prompt = build_sql_prompt(
        question="Show total sales",
        schema="orders(id, total)",
        database_type="mysql",
    )

    assert "mysql" in prompt.lower()
    assert "%s" in prompt


def test_build_sql_prompt_for_sqlserver():
    prompt = build_sql_prompt(
        question="Show total sales",
        schema="orders(id, total)",
        database_type="sqlserver",
    )

    assert "sqlserver" in prompt.lower()
    assert "?" in prompt


def test_sql_prompt_includes_business_semantics():
    prompt = build_sql_prompt(
        question="What are the total sales?",
        schema="orders(id, total_amount)",
    )

    assert "Business semantics:" in prompt
    assert "total_sales" in prompt
    assert "sum of order_items.line_total" in prompt
