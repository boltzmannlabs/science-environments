#!/usr/bin/env python
"""
task_004: evaluate frozen candidates against the held-out 5bv7 native reference
using the AbFlow authors' own evaluation stack (cal_metrics.py functions):
  AAR/CAAR (H3), whole-antibody CA RMSD (un-aligned), CDR-H3 CA RMSD
  (Kabsch-aligned), TMscore, lDDT, DockQ (cdrh3_only, HERN-consistent).
Runs as a module inside the AbFlow repo:  python -m score_candidates ...
"""
import csv
import json
import os
import pickle
import sys
import time
from pathlib import Path

REPO = Path('/home/boltzmann10/lcat_task004/AbFlow').resolve()
sys.path.insert(0, str(REPO))
os.chdir(REPO)

from cal_metrics import cal_metrics  # authors' per-item evaluator


def main():
    base = Path('/home/boltzmann10/lcat_task004/run_5bv7_abflow')

    # ---------------------------------------------------------------- native reference (held out until now)
    ref_entry = json.loads(open(base / 'reference/native_5bv7.json').read())
    H, L, A = ref_entry['heavy_chain'], ref_entry['light_chain'], ref_entry['antigen_chains']
    ref_pdb = str((base / 'reference/native_5bv7.pdb').resolve())

    results = {}
    for run in ['gen_1shot', 'gen_g30', 'gen_mcdr_1shot']:
        gen_dir = base / run
        rows = list(csv.DictReader(open(gen_dir / 'candidates.csv')))
        frozen = list(csv.DictReader(open(gen_dir / 'shortlist_frozen.csv')))
        frozen_order = {r['candidate_id']: int(r['frozen_rank']) for r in frozen}
        out_rows = []
        for r in rows:
            cid = r['candidate_id']
            t0 = time.time()
            m = cal_metrics([
                os.path.join(gen_dir, cid + '.pdb'),  # mod_pdb
                ref_pdb,                              # ref_pdb
                H, L, A,                              # chains
                ['H3'],                               # cdr_type
            ])
            m['frozen_rank'] = frozen_order[cid]
            m['candidate_id'] = cid
            m['pdb_sha256'] = sha256(os.path.join(gen_dir, cid + '.pdb'))
            m['seconds'] = round(time.time() - t0, 1)
            out_rows.append(m)
            print(run, cid, json.dumps({k: round(v, 4) if isinstance(v, float) else v
                                         for k, v in m.items() if k not in ('pdb_sha256',)}), flush=True)
        with open(gen_dir / 'metrics_per_candidate.json', 'w') as f:
            json.dump(out_rows, f, indent=2)
        results[run] = out_rows

    # ---------------------------------------------------------------- summary
    def summarize(rows, label):
        import numpy as np
        keys = ['AAR H3', 'CAAR H3', 'AAR', 'CAAR', 'RMSD(CA) aligned', 'RMSD(CA) CDRH3',
                'RMSD(CA) CDRH3 aligned', 'TMscore', 'LDDT', 'DockQ']
        out = {'population': label, 'n': len(rows)}
        for k in keys:
            vals = [r[k] for r in rows if k in r and r[k] is not None]
            if vals:
                out[k] = {'mean': round(float(np.mean(vals)), 4), 'std': round(float(np.std(vals)), 4),
                          'min': round(float(np.min(vals)), 4), 'max': round(float(np.max(vals)), 4)}
        return out

    summary = {
        'one_shot': summarize(results['gen_1shot'], 'AbFlow 1-shot, seed 2023 (paper Table 1 protocol)'),
        'abflow_g30': summarize(results['gen_g30'], 'AbFlow-G 32-draw pool, seed 20261114 (1-shot mean over pool)'),
        'multi_cdr_1shot': summarize(results['gen_mcdr_1shot'], 'AbFlow multi-CDR 1-shot, seed 2023 (paper Table 2 protocol; declared separate track)'),
        'metric_definitions': {
            'AAR H3': 'CDR-H3 identity fraction, positions 95-113 (19 aa) of heavy chain, authors cal_metrics',
            'CAAR H3': 'AAR restricted to H3 residues in antigen contact (<6.6 A any-atom) in native',
            'RMSD(CA) aligned': 'whole-antibody (VH+VL) CA RMSD AFTER Kabsch superposition (compute_rmsd aligned=False applies kabsch)',
            'RMSD(CA) CDRH3': 'CDR-H3 CA RMSD in complex frame WITHOUT superposition (compute_rmsd aligned=True skips kabsch) — paper Appendix C Table-1 RMSD definition',
            'RMSD(CA) CDRH3 aligned': 'CDR-H3 CA RMSD after Kabsch superposition of the loop itself',
            'TMscore': 'TM-score of antibody (H+L merged), TMscore binary in repo',
            'LDDT': 'lDDT of antibody vs native, lddt binary (-x); agreement-to-reference, NOT predicted confidence',
            'DockQ': 'DockQ v1 (repo binary) on antigen vs CDR-H3-only reduced complex (cdrh3_only=True, HERN-consistent)',
        },
        'evaluator_provenance': 'AbFlow repo @ df39b47, cal_metrics.cal_metrics, evaluation/{tm_score,lddt,bak_dockq}.py',
    }
    with open(base / 'metrics_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


def sha256(p):
    h = __import__('hashlib').sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


if __name__ == '__main__':
    main()
