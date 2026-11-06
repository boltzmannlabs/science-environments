"""Portable, bounded wrapper around the existing research-prototype simulator.

No second kinetic model is implemented here. Configuration is JSON (YAML 1.2
subset). Output directories must be new so historical reports cannot be replaced.
"""

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
from pathlib import Path

from evaluation.exploratory_scenarios import recipe, run
from evaluation.exploratory_verifier import verify_scenario


def load_problem(path):
    path = Path(path).resolve()
    manifest = json.loads(path.read_text())
    if (
        manifest.get("schema_version") != 1
        or manifest.get("mode") != "research_scenario"
    ):
        raise ValueError("schema_version=1 and research_scenario mode required")
    if manifest.get("experimental_observations") is not None:
        raise ValueError(
            "use scripts/evaluate_results.py --comparison for supplied measured profiles; never silently substitute them"
        )
    scenario_path = (path.parent / manifest["scenario_config"]).resolve()
    cfg = json.loads(scenario_path.read_text())
    space = cfg["bounded_exploratory_space_assumed_not_approved"]
    search = cfg["sampling_and_search"]
    # This inherited simulator is a 500 mg / 695 mg case study, not a general
    # dose converter. Reject unsupported reinterpretations of hard-coded units.
    if cfg["paper_mass_mg"] != {
        "tablet_total": 695,
        "ranolazine": 500,
        "povidone_K30": 10,
        "aerosil": 5,
        "titanium_dioxide": 15,
    }:
        raise ValueError(
            "only the documented 500 mg / 695 mg research recipe is supported"
        )
    if (
        space["strength_mg"] != 500
        or space["tablet_total_mg"] != 695
        or space["potency_fraction"] != 1
    ):
        raise ValueError("dose, total mass and potency must match the case study")
    times = space["time_h"]
    if (
        not isinstance(times, list)
        or len(times) < 3
        or not all(
            isinstance(x, (int, float))
            and not isinstance(x, bool)
            and math.isfinite(x)
            and x >= 0
            for x in times
        )
        or times != sorted(set(times))
        or not {0, 2, 24}.issubset(times)
    ):
        raise ValueError(
            "unique increasing finite hour times including 0, 2 and 24 required"
        )
    for key in (
        "compritol_mg",
        "carbopol_934_mg",
        "avicel_PH101_mg",
        "hardness_kg_per_cm2",
    ):
        bounds = space[key]
        if (
            len(bounds) != 2
            or not all(
                isinstance(v, (int, float))
                and not isinstance(v, bool)
                and math.isfinite(v)
                for v in bounds
            )
            or bounds[0] > bounds[1]
        ):
            raise ValueError("invalid bounds: " + key)
    for key, bounds in cfg["release_assumptions_unfitted"].items():
        if not key.endswith("_uniform"):
            continue
        if (
            len(bounds) != 2
            or not all(
                isinstance(v, (int, float))
                and not isinstance(v, bool)
                and math.isfinite(v)
                for v in bounds
            )
            or bounds[0] > bounds[1]
        ):
            raise ValueError("invalid parameter range: " + key)
        if (
            key
            in (
                "first_order_k1_per_h_uniform",
                "weibull_beta_time_h_uniform",
                "weibull_alpha_uniform",
            )
            and bounds[0] <= 0
        ):
            raise ValueError("positive kinetic parameters required")
    for key in ("samples_per_model", "seed"):
        if (
            not isinstance(search[key], int)
            or isinstance(search[key], bool)
            or search[key] < (1 if key == "samples_per_model" else 0)
        ):
            raise ValueError("invalid integer: " + key)
    weights = search["score_weights_assumed"]
    expected = {"joint_scenario_fraction", "clipped_margin", "lower_polymer_mass_proxy"}
    if set(weights) != expected or not all(
        isinstance(w, (int, float))
        and not isinstance(w, bool)
        and math.isfinite(w)
        and w >= 0
        for w in weights.values()
    ):
        raise ValueError("explicit finite nonnegative score weights required")
    feasible = []
    for key in ("compritol_grid_mg", "carbopol_grid_mg", "hardness_grid_kg_per_cm2"):
        values = search[key]
        if (
            not isinstance(values, list)
            or not values
            or len(values) != len(set(values))
            or not all(
                isinstance(v, (int, float))
                and not isinstance(v, bool)
                and math.isfinite(v)
                for v in values
            )
        ):
            raise ValueError("invalid search grid: " + key)
    for c in search["compritol_grid_mg"]:
        for b in search["carbopol_grid_mg"]:
            if (
                not space["avicel_PH101_mg"][0]
                <= 165 - c - b
                <= space["avicel_PH101_mg"][1]
            ):
                continue
            for h in search["hardness_grid_kg_per_cm2"]:
                recipe(
                    c, b, h, cfg
                )  # original mass/dose/bounds checks, before any model call
                feasible.append((c, b, h))
    if len({(c, b) for c, b, h in feasible}) < 3:
        raise ValueError(
            "at least three distinct feasible compositions required by this simulator"
        )
    budget = manifest["budget"]
    for key in ("max_candidates", "max_scenarios_per_candidate"):
        if (
            not isinstance(budget[key], int)
            or isinstance(budget[key], bool)
            or budget[key] < 0
        ):
            raise ValueError("explicit nonnegative integer budget required: " + key)
    return manifest, cfg, scenario_path, feasible


