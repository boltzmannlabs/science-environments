#!/usr/bin/env python3
"""Recompute task_002 candidate novelty metrics against H5.

This reconstructs the inline novelty calculation used for the retained result.
It does not claim the paper's interface-similarity metric.
"""
from __future__ import annotations
import argparse, csv, json
from difflib import SequenceMatcher
from pathlib import Path


def read_fasta(path: Path) -> dict[str, str]:
    records, name, chunks = {}, None, []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                records[name] = "".join(chunks)
            name, chunks = line[1:].split()[0], []
        elif line.strip():
            chunks.append(line.strip())
    if name is not None:
        records[name] = "".join(chunks)
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    root = args.task_root.resolve()
    candidates = json.loads((root / "outputs/rfantibody_candidates.json").read_text())
    candidate_map = {row["id"]: row for row in candidates}
    h5 = read_fasta(root / "source/h5_reference.fasta")
    h5_vh, h5_vl = h5["h5_VH"], h5["h5_VL"]
    props = {}
    with (root / "outputs/antibody_pred_output.csv").open() as handle:
        for row in csv.DictReader(handle):
            props[row["seq_id"]] = row

    result = {
        "reference": {"vh": h5_vh, "vl": h5_vl, "cdr3h": "WPYSIVMLPFHG"},
        "method": "difflib.SequenceMatcher ratio; H5 CDR3-H boundary retained from task analysis",
        "candidates": {},
    }
    for cid, row in sorted(props.items()):
        if cid not in candidate_map:
            continue
        c = candidate_map[cid]
        cdr3h = row["H_CDR3"]
        result["candidates"][cid] = {
            "vh_identity": round(SequenceMatcher(None, c["vh"], h5_vh).ratio(), 3),
            "vl_identity": round(SequenceMatcher(None, c["vl"], h5_vl).ratio(), 3),
            "cdr3h_identity": round(SequenceMatcher(None, cdr3h, "WPYSIVMLPFHG").ratio(), 3),
            "cdr3h": cdr3h,
        }
    out = args.output or (root / "outputs/novelty_recomputed.json")
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
