from app.services.answer_prompt import build_answer_prompt


def test_build_answer_prompt_contains_question_and_result():
    prompt = build_answer_prompt(
        question="What are the total sales?",
        columns=["total_sales"],
        rows=[{"total_sales": "1022033.54"}],
    )

    assert "What are the total sales?" in prompt
    assert "total_sales" in prompt
    assert "1022033.54" in prompt


def test_build_answer_prompt_contains_answer_rules():
    prompt = build_answer_prompt(
        question="What are the total sales?",
        columns=["total_sales"],
        rows=[{"total_sales": "1022033.54"}],
    )

    assert "Do not invent information." in prompt
    assert "Return only the natural-language answer." in prompt
    assert "Do not mention SQL, database, tables, or internal processing." in prompt
