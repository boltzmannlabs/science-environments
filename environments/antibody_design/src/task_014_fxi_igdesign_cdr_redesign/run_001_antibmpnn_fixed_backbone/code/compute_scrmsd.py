#!/usr/bin/env python3
"""S4b: scRMSD for task_014 run_001 (AntiBMPNN candidates), shared protocol with run_002.

Identical to run_002 code/compute_scrmsd.py (sorted chain+resnum correspondence,
Kabsch framework fit, same regions, same reference model). Only LABELS/paths differ.
Reference geometry: run_002's Boltz2 prediction of the unmodified Osocimab Fv
(doc 6afb0ef99850a93adf684d5e).
"""
import json
import os

import numpy as np

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
RES = os.path.join(A, "results/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone")
R2 = os.path.join(A, "results/task_014_fxi_igdesign_cdr_redesign/run_002_igdesign_native_reconstruction")

CDR_IDX = (list(range(25, 33)) + list(range(50, 58)) + list(range(96, 109)))
REGIONS = {
    "hcdr1": list(range(25, 33)),
    "hcdr2": list(range(50, 58)),
    "hcdr3": list(range(96, 109)),
    "hcdr123": CDR_IDX,
    "fv": None,
}
LABELS = ["hcdr3_s02", "hcdr3_s15", "hcdr3_s16", "hcdr3_s11", "hcdr3_s01",
          "hcdr123_s02", "hcdr123_s01", "hcdr123_s13", "hcdr123_s16", "hcdr123_s05"]


def ca_coords(pdb):
    seen = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            ch = line[21]
            key = line[22:27]
            seen[(ch, key)] = [float(line[30:38]), float(line[38:46]),
                               float(line[46:54])]
    def skey(t):
        ch, key = t
        num = int(key[:4]) if key[:4].strip().isdigit() else 0
        return (ch, num, key)
    out = sorted(seen, key=skey)
    return np.array([seen[k] for k in out])


def kabsch_rmsd(P, Q):
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    V, S, W = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(V @ W))
    R = V @ np.diag([1.0, 1.0, d]) @ W
    diff = (Pc @ R) - Qc
    return float(np.sqrt((diff ** 2).sum() / len(P)))


def main():
    ref = ca_coords(os.path.join(R2, "raw/boltz2/reference/boltz_pdb/1_model_0.pdb"))
    assert len(ref) == 227
    fw_idx = [i for i in range(120) if i not in set(CDR_IDX)] + list(range(120, 227))

    results = {}
    self_rmsd = {name: round(kabsch_rmsd(ref, ref), 6) for name in REGIONS}
    assert all(v == 0.0 for v in self_rmsd.values()), "self-check failed"

    for label in LABELS:
        pdb = os.path.join(RES, "raw/boltz2", label, "boltz_pdb/boltz_pdb/1_model_0.pdb")
        mob = ca_coords(pdb)
        assert len(mob) == 227, f"{label}: {len(mob)} CA atoms"
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

    # framework-region RMSD per candidate (fit quality diagnostic, reported too)
    fw_diag = {}
    for label in LABELS:
        mob = ca_coords(os.path.join(RES, "raw/boltz2", label, "boltz_pdb/boltz_pdb/1_model_0.pdb"))
        fw_diag[label] = round(kabsch_rmsd(mob[fw_idx], ref[fw_idx]), 4)

    out = os.path.join(RES, "scrmsd_results.json")
    with open(out, "w") as f:
        json.dump({
            "protocol": {
                "predictor": "Boltz2 (boltz-structure-prediction), single model per sequence",
                "reference": "Boltz2 prediction of unmodified Osocimab Fv (run_002 doc 6afb0ef99850a93adf684d5e)",
                "atoms": "CA", "units": "angstrom",
                "alignment": "Kabsch on framework CA (VH non-CDR + all VL), single fit, no refit",
                "correspondence": "positional, sorted by (chain, residue number) — identical to run_002",
                "regions_0based_vh": {"hcdr1": "25-32", "hcdr2": "50-57",
                                      "hcdr3": "96-108"},
            },
            "self_check": self_rmsd,
            "framework_fit_rmsd": fw_diag,
            "candidates": results,
        }, f, indent=1)
    print("WROTE", out)


if __name__ == "__main__":
    main()
