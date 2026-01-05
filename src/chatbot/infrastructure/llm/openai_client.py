from __future__ import annotations

from typing import Optional

from django.conf import settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class DummyLLMClient:
    def answer(self, system: str, user: str) -> str:
        return (
            "Based on my data: I am Shintaro Miyata, and my main skills include "
            "Python/Django. (Sources: profile.txt, skills.txt)"
        )


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        self._model = getattr(settings, "OPENAI_MODEL", model)

    def answer(self, system: str, user: str) -> str:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed")
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = OpenAI(api_key=self._api_key)
        resp = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        content = resp.choices[0].message.content
        return content or ""
