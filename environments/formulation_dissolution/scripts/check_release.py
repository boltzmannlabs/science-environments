"""Run release checks and write real execution receipts, never synthetic test logs.

Run from the environment checkout using an interpreter with .[simulation,test],
build and Ruff installed. New scientific outputs go under ignored .checks/.
Original source-run artifacts are only read/hashed when --source-run is supplied.
"""

import argparse
import ast
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-run", type=Path)
    args = p.parse_args()
    os.chdir(ROOT)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    check = ROOT / ".checks" / stamp
    check.mkdir(parents=True, exist_ok=False)
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    records = []
    logs = []

    def call(name, argv, *, cwd=ROOT, expected=0):
        done = subprocess.run(
            [str(v) for v in argv],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=300,
        )
        entry = {
            "name": name,
            "argv": [str(v) for v in argv],
            "cwd": str(cwd),
            "exit_code": done.returncode,
            "expected_exit_code": expected,
            "passed": done.returncode == expected,
            "output": done.stdout,
        }
        records.append(entry)
        logs.append("$ " + " ".join(entry["argv"]) + "\n" + done.stdout + "\n")
        print(f"{name}: exit {done.returncode} (expected {expected})", flush=True)
        return entry["passed"]

    py = sys.executable
    call("pytest-full", [py, "-m", "pytest", "-q"])
    call("unittest-full", [py, "-m", "unittest", "discover", "-s", "tests", "-q"])
    call("fatal-error-lint", [py, "-m", "ruff", "check", "."])
    call(
        "new-code-format",
        [
            py,
            "-m",
            "ruff",
            "format",
            "--check",
            "simulation.py",
            "scripts",
            "evaluation/profile_comparison.py",
            "tests/test_environment.py",
            "tests/test_constraints.py",
            "tests/test_dissolution_models.py",
            "tests/test_optimization.py",
            "tests/test_reproducibility.py",
            "tests/test_workflow.py",
        ],
    )
    call("pip-check", [py, "-m", "pip", "check"])
    call(
        "bounded-simulation",
        [
            py,
            "scripts/run_simulation.py",
            "--config",
            "configs/environment.yaml",
            "--out",
            check / "scenario",
        ],
    )
    call(
        "scenario-audit",
        [py, "scripts/evaluate_results.py", "--run", check / "scenario"],
    )
    call(
        "selection-negative-control",
        [
            py,
            "-m",
            "evaluation.exploratory_selection_benchmark",
            "--config",
            "configs/exploratory_ranolazine_500.json",
            "--scenario",
            check / "scenario/scenario.json",
            "--out",
            check / "selection.json",
        ],
    )
    call(
        "six-models",
        [
            py,
            "-m",
            "evaluation.six_model_pipeline",
            "--literature",
            "data/processed/literature_profiles.json",
            "--out",
            check / "six-model",
        ],
    )
    call(
        "six-model-audit",
        [
            py,
            "-m",
            "evaluation.six_model_verifier",
            "--result",
            check / "six-model/six_model_results.json",
            "--fixture",
            check / "six-model/synthetic_batch_fixture.json",
            "--out",
            check / "six-model/verification.json",
        ],
    )
    call(
        "fixture-benchmark",
        [
            py,
            "-m",
            "cli",
            "benchmark",
            "--config",
            "configs/benchmark.yaml",
            "--track",
            "fixtures",
        ],
    )
    call(
        "predict-abstention",
        [
            py,
            "-m",
            "cli",
            "solve",
            "--config",
            "configs/task.yaml",
            "--mode",
            "predict",
        ],
    )
    call("build-wheel", [py, "-m", "build", "--wheel", "--outdir", check / "wheels"])
    wheel_files = list((check / "wheels").glob("*.whl"))
    if len(wheel_files) == 1:
        wheel = wheel_files[0]
        call("fresh-base-venv", [py, "-m", "venv", check / "wheel-venv"])
        basepy = check / "wheel-venv/bin/python"
        call(
            "wheel-install-no-dependencies",
            [basepy, "-m", "pip", "install", "--no-index", "--no-deps", wheel],
        )
        outside = check / "outside-source"
        outside.mkdir()
        call(
            "installed-base-cli",
            [check / "wheel-venv/bin/formulation-gym", "sample"],
            cwd=outside,
        )
        call(
            "installed-history-cli",
            [check / "wheel-venv/bin/formulation-history", "--help"],
            cwd=outside,
        )
        call(
            "installed-simulation-cli",
            [check / "wheel-venv/bin/formulation-simulate", "--help"],
            cwd=outside,
        )
    installed = []
    for dist in sorted(
        metadata.distributions(), key=lambda d: d.metadata["Name"].lower()
    ):
        info = dist.metadata
        installed.append(
            {
                "name": info["Name"],
                "version": dist.version,
                "license_metadata": (
                    info.get("License-Expression")
                    or info.get("License")
                    or "not declared"
                ).splitlines()[0][:180],
            }
        )
    direct_imports = {}
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if any(
            part.startswith(".") or part in ("build", "dist", "__pycache__")
            for part in rel.parts
        ):
            continue
        tree = ast.parse(path.read_text())
        names = {
            n.module.split(".")[0]
            for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module
        }
        names.update(
            a.name.split(".")[0]
            for n in ast.walk(tree)
            if isinstance(n, ast.Import)
            for a in n.names
        )
        direct_imports[str(rel)] = sorted(names)
    receipt = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "scientific_validation": "not_established",
        "commands": records,
        "all_commands_passed": all(r["passed"] for r in records),
        "installed_distributions": installed,
        "direct_imports": direct_imports,
        "artifact_root": str(check.relative_to(ROOT)),
        "wheel_sha256": sha(wheel_files[0]) if len(wheel_files) == 1 else None,
        "new_run_artifact_sha256": {
            str(f.relative_to(check)): sha(f)
            for d in ("scenario", "six-model")
            for f in sorted((check / d).glob("*"))
            if f.is_file()
        },
    }
    (results / "validation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (results / "validation.txt").write_text("\n".join(logs).rstrip() + "\n")
    (ROOT / "configs/tested-dependencies.txt").write_text(
        "# Tested integration environment; Python "
        + platform.python_version()
        + " on "
        + platform.system()
        + "\n"
        + "# Includes build/test tooling. Install the checkout separately; not a portable cross-platform lock.\n"
        + "\n".join(
            x["name"] + "==" + x["version"]
            for x in installed
            if x["name"].lower() != "formulation-optimization-gym"
        )
        + "\n"
    )
    if args.source_run:
        source = args.source_run.resolve()
        files = []
        for path in sorted(source.rglob("*")):
            rel = path.relative_to(source)
            if not path.is_file() or any(
                part.startswith(".") or part == "__pycache__" for part in rel.parts
            ):
                continue
            target = ROOT / rel
            local_only = path.suffix == ".html" or (
                path.suffix == ".txt" and "agent" in path.name
            )
            files.append(
                {
                    "source_relative_path": str(rel),
                    "sha256": sha(path),
                    "bytes": path.stat().st_size,
                    "target": None if local_only or not target.exists() else str(rel),
                    "copy_status": "indexed_local_only"
                    if local_only
                    else "identical"
                    if target.is_file() and sha(target) == sha(path)
                    else "adapted"
                    if target.is_file()
                    else "not_included",
                }
            )
        provenance = {
            "source_run": "local://formulation-optimization-gym",
            "source_root_at_integration": str(source),
            "originals_modified": False,
            "scope": "read/hash originals; reuse algorithms, adapt packaging/config/guards; synthetic and literature labels retained",
            "files": files,
        }
        (ROOT / "SOURCE_PROVENANCE.json").write_text(
            json.dumps(provenance, indent=2) + "\n"
        )
        historical = json.loads(
            (
                source / "data/processed/six_model_pipeline/six_model_results.json"
            ).read_text()
        )
        scenario = json.loads(
            (
                source / "data/processed/ranolazine_500_exploratory_new_run.json"
            ).read_text()
        )
        summary = {
            "origin": "source-run historical outputs, NOT fresh experimental data",
            "six_model_source_sha256": sha(
                source / "data/processed/six_model_pipeline/six_model_results.json"
            ),
            "synthetic_seed": historical["synthetic"]["seed"],
            "synthetic_batch_counts": historical["synthetic"]["batch_counts"],
            "synthetic_model_metrics": historical["synthetic"]["models"],
            "published_fit_count": len(historical["published"]["fits"]),
            "scenario_source_sha256": sha(
                source / "data/processed/ranolazine_500_exploratory_new_run.json"
            ),
            "scenario_grid_size": scenario["grid_size"],
            "scenario_count_per_candidate": scenario["scenario_count_per_candidate"],
            "scenario_status": scenario["status"],
            "experimental_validation": None,
        }
        (results / "historical_run_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n"
        )
    if not receipt["all_commands_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
