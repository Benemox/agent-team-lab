from __future__ import annotations

import os
from typing import Any

from .base import ProviderResponse


def _usage_to_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return {"raw": str(usage)}


class OpenAIResponsesProvider:
    name = "openai"

    def __init__(self, model: str | None = None) -> None:
        from openai import OpenAI

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.client = OpenAI()

    def complete(self, *, instructions: str, prompt: str, project_path: str) -> ProviderResponse:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
        )
        return ProviderResponse(
            content=response.output_text,
            provider=self.name,
            model=self.model,
            usage=_usage_to_dict(getattr(response, "usage", None)),
        )


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(self, model: str | None = None) -> None:
        from openai import OpenAI

        base_url = os.environ["OPENAI_COMPATIBLE_BASE_URL"]
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY", "local")
        self.model = model or os.getenv("OPENAI_COMPATIBLE_MODEL", "local-model")
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def complete(self, *, instructions: str, prompt: str, project_path: str) -> ProviderResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return ProviderResponse(
            content=content,
            provider=self.name,
            model=self.model,
            usage=_usage_to_dict(getattr(response, "usage", None)),
        )
