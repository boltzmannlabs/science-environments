#!/usr/bin/env python
"""Generate Boltz2 payloads for reference + 5 shortlist candidates."""
import json

cfull = json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_candidates.json"))
short = {c["id"]: c for c in json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json"))["shortlist"]}
seqs = json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_seqs.json"))
HER2 = seqs["HER2"]
REF_VH, REF_VL = cfull["ref_vh"], cfull["ref_vl"]

ids = ["REF_1N8Z", "AB_08", "AB_20", "AB_04", "AB_05", "AB_13"]
payloads = {}
for cid in ids:
    if cid == "REF_1N8Z":
        vh, vl = REF_VH, REF_VL
    else:
        vh, vl = short[cid]["heavy"], short[cid]["light"]
    payloads[cid] = {
        "Protein_Sequences": [vh, vl, HER2],
        "DNA_Sequences": [],
        "RNA_Sequences": [],
        "SMILES": [],
    }
    print(f"{cid}: VH={len(vh)} VL={len(vl)} HER2={len(HER2)} total={len(vh)+len(vl)+len(HER2)}")

with open("/home/boltzmann10/.sci/cache/scratch/task001_boltz2_payloads.json","w") as f:
    json.dump(payloads, f)
print("Saved payloads.")
