from unittest.mock import patch

from app.services.answer import AnswerService


def test_generate_answer_returns_llm_response():
    with patch("app.services.answer.LLMService") as mock_llm:
        mock_llm.return_value.generate.return_value = (
            "The total sales are 1,022,033.54."
        )

        service = AnswerService()

        result = service.generate_answer(
            question="What are the total sales?",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
        )

        assert result == "The total sales are 1,022,033.54."


def test_generate_answer_passes_prompt_to_llm():
    with patch("app.services.answer.LLMService") as mock_llm:
        mock_llm.return_value.generate.return_value = (
            "The total sales are 1,022,033.54."
        )

        service = AnswerService()

        service.generate_answer(
            question="What are the total sales?",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
        )

        mock_llm.return_value.generate.assert_called_once()

        prompt = mock_llm.return_value.generate.call_args.args[0]

        assert "What are the total sales?" in prompt
        assert "1022033.54" in prompt


def test_generate_answer_strips_llm_response():
    with patch("app.services.answer.LLMService") as mock_llm:
        mock_llm.return_value.generate.return_value = (
            "  The total sales are 1,022,033.54.  \n"
        )

        service = AnswerService()

        result = service.generate_answer(
            question="What are the total sales?",
            columns=["total_sales"],
            rows=[{"total_sales": "1022033.54"}],
        )

        assert result == "The total sales are 1,022,033.54."
