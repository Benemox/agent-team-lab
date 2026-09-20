from __future__ import annotations

import os
import shutil
import subprocess

from .base import ProviderResponse


class HermesCliProvider:
    name = "hermes"

    def __init__(self) -> None:
        self.binary = os.getenv("HERMES_BINARY", "hermes")
        self.timeout = int(os.getenv("HERMES_TIMEOUT_SECONDS", "300"))
        if shutil.which(self.binary) is None:
            raise RuntimeError(
                "No se encuentra Hermes. Instálalo y ejecuta `hermes setup`, "
                "o selecciona AGENT_TEAM_PROVIDER=openai."
            )

    def complete(self, *, instructions: str, prompt: str, project_path: str) -> ProviderResponse:
        full_prompt = f"{instructions}\n\n{prompt}"
        process = subprocess.run(
            [self.binary, "chat", "--oneshot", "-q", full_prompt],
            cwd=project_path,
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if process.returncode != 0:
            error = process.stderr.strip() or "Hermes terminó sin explicar el error"
            raise RuntimeError(f"Hermes falló ({process.returncode}): {error}")
        return ProviderResponse(content=process.stdout.strip(), provider=self.name)
