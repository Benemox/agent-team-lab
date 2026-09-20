from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ProviderResponse:
    content: str
    provider: str
    model: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)


class AgentProvider(Protocol):
    name: str

    def complete(
        self, *, instructions: str, prompt: str, project_path: str
    ) -> ProviderResponse: ...
