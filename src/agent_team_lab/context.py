from __future__ import annotations

import os
from pathlib import Path

DEFAULT_EXTENSIONS = {
    ".css",
    ".env.example",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rs",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}
IGNORED_DIRS = {
    ".git",
    ".idea",
    ".next",
    ".pytest_cache",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "var",
    "vendor",
}


class ProjectAccessError(ValueError):
    pass


class ProjectContextCollector:
    def __init__(
        self,
        allowed_root: str | Path | None = None,
        max_bytes: int = 120_000,
        max_files: int = 80,
    ) -> None:
        configured = allowed_root or os.getenv("AGENT_TEAM_ALLOWED_ROOT") or Path.cwd()
        self.allowed_root = Path(configured).expanduser().resolve()
        self.max_bytes = max_bytes
        self.max_files = max_files

    def resolve_project(self, project_path: str | Path) -> Path:
        project = Path(project_path).expanduser().resolve()
        if not project.is_dir():
            raise ProjectAccessError(f"El proyecto no existe o no es un directorio: {project}")
        if not project.is_relative_to(self.allowed_root):
            raise ProjectAccessError(
                f"El proyecto debe estar dentro de AGENT_TEAM_ALLOWED_ROOT={self.allowed_root}"
            )
        return project

    def collect(self, project_path: str | Path) -> tuple[Path, str]:
        project = self.resolve_project(project_path)
        chunks: list[str] = []
        total = 0
        file_count = 0

        for path in sorted(project.rglob("*")):
            if file_count >= self.max_files or total >= self.max_bytes:
                break
            if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.name not in {"Dockerfile", "Makefile", "composer.json"} and (
                path.suffix.lower() not in DEFAULT_EXTENSIONS
            ):
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if b"\x00" in data:
                continue
            remaining = self.max_bytes - total
            text = data[:remaining].decode("utf-8", errors="replace")
            relative = path.relative_to(project)
            chunk = f"\n--- FILE: {relative} ---\n{text}"
            chunks.append(chunk)
            total += len(chunk.encode("utf-8"))
            file_count += 1

        summary = (
            f"Project root: {project}\n"
            f"Files included: {file_count}\n"
            f"Context truncated: {'yes' if total >= self.max_bytes else 'no'}\n"
        )
        return project, summary + "".join(chunks)
