#!/usr/bin/env python
"""
task_004: 5bv7 CDR-H3 reconstruction via AbFlow released checkpoint.

Stage 1 (this script): generation ONLY.
  - loads paratope_centric_design.ckpt (H3 co-design, pose-blind cmask)
  - dataset = masked 5bv7 entry (native H3 seq removed) x N replicates
  - writes candidate PDBs + candidate table (id, H3 seq, full seqs, pmets)
Generation happens BEFORE any native-reference scoring (freeze protocol).
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader


def setup_imports(abflow_repo):
    sys.path.insert(0, str(abflow_repo))
    os.chdir(abflow_repo)
    from data.dataset import E2EDataset
    from generate import to_cplx
    from utils.random_seed import setup_seed
    return E2EDataset, to_cplx, setup_seed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--test-set', required=True, help='masked input json (xN replicate file)')
    ap.add_argument('--save-dir', required=True)
    ap.add_argument('--surf-file', required=True)
    ap.add_argument('--pep-file', required=True)
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--seed', type=int, default=2023)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--batch-size', type=int, default=8)
    args = ap.parse_args()

    args.test_set = str(Path(args.test_set).resolve())
    args.surf_file = str(Path(args.surf_file).resolve())
    args.pep_file = str(Path(args.pep_file).resolve())
    args.ckpt = str(Path(args.ckpt).resolve())
    args.save_dir = str(Path(args.save_dir).resolve())

    repo = Path(args.repo).resolve()
    E2EDataset, to_cplx, setup_seed = setup_imports(repo)
    setup_seed(args.seed)

    save_dir = Path(args.save_dir).resolve()
    save_dir.mkdir(parents=True, exist_ok=True)

    model = torch.load(args.ckpt, map_location='cpu', weights_only=False)
    if not hasattr(model, 'pep_seq'):
        model.pep_seq = True
    if not hasattr(model, 'pep_struct'):
        model.pep_struct = True
    device = torch.device(f'cuda:{args.gpu}' if args.gpu >= 0 else 'cpu')
    model.to(device)
    model.eval()
    print(f'model: {type(model).__name__} cdr_type={model.cdr_type} paratope={model.paratope}', flush=True)

    dataset = E2EDataset(
        args.test_set,
        save_dir=str(save_dir / 'processed'),
        pep_file=args.pep_file,
        surf_file=args.surf_file,
        cdr=model.cdr_type,
        paratope=model.paratope,
    )
    loader = DataLoader(dataset, batch_size=args.batch_size, num_workers=0,
                        collate_fn=E2EDataset.collate_fn)

    rows = []
    idx = 0
    t0 = time.time()
    for batch in tqdm_notebook_free(loader):
        with torch.no_grad():
            for k in batch:
                if hasattr(batch[k], 'to'):
                    batch[k] = batch[k].to(device)
            batch.pop('xloss_mask', None)
            X, S, pmets = model.sample(**batch)
            X, S, pmets = X.tolist(), S.tolist(), pmets.tolist()
        X_list, S_list = [], []
        lengths = batch['lengths']
        batch_id = torch.zeros_like(torch.tensor(S))
        batch_id[torch.cumsum(lengths, dim=0)[:-1]] = 1
        batch_id = batch_id.cumsum(dim=0).tolist()
        cur = -1
        for x, s, bid in zip(X, S, batch_id):
            if bid != cur:
                cur = bid
                X_list.append([])
                S_list.append([])
            X_list[-1].append(x)
            S_list[-1].append(s)
        for i, (x, s) in enumerate(zip(X_list, S_list)):
            ori = dataset.data[idx]
            cplx = to_cplx(ori, x, s)
            cid = f'5bv7_h3_{idx:03d}'
            pdb_path = save_dir / f'{cid}.pdb'
            cplx.to_pdb(str(pdb_path))
            # pmets is per batch ITEM (len = batch size), not global idx
            pmets_val = pmets[i] if i < len(pmets) else None
            rows.append({
                'candidate_id': cid,
                'pdb': str(pdb_path),
                'heavy_sequence': cplx.get_heavy_chain().get_seq(),
                'light_sequence': cplx.get_light_chain().get_seq(),
                'pmets': pmets_val,
            })
            idx += 1
        print(f'[{time.time()-t0:.1f}s] {idx} samples done', flush=True)

    with open(save_dir / 'candidates.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['candidate_id', 'pdb', 'heavy_sequence', 'light_sequence', 'pmets'])
        w.writeheader()
        w.writerows(rows)
    # freeze record
    import hashlib
    def sha(p):
        h = hashlib.sha256()
        with open(p, 'rb') as fh:
            for c in iter(lambda: fh.read(1 << 20), b''):
                h.update(c)
        return h.hexdigest()
    freeze = {
        'n_candidates': len(rows),
        'seed': args.seed,
        'ckpt': str(args.ckpt),
        'generated_at': time.strftime('%F %T'),
        'candidate_pdb_sha256': {r['candidate_id']: sha(r['pdb']) for r in rows},
        'ranking_rule': 'model pmets (mean NLL of H3 seq under model, lower=better) frozen BEFORE native scoring',
    }
    with open(save_dir / 'generation_freeze.json', 'w') as f:
        json.dump(freeze, f, indent=2)
    print(json.dumps({k: v for k, v in freeze.items() if k != 'candidate_pdb_sha256'}, indent=2))


def tqdm_notebook_free(x):
    try:
        from tqdm import tqdm
        return tqdm(x)
    except ImportError:
        return x


if __name__ == '__main__':
    main()
