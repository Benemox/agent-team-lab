from __future__ import annotations

from mcp.server import MCPServer

from .orchestrator import TeamOrchestrator
from .providers import build_provider
from .roles import load_roles

mcp = MCPServer("Agent Team Lab")


@mcp.tool()
def list_experts() -> list[dict[str, str]]:
    """List the expert roles available in this agent team."""
    return [
        {"id": role.id, "name": role.name, "description": role.description}
        for role in load_roles().values()
    ]


@mcp.tool()
def ask_expert(
    task: str, role_id: str, project_path: str = ".", provider: str | None = None
) -> dict:
    """Ask one specialist to review a task and the readable source files in a project."""
    orchestrator = TeamOrchestrator(build_provider(provider))
    return orchestrator.ask_expert(
        role_id=role_id,
        task=task,
        project_path=project_path,
    ).to_dict()


@mcp.tool()
def run_team(task: str, project_path: str = ".", provider: str | None = None) -> dict:
    """Run the connected PM, architecture, programming, QA and security workflow."""
    orchestrator = TeamOrchestrator(build_provider(provider))
    return orchestrator.run(task=task, project_path=project_path).to_dict()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
