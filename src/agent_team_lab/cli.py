from __future__ import annotations

import argparse
import json

from .api import main as serve_api
from .orchestrator import TeamOrchestrator
from .providers import build_provider
from .roles import load_roles


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="agent-team")
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("roles", help="Lista los expertos disponibles")

    run = commands.add_parser("run", help="Ejecuta el flujo completo")
    run.add_argument("task")
    run.add_argument("--project", default=".")
    run.add_argument("--provider", default=None)
    run.add_argument("--model", default=None)

    expert = commands.add_parser("ask", help="Consulta a un experto")
    expert.add_argument("role")
    expert.add_argument("task")
    expert.add_argument("--project", default=".")
    expert.add_argument("--provider", default=None)
    expert.add_argument("--model", default=None)

    commands.add_parser("serve", help="Levanta la API REST")
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "roles":
        print(
            json.dumps(
                [role.__dict__ for role in load_roles().values()], indent=2, ensure_ascii=False
            )
        )
        return
    if args.command == "serve":
        serve_api()
        return

    orchestrator = TeamOrchestrator(build_provider(args.provider, args.model))
    if args.command == "run":
        result = orchestrator.run(task=args.task, project_path=args.project)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        result = orchestrator.ask_expert(
            role_id=args.role,
            task=args.task,
            project_path=args.project,
        )
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
