#!/usr/bin/env python3
"""Reconstruct the task_002 evaluated-candidate table and shortlist FASTA."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

SHORTLIST = ["rf1_d5", "rf1_d2", "rf1_d3", "rf0_d5", "rf0_d0"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--results-root", type=Path, default=None)
    args = ap.parse_args()
    root = args.task_root.resolve()
    result_root = (args.results_root or root.parents[1] / "results" / "task_002_pdl1_epitope_targeted_scfv_design").resolve()
    analysis = json.loads((root / "outputs/boltz2_analysis.json").read_text())
    candidates = {r["id"]: r for r in json.loads((root / "outputs/rfantibody_candidates.json").read_text())}
    props = {}
    with (root / "outputs/antibody_pred_output.csv").open() as handle:
        for row in csv.DictReader(handle):
            props[row["seq_id"]] = row

    for cid, row in analysis.items():
        row["score"] = round(
            row["ipTM"] + 0.08 * len(row["hotspot_residues_touched"])
            - 0.03 * row["ipDE"] - 0.01 * row["clashes"], 3
        )
    ranked = sorted(analysis.items(), key=lambda item: -item[1]["score"])
    result_root.mkdir(parents=True, exist_ok=True)
    with (result_root / "candidates_recomputed.csv").open("w", newline="") as handle:
        fields = ["candidate_id", "score", "ipTM", "ipDE", "hotspot_residues_touched", "hotspot_contact_pairs", "shortlisted", "thermal_stab_protbert", "thermal_stab_esm", "solubility_esm"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for cid, row in ranked:
            p = props.get(cid, {})
            writer.writerow({
                "candidate_id": cid,
                "score": row["score"],
                "ipTM": row["ipTM"],
                "ipDE": row["ipDE"],
                "hotspot_residues_touched": ",".join(map(str, row["hotspot_residues_touched"])),
                "hotspot_contact_pairs": row["hotspot_contact_pairs"],
                "shortlisted": cid in SHORTLIST,
                "thermal_stab_protbert": p.get("Thermal_stab_protbert", ""),
                "thermal_stab_esm": p.get("Thermal_stab_esm", ""),
                "solubility_esm": p.get("solubility", ""),
            })
    with (result_root / "sequences_recomputed.fasta").open("w") as handle:
        for cid in SHORTLIST:
            handle.write(f">{cid}|chain=scfv\n{candidates[cid]['scfv']}\n")
    print(f"evaluated={len(analysis)} generated={len(candidates)} shortlist={len(SHORTLIST)}")


if __name__ == "__main__":
    main()
