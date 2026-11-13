#!/usr/bin/env python
"""Task 005: build Boltz2 FASTAs for BDBV-43 reference + top designed CDR-H3
candidates vs LGALS3BP (Gal-3BP, UniProt Q08380)."""
import json, os
# Native BDBV-43 sequences (verified from PDB 7KEW chains G/J)
NATIVE_VH = "QVQLVQSGAEVKKPGSSVKVSCRASGDSFSRKYGIWVRQAPGQGFEWMGTIMIVGLTTSAQKFQGRVTITADKSTSTAHMELTSEDTAIYYCARDEIIGADSWGQGTLVTVS"
NATIVE_VL = "EIVMTQSPAIMSVSPGKRATLSCRASQSVSSNLAWYQRKPGQAPRLLIYGSSTRATGIPARFSGSGSGTEFTLTISSLQSEDFAVYYCLQYYNWPRTFGQGTKVEI"
NATIVE_H3 = "ARDEIIGADS"

fa = "/home/boltzmann10/shared_metric_tools/results/task005_proteinmpnn/seqs/task005_bdbv43_fab.fa"
lines = open(fa).read().splitlines()
res = []
for i, ln in enumerate(lines):
    if ln.startswith(">T=") and "sample=" in ln:
        sid = int(ln.split("sample=")[1].split(",")[0])
        score = float(ln.split("score=")[1].split(",")[0])
        seq = lines[i+1].strip()
        vh, vl = seq.split("/")[:2]
        i2 = vh.rfind("YYC"); j2 = vh.find("WGQG")
        res.append({"sample": sid, "pmnn_score": score, "vh": vh, "vl": vl, "cdr": vh[i2+3:j2]})
seen = set(); uniq = [r for r in res if not (r["cdr"] in seen or seen.add(r["cdr"]))]
json.dump({"native_cdrh3": NATIVE_H3, "candidates": res, "unique": len(uniq)},
          open("/home/boltzmann10/shared_metric_tools/results/task005_cdrh3_designed.json", "w"), indent=1)

# LGALS3BP (Q08380, canonical 585 aa)
lg = ""
for line in open("/tmp/lgals3bp.fasta"):
    if not line.startswith(">"): lg += line.strip()

# top 3 unique by score
seen = set(); top = []
for r in sorted(res, key=lambda x: -x["pmnn_score"]):
    if r["cdr"] in seen: continue
    seen.add(r["cdr"]); top.append(r)
    if len(top) == 3: break

outdir = "/home/boltzmann10/shared_metric_tools/prepared/task005_struct"
os.makedirs(outdir, exist_ok=True)
def write(tag, vh):
    open(f"{outdir}/{tag}.fasta", "w").write(
        f">A|protein\n{vh}\n>B|protein\n{NATIVE_VL}\n>C|protein\n{lg}\n")
write("task005_ref_bdbv43", NATIVE_VH)
for r in top: write(f"task005_cand{r['sample']}", r["vh"])
print(f"{len(res)} designed, {len(uniq)} unique; top3:", [r['cdr'] for r in top])