def versions():
    out: dict[str, str | None] = {"python": platform.python_version()}
    for package in ("openpkflow", "numpy", "scipy", "pandas", "matplotlib"):
        try:
            out[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            out[package] = None
    return out


def execute(config_path, output_dir):
    manifest, cfg, source, grid = load_problem(config_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=False)
    required = {
        "candidates": len(grid),
        "scenarios_per_candidate": 2 * cfg["sampling_and_search"]["samples_per_model"],
    }
    record = {
        "schema_version": 1,
        "status": "pending",
        "versions": versions(),
        "configuration": manifest,
        "scenario_configuration": cfg,
        "seed": cfg["sampling_and_search"]["seed"],
        "input_sha256": {
            "problem": hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),
            "scenario": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        "required_budget": required,
        "evaluated_candidates": 0,
        "budget_policy": "all-or-abstain preflight; no partial-grid ranking",
        "experimental_observations": None,
        "experimental_comparison": {
            "status": "not_evaluated",
            "reason": "no measured observations supplied",
        },
        "scientific_validation": "not_established",
        "constraint_violations": [],
    }
    if (
        required["candidates"] > manifest["budget"]["max_candidates"]
        or required["scenarios_per_candidate"]
        > manifest["budget"]["max_scenarios_per_candidate"]
    ):
        record["status"] = "budget_exhausted"
    else:
        try:
            candidates = []
            scenario = run(cfg, candidate_records=candidates)
            findings = verify_scenario(scenario, cfg)
            if findings:
                raise ValueError("scenario audit failed: " + ", ".join(findings))
            (out / "scenario.json").write_text(
                json.dumps(scenario, indent=2, allow_nan=False) + "\n"
            )
            (out / "candidates.json").write_text(
                json.dumps(candidates, indent=2, allow_nan=False) + "\n"
            )
            record.update(
                status="completed_scenario_only",
                evaluated_candidates=len(candidates),
                selected_id=scenario["all_scenario_rankings"][0]["id"],
                mechanical_audit={
                    "findings": findings,
                    "scope": "not experimental validation",
                },
                compatibility={"status": "insufficient_data"},
                stability={"status": "insufficient_data"},
            )
        except ImportError as exc:
            record.update(status="tool_unavailable", reason=type(exc).__name__)
        except (ValueError, RuntimeError, OverflowError) as exc:
            record.update(status="failure", reason=str(exc))
    record["artifact_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.glob("*.json"))
    }
    (out / "report.json").write_text(
        json.dumps(record, indent=2, allow_nan=False) + "\n"
    )
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/environment.yaml"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        record = execute(args.config, args.out)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"{type(exc).__name__}: {exc}\n")
    print(json.dumps(record, indent=2))
    if record["status"] != "completed_scenario_only":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
