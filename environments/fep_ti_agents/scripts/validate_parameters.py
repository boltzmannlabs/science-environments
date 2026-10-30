"""Audit a concrete FEP topology against a declared force-field inventory."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def validate(system_path: Path, ff_path: Path, out: Path) -> dict:
    system, ff = json.loads(system_path.read_text()), json.loads(ff_path.read_text())
    missing = []
    supported = set(ff.get("supported_atom_types", []))
    bonded = set(ff.get("bonded_parameters", []))
    for atom in system.get("atoms", []):
        if atom.get("type") not in supported:
            missing.append({"kind": "atom_type", "atom": atom.get("index"), "value": atom.get("type")})
        if not isinstance(atom.get("charge"), (int, float)):
            missing.append({"kind": "charge", "atom": atom.get("index"), "value": atom.get("charge")})
    for bond in system.get("bonds", []):
        atoms = {a["index"]: a for a in system.get("atoms", [])}
        if len(bond) != 2 or any(i not in atoms for i in bond):
            missing.append({"kind": "bond", "value": bond}); continue
        types = "-".join(sorted((atoms[bond[0]]["type"], atoms[bond[1]]["type"])))
        forward = "-".join((atoms[bond[0]]["type"], atoms[bond[1]]["type"]))
        reverse = "-".join((atoms[bond[1]]["type"], atoms[bond[0]]["type"]))
        if types not in bonded and forward not in bonded and reverse not in bonded:
            missing.append({"kind": "bonded_parameter", "bond": bond, "value": types})
    expected = system.get("protein_atoms", 0) + system.get("ligand_atoms", 0)
    errors = []
    if len(system.get("atoms", [])) != expected:
        errors.append(f"atom count {len(system.get('atoms', []))} != declared {expected}")
    charge = sum(float(a.get("charge", 0)) for a in system.get("atoms", []))
    charge_error = abs(charge - float(system.get("total_charge", 0)))
    if charge_error > 1e-6: errors.append(f"total charge mismatch: {charge} vs {system.get('total_charge')}")
    if system.get("water_model") != ff.get("water_model") or system.get("ion_model") != ff.get("ion_model"):
        errors.append("water/ion model incompatible with force-field inventory")
    status = "FAIL" if missing or errors else "PASS"
    result = {"task_id": system.get("task_id"), "status": status, "missing_parameters": missing, "errors": errors, "charge": {"computed": charge, "declared": system.get("total_charge"), "absolute_error": charge_error}, "immutable_inputs": True}
    out.mkdir(parents=True, exist_ok=True)
    (out / "parameter_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "missing_parameters.csv").open("w", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=["kind", "atom", "bond", "value"], extrasaction="ignore"); writer.writeheader(); writer.writerows(missing)
    (out / "charge_audit.json").write_text(json.dumps(result["charge"], indent=2) + "\n")
    (out / "topology_validation_report.md").write_text(f"# Parameter validation: {status}\n\nMissing entries: {len(missing)}\n\nErrors: {len(errors)}\n")
    (out / "qualification.json").write_text(json.dumps({"task_id": result["task_id"], "qualification": status, "evidence": "parameter_validation.json"}, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("system", type=Path); p.add_argument("forcefield", type=Path); p.add_argument("--output-dir", type=Path, required=True); a = p.parse_args(); print(json.dumps(validate(a.system, a.forcefield, a.output_dir), indent=2))
