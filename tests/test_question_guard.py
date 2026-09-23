import pytest

from app.services.question_guard import is_write_request


@pytest.mark.parametrize(
    "question",
    [
        "Delete all orders",
        "delete all orders",
        "Please drop the products table",
        "Can you update the price of every product?",
        "  Truncate customers",
    ],
)
def test_write_requests_are_detected(question):
    assert is_write_request(question) is True


@pytest.mark.parametrize(
    "question",
    [
        "What are the top 5 products by total sales?",
        "Which products had the biggest price drop?",
        "Show orders that were deleted last month",
        "When was the last update to the customers table?",
    ],
)
def test_read_questions_are_not_blocked(question):
    assert is_write_request(question) is False
