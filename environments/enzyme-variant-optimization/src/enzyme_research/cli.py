"""Operator entrypoint; synthetic and live operations are kept explicit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import ResearchError, strict_load
from .store import Store


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("demo")
    sub.add_argument("--output", required=True)
    sub.add_argument("--upstream", required=True)
    sub = commands.add_parser("start")
    sub.add_argument("--task", required=True)
    sub.add_argument("--state", required=True)
    sub.add_argument("--arm", choices=["fixed", "base", "specialist"], required=True)
    for name in ("status", "report"):
        sub = commands.add_parser(name)
        sub.add_argument("--state", required=True)
        sub.add_argument("--campaign", required=True)
        if name == "report":
            sub.add_argument("--output", help="Optional NEW directory for the complete joined JSON/CSV report")
            sub.add_argument("--workflow-source", help="Optional original executor source, needed to reparse the supplied parent")
    sub = commands.add_parser("connector-check")
    sub.add_argument("--runtime", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            from .demo import demo
            result = demo(args.output, args.upstream)
        elif args.command == "connector-check":
            from .connector import NativeConnector
            result = NativeConnector(args.runtime).call("connector_availability", {})
        else:
            store = Store(args.state)
            if args.command == "start":
                result = {"campaign_id": store.start(strict_load(args.task), args.arm), "scientific_jobs_submitted": 0}
            else:
                result = store.status(args.campaign)
                if args.command == "report":
                    if args.workflow_source:
                        from .workflow import load_workflow
                        load_workflow(args.workflow_source)
                    from .reporting import build_report, export_report, summary
                    report = build_report(store, args.campaign)
                    result = summary(report)
                    if args.output:
                        result["export"] = export_report(report, args.output)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ResearchError, OSError, ValueError) as exc:
        parser.exit(2, "Research operation failed: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
