import json

import requests

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.num_ctx = settings.ollama_num_ctx

    def _options(self) -> dict:
        return {
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
        }

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": self._options(),
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()["response"]

    def generate_json(self, prompt: str) -> dict:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": self._options(),
            },
            timeout=120,
        )

        response.raise_for_status()

        return json.loads(response.json()["response"])

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict],
    ) -> dict:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "tools": tools,
                "stream": False,
                "options": self._options(),
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()
