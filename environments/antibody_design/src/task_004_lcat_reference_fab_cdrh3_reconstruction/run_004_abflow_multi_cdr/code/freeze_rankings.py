#!/usr/bin/env python
"""
task_004: freeze candidate rankings BEFORE any native-reference scoring.

Ordering rule (frozen here, never changed afterwards):
  primary: pmets ascending (model mean NLL over H3 positions; lower = more
           confident sequence under the released model; pose-blind)
  tie-break: candidate_id ascending
Outputs run/<name>/shortlist_frozen.csv for every generation directory.
"""
import csv
import hashlib
import json
import os
import sys


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def freeze(gen_dir, protocol_label):
    rows = list(csv.DictReader(open(os.path.join(gen_dir, 'candidates.csv'))))
    for r in rows:
        r['pmets'] = float(r['pmets']) if r['pmets'] not in (None, '') else None
    # verify PDB hashes recorded at generation still match
    frz = json.load(open(os.path.join(gen_dir, 'generation_freeze.json')))
    mism = [cid for cid, h in frz['candidate_pdb_sha256'].items()
            if sha256(os.path.join(gen_dir, cid + '.pdb')) != h]
    if mism:
        raise SystemExit(f'hash mismatch after generation: {mism}')
    rows.sort(key=lambda r: (r['pmets'] if r['pmets'] is not None else 1e9, r['candidate_id']))
    out = os.path.join(gen_dir, 'shortlist_frozen.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['frozen_rank', 'candidate_id', 'pmets', 'h3_sequence', 'pdb_sha256'])
        for i, r in enumerate(rows, 1):
            h3 = r['heavy_sequence'][95:114]
            w.writerow([i, r['candidate_id'], r['pmets'], h3,
                        frz['candidate_pdb_sha256'][r['candidate_id']]])
    meta = {
        'protocol': protocol_label,
        'ranking_rule': 'pmets asc (model mean NLL, pose-blind), tie-break candidate_id',
        'frozen_at': __import__('time').strftime('%F %T'),
        'n': len(rows),
        'unique_h3': len(set(r['heavy_sequence'][95:114] for r in rows)),
        'hash_check': 'all candidate PDB sha256 verified against generation_freeze.json',
    }
    with open(os.path.join(gen_dir, 'freeze_record.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta))


if __name__ == '__main__':
    base = 'run_5bv7_abflow'
    # default: the two H3-track pools; extra pool dirs may be passed as args
    jobs = [
        (f'{base}/gen_1shot', 'AbFlow 1-shot, seed 2023 (paper Table 1 protocol)'),
        (f'{base}/gen_g30', 'AbFlow-G 30-sample pool, seed 20261114 (paper AbFlow-G protocol; 32 draws)'),
        (f'{base}/gen_mcdr_1shot', 'AbFlow multi-CDR 1-shot, seed 2023 (paper Table 2 protocol; declared separate track)'),
    ]
    extra = sys.argv[1:]
    if extra:
        jobs = [(d, f'extra pool {d}') for d in extra]
    for d, label in jobs:
        freeze(d, label)
