#!/usr/bin/env python3
"""run_002_esmfold_proteinmpnn_evaluation: ESMFold all eval sequences -> per-residue pLDDT mean (benchmark endpoint 1).
Usage: esmfold_eval.py <fasta> <outdir>"""
import json, os, sys

fasta, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
import torch
from esm import esmfold_v1
model = esmfold_v1.pretrained_esmfold().cuda().eval()

summary = {}
with open(fasta) as f:
    for l in f:
        if l.startswith('>'):
            name = l[1:].strip()
        else:
            pass
# simpler parse
for l in open(fasta):
    if l.startswith('>'):
        name = l[1:].strip(); recs.append([name, ''])
    else:
        recs[-1][1] += l.strip()

for name, seq in recs:
    out = model.infer([seq])
    plddt = out['plddt'][:, 1:-1].cpu().numpy().mean()
    pdb = model.output_to_pdb(out)[0]
    with open(os.path.join(outdir, f'{name}.pdb'), 'w') as f:
        f.write(pdb)
    summary[name] = {'mean_plddt': float(plddt), 'len': len(seq)}
    print(name, round(float(plddt), 4), flush=True)
    del out
    torch.cuda.empty_cache()
json.dump(summary, open(os.path.join(outdir, 'esmfold_summary.json'), 'w'), indent=1)
print('done', len(summary))
