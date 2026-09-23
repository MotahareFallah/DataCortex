from unittest.mock import Mock, patch

from app.core.config import settings
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
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": "Test prompt",
            "stream": False,
            "options": {
                "temperature": settings.ollama_temperature,
                "num_ctx": settings.ollama_num_ctx,
            },
        },
        timeout=120,
    )
