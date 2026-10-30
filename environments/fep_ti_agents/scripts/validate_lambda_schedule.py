"""Validate FEP electrostatic/steric lambda schedules without rewriting them."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path


def validate(config_path: Path, out: Path) -> dict:
    cfg = json.loads(config_path.read_text())
    errors, warnings, recommendations = [], [], []
    electro = cfg.get("lambda_electrostatics", [])
    steric = cfg.get("lambda_sterics", [])
    if not electro or not steric or len(electro) != len(steric):
        errors.append("electrostatic and steric schedules must be non-empty and equal length")
    if electro and (not math.isclose(electro[0], 1.0) or not math.isclose(electro[-1], 0.0)): errors.append("electrostatic schedule must cover 1.0 to 0.0")
    if steric and (not math.isclose(steric[0], 1.0) or not math.isclose(steric[-1], 0.0)): errors.append("steric schedule must cover 1.0 to 0.0")
    for name, values in (("electrostatics", electro), ("sterics", steric)):
        if any(not isinstance(x, (int, float)) or x < 0 or x > 1 for x in values): errors.append(f"{name} contains a value outside [0,1]")
        collapsed = [x for i, x in enumerate(values) if i == 0 or x != values[i - 1]]
        if len(set(collapsed)) != len(collapsed): errors.append(f"{name} contains non-adjacent duplicate lambda values")
        if any(values[i] < values[i + 1] for i in range(len(values) - 1)): errors.append(f"{name} is not monotonically decreasing")
        gaps = [abs(values[i] - values[i + 1]) for i in range(len(values) - 1)]
        if gaps and max(gaps) > float(cfg.get("max_adjacent_gap", 0.2)) + 1e-12:
            warnings.append(f"{name} has an adjacent gap of {max(gaps):.3f}")
            recommendations.append(f"add a window near the largest {name} gap")
    soft = cfg.get("softcore", {})
    if any(x < 1.0 for x in steric) and (not soft.get("enabled") or float(soft.get("alpha", 0)) <= 0): errors.append("steric decoupling requires enabled soft-core alpha > 0")
    if cfg.get("charge_change") and not any(math.isclose(x, 0.0) for x in electro[1:-1]):
        warnings.append("charge-changing transformation has no intermediate electrostatics-off window")
        recommendations.append("use an explicit electrostatics-to-zero staging segment before steric decoupling")
    if len(electro) < int(cfg.get("sampling_budget_windows", len(electro))): warnings.append("schedule uses fewer windows than the declared budget")
    status = "FAIL" if errors else ("REVIEW" if warnings else "PASS")
    result = {"task_id": cfg.get("task_id"), "status": status, "windows": len(electro), "max_electrostatic_gap": max((abs(electro[i]-electro[i+1]) for i in range(len(electro)-1)), default=0), "max_steric_gap": max((abs(steric[i]-steric[i+1]) for i in range(len(steric)-1)), default=0), "errors": errors, "warnings": warnings, "recommendations": recommendations, "immutable_input": True}
    out.mkdir(parents=True, exist_ok=True); windows_dir = out / "window_configuration"; windows_dir.mkdir(exist_ok=True)
    (out / "lambda_schedule.json").write_text(json.dumps({"electrostatics": electro, "sterics": steric, "softcore": soft}, indent=2) + "\n")
    (out / "lambda_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    for index, (electrostatic, steric_value) in enumerate(zip(electro, steric)):
        (windows_dir / f"window_{index:03d}.json").write_text(json.dumps({"index": index, "lambda_electrostatics": electrostatic, "lambda_sterics": steric_value, "softcore": soft}, indent=2) + "\n")
    (out / "schedule_recommendations.md").write_text("# Lambda schedule recommendations\n\n" + "\n".join(f"- {x}" for x in recommendations) + "\n")
    (out / "qualification.json").write_text(json.dumps({"task_id": result["task_id"], "qualification": status, "evidence": "lambda_validation.json"}, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("config", type=Path); p.add_argument("--output-dir", type=Path, required=True); a = p.parse_args(); print(json.dumps(validate(a.config, a.output_dir), indent=2))
