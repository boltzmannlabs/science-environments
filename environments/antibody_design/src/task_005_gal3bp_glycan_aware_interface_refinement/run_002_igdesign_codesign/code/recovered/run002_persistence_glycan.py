#!/usr/bin/env python
"""run_002 persistence + glycan on each candidate's 5 AFM models (same conventions as run run_001_antibmpnn_interface_refinement)."""
import glob, json
import numpy as np
from Bio.SVDSuperimposer import SVDSuperimposer
import subprocess

S = "/home/boltzmann10/.sci/cache/scratch/gal3bp_run"
out = {}
for C in ("G3I-01", "G3I-02", "G3I-03"):
    files = sorted(glob.glob(f"{S}/run002_{C}/**/*unrelaxed_rank_0*.pdb", recursive=True))
    assert len(files) == 5, (C, len(files))
    def parse(p):
        res = {}
        for l in open(p):
            if l.startswith("ATOM"):
                if l[12:16].strip() == "CA":
                    res[(l[21], int(l[22:26]))] = np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])
        return res
    models = {f.split("rank_")[1][:3]: parse(f) for f in files}
    def pairs(res, cut=6.0):
        ab = [k for k in res if k[0] in "AB"]; ag = [k for k in res if k[0] == "C"]
        return {(a, b) for a in ab for b in ag if np.linalg.norm(res[a] - res[b]) < cut}
    per = {r: pairs(models[r]) for r in models}
    r0 = "001"
    para = sorted({a for a, b in per[r0]})
    pers = {f"{a[0]}{a[1]:03d}|C{b[1]:03d}": sum((a, b) in per[r] for r in per) / 5.0 for (a, b) in per[r0]}
    ag0 = {k[1]: v for k, v in models[r0].items() if k[0] == "C"}
    rmsds = {}
    for r in sorted(models):
        if r == r0: continue
        agm = {k[1]: v for k, v in models[r].items() if k[0] == "C"}
        common = sorted(set(ag0) & set(agm))
        sup = SVDSuperimposer()
        sup.set(np.array([ag0[c] for c in common]), np.array([agm[c] for c in common]))
        sup.run(); rot, tran = sup.get_rotran()
        keys = [k for k in para if k in models[r0] and k in models[r]]
        if not keys: rmsds[r] = None; continue
        A = np.array([models[r0][k] for k in keys])
        B = np.array([models[r][k] for k in keys]) @ rot.T + tran
        rmsds[r] = round(float(np.sqrt(((A - B) ** 2).sum(1).mean())), 2)
    # glycan dSASA via skill script
    import os
    p1 = f"{S}/run002_{C}_rank1_clean.pdb"
    gj = f"{S}/run002_glycan_{C}.json"
    r = subprocess.run(["/home/boltzmann10/anaconda3/bin/python",
                        "/home/boltzmann10/.sci/skills/antibody-design-benchmark/scripts/glycan_dsasa.py",
                        "--pdb", p1, "--antigen-chain", "C", "--epitope-range", "276-350",
                        "--glycosite", "344", "--ab-chains", "A", "B", "--output", gj],
                       capture_output=True, text=True)
    gly = json.load(open(gj)) if os.path.exists(gj) else {"error": r.stderr[-200:]}
    out[C] = {
        "per_sample_pair_counts": {r: len(per[r]) for r in sorted(per)},
        "rank001_pairs": len(per[r0]),
        "n_pairs_in_ge3_of_5": sum(1 for v in pers.values() if v >= 0.6),
        "interface_ca_rmsd_to_rank001_A": rmsds,
        "glycan_dsasa_A2": gly.get("glycan_dsasa_A2"),
        "glycan_clashes": gly.get("glycan_antibody_clashes_n2p5A"),
    }
    print(C, out[C]["per_sample_pair_counts"], "| persist>=3/5:", out[C]["n_pairs_in_ge3_of_5"], "/",
          out[C]["rank001_pairs"], "| RMSD:", rmsds, "| glycan:", out[C]["glycan_dsasa_A2"], out[C]["glycan_clashes"])
json.dump(out, open(f"{S}/run002_persistence_glycan.json", "w"), indent=1)
print("wrote run002_persistence_glycan.json")
