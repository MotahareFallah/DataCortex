from app.services.answer import AnswerService


def test_generate_answer_formats_multiple_rows():
    service = AnswerService()

    result = service.generate_answer(
        question="What are the top products by total sales?",
        columns=["name", "total_sales"],
        rows=[
            {
                "name": "Product A",
                "total_sales": "31642.81",
            },
            {
                "name": "Product B",
                "total_sales": "24842.32",
            },
        ],
    )

    assert result == ("1. Product A — 31642.81\n2. Product B — 24842.32")


def test_generate_answer_formats_single_value():
    service = AnswerService()

    result = service.generate_answer(
        question="What are the total sales?",
        columns=["total_sales"],
        rows=[{"total_sales": "1022033.54"}],
    )

    assert result == "total_sales: 1022033.54"


def test_generate_answer_handles_empty_rows():
    service = AnswerService()

    result = service.generate_answer(
        question="What are the total sales?",
        columns=["total_sales"],
        rows=[],
    )

    assert result == "No results found."
