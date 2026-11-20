#!/usr/bin/env python
"""Task 013 matched structural analysis (Boltz2 + ESMFold tracks).

Against the SAME predictor's native reference model, identical preparation:
  - Fv scRMSD: CA RMSD over all VH+VL residues after Kabsch alignment on
    framework CA atoms (VH non-CDR positions + all VL).
  - Per-CDR CA RMSD (HCDR1 26-33, HCDR2 51-58, HCDR3 97-111, 1-based VH),
    evaluated in the framework-defined frame (no per-region realignment).
  - mean pLDDT from each model's own per-residue B-factor column.
"""
import json
import numpy as np

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
B2 = f"{A}/src/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/inputs/submitted_requests/boltz2"
ESM = f"{A}/results/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/structures/esmfold"
CDR = {"HCDR1": list(range(26, 34)), "HCDR2": list(range(51, 59)), "HCDR3": list(range(97, 112))}
FW_H = [i for i in range(1, 123) if not any(i in r for r in CDR.values())]

def load_ca(pdb):
    """chain -> ((N,3) coords, (N,) bfactor), file order."""
    ch = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            ch.setdefault(line[21], []).append(
                ([float(line[30:38]), float(line[38:46]), float(line[46:54])],
                 float(line[60:66])))
    return {c: (np.array([x[0] for x in v]), np.array([x[1] for x in v])) for c, v in ch.items()}

def b2_fv(pdb):
    ch = load_ca(pdb)
    heavy = max(ch, key=lambda c: len(ch[c][0])); light = min(ch, key=lambda c: len(ch[c][0]))
    H, Hp = ch[heavy]; L, Lp = ch[light]
    return H, Hp, L, Lp

def esm_fv(pdb):
    """Single chain: VH 1-122, linker 123-137, VL 138-244 (0-based slices)."""
    ch = load_ca(pdb)
    c = list(ch)[0]
    X, P = ch[c]
    return X[:122], P[:122], X[137:244], P[137:244]

def kabsch(P, Q):
    """Row-vector convention: returns R with (P-Pm) @ R + Qm ≈ Q."""
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    U, S, Vt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(U @ Vt))
    R = U @ np.diag([1.0, 1.0, d]) @ Vt
    return R, P.mean(0), Q.mean(0)

def rmsd(X, Y):
    return float(np.sqrt(((X - Y) ** 2).sum(1).mean()))

def analyze(track, loader, models, out):
    Hr, Hpr, Lr, Lpr = loader(models["native"])
    for name, pdb in models.items():
        H, Hp, L, Lp = loader(pdb)
        P = np.vstack([H[[i - 1 for i in FW_H]], L])
        Q = np.vstack([Hr[[i - 1 for i in FW_H]], Lr])
        R, Pm, Qm = kabsch(P, Q)
        Ha = (H - Pm) @ R + Qm
        La = (L - Pm) @ R + Qm
        rec = {
            "fv_scrmsd": round(rmsd(np.vstack([Ha, La]), np.vstack([Hr, Lr])), 3),
            "mean_plddt": round(float((Hp.mean() + Lp.mean()) / 2), 2),
        }
        for k, rng in CDR.items():
            idx = [i - 1 for i in rng]
            rec[k.lower() + "_scrmsd"] = round(rmsd(Ha[idx], Hr[idx]), 3)
        allcdr = [i - 1 for r in CDR.values() for i in r]
        rec["hcdr123_scrmsd"] = round(rmsd(Ha[allcdr], Hr[allcdr]), 3)
        out[f"{track}:{name}"] = rec
        print(track, name, rec)

if __name__ == "__main__":
    results = {}
    names = ["native", "ab_hcdr123_s065", "ab_hcdr3only_s045", "ig_hcdr123_s069",
             "ig_hcdr123_s063", "ig_hcdr3_s002", "ig_hcdr3_s031"]
    analyze("boltz2", b2_fv, {n: f"{B2}/{n}/boltz_pdb/1_model_0.pdb" for n in names}, results)
    analyze("esmfold", esm_fv, {n: f"{ESM}/esmfold_{n}.pdb" for n in names}, results)
    dest = f"{A}/results/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/raw/scrmsd_analysis.json"
    json.dump(results, open(dest, "w"), indent=1)
    print("->", dest)
