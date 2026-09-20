from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class ProviderName(StrEnum):
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai-compatible"
    HERMES = "hermes"
    MOCK = "mock"


@dataclass(frozen=True)
class Role:
    id: str
    name: str
    description: str
    instructions: str


@dataclass(frozen=True)
class Stage:
    id: str
    objective: str
    roles: tuple[str, ...]


@dataclass
class AgentResult:
    stage: str
    role: str
    content: str
    provider: str
    model: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TeamRun:
    task: str
    project_path: str
    results: list[AgentResult]

    @property
    def final_answer(self) -> str:
        return self.results[-1].content if self.results else ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "project_path": self.project_path,
            "results": [result.to_dict() for result in self.results],
            "final_answer": self.final_answer,
        }
