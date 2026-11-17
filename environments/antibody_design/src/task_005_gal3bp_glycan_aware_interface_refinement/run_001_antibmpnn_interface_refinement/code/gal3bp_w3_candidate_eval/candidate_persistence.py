#!/usr/bin/env python3
"""W4 extension: per-sample interface persistence for each candidate.

For each candidate's 5 AFM models: CA-CA<6A interface pairs per model,
pairwise interface RMSD to rank_001 (align antigen CA, RMSD on antibody
interface atoms), and persistence of rank_001 pairs across the 5 models.
Retained per-sample as required by the task metrics table.
"""
import glob, json, sys
import numpy as np
from Bio.SVDSuperimposer import SVDSuperimposer

B = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement"
out = {}
for C in ("G3BPD-14", "G3BPD-04", "G3BPD-17"):
    files = sorted(glob.glob(f"{B}/gal3bp_w3_candidate_eval/outputs_{C}/extracted/**/*unrelaxed_rank_0*.pdb", recursive=True))
    assert len(files) == 5, f"{C}: {len(files)} models"
    def parse(p):
        res = {}
        for l in open(p):
            if l.startswith("ATOM"):
                nm = l[12:16].strip()
                if nm == "CA":
                    res[(l[21], int(l[22:26]))] = np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])
        return res
    models = {f.split("rank_")[1][:3]: parse(f) for f in files}
    def pairs(res, cut=6.0):
        ab = [k for k in res if k[0] in "AB"]; ag = [k for k in res if k[0] == "C"]
        return {(k1, k2) for k1 in ab for k2 in ag if np.linalg.norm(res[k1] - res[k2]) < cut}
    per = {r: pairs(models[r]) for r in models}
    r0 = "001"
    para = sorted({a for a, b in per[r0]})
    # persistence of rank_001 pairs across all 5 models
    pers = {f"{a[0]}{a[1]:03d}|C{b[1]:03d}": sum((a, b) in per[r] for r in per) / 5.0 for (a, b) in per[r0]}
    # interface RMSD vs rank_001: align on antigen CA, RMSD over rank_001 paratope residue CAs
    ag0 = {k[1]: v for k, v in models[r0].items() if k[0] == "C"}
    def para_ca(res):
        return {k[1]: v for k, v in res.items() if k in set((('A', p) for p in range(1, 123))) or k in set((('B', p) for p in range(1, 107)))}
    rmsds = {}
    for r in sorted(models):
        if r == r0: continue
        agm = {k[1]: v for k, v in models[r].items() if k[0] == "C"}
        common = sorted(set(ag0) & set(agm))
        sup = SVDSuperimposer()
        sup.set(np.array([ag0[c] for c in common]), np.array([agm[c] for c in common]))
        sup.run(); rot, tran = sup.get_rotran()
        # rank_001 paratope CAs present in both
        keys = [k for k in para if k in models[r0] and k in models[r]]
        if not keys: rmsds[r] = None; continue
        A = np.array([models[r0][k] for k in keys])
        Bm = np.array([models[r][k] for k in keys]) @ rot.T + tran
        rmsds[r] = round(float(np.sqrt(((A - Bm) ** 2).sum(1).mean())), 2)
    out[C] = {
        "per_sample_pair_counts": {r: len(per[r]) for r in sorted(per)},
        "rank001_pairs": len(per[r0]),
        "rank001_pair_persistence": pers,
        "n_pairs_in_5_of_5": sum(1 for v in pers.values() if v == 1.0),
        "n_pairs_in_ge3_of_5": sum(1 for v in pers.values() if v >= 0.6),
        "interface_ca_rmsd_to_rank001_A": rmsds,
        "definition": "interface = CA-CA<6A pairs; persistence = fraction of the 5 AFM models containing each rank_001 pair; RMSD: align antigen CA, RMSD on rank_001 paratope CA atoms",
    }
    print(C, "pairs/model:", out[C]["per_sample_pair_counts"],
          "| persist>=3/5:", out[C]["n_pairs_in_ge3_of_5"], "/", len(pers),
          "| RMSD:", rmsds)
json.dump(out, open("/home/boltzmann10/.sci/cache/scratch/gal3bp_run/candidate_per_sample_persistence.json", "w"), indent=2)
print("wrote candidate_per_sample_persistence.json")
