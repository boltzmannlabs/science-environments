"""Stage 6: consolidated evaluation — Prodigy affinity, epitope recovery, CDR pLDDT.

Metric definitions (per task benchmark):
- prodigy_dG_rec1/rec2: predicted binding free energy (kcal/mol) for HER2+VH / HER2+VL
  pairwise Boltz2 records; Kd = exp(dG/RT), T=298.15, R=0.001987 kcal/mol/K.
- epitope_recovery_rec2: |prodigy HER2 interface ∩ crystal 1N8Z epitope| / |crystal epitope|
  (record 2 = HER2+VL, which consistently lands on domain IV epitope).
- cdr_plddt_rec1/rec2: mean per-residue pLDDT over CDR positions (from plddt npz),
  VH CDRs for record 1, VL CDRs for record 2.
Outputs: results/.../raw/evaluation.csv + evaluation.json
"""
import csv
import io
import json
import os
import re
import zipfile
import math

RUN = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched"
INP = RUN + "/inputs"
RAW = RUN + "/../../results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/raw"
R = 0.0019872041  # kcal/mol/K
T = 298.15

# crystal epitope: stage0 wrote antibody+antigen contacts under the light-chain label;
# antibody (VL) residues are <=214, so HER2 residues are the >214 entries.
epitope = set()
for row in csv.DictReader(open(INP + "/crystal_contacts.csv")):
    if int(row["residue_pdb"]) > 214:
        epitope.add(int(row["residue_pdb"]))
if not epitope:
    txt = open(INP + "/crystal_contacts.csv").read()
    print("WARNING no HER2 rows; header:")
    print(txt[:300])

MASK = {
    "H": set(list(range(31, 36)) + list(range(50, 66)) + list(range(95, 103))),
    "L": set(list(range(24, 35)) + list(range(50, 57)) + list(range(89, 98))),
}

cands = json.load(open(INP + "/candidates.json"))["candidates"]
cand_by_id = {c["candidate_id"]: c for c in cands}

def parse_prodigy(cid):
    rows = list(csv.DictReader(open(INP + "/prodigy/%s/prodigy.csv" % cid)))
    out = {}
    for r in rows:
        nums = set(int(m.group(1)) for m in re.finditer(r"[A-Z]{3}\s+(\d+)", r["chain_A of AB"]))
        rid = r["id"].split("_")[0]
        dG = float(r["binding_affinity for AB"])
        out[rid] = {"dG": dG, "kd_um": math.exp(dG / (R * T)) * 1e6, "interface": nums,
                    "recovery": (len(nums & epitope) / len(epitope)) if epitope else None}
    return out

def cdr_plddt(zpath, rec):
    z = zipfile.ZipFile(zpath)
    n = "boltz_outputs/boltz_results_%s/predictions/%s/plddt_%s_model_0.npz" % (rec, rec, rec)
    try:
        import numpy as np
        arr = np.load(io.BytesIO(z.read(n)))
        key = [k for k in arr.files if "plddt" in k][0]
        vals = arr[key]
    except Exception:
        return None
    # record layout: chain A = HER2 (607), chain B = VH(120) or VL(107)
    m = MASK["H"] if rec == "1" else MASK["L"]
    off = 607  # antibody chain starts after HER2 in flattened array
    idx = [off + (p - 1) for p in sorted(m)]
    if max(idx) >= len(vals):
        return None
    cdr = float(vals[idx].mean())
    fw_idx = [off + i for i in range(len(vals) - off) if (i + 1) not in m]
    return {"cdr_plddt": round(cdr, 4), "fw_plddt": round(float(vals[fw_idx].mean()), 4)}

rows = []
conf = json.load(open(RAW + "/boltz2_confidence.json"))
for cid in ["REFERENCE"] + ["T001-C%03d" % i for i in range(1, 9)]:
    zdir = INP + "/boltz2_reference" if cid == "REFERENCE" else INP + "/boltz2_candidates/" + cid
    pz = parse_prodigy(cid)
    pl1 = cdr_plddt(zdir + "/outputs.zip", "1")
    pl2 = cdr_plddt(zdir + "/outputs.zip", "2")
    c = cand_by_id.get(cid, {})
    row = {
        "candidate": cid,
        "n_mutations": c.get("n_mutations", 0),
        "mut_H": " ".join(c.get("mut_H", [])),
        "mut_L": " ".join(c.get("mut_L", [])),
        "design_score": c.get("score"),
        "dG_rec1_H": pz["1"]["dG"], "Kd_uM_rec1": round(pz["1"]["kd_um"], 2),
        "dG_rec2_L": pz["2"]["dG"], "Kd_uM_rec2": round(pz["2"]["kd_um"], 2),
        "epitope_recovery_rec2": round(pz["2"]["recovery"], 3) if pz["2"]["recovery"] is not None else None,
        "epitope_recovery_rec1": round(pz["1"]["recovery"], 3) if pz["1"]["recovery"] is not None else None,
        "iptm_rec1": round(conf[cid]["1"]["iptm"], 3), "iptm_rec2": round(conf[cid]["2"]["iptm"], 3),
        "iplddt_rec1": round(conf[cid]["1"]["complex_iplddt"], 3), "iplddt_rec2": round(conf[cid]["2"]["complex_iplddt"], 3),
        "cdr_plddt_VH": pl1["cdr_plddt"] if pl1 else None, "cdr_plddt_VL": pl2["cdr_plddt"] if pl2 else None,
        "fw_plddt_VH": pl1["fw_plddt"] if pl1 else None, "fw_plddt_VL": pl2["fw_plddt"] if pl2 else None,
        "liabilities": ";".join(c.get("liabilities", [])),
    }
    rows.append(row)

with open(RAW + "/evaluation.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
json.dump(rows, open(RAW + "/evaluation.json", "w"), indent=2)
print("crystal epitope size:", len(epitope), "range", min(epitope), max(epitope))
for r in rows:
    print(r["candidate"], "muts=%s" % r["n_mutations"], "dG(VH)=%.1f dG(VL)=%.1f" % (r["dG_rec1_H"], r["dG_rec2_L"]),
          "epiRec=%.2f" % (r["epitope_recovery_rec2"] or 0), "ipTM(VL)=%.2f" % r["iptm_rec2"],
          "cdrLDDT(VH)=%s cdrLDDT(VL)=%s" % (r["cdr_plddt_VH"], r["cdr_plddt_VL"]))
