#!/usr/bin/env python3
"""Score an agent's output directory for one PBMC3k benchmark task.

Usage:  python benchmark/score.py TASK_ID AGENT_OUTPUT_DIR [--bench-dir DIR | $PBMC_REF_DIR] [--out score.json]

Evaluator-only. Each task has benchmark/<TASK_ID>/task_spec.json listing graders, weights and parameters.
A grader that returns None (optional artifact missing) is excluded and the remaining weights are
renormalized; `weight_scored` reports how much of the rubric could be scored.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graders import annotation, clustering, markers, normalization, qc, report  # noqa: E402
from graders.common import CANARY, Ctx  # noqa: E402

GRADERS = {"qc": qc.grade, "normalization": normalization.grade, "clustering": clustering.grade,
           "markers": markers.grade, "annotation": annotation.grade, "report": report.grade}


def score_task(task_id, agent_dir, bench_dir):
    ref_dir = Path(bench_dir) / task_id
    if not (ref_dir / "task_spec.json").exists():
        sys.exit(f"Reference files for {task_id} not found at {ref_dir}. Pass --bench-dir or set PBMC_REF_DIR "
                 "to the folder that holds the per-task reference folders (see benchmark/README.md).")
    spec = json.loads((ref_dir / "task_spec.json").read_text())
    ctx = Ctx(agent_dir, ref_dir)
    sections, details, weights = {}, {}, {}
    for g in spec["graders"]:
        score, info = GRADERS[g["name"]](ctx, g["params"])
        sections[g["name"]], details[g["name"]], weights[g["name"]] = score, info, g["weight"]
    scored = {k: v for k, v in sections.items() if v is not None}
    total = sum(weights.values())
    used = sum(weights[k] for k in scored)
    overall = sum(weights[k] * v for k, v in scored.items()) / used if used else 0.0
    return {"task_id": task_id, "overall": overall, "weight_scored": round(used / total, 3),
            "sections": sections, "weights": weights, "details": details, "canary": CANARY}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_id")
    ap.add_argument("agent_dir")
    ap.add_argument("--bench-dir", default=os.environ.get("PBMC_REF_DIR") or str(Path(__file__).resolve().parent),
                    help="folder with the per-task reference files (default: $PBMC_REF_DIR, else this folder)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = score_task(a.task_id, a.agent_dir, a.bench_dir)
    print(f"\n=== {res['task_id']}: {a.agent_dir} ===")
    for k, v in res["sections"].items():
        print(f"  {k:<14} {'not scored' if v is None else f'{v:.3f}'}   (weight {res['weights'][k]})")
    print(f"  {'OVERALL':<14} {res['overall']:.3f}   (weight scored {res['weight_scored']})\n")
    print(json.dumps(res["details"], indent=2, default=str))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
