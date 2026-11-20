#!/usr/bin/env python
"""Task 013 run_001 result tables + native-vs-crystal benchmark comparison.

benchmark_comparison.csv rows:
  - native control: predictor Fv scRMSD / per-CDR scRMSD vs crystal 5I5K Fv
    (framework-aligned, CA atoms) — comparator: released positive-control row
    (ABB2/ABB3/ABB3-LM/ESMFold) from benchmark reference.md.
  - candidate structural consistency: vs same-predictor native model.
  - AAR endpoints vs released benchmark inverse-folding rows.
"""
import csv
import json
import numpy as np

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
TASK = "task_013_c5_igdesign_cdr_redesign"
R1 = f"{A}/results/{TASK}/run_001_antibmpnn_matched"
CRYSTAL = f"{A}/src/{TASK}/run_001_antibmpnn_matched/inputs/5i5k_HLB.pdb"
B2 = f"{R1}/raw/boltz2"
ESM = f"{R1}/structures/esmfold"
CDR = {"HCDR1": list(range(26, 34)), "HCDR2": list(range(51, 59)), "HCDR3": list(range(97, 112))}
FW_H = [i for i in range(1, 123) if not any(i in r for r in CDR.values())]

def load_ca(pdb, chains=None):
    ch = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            c = line[21]
            if chains and c not in chains:
                continue
            ch.setdefault(c, []).append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    return {c: np.array(v) for c, v in ch.items()}

def kabsch_apply(P, Q, X):
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    U, S, Vt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(U @ Vt))
    R = U @ np.diag([1.0, 1.0, d]) @ Vt
    return (X - P.mean(0)) @ R + Q.mean(0)

def rmsd(X, Y):
    return float(np.sqrt(((X - Y) ** 2).sum(1).mean()))

# crystal Fv: chain H (VH residues 1-122) + chain L (VL residues 1-107) from 5I5K;
# chains carry additional constant-region residues (H 221, L 213 total) — take variable domains only
crys = load_ca(CRYSTAL, {"H", "L"})
Hc, Lc = crys["H"][:122], crys["L"][:107]

def vs_crystal(H, L):
    P = np.vstack([H[[i - 1 for i in FW_H]], L])
    Q = np.vstack([Hc[[i - 1 for i in FW_H]], Lc])
    Ha = kabsch_apply(P, Q, H)
    La = kabsch_apply(P, Q, L)
    out = {"fv": round(rmsd(np.vstack([Ha, La]), np.vstack([Hc, Lc])), 4)}
    for k, rng in CDR.items():
        idx = [i - 1 for i in rng]
        out[k.lower()] = round(rmsd(Ha[idx], Hc[idx]), 4)
    allc = [i - 1 for r in CDR.values() for i in r]
    out["hcdr123"] = round(rmsd(Ha[allc], Hc[allc]), 4)
    return out

def b2_fv(p):
    ch = load_ca(p)
    heavy = max(ch, key=lambda c: len(ch[c])); light = min(ch, key=lambda c: len(ch[c]))
    return ch[heavy], ch[light]

def esm_fv(p):
    ch = load_ca(p)
    X = list(ch.values())[0]
    return X[:122], X[137:244]

sel = json.load(open(f"{A}/src/{TASK}/run_001_antibmpnn_matched/inputs/selected_candidates.json"))
aar = json.load(open(f"{A}/results/{TASK}/run_002_igdesign_reconstruction/aar_evaluation.json"))
scr = json.load(open(f"{R1}/raw/scrmsd_analysis.json"))

# native vs crystal (benchmark positive control reproduction)
nat_b2 = vs_crystal(*b2_fv(f"{B2}/boltz2_native_model_0.pdb"))
nat_esm = vs_crystal(*esm_fv(f"{ESM}/esmfold_native.pdb"))

