"""Stage 4: extract Boltz2 confidence metrics for reference + 8 candidates.

Each job yields two records (pairwise scheduling): 1 = HER2+VH, 2 = HER2+VL.
Metrics extracted per record: iptm, ptm, complex_plddt, complex_iplddt,
confidence_score, pair_chains_iptm cross-terms.
Writes results/.../raw/boltz2_confidence.json + .csv
"""
import json
import zipfile
import os

RUN = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched"
INP = RUN + "/inputs"
RAW = RUN + "/../../results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/raw"
os.makedirs(RAW, exist_ok=True)

def conf_from_zip(zpath):
    z = zipfile.ZipFile(zpath)
    out = {}
    for n in z.namelist():
        parts = n.split("/")
        if len(parts) >= 3 and parts[1].startswith("boltz_results_") and "confidence_" in n and n.endswith(".json"):
            rec = parts[1].split("_")[-1]
            c = json.loads(z.read(n).decode())
            out[rec] = {
                "iptm": c.get("iptm"), "ptm": c.get("ptm"),
                "complex_plddt": c.get("complex_plddt"), "complex_iplddt": c.get("complex_iplddt"),
                "confidence_score": c.get("confidence_score"),
                "cross_iptm_0_1": c.get("pair_chains_iptm", {}).get("0", {}).get("1"),
                "cross_iptm_1_0": c.get("pair_chains_iptm", {}).get("1", {}).get("0"),
            }
    return out

rows = {}
# reference
rows["REFERENCE"] = conf_from_zip(INP + "/boltz2_reference/outputs.zip")
# candidates
for cid in sorted(os.listdir(INP + "/boltz2_candidates")):
    p = INP + "/boltz2_candidates/" + cid + "/outputs.zip"
    if os.path.exists(p):
        rows[cid] = conf_from_zip(p)

json.dump(rows, open(RAW + "/boltz2_confidence.json", "w"), indent=2)

# CSV summary
with open(RAW + "/boltz2_confidence.csv", "w") as f:
    f.write("candidate,record,iptm,ptm,complex_plddt,complex_iplddt,confidence_score,cross_iptm_0_1,cross_iptm_1_0\n")
    for cid in sorted(rows):
        for rec in sorted(rows[cid]):
            m = rows[cid][rec]
            f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                cid, rec, m["iptm"], m["ptm"], m["complex_plddt"], m["complex_iplddt"],
                m["confidence_score"], m["cross_iptm_0_1"], m["cross_iptm_1_0"]))

print(open(RAW + "/boltz2_confidence.csv").read())
EOF_MARKER = None
