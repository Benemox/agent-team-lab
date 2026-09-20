from __future__ import annotations

import os

from .base import AgentProvider
from .hermes_provider import HermesCliProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAICompatibleProvider, OpenAIResponsesProvider


def build_provider(name: str | None = None, model: str | None = None) -> AgentProvider:
    selected = (name or os.getenv("AGENT_TEAM_PROVIDER", "openai")).lower()
    if selected == "openai":
        return OpenAIResponsesProvider(model=model)
    if selected == "openai-compatible":
        return OpenAICompatibleProvider(model=model)
    if selected == "hermes":
        return HermesCliProvider()
    if selected == "mock":
        return MockProvider()
    raise ValueError(f"Proveedor no soportado: {selected}")
