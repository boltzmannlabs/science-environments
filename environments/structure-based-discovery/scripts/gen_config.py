"""Regenerate config/environment.json, benchmark/benchmark.json and
benchmark/papers.csv from the task documents (source of truth).
Usage: python3 scripts/gen_config.py"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import env_lib  # noqa: E402


def main():
    tasks = []
    for fname in env_lib.task_files():
        parsed = env_lib.parse_task(os.path.join(env_lib.tasks_dir(), fname))
        tasks.append({
            "id": parsed["id"],
            "file": parsed["file"],
            "title": parsed["title"],
            "target": parsed["target"],
            "disease": parsed["disease"],
            "doi": parsed["doi"],
            "pmc": parsed["pmc"],
            "pdbs": parsed["pdbs"],
            "pass_bar": parsed["pass_bar"],
            "expected_outputs": parsed["expected_outputs"],
            "evaluation_metrics": parsed["evaluation_metrics"],
            "time_limit_minutes": 240,
        })

    environment = {
        "name": os.path.basename(env_lib.env_dir()),
        "task_count": len(tasks),
        "time_limit_minutes": 240,
        "reference_policy": "agents must not look up the source publication to copy hit lists or scores",
        "grading": {
            "method": "pass-bar anchored; scripts/grade_run.py checks expected output files and metrics.json",
            "note": "docking kcal/mol anchors are engine-relative (paper engine vs platform Vina/Diffdock); see each task's engine note",
        },
        "tasks": tasks,
    }

    config_path = os.path.join(env_lib.env_dir(), "config", "environment.json")
    with open(config_path, "w", encoding="utf-8") as fh:
        json.dump(environment, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    benchmark = {
        "name": environment["name"],
        "tasks": [
            {
                "id": t["id"],
                "file": t["file"],
                "doi": t["doi"],
                "pmc": t["pmc"],
                "pdbs": t["pdbs"],
                "pass_bar": t["pass_bar"],
                "expected_outputs": t["expected_outputs"],
                "evaluation_metrics": t["evaluation_metrics"],
            }
            for t in tasks
        ],
    }
    bench_path = os.path.join(env_lib.env_dir(), "benchmark", "benchmark.json")
    with open(bench_path, "w", encoding="utf-8") as fh:
        json.dump(benchmark, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    papers_path = os.path.join(env_lib.env_dir(), "benchmark", "papers.csv")
    with open(papers_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "task_id", "file", "title", "target", "disease", "doi", "pmc", "pdbs"])
        writer.writeheader()
        for t in tasks:
            writer.writerow({
                "task_id": t["id"], "file": t["file"], "title": t["title"],
                "target": t["target"], "disease": t["disease"],
                "doi": t["doi"], "pmc": t["pmc"], "pdbs": ";".join(t["pdbs"]),
            })

    print(f"wrote {config_path}")
    print(f"wrote {bench_path}")
    print(f"wrote {papers_path} ({len(tasks)} tasks)")


if __name__ == "__main__":
    main()
