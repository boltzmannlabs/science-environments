#!/usr/bin/env python
"""
task_004 LCAT reference Fab CDR-H3 reconstruction — run builder.

Creates a pose/sequence-blind design input bundle for 5bv7 (AbFlow RAbD test entry)
and replicates it N times for multi-sample generation, WITHOUT touching the native
CDR-H3 sequence or coordinates:

  run_dir/
    input/test_5bv7.json        # masked design input (native H3 seq REMOVED)
    input/test_5bv7_xN.json     # N replicated entries (distinct pdb ids) for batch sampling
    input/summary.tsv           # provenance of inputs
    reference/                  # HELD-OUT native record (sealed until freeze)

Masking implemented on the dataset record:
  - cdrh3_seq field dropped (sequence blind)
  - 'cdr' field set to 'H3' (E2EDataset masks H3 smask positions)
  - native PDB coordinates never exposed to generation (cmask=1 whole antibody;
    init_interface noise-initializes the H3 paratope).
The reference directory keeps the untouched test.json entry + native PDB with
sha256 checksums, and is not read by any generation code path.
"""
import hashlib
import json
import os
import shutil
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    repo = os.path.realpath('AbFlow')
    run_root = sys.argv[1] if len(sys.argv) > 1 else 'run_5bv7_abflow'
    n_rep = int(sys.argv[2]) if len(sys.argv) > 2 else 32

    test_json = os.path.join(repo, 'all_data/RAbD/test.json')
    entries = [json.loads(l) for l in open(test_json)]
    e5 = [e for e in entries if e['pdb'] == '5bv7'][0]

    os.makedirs(os.path.join(run_root, 'input'), exist_ok=True)
    os.makedirs(os.path.join(run_root, 'reference'), exist_ok=True)

    # ---- masked design input -------------------------------------------------
    masked = dict(e5)
    masked.pop('cdrh3_seq', None)          # sequence blind
    masked['cdr'] = 'H3'                    # smask restricted to H3 (dataset.py)
    masked['note'] = ('masked design input for task_004: native CDR-H3 sequence removed; '
                      'generation masks H3 sequence and full antibody coordinates')
    input_path = os.path.join(run_root, 'input', 'test_5bv7.json')
    with open(input_path, 'w') as f:
        f.write(json.dumps(masked) + '\n')

    # ---- replicated dataset for batched sampling ------------------------------
    rep_entries = []
    for i in range(n_rep):
        e = dict(masked)
        e['pdb'] = f'5bv7' if i == 0 else f'5bv7'  # pdb id must stay 4-char; keep same id
        rep_entries.append(e)
    rep_path = os.path.join(run_root, 'input', 'test_5bv7_xN.json')
    with open(rep_path, 'w') as f:
        f.writelines(json.dumps(e) + '\n' for e in rep_entries)

    # ---- held-out reference (sealed) ------------------------------------------
    ref_entry_path = os.path.join(run_root, 'reference', 'native_5bv7.json')
    shutil.copy2(test_json, os.path.join(run_root, 'reference', 'test_full.json'))
    with open(ref_entry_path, 'w') as f:
        f.write(json.dumps(e5) + '\n')
    shutil.copy2(os.path.join(repo, 'datasets/pdb/5bv7.pdb'),
                 os.path.join(run_root, 'reference', 'native_5bv7.pdb'))

    manifest = {
        'native_entry_sha256': sha256(ref_entry_path),
        'native_pdb_sha256': sha256(os.path.join(run_root, 'reference', 'native_5bv7.pdb')),
        'masked_input_sha256': sha256(input_path),
        'replicated_input_sha256': sha256(rep_path),
        'n_replicates': n_rep,
        'mask_definition': {
            'sequence_mask': 'cdrh3_seq removed from input; smask = H3 only',
            'coordinate_mask': 'cmask = full antibody; native pose withheld (init_interface noise init)',
            'antigen_conditioning': 'antigen chain A coordinates + released surface features (test_surf.pkl)',
        },
    }
    with open(os.path.join(run_root, 'reference', 'freeze_manifest.json'), 'f'.replace('f', 'w')) as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
