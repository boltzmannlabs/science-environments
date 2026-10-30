"""Validate whether two mapped ligand endpoints are FEP-feasible."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _mol2(path: Path):
    lines = path.read_text().splitlines()
    try:
        a0 = lines.index("@<TRIPOS>ATOM") + 1
        b0 = lines.index("@<TRIPOS>BOND") + 1
    except ValueError as exc:
        raise ValueError(f"missing MOL2 section in {path}") from exc
    atoms = {}
    for row in lines[a0:b0 - 1]:
        fields = row.split()
        if len(fields) >= 6 and fields[0].isdigit():
            element = fields[5].split(".")[0]
            atoms[int(fields[0])] = {"element": element, "name": fields[1]}
    bonds = {}
    for row in lines[b0:]:
        fields = row.split()
        if len(fields) >= 4 and fields[0].isdigit():
            bonds[tuple(sorted((int(fields[1]), int(fields[2]))))] = fields[3]
    if not atoms:
        raise ValueError(f"no atoms in {path}")
    return atoms, bonds


def validate(config: Path, output_dir: Path) -> dict:
    cfg = json.loads(config.read_text())
    required = ["ligand_a", "ligand_b", "atom_map", "charge_a", "charge_b", "force_field", "allowed_elements"]
    missing = [key for key in required if key not in cfg]
    if missing:
        result = {"task_id": cfg.get("task_id", "unknown"), "status": "FAIL", "errors": [f"missing field: {x}" for x in missing]}
        _write(result, [], output_dir)
        return result
    base = config.parent
    a, abonds = _mol2((base / cfg["ligand_a"]).resolve())
    b, bbonds = _mol2((base / cfg["ligand_b"]).resolve())
    mapping = json.loads(((base / cfg["atom_map"]).resolve()).read_text()).get("mapping", [])
    amap = {int(x["a"]): int(x["b"]) for x in mapping}
    errors, warnings, changes = [], [], []
    allowed = set(cfg["allowed_elements"])
    unsupported = sorted({x["element"] for x in list(a.values()) + list(b.values()) if x["element"] not in allowed})
    if unsupported:
        errors.append(f"unsupported elements: {', '.join(unsupported)}")
    for ai, bi in amap.items():
        if ai not in a or bi not in b:
            errors.append(f"mapping references missing atom {ai}->{bi}")
        elif a[ai]["element"] != b[bi]["element"]:
            errors.append(f"element mismatch {ai}->{bi}: {a[ai]['element']} vs {b[bi]['element']}")
    mapped_a = set(amap)
    mapped_b = set(amap.values())
    for ai in sorted(set(a) - mapped_a):
        changes.append({"kind": "unmapped_atom", "endpoint": "A", "atom": ai, "element": a[ai]["element"]})
    for bi in sorted(set(b) - mapped_b):
        changes.append({"kind": "unmapped_atom", "endpoint": "B", "atom": bi, "element": b[bi]["element"]})
    for (ai, aj), order in abonds.items():
        if ai in amap and aj in amap:
            target = tuple(sorted((amap[ai], amap[aj])))
            if target not in bbonds:
                changes.append({"kind": "bond_deleted", "a": [ai, aj], "b": list(target), "order_a": order})
            elif bbonds[target] != order:
                changes.append({"kind": "bond_order_change", "a": [ai, aj], "b": list(target), "order_a": order, "order_b": bbonds[target]})
    for (bi, bj), order in bbonds.items():
        if bi in mapped_b and bj in mapped_b:
            source = tuple(sorted((next(ai for ai, x in amap.items() if x == bi), next(ai for ai, x in amap.items() if x == bj))))
            if source not in abonds:
                changes.append({"kind": "bond_added", "a": list(source), "b": [bi, bj], "order_b": order})
    heavy_a = {i for i, x in a.items() if x["element"] != "H"}
    heavy_b = {i for i, x in b.items() if x["element"] != "H"}
    mapped_heavy = len(heavy_a & mapped_a)
    overlap = mapped_heavy / max(1, min(len(heavy_a), len(heavy_b)))
    if overlap < 0.5:
        warnings.append(f"low mapped heavy-atom fraction: {overlap:.3f}")
    if cfg["charge_a"] != cfg["charge_b"]:
        warnings.append("net-charge change requires electrostatic correction and matched complex/solvent treatment")
    if cfg.get("protonation_a") != cfg.get("protonation_b"):
        warnings.append("protonation-state change requires separate state treatment")
    if cfg.get("tautomer_a") != cfg.get("tautomer_b"):
        warnings.append("tautomer change requires separate state treatment")
    if len(changes) > max(4, len(amap)):
        warnings.append("large endpoint chemical change or dummy-atom region")
    status = "FAIL" if errors else ("REVIEW" if warnings else "PASS")
    result = {"task_id": cfg["task_id"], "status": status, "ligand_a_atoms": len(a), "ligand_b_atoms": len(b), "mapped_atoms": len(amap), "mapped_heavy_fraction": overlap, "charge_change": cfg["charge_b"] - cfg["charge_a"], "force_field": cfg["force_field"], "errors": errors, "warnings": warnings, "chemical_changes": changes, "provenance": {"config": str(config), "immutable_inputs": True}}
    _write(result, changes, output_dir)
    return result


def _write(result, changes, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    (out / "transformation_assessment.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "chemical_changes.csv").open("w", newline="") as handle:
        fields = ["kind", "endpoint", "atom", "a", "b", "element", "order_a", "order_b"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(changes)
    lines = [f"# Transformation feasibility: {result['status']}", "", f"Mapped atoms: {result.get('mapped_atoms', 0)}", f"Mapped heavy-atom fraction: {result.get('mapped_heavy_fraction', 0):.3f}", f"Charge change: {result.get('charge_change', 'unknown')}", "", "## Warnings"] + [f"- {x}" for x in result.get("warnings", [])] + ["", "## Errors"] + [f"- {x}" for x in result.get("errors", [])]
    (out / "feasibility_report.md").write_text("\n".join(lines) + "\n")
    (out / "qualification.json").write_text(json.dumps({"task_id": result["task_id"], "qualification": result["status"], "evidence": "transformation_assessment.json", "immutable_inputs": True}, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.config, args.output_dir), indent=2))