REF_RELEASED = {  # released positive-control row, Å (benchmark reference.md)
    "ABB2": {"hcdr1": 1.1479, "hcdr2": 1.0812, "hcdr3": 2.2289, "hcdr123": 1.7452, "fv": 1.2950},
    "ABB3": {"hcdr1": 1.3176, "hcdr2": 1.1441, "hcdr3": 2.3998, "hcdr123": 1.8901, "fv": 1.3017},
    "ABB3-LM": {"hcdr1": 1.2021, "hcdr2": 1.1968, "hcdr3": 1.8354, "hcdr123": 1.5403, "fv": 1.2441},
    "ESMFold": {"hcdr1": 0.8494, "hcdr2": 1.0668, "hcdr3": 1.6620, "hcdr123": 1.3477, "fv": 1.2044},
}

rows = []
for predictor, vals, comp in [("Boltz2", nat_b2, "ABB3 (closest platform analog)"), ("ESMFold", nat_esm, "ESMFold released row")]:
    rows.append({
        "endpoint": f"native {predictor} vs crystal 5I5K scRMSD (A)",
        "comparator": f"released positive-control {comp} (A)",
        "hcdr1": vals["hcdr1"], "hcdr2": vals["hcdr2"], "hcdr3": vals["hcdr3"],
        "hcdr123": vals["hcdr123"], "fv": vals["fv"],
        "sample_scope": "native unmodified reference Fv, framework-aligned CA",
    })
for p, r in REF_RELEASED.items():
    rows.append({"endpoint": f"released reference {p} scRMSD (A)", "comparator": "published CSV row",
                 "hcdr1": r["hcdr1"], "hcdr2": r["hcdr2"], "hcdr3": r["hcdr3"],
                 "hcdr123": r["hcdr123"], "fv": r["fv"], "sample_scope": "released positive control"})

# candidate rows (structural consistency vs same-predictor native)
for c in sel:
    cid = c["candidate_id"]
    rows.append({
        "endpoint": f"{cid} Boltz2 scRMSD vs Boltz2-native (A)", "comparator": "same-predictor native model",
        "hcdr1": scr[f"boltz2:{cid}"]["hcdr1_scrmsd"], "hcdr2": scr[f"boltz2:{cid}"]["hcdr2_scrmsd"],
        "hcdr3": scr[f"boltz2:{cid}"]["hcdr3_scrmsd"], "hcdr123": scr[f"boltz2:{cid}"]["hcdr123_scrmsd"],
        "fv": scr[f"boltz2:{cid}"]["fv_scrmsd"], "sample_scope": f"{c['pool']} pool, aar_sum {c['aar_sum']}",
    })
    rows.append({
        "endpoint": f"{cid} ESMFold scRMSD vs ESMFold-native (A)", "comparator": "same-predictor native model",
        "hcdr1": scr[f"esmfold:{cid}"]["hcdr1_scrmsd"], "hcdr2": scr[f"esmfold:{cid}"]["hcdr2_scrmsd"],
        "hcdr3": scr[f"esmfold:{cid}"]["hcdr3_scrmsd"], "hcdr123": scr[f"esmfold:{cid}"]["hcdr123_scrmsd"],
        "fv": scr[f"esmfold:{cid}"]["fv_scrmsd"], "sample_scope": f"{c['pool']} pool, aar_sum {c['aar_sum']}",
    })

