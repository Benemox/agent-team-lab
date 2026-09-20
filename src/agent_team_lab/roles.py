from __future__ import annotations

import re
from pathlib import Path

from .models import Role

ROLE_NAMES = {
    "agent-pm": "Product Manager",
    "agent-architect": "Software Architect",
    "agent-programmer": "Programmer",
    "agent-qa": "QA Engineer",
    "agent-security": "Security Engineer",
}


def default_skills_dir() -> Path:
    source_checkout = Path(__file__).resolve().parents[2] / "skills"
    if source_checkout.is_dir():
        return source_checkout
    return Path.cwd() / "skills"


def _parse_skill(path: Path, role_id: str) -> Role:
    raw = path.read_text(encoding="utf-8")
    description = ""
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            frontmatter, body = parts[1], parts[2]
            match = re.search(r"^description:\s*[\"']?(.*?)[\"']?\s*$", frontmatter, re.MULTILINE)
            description = match.group(1) if match else ""
    return Role(
        id=role_id,
        name=ROLE_NAMES.get(role_id, role_id),
        description=description,
        instructions=body.strip(),
    )


def load_roles(skills_dir: Path | None = None) -> dict[str, Role]:
    root = skills_dir or default_skills_dir()
    roles: dict[str, Role] = {}
    for role_id in ROLE_NAMES:
        skill_path = root / role_id / "SKILL.md"
        if not skill_path.is_file():
            raise FileNotFoundError(f"No se encuentra el skill requerido: {skill_path}")
        roles[role_id] = _parse_skill(skill_path, role_id)
    return roles
