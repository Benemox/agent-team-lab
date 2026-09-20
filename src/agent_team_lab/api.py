from __future__ import annotations

import os
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .orchestrator import TeamOrchestrator
from .providers import build_provider
from .roles import load_roles

app = FastAPI(title="Agent Team Lab", version="0.1.0")


class RunRequest(BaseModel):
    task: str = Field(min_length=3, max_length=20_000)
    project_path: str = "."
    provider: str | None = None
    model: str | None = None


def authorize(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("AGENT_TEAM_API_TOKEN")
    if expected and authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/roles", dependencies=[Depends(authorize)])
def roles() -> list[dict[str, str]]:
    return [
        {"id": role.id, "name": role.name, "description": role.description}
        for role in load_roles().values()
    ]


@app.post("/v1/team/run", dependencies=[Depends(authorize)])
def run_team(request: RunRequest) -> dict:
    try:
        orchestrator = TeamOrchestrator(build_provider(request.provider, request.model))
        return orchestrator.run(task=request.task, project_path=request.project_path).to_dict()
    except (KeyError, RuntimeError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/experts/{role_id}", dependencies=[Depends(authorize)])
def ask_expert(role_id: str, request: RunRequest) -> dict:
    try:
        orchestrator = TeamOrchestrator(build_provider(request.provider, request.model))
        return orchestrator.ask_expert(
            role_id=role_id,
            task=request.task,
            project_path=request.project_path,
        ).to_dict()
    except (KeyError, RuntimeError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def main() -> None:
    uvicorn.run(
        "agent_team_lab.api:app",
        host=os.getenv("AGENT_TEAM_HOST", "127.0.0.1"),
        port=int(os.getenv("AGENT_TEAM_PORT", "8008")),
    )
