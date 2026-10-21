from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .dataset import load_dataset
from .evaluator import BenchmarkEvaluator, ReferenceStore
from .models import Approach, CaseRun, Split
from .policies import (
    AgentScientistPolicy,
    CommandDecisionProvider,
    FixedWorkflowPolicy,
    SpecialistAssistedPolicy,
)
from .report import markdown_report
from .runner import BenchmarkRunner, LocalSubprocessBackend


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_approaches(value: str) -> tuple[Approach, ...]:
    if value == "all":
        return tuple(Approach)
    try:
        parsed = tuple(Approach(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not parsed:
        raise argparse.ArgumentTypeError("at least one approach is required")
    return parsed


def _policies(approaches: Iterable[Approach], decision_command: str | None):
    provider = (
        CommandDecisionProvider.from_command_line(decision_command)
        if decision_command
        else None
    )
    for approach in approaches:
        if approach is Approach.FIXED:
            yield FixedWorkflowPolicy()
        elif provider is None:
            raise SystemExit(
                f"{approach.value} requires --decision-command; no proxy agent results will be fabricated"
            )
        elif approach is Approach.AGENT:
            yield AgentScientistPolicy(provider)
        else:
            yield SpecialistAssistedPolicy(provider)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the controlled Boltzmann SPE benchmark")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("benchmark/spe_v1/dataset_manifest.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=("development", "held-out", "all"), default="development")
    parser.add_argument("--approaches", type=_parse_approaches, default=(Approach.FIXED,))
    parser.add_argument("--decision-command")
    parser.add_argument("--module-root", type=Path, default=None)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--repeat-index", type=int, default=1)
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else project_root / args.manifest
    output = args.output if args.output.is_absolute() else project_root / args.output
    dataset = load_dataset(manifest, project_root)
    split = None if args.split == "all" else Split(args.split)
    cases = list(dataset.cases_for_split(split))
    if args.case_ids:
        requested = set(args.case_ids)
        cases = [case for case in cases if case.case_id in requested]
        missing = requested - {case.case_id for case in cases}
        if missing:
            raise SystemExit(f"unknown or split-excluded case IDs: {', '.join(sorted(missing))}")
    if not cases:
        raise SystemExit("no benchmark cases selected")

    output.mkdir(parents=True, exist_ok=True)
    backend = LocalSubprocessBackend(output / "backend_runs", args.module_root)
    runner = BenchmarkRunner(
        backend,
        dataset.budget,
        supported_methods=dataset.permitted_methods,
        supported_basis_sets=dataset.permitted_basis_sets,
    )
    runs: list[CaseRun] = []
    for policy in _policies(args.approaches, args.decision_command):
        for case in cases:
            runs.append(runner.run_case(case, policy))
            (output / "case_runs").mkdir(exist_ok=True)
            case_path = output / "case_runs" / f"{policy.approach.value}__{case.case_id}.json"
            case_path.write_text(
                json.dumps(runs[-1].to_dict(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    references = ReferenceStore(dataset.reference_store_path)
    evaluator = BenchmarkEvaluator(references)
    mapping = {case.case_id: case.reference_id for case in cases if case.reference_id}
    bundle = evaluator.evaluate(runs, mapping)
    completed_approaches = sorted({run.approach.value for run in runs})
    expected_approaches = {item.value for item in Approach}
    run_status = "complete" if set(completed_approaches) == expected_approaches else "partial"
    result = {
        "schema_version": "1.0",
        "benchmark_id": dataset.benchmark_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_status": run_status,
        "split": args.split,
        "repeat_index": args.repeat_index,
        "approaches_executed": completed_approaches,
        "backend": "LocalBoltzmannSPEAdapter isolated subprocess",
        "manifest": {
            "path": str(dataset.manifest_path),
            "sha256": dataset.manifest_sha256,
        },
        "reference_store": {
            "path": str(dataset.reference_store_path),
            "sha256": dataset.reference_store_sha256,
            "access": "evaluator-only",
        },
        "budget": {
            "max_tool_calls": dataset.budget.max_tool_calls,
            "max_retries": dataset.budget.max_retries,
            "per_attempt_timeout_seconds": dataset.budget.per_attempt_timeout_seconds,
            "max_case_wall_seconds": dataset.budget.max_case_wall_seconds,
        },
        "runs": [run.to_dict() for run in runs],
        "evaluation": bundle.to_dict(),
    }
    results_path = output / "benchmark_results.json"
    results_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = output / "benchmark_report.md"
    report_path.write_text(
        markdown_report(
            bundle.metrics,
            benchmark_id=dataset.benchmark_id,
            reference_scope=bundle.reference_scope,
            run_status=run_status,
        ),
        encoding="utf-8",
    )
    integrity = {
        "benchmark_results.json": _sha256(results_path),
        "benchmark_report.md": _sha256(report_path),
    }
    (output / "integrity.json").write_text(
        json.dumps(integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
