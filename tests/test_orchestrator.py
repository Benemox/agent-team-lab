from pathlib import Path

import pytest

from agent_team_lab.context import ProjectAccessError, ProjectContextCollector
from agent_team_lab.orchestrator import TeamOrchestrator, load_stages
from agent_team_lab.providers.mock_provider import MockProvider
from agent_team_lab.roles import load_roles


def test_team_runs_all_stages_and_keeps_final_decision(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    collector = ProjectContextCollector(allowed_root=tmp_path)
    orchestrator = TeamOrchestrator(
        MockProvider(),
        collector=collector,
        roles=load_roles(),
        stages=load_stages(),
    )

    result = orchestrator.run(task="Añade una comprobación de salud", project_path=tmp_path)

    assert [item.stage for item in result.results] == [
        "discovery",
        "architecture",
        "implementation",
        "validation",
        "validation",
        "decision",
    ]
    assert result.results[-1].role == "agent-pm"
    assert result.final_answer.startswith("MOCK RESULT")


def test_collector_rejects_paths_outside_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    collector = ProjectContextCollector(allowed_root=allowed)

    with pytest.raises(ProjectAccessError):
        collector.collect(outside)


def test_single_expert_rejects_unknown_role(tmp_path: Path) -> None:
    orchestrator = TeamOrchestrator(
        MockProvider(),
        collector=ProjectContextCollector(allowed_root=tmp_path),
        roles=load_roles(),
        stages=load_stages(),
    )

    with pytest.raises(ValueError, match="Rol desconocido"):
        orchestrator.ask_expert(role_id="wizard", task="Revisa esto", project_path=tmp_path)
