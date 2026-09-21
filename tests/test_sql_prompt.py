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
