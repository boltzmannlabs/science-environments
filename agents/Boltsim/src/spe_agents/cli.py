from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .evaluation import IndependentEvaluator
from .models import SPEConfigurationError
from .prompts import build_system_prompt
from .registry import SPERegistry


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect Boltzmann Labs SPE agent environments")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="validate all 18 active SPE contracts")
    commands.add_parser("list", help="list SPE contracts")
    show = commands.add_parser("show", help="show one SPE contract")
    show.add_argument("identifier")
    prompt = commands.add_parser("prompt", help="render one specialist system prompt")
    prompt.add_argument("identifier")
    route = commands.add_parser("route", help="rank candidate SPE specialists")
    route.add_argument("task")
    route.add_argument("--limit", type=int, default=3)
    evaluate = commands.add_parser("evaluate", help="evaluate acceptance evidence from JSON")
    evaluate.add_argument("identifier")
    evaluate.add_argument("evidence", help="JSON file mapping exact acceptance criteria to true, false, or null")
    evaluate.add_argument("--execution-completed", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        registry = SPERegistry()
        if args.command == "validate":
            print(f"Validated {len(registry.all())} SPE agent environments.")
        elif args.command == "list":
            print(json.dumps([agent.summary() for agent in registry.all()], indent=2))
        elif args.command == "show":
            print(json.dumps(registry.get(args.identifier).__dict__, indent=2, default=str))
        elif args.command == "prompt":
            print(build_system_prompt(registry.get(args.identifier)), end="")
        elif args.command == "route":
            matches = [
                {"score": score, **agent.summary()}
                for agent, score in registry.route(args.task, limit=args.limit)
            ]
            print(json.dumps(matches, indent=2))
            return 0 if matches else 2
        elif args.command == "evaluate":
            raw = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or not all(
                isinstance(key, str) and (value is None or isinstance(value, bool))
                for key, value in raw.items()
            ):
                raise SPEConfigurationError("evidence JSON must map strings to true, false, or null")
            report = IndependentEvaluator().evaluate(
                registry.get(args.identifier),
                raw,
                execution_completed=args.execution_completed,
            )
            print(json.dumps(report.to_dict(), indent=2))
            return 0 if report.decision.value == "pass" else 2
    except (SPEConfigurationError, KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
