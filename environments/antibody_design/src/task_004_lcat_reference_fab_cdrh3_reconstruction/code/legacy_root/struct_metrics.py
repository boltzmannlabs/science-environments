#!/usr/bin/env python
"""Task 004: structural metrics (fixed (chain,resi) dedup)."""
import sys, json, os
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import numpy as np
import metrics as m

base = "/home/boltzmann10/shared_metric_tools/prepared"
out = "/home/boltzmann10/shared_metric_tools/results"
aar = json.load(open(f"{out}/task004_aar.json"))
native_res = set(range(97, 116))

def ca_by_chain(atoms, chain):
    """CA coords in file order, dedup by resi within chain."""
    seen = set(); coords = []
    for a in atoms:
        if a[0] == chain and a[3] == "CA" and not a[7] and a[1] not in seen:
            seen.add(a[1]); coords.append([a[4], a[5], a[6]])
    return np.array(coords)

def ca_fw(atoms, chain, exclude=None):
    seen = set(); coords = []
    for a in atoms:
        if a[0] == chain and a[3] == "CA" and not a[7] and a[1] not in seen:
            if exclude and a[1] in exclude: continue
            seen.add(a[1]); coords.append([a[4], a[5], a[6]])
    return np.array(coords)

nat = m.parse_pdb(f"{base}/5BV7.pdb")
# native framework: B (all) + C (minus CDR-H3)
fw = np.vstack([ca_by_chain(nat, "B"), ca_fw(nat, "C", native_res)])
# native CDR-H3
nh3 = ca_fw(nat, "C", None)
# extract CDR-H3 from native C by position (96-114 1-based)
nC = ca_by_chain(nat, "C")
nh3 = nC[95:114]
print(f"native fw len {len(fw)}, native CDR-H3 len {len(nh3)}")

results = {}
for s in [1, 6, 9]:
    pred = f"{out}/task004_struct_boltz2/boltz_results_task004_sample{s}/predictions/task004_sample{s}/task004_sample{s}_model_0.pdb"
    if not os.path.exists(pred): continue
    pa = m.parse_pdb(pred)
    pB = ca_by_chain(pa, "B"); pC = ca_by_chain(pa, "C")
    pC_h3 = pC[95:114]
    pC_fw = np.concatenate([pC[:95], pC[114:]])
    pfw = np.vstack([pB, pC_fw])
    assert len(fw) == len(pfw), f"len mismatch {len(fw)} vs {len(pfw)}"
    R, t = m.kabsch(fw, pfw)
    def xf(c): return c @ R.T + t
    h3_rmsd = float(np.sqrt(np.mean(np.sum((nh3 - xf(pC_h3))**2, axis=1))))
    h3_tm = m.tm_score(nh3, xf(pC_h3))
    h3_lddt = m.lddt(xf(pC_h3), nh3)
    conf_path = os.path.join(os.path.dirname(pred), f"confidence_task004_sample{s}_model_0.json")
    conf = json.load(open(conf_path)) if os.path.exists(conf_path) else {}
    results[str(s)] = {"cdrh3_CA_RMSD_A": round(h3_rmsd,3), "cdrh3_TMscore": round(h3_tm,4),
                       "cdrh3_lDDT": round(h3_lddt,2),
                       "confidence": {"ptm": conf.get("ptm"), "iptm": conf.get("iptm"), "pddt": conf.get("complex_plddt")}}
    print(f"sample {s}: RMSD {h3_rmsd:.3f} TM {h3_tm:.4f} lDDT {h3_lddt:.2f}")

outj = {"candidates": results,
  "protocol": "Boltz2 prediction (designed heavy + native light + LCAT); align on antibody framework C-alpha (B all + C minus CDR-H3); CDR-H3 C-alpha metrics",
  "benchmark_table1": {"AAR":"0.4234±0.1334","TM-score":"0.9736±0.0090","lDDT":"0.8522±0.0216","CAAR":"0.2824±0.2037","RMSD":"8.25±4.55 A","DockQ":"0.423±0.161"},
  "benchmark_scope": "60-case RAbD aggregate (AbFlow Table 1), not 5BV7-specific",
  "our_aar": aar["candidates"][0]["aar"], "our_caar": aar["candidates"][0].get("caar")}
open(f"{out}/task004_struct_metrics.json","w").write(json.dumps(outj, indent=2))
print("saved")
