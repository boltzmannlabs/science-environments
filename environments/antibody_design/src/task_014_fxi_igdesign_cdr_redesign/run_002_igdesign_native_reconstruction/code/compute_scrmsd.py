#!/usr/bin/env python3
"""S4: scRMSD computation for task_014 run_002 (Boltz2 protocol).

Protocol (identical for reference and every candidate):
- Predictor: Boltz2 (boltz-structure-prediction), single model per sequence,
  sequence-only Fv jobs [VH, VL]; doc IDs in inputs/execution_records/boltz2_doc_ids.json.
- Reference geometry: the Boltz2 prediction of the unmodified Osocimab Fv.
- Correspondence: positional (candidate VH/VL differ from reference only inside
  the CDR masks; lengths verified equal by sequence echo).
- Alignment: Kabsch on framework CA atoms = all Fv residues EXCEPT HCDR1/2/3
  (0-based 25-32, 50-57, 96-108 in the 120-aa VH) — i.e. VH-non-CDR + all VL.
- Reported: CA RMSD (A) on HCDR1, HCDR2, HCDR3, HCDR123 (union), Fv (all 227),
  measured after the single framework fit without refit.
- Self-check: reference vs itself must be 0.000 on every region.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "..")
RES = os.path.abspath(os.path.join(RUN, "..", "..", "..", "results",
                                   "task_014_fxi_igdesign_cdr_redesign",
                                   "run_002_igdesign_native_reconstruction"))
B2 = os.path.join(RES, "raw", "boltz2")

CDR_IDX = (list(range(25, 33)) + list(range(50, 58)) + list(range(96, 109)))
REGIONS = {
    "hcdr1": list(range(25, 33)),
    "hcdr2": list(range(50, 58)),
    "hcdr3": list(range(96, 109)),
    "hcdr123": CDR_IDX,
    "fv": None,  # all
}

LABELS = ["reference", "hcdr3_c012", "hcdr3_c022", "hcdr3_c027", "hcdr3_c065",
          "hcdr3_c082", "hcdr123_c034", "hcdr123_c035", "hcdr123_c067",
          "hcdr123_c070", "hcdr123_c082"]


def ca_coords(pdb):
    """Ordered CA coords [(chain, resseq, xyz)] for standard residues."""
    seen = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            ch = line[21]
            key = line[22:27]
            seen[(ch, key)] = [float(line[30:38]), float(line[38:46]),
                               float(line[46:54])]
    # order: chain A (VH) then B (VL) by residue number — matches echo order
    def skey(t):
        ch, key = t
        num = int(key[:4]) if key[:4].strip().isdigit() else 0
        return (ch, num, key)
    out = sorted(seen, key=skey)
    return np.array([seen[k] for k in out])


def kabsch_rmsd(P, Q):
    """RMSD after optimal superposition of P onto Q."""
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    V, S, W = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(V @ W))
    R = V @ np.diag([1.0, 1.0, d]) @ W
    diff = (Pc @ R) - Qc
    return float(np.sqrt((diff ** 2).sum() / len(P)))


def main():
    coords = {}
    for label in LABELS:
        pdb = os.path.join(B2, label, "boltz_pdb", "1_model_0.pdb")
        c = ca_coords(pdb)
        assert len(c) == 227, f"{label}: {len(c)} CA atoms (expected 227)"
        coords[label] = c

    ref = coords["reference"]
    # framework indices: VH non-CDR (0..119 minus CDR) + all VL (120..226)
    fw_idx = [i for i in range(120) if i not in set(CDR_IDX)] + list(range(120, 227))

    results = {}
    # self-check
    self_rmsd = {name: round(kabsch_rmsd(ref, ref), 6) for name in REGIONS}
    results["_self_check_reference_vs_itself"] = self_rmsd
    assert all(v == 0.0 for v in self_rmsd.values()), "self-check failed"

    for label in LABELS:
        if label == "reference":
            continue
        mob = coords[label]
        # single framework fit
        Pc, Rc = mob[fw_idx], ref[fw_idx]
        mc, rc = Pc.mean(0), Rc.mean(0)
        V, S, W = np.linalg.svd((Pc - mc).T @ (Rc - rc))
        d = np.sign(np.linalg.det(V @ W))
        R = V @ np.diag([1.0, 1.0, d]) @ W
        fit = (mob - mc) @ R + rc
        row = {}
        for name, idx in REGIONS.items():
            sel = idx if idx is not None else list(range(227))
            row[name] = round(float(np.sqrt(((fit[sel] - ref[sel]) ** 2).sum()
                                             / len(sel))), 4)
        results[label] = row
        print(f"{label:14s} " + " ".join(f"{k}={v:.3f}" for k, v in row.items()))

    out = os.path.join(RES, "scrmsd_results.json")
    with open(out, "w") as f:
        json.dump({
            "protocol": {
                "predictor": "Boltz2 (boltz-structure-prediction), single model per sequence",
                "reference": "Boltz2 prediction of unmodified Osocimab Fv (doc 6afb0ef99850a93adf684d5e)",
                "atoms": "CA", "units": "angstrom",
                "alignment": "Kabsch on framework CA (VH non-CDR + all VL), single fit, no refit",
                "correspondence": "positional (sequence-echo verified)",
                "regions_0based_vh": {"hcdr1": "25-32", "hcdr2": "50-57",
                                      "hcdr3": "96-108"},
            },
            "self_check": self_rmsd,
            "candidates": results,
        }, f, indent=1)
    print(f"WROTE {out}")


if __name__ == "__main__":
    main()
