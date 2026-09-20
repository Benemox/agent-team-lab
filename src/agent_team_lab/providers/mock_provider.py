from __future__ import annotations

from .base import ProviderResponse


class MockProvider:
    name = "mock"

    def complete(self, *, instructions: str, prompt: str, project_path: str) -> ProviderResponse:
        marker = prompt.splitlines()[0] if prompt else "empty"
        return ProviderResponse(
            content=f"MOCK RESULT | {marker} | project={project_path}",
            provider=self.name,
            model="deterministic-test-provider",
        )
