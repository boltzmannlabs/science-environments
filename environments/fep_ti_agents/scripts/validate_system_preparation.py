"""Audit FEP complex/solvent preparation and equilibration evidence."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def validate(config: Path, out: Path) -> dict:
    data = json.loads(config.read_text()); t = data.get("thresholds", {}); leg_results = []; errors = []
    for leg in data.get("legs", []):
        e = []
        if leg.get("topology_atoms") != leg.get("coordinate_atoms"): e.append("topology/coordinate atom count mismatch")
        if not leg.get("box_nm") or any(float(x) <= 0 for x in leg["box_nm"]): e.append("periodic box is missing or invalid")
        if not leg.get("neutralized"): e.append("system is not documented as neutralized")
        minim = leg.get("minimization", {}); eq = leg.get("equilibration", {})
        if not minim.get("converged"): e.append("energy minimization did not converge")
        if float(minim.get("final_force_kj_mol_nm", float("inf"))) > float(t.get("final_force_max_kj_mol_nm", 10)):
            e.append("final minimization force exceeds threshold")
        if not eq.get("nvt_complete") or not eq.get("npt_complete"): e.append("NVT/NPT equilibration is incomplete")
        if abs(float(eq.get("temperature_mean_K", 0)) - float(t.get("temperature_target_K", 300))) > float(t.get("temperature_mean_tolerance_K", 5)): e.append("mean temperature outside tolerance")
        if float(eq.get("temperature_std_K", float("inf"))) > float(t.get("temperature_std_max_K", 10)): e.append("temperature fluctuation outside tolerance")
        if abs(float(eq.get("pressure_mean_bar", 0)) - float(t.get("pressure_target_bar", 1))) > float(t.get("pressure_mean_tolerance_bar", 100)): e.append("mean pressure outside tolerance")
        if float(eq.get("pressure_std_bar", float("inf"))) > float(t.get("pressure_std_max_bar", 200)): e.append("pressure fluctuation outside tolerance")
        if abs(float(eq.get("density_mean_g_cm3", 0)) - float(t.get("density_target_g_cm3", 1))) > float(t.get("density_mean_tolerance_g_cm3", .08)): e.append("mean density outside tolerance")
        if float(eq.get("density_std_g_cm3", float("inf"))) > float(t.get("density_std_max_g_cm3", .08)): e.append("density fluctuation outside tolerance")
        status = "FAIL" if e else "PASS"; leg_results.append({"system": leg.get("system"), "leg": leg.get("leg"), "status": status, "errors": e, "atom_count": leg.get("topology_atoms")}); errors.extend(e)
    status = "FAIL" if errors else "PASS"
    result = {"task_id": data.get("task_id"), "status": status, "legs": leg_results, "thresholds": t, "source_revision": data.get("source_revision"), "immutable_input": True}
    out.mkdir(parents=True, exist_ok=True)
    (out / "equilibration_metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    for leg in leg_results:
        (out / f"{leg['leg']}_preparation_report.md").write_text(f"# {leg['system']} {leg['leg']} preparation: {leg['status']}\n\n" + "\n".join(f"- {x}" for x in leg["errors"]) + "\n")
    (out / "production_readiness.json").write_text(json.dumps({"task_id": result["task_id"], "readiness": status, "evidence": "equilibration_metrics.json", "limitations": ["metadata and recorded metrics audit; does not rerun MD"]}, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("config", type=Path); p.add_argument("--output-dir", type=Path, required=True); a = p.parse_args(); print(json.dumps(validate(a.config, a.output_dir), indent=2))
