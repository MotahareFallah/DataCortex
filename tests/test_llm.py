from unittest.mock import Mock, patch

from app.services.llm import LLMService


@patch("app.services.llm.requests.post")
def test_llm_generate_returns_response(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"response": "DataCortex works."}
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    service = LLMService()

    result = service.generate("Say hello.")

    assert result == "DataCortex works."

    mock_post.assert_called_once()


@patch("app.services.llm.requests.post")
def test_llm_generate_sends_correct_payload(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"response": "OK"}
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    service = LLMService()

    service.generate("Test prompt")

    mock_post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5-coder:1.5b",
            "prompt": "Test prompt",
            "stream": False,
        },
        timeout=120,
    )
