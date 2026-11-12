#!/usr/bin/env python
"""Task 003: build FASTA for top designed CDR-H3 candidates (Boltz2 input).
VH = designed (H965 framework + new CDR-H3), VL = H965, C = PD-1."""
import json, os
d = json.load(open("/home/boltzmann10/shared_metric_tools/results/task003_cdrh3_designed.json"))
# H965 VL + PD-1
vl = "DIQMTQSPSTLSASVGDRVTITCRASQSISSWLAWYQQKPGKAPKLLIYAASRLQSGVPSRFSGSGSGTEFTLTISSLQPDDFATYYCQQSYSYPPLTFGQGTKVEIK"
pd1 = "NPPTFSPALLVVTEGDNATFTCSFSNTSESFVLNWYRMSPSNQTDKLAAFPESRFRVTQLPNGRDFHMSVVRARRNDSGTYLCGAISLAPKAQIKESLRAELRVTE"
# top 3 unique by pmnn score
seen = set(); top = []
for r in sorted(d["candidates"], key=lambda x: -x["pmnn_score"]):
    if r["cdr"] in seen: continue
    seen.add(r["cdr"]); top.append(r)
    if len(top) == 3: break
outdir = "/home/boltzmann10/shared_metric_tools/prepared/task003_struct"
os.makedirs(outdir, exist_ok=True)
for r in top:
    vh = r["vh"]
    fasta = f">A|protein\n{vh}\n>B|protein\n{vl}\n>C|protein\n{pd1}\n"
    path = f"{outdir}/task003_cand{r['sample']}.fasta"
    open(path, "w").write(fasta)
    print(f"candidate {r['sample']}: CDR-H3 {r['cdr']} -> {path}")
