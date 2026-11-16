#!/usr/bin/env python
"""Score run_002 (DiffAb grafted) and run_003 (AntiBMPNN native-backbone) with the
authors' cal_metrics evaluator; freeze rankings BEFORE scoring.

Frozen ranking rules (declared before scoring):
  run_002: DiffAb provides no per-sample confidence -> deterministic filename
           order (deterministic seeded sampling order). 32 candidates.
  run_003: AntiBMPNN model score ascending (tool's own FASTA-header confidence).
"""
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/boltzmann10/lcat_task004/AbFlow')
import os as _os
_os.chdir('/home/boltzmann10/lcat_task004/AbFlow')  # evaluator shells out to ./DockQ/DockQ.py relative to repo
from cal_metrics import cal_metrics  # authors' evaluator

WS = Path('/home/boltzmann10/lcat_task004')
DIFFAB = WS / 'run_5bv7_diffab'
BASE = WS / 'run_5bv7_abflow'


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def run_pool(tag, cand_entries, ref_pdb, H, L, A):
    gen_dir = DIFFAB / f'scored_{tag}'
    gen_dir.mkdir(exist_ok=True)
    out = []
    for rank, ent in enumerate(cand_entries, 1):
        m = cal_metrics([ent['pdb'], ref_pdb, H, L, A, ['H3']])
        m['frozen_rank'] = rank
        m['candidate_id'] = ent['candidate_id']
        m['pdb_sha256'] = sha256(ent['pdb'])
        out.append(m)
        print(tag, ent['candidate_id'], {k: (round(v, 4) if isinstance(v, float) else v)
              for k, v in m.items() if k in ('AAR H3', 'CAAR H3', 'RMSD(CA) CDRH3',
              'RMSD(CA) CDRH3 aligned', 'TMscore', 'LDDT', 'DockQ')}, flush=True)
    json.dump(out, open(gen_dir / 'metrics_per_candidate.json', 'w'), indent=2)
    return out


if __name__ == '__main__':
    ref_entry = json.loads(open(BASE / 'reference/native_5bv7.json').read())
    H, L, A = ref_entry['heavy_chain'], ref_entry['light_chain'], ref_entry['antigen_chains']
    ref_pdb = str((BASE / 'reference/native_5bv7.pdb').resolve())

    # run_002: grafted DiffAb, filename order = frozen order
    diffab_rows = json.load(open(DIFFAB / 'diffab_grafted_manifest.json'))
    for i, r in enumerate(diffab_rows, 1):
        r['frozen_rank'] = i
    json.dump(diffab_rows, open(DIFFAB / 'diffab_frozen_shortlist.json', 'w'), indent=2)
    r2 = run_pool('diffab', diffab_rows, ref_pdb, H, L, A)

    # run_003: AntiBMPNN, model-score ascending (already computed in prep)
    ab_rows = json.load(open(DIFFAB / 'antibmpnn_prep.json'))
    r3 = run_pool('antibmpnn', ab_rows, ref_pdb, H, L, A)

    # summary
    import numpy as np
    def summarize(rows, label):
        keys = ['AAR H3', 'CAAR H3', 'RMSD(CA) CDRH3', 'RMSD(CA) CDRH3 aligned',
                'RMSD(CA) aligned', 'TMscore', 'LDDT', 'DockQ']
        out = {'population': label, 'n': len(rows)}
        for k in keys:
            vals = [r[k] for r in rows if k in r and r[k] is not None]
            if vals:
                out[k] = {'mean': round(float(np.mean(vals)), 4), 'std': round(float(np.std(vals)), 4),
                          'min': round(float(np.min(vals)), 4), 'max': round(float(np.max(vals)), 4)}
        return out
    summary = {
        'diffab_grafted_n32': summarize(r2, 'DiffAb in-context H3 co-design, grafted onto native IMGT scaffold, n=32'),
        'antibmpnn_fixedbb_n32': summarize(r3, 'AntiBMPNN fixed-backbone H3 sequence design (Boltzmann platform), n=32'),
        'metric_definitions': json.load(open(BASE / 'metrics_summary.json'))['metric_definitions'],
        'evaluator_provenance': 'AbFlow repo @ df39b47, cal_metrics.cal_metrics (same evaluator as run_001/run_004)',
        'protocol_notes': {
            'diffab': 'DiffAb outputs Chothia-renumbered terminally-cropped complexes; evaluation models transplant the full-atom designed H3 block onto the native IMGT scaffold 1:1 by sequence position. ALL design content (H3 seq+structure+sidechains) is DiffAb-generated; framework/pose conditioning is the in-context protocol (native complex provided), declared separate from pose-blind AbFlow tracks.',
            'antibmpnn': 'AntiBMPNN designed H3 sequences on the native backbone (fixed-backbone track, user-authorized declared variant). Models = native complex with H3 residues mutated to designed sequence (backbone atoms + CB only). Sequence-recovery metrics are informative; RMSD/TM/lDDT/DockQ are structural-trivial (backbone native) and reported as such.',
        },
    }
    json.dump(summary, open(DIFFAB / 'runs23_metrics_summary.json', 'w'), indent=2)
    print('DONE')