# AAR endpoints
aar_rows = [
    ("run_002 IgDesign HCDR3 1-shot", aar["run_002_hcdr3_1shot"]["HCDR3"], "released HCDR3-only IF row mean 0.4828/max 0.5333", "n=1"),
    ("run_002 IgDesign HCDR3 best-of-100", aar["run_002_hcdr3_100"]["HCDR3"], "released HCDR3-only IF row mean 0.4828/max 0.5333", "n=100"),
    ("run_002 IgDesign HCDR123 1-shot HCDR3", aar["run_002_hcdr123_1shot"]["HCDR3"], "released HCDR123 IF row mean 0.4776/max 0.5333", "n=1"),
    ("run_002 IgDesign HCDR123 best-of-100 HCDR3", aar["run_002_hcdr123_100"]["HCDR3"], "released HCDR123 IF row mean 0.4776/max 0.5333", "n=100"),
    ("run_002 IgDesign HCDR123 best-of-100 HCDR1", aar["run_002_hcdr123_100"]["HCDR1"], "released HCDR123 IF row 0.6250", "n=100"),
    ("run_002 IgDesign HCDR123 best-of-100 HCDR2", aar["run_002_hcdr123_100"]["HCDR2"], "released HCDR123 IF row 0.7500", "n=100"),
    ("run_001 AntiBMPNN HCDR3-only HCDR3 AAR", aar["run_001_hcdr3only"]["HCDR3"], "released HCDR3-only IF row mean 0.4828", "n=100"),
    ("run_001 AntiBMPNN HCDR123 HCDR3 AAR", aar["run_001_hcdr123"]["HCDR3"], "released HCDR123 IF row mean 0.4776", "n=100"),
]
for name, v, comp, n in aar_rows:
    rows.append({"endpoint": f"{name} AAR (fraction)", "comparator": comp,
                 "hcdr1": "", "hcdr2": "", "hcdr3": "", "hcdr123": "", "fv": "",
                 "sample_scope": f"{n}; mean {v['mean_aar']}, max {v['max_aar']}, full recoveries {v.get('n_full_recovery','')}"})

with open(f"{R1}/benchmark_comparison.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["endpoint", "comparator", "hcdr1", "hcdr2", "hcdr3", "hcdr123", "fv", "sample_scope"])
    w.writeheader()
    w.writerows(rows)
print(f"benchmark_comparison.csv: {len(rows)} rows")
print("native Boltz2 vs crystal:", nat_b2)
print("native ESMFold vs crystal:", nat_esm)

# candidates.csv / metrics.csv
cd = []
for c in sel:
    cid = c["candidate_id"]
    cd.append({
        "candidate_id": cid, "run": c["run"], "pool": c["pool"], "aar_sum": c["aar_sum"],
        "b2_fv_scrmsd": scr[f"boltz2:{cid}"]["fv_scrmsd"], "b2_hcdr123_scrmsd": scr[f"boltz2:{cid}"]["hcdr123_scrmsd"],
        "b2_hcdr3_scrmsd": scr[f"boltz2:{cid}"]["hcdr3_scrmsd"], "b2_mean_plddt": scr[f"boltz2:{cid}"]["mean_plddt"],
        "esm_fv_scrmsd": scr[f"esmfold:{cid}"]["fv_scrmsd"], "esm_hcdr123_scrmsd": scr[f"esmfold:{cid}"]["hcdr123_scrmsd"],
        "esm_hcdr3_scrmsd": scr[f"esmfold:{cid}"]["hcdr3_scrmsd"], "esm_mean_plddt": scr[f"esmfold:{cid}"]["mean_plddt"],
        "vh_sha256_16": __import__("hashlib").sha256(c["vh"].encode()).hexdigest()[:16],
    })
fields = list(cd[0])
with open(f"{R1}/candidates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(cd)

# shortlist: rank by combined structural consistency (mean of both predictors' Fv scRMSD), report top 3
ranked = sorted(cd, key=lambda r: (r["b2_fv_scrmsd"] + r["esm_fv_scrmsd"]) / 2)
for i, r in enumerate(ranked, 1):
    r["rank"] = i
with open(f"{R1}/shortlist.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["rank"] + fields); w.writeheader(); w.writerows(ranked)
print("shortlist order:", [r["candidate_id"] for r in ranked])

json.dump({"native_vs_crystal": {"boltz2": nat_b2, "esmfold": nat_esm},
           "released_reference": REF_RELEASED}, open(f"{R1}/raw/native_vs_crystal.json", "w"), indent=1)
