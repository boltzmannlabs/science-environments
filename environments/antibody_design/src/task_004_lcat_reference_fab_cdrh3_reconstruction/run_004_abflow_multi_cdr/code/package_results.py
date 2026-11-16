#!/usr/bin/env python
"""Package task_004 deliverables into the repo results tree."""
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

BASE = Path('/home/boltzmann10/lcat_task004/run_5bv7_abflow')
REPO_RESULTS = Path('/home/boltzmann10/new_agent_scienece_env/science-environments/'
                    'environments/antibody_design/results/task_004_lcat_reference_fab_cdrh3_reconstruction')
BUNDLE = REPO_RESULTS / 'lcat_results'
BUNDLE.mkdir(parents=True, exist_ok=True)
(BUNDLE / 'structures').mkdir(exist_ok=True)
(BUNDLE / 'raw').mkdir(exist_ok=True)

REF = json.loads(open(BASE / 'reference/native_5bv7.json').read())
NATIVE_H3 = REF['heavy_chain_seq'][95:114]
PAPER = {  # published aggregates, benchmark md (AbFlow KDD 2026, Tables 1-2)
    'AAR': (0.4234, 0.1334), 'TMscore': (0.9736, 0.0090), 'lDDT': (0.8522, 0.0216),
    'CAAR': (0.2824, 0.2037), 'RMSD': (8.25, 4.55), 'DockQ': (0.423, 0.161),
}

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

# ---------------------------------------------------------------- gather
pools = {}
for run, label in [
    ('gen_1shot', 'abflow_1shot_seed2023'),
    ('gen_g30', 'abflow_g30_seed20261114'),
]:
    cands = list(csv.DictReader(open(BASE / run / 'candidates.csv')))
    frozen = list(csv.DictReader(open(BASE / run / 'shortlist_frozen.csv')))
    metrics = json.load(open(BASE / run / 'metrics_per_candidate.json'))
    mby = {m['candidate_id']: m for m in metrics}
    fby = {f['candidate_id']: f for f in frozen}
    rows = []
    for c in cands:
        cid = c['candidate_id']
        m, f = mby[cid], fby[cid]
        h3 = c['heavy_sequence'][95:114]
        rows.append({
            'candidate_id': cid, 'protocol': label,
            'frozen_rank': int(f['frozen_rank']),
            'h3_designed': h3,
            'h3_native_matches': sum(a == b for a, b in zip(h3, NATIVE_H3)),
            'pmets': float(c['pmets']),
            'AAR_H3': round(m['AAR H3'], 4),
            'CAAR_H3': round(m['CAAR H3'], 4),
            'RMSD_CA_H3_inplace_A': round(m['RMSD(CA) CDRH3'], 3),
            'RMSD_CA_H3_kabsch_A': round(m['RMSD(CA) CDRH3 aligned'], 3),
            'RMSD_CA_antibody_kabsch_A': round(m['RMSD(CA) aligned'], 3),
            'TMscore': round(m['TMscore'], 4),
            'lDDT': round(m['LDDT'], 4),
            'DockQ_v1_cdrh3': round(m['DockQ'], 4),
            'pdb_sha256': f['pdb_sha256'],
            'heavy_sequence_sha256': hashlib.sha256(c['heavy_sequence'].encode()).hexdigest(),
            'light_sequence_sha256': hashlib.sha256(c['light_sequence'].encode()).hexdigest(),
        })
    pools[label] = rows

# ---------------------------------------------------------------- designed_sequences.fasta
with open(BUNDLE / 'designed_sequences.fasta', 'w') as f:
    seen = set()
    for label, run in [('abflow_1shot_seed2023', 'gen_1shot'), ('abflow_g30_seed20261114', 'gen_g30')]:
        cands = {c['candidate_id']: c for c in csv.DictReader(open(BASE / run / 'candidates.csv'))}
        for r in pools[label]:
            key = r['heavy_sequence_sha256']
            if key in seen:
                continue
            seen.add(key)
            hv = cands[r['candidate_id']]['heavy_sequence']
            lv = cands[r['candidate_id']]['light_sequence']
            f.write(f">{r['candidate_id']}|{r['protocol']}|frozen_rank={r['frozen_rank']}|chain=H\n{hv}\n")
            f.write(f">{r['candidate_id']}|{r['protocol']}|frozen_rank={r['frozen_rank']}|chain=L\n{lv}\n")

# ---------------------------------------------------------------- metrics.json
import numpy as np
def pool_stats(rows):
    out = {}
    for k in ['AAR_H3', 'CAAR_H3', 'RMSD_CA_H3_inplace_A', 'RMSD_CA_H3_kabsch_A',
              'RMSD_CA_antibody_kabsch_A', 'TMscore', 'lDDT', 'DockQ_v1_cdrh3']:
        v = [r[k] for r in rows]
        out[k] = {'mean': round(float(np.mean(v)), 4), 'std': round(float(np.std(v)), 4),
                  'min': round(float(np.min(v)), 4), 'max': round(float(np.max(v)), 4)}
    return out

metrics_doc = {
    'task': 'task_004_lcat_reference_fab_cdrh3_reconstruction',
    'target': {'pdb': '5BV7', 'antigen': 'human LCAT (L4F/N5D construct), chain A',
               'heavy': 'chain C (27C3 Fab1 heavy)', 'light': 'chain B (27C3 Fab1 light)',
               'native_cdr_h3': NATIVE_H3, 'cdr_h3_positions': 'IMGT-masked heavy positions 95-113 (19 aa, dataset entry)'},
    'generation': {
        'method': 'AbFlow paratope-centric CDR-H3 co-design (authors-released checkpoint paratope_centric_design.ckpt, repo commit df39b47)',
        'input_isolation': 'native CDR-H3 sequence removed from design input; sampler noise-initializes H3 sequence and coordinates (init_interface); whole-antibody coordinates regenerated (cmask); antigen chain A + released epitope surface features as conditioning',
        'protocols': {
            'abflow_1shot_seed2023': {'n': 1, 'seed': 2023, 'description': 'paper Table 1 1-shot protocol, authors default seed'},
            'abflow_g30_seed20261114': {'n': 32, 'seed': 20261114, 'description': 'paper AbFlow-G multi-sample protocol (30 samples; 32 draws run)'},
            'abflow_pool_seed2023': {'n': 32, 'seed': 2023, 'description': 'diagnostic repeat pool (seed stability)'},
        },
        'freeze': 'rankings frozen by model pmets (mean NLL of designed H3, pose-blind) BEFORE any native-reference scoring; candidate PDB sha256 recorded at generation and re-verified at freeze',
    },
    'evaluation': {
        'evaluator': 'AbFlow authors cal_metrics.cal_metrics (repo df39b47), unmodified',
        'metric_definitions': {
            'AAR_H3': 'identity fraction over the 19 CDR-H3 positions (heavy 95-113), length mismatch scores 0',
            'CAAR_H3': 'AAR restricted to native CDR-H3 residues with any-atom antigen distance < 6.6 A (CONTACT_DIST)',
            'RMSD_CA_H3_inplace_A': 'CA RMSD of CDR-H3 in complex frame WITHOUT superposition — the paper Appendix C Table-1 RMSD definition',
            'RMSD_CA_H3_kabsch_A': 'CA RMSD of CDR-H3 after Kabsch superposition of the loop itself',
            'RMSD_CA_antibody_kabsch_A': 'whole-antibody (VH+VL) CA RMSD after Kabsch superposition',
            'TMscore': 'TM-score antibody vs native (authors TMscore binary)',
            'lDDT': 'lDDT antibody vs native (lddt binary -x); agreement-to-reference, NOT predicted confidence',
            'DockQ_v1_cdrh3': 'DockQ v1 on reduced [antigen + CDR-H3] complex, cdrh3_only=True (HERN-consistent), authors DockQ build',
        },
        'reference': 'held-out native 5bv7 dataset entry + IMGT-renumbered PDB (sha256 in reference/freeze_manifest.json), unsealed only after generation freeze',
    },
    'constraint_compliance': {
        'framework_preserved': 'VH positions outside 95-113 byte-identical to native in all 65 candidates',
        'light_chain_preserved': 'VL byte-identical to native in all 65 candidates',
        'h3_length_conserved': '19/19 aa in all candidates (no indels)',
        'native_copy_check': '0 exact native CDR-H3 copies among candidates',
        'pairing': 'VH/VL pairing preserved per candidate (single paired design per draw)',
    },
    'candidates': {label: rows for label, rows in pools.items()},
    'pool_statistics': {label: pool_stats(rows) for label, rows in pools.items()},
    'provenance': {
        'generation_workspace': '/home/boltzmann10/lcat_task004 (scripts: build_run.py, generate_candidates.py, freeze_rankings.py, score_candidates.py)',
        'abflow_repo': 'authors github.com/wenda8759/AbFlow @ df39b47 (local copy), checkpoints from HF wenda8759/AbFlow',
        'dataset': 'authors-released RAbD test.json/test.pkl/test_surf.pkl (HF datasets.zip), 5bv7 entry, cluster 3sm5 held out of train/valid (verified)',
    },
}
with open(BUNDLE / 'metrics.json', 'w') as f:
    json.dump(metrics_doc, f, indent=2)

# ---------------------------------------------------------------- shortlist.csv
with open(BUNDLE / 'shortlist.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['frozen_rank', 'candidate_id', 'protocol', 'h3_designed', 'pmets_model_nll',
                'eligibility', 'eligibility_reason'])
    for label in ['abflow_1shot_seed2023', 'abflow_g30_seed20261114']:
        for r in sorted(pools[label], key=lambda x: x['frozen_rank']):
            w.writerow([r['frozen_rank'], r['candidate_id'], label, r['h3_designed'], r['pmets'],
                        'eligible', 'mask-compliant: framework+VL preserved, H3 length 19, not a native copy'])

# ---------------------------------------------------------------- benchmark_comparison.csv
one = pools['abflow_1shot_seed2023'][0]
g30 = pool_stats(pools['abflow_g30_seed20261114'])
rows = [
    ['AAR', f"{PAPER['AAR'][0]} ± {PAPER['AAR'][1]}", 'published 60-case aggregate mean±SD (Table 1)',
     str(one['AAR_H3']), f"{g30['AAR_H3']['mean']} ± {g30['AAR_H3']['std']} (n=32)",
     'not comparable as reproduction: single case vs 60-case aggregate; single-case value within paper SD'],
    ['CAAR', f"{PAPER['CAAR'][0]} ± {PAPER['CAAR'][1]}", 'published 60-case aggregate mean±SD (Table 1)',
     str(one['CAAR_H3']), f"{g30['CAAR_H3']['mean']} ± {g30['CAAR_H3']['std']} (n=32)",
     'not comparable as reproduction: single case vs aggregate; 0.333 above aggregate mean but inside SD'],
    ['TMscore', f"{PAPER['TMscore'][0]} ± {PAPER['TMscore'][1]}", 'published 60-case aggregate mean±SD (Table 1)',
     str(one['TMscore']), f"{g30['TMscore']['mean']} ± {g30['TMscore']['std']} (n=32)",
     'not comparable as reproduction: single case; value ~0.9σ below aggregate mean'],
    ['lDDT', f"{PAPER['lDDT'][0]} ± {PAPER['lDDT'][1]}", 'published 60-case aggregate mean±SD (Table 1)',
     str(one['lDDT']), f"{g30['lDDT']['mean']} ± {g30['lDDT']['std']} (n=32)",
     'not comparable as reproduction: single case; value ~1.9σ below aggregate mean'],
    ['RMSD (Appendix C: in-place CDR-H3 CA, no Kabsch)', f"{PAPER['RMSD'][0]} ± {PAPER['RMSD'][1]}",
     'published 60-case aggregate mean±SD (Table 1); Section 5.2 wording differs (alignment of CDR-H3 region)',
     f"{one['RMSD_CA_H3_inplace_A']}", f"{g30['RMSD_CA_H3_inplace_A']['mean']} ± {g30['RMSD_CA_H3_inplace_A']['std']} (n=32)",
     'not comparable as reproduction: single case, 1.4σ above aggregate mean; paper RMSD definition discrepancy (5.2 vs Appendix C) unresolved — both variants reported'],
    ['RMSD (Kabsch CDR-H3 CA)', 'not published separately', '—',
     str(one['RMSD_CA_H3_kabsch_A']), f"{g30['RMSD_CA_H3_kabsch_A']['mean']} ± {g30['RMSD_CA_H3_kabsch_A']['std']} (n=32)",
     'supplementary local-loop metric'],
    ['RMSD (Kabsch whole-antibody CA)', 'not published separately', '—',
     str(one['RMSD_CA_antibody_kabsch_A']), f"{g30['RMSD_CA_antibody_kabsch_A']['mean']} ± {g30['RMSD_CA_antibody_kabsch_A']['std']} (n=32)",
     'supplementary global-fold metric'],
    ['DockQ', f"{PAPER['DockQ'][0]} ± {PAPER['DockQ'][1]}", 'published 60-case aggregate mean±SD (Table 1, DockQ v1 cdrh3_only)',
     str(one['DockQ_v1_cdrh3']), f"{g30['DockQ_v1_cdrh3']['mean']} ± {g30['DockQ_v1_cdrh3']['std']} (n=32)",
     'not comparable as reproduction: single case far above aggregate mean (DockQ is the highest-variance metric); same evaluator code as paper'],
    ['Multi-CDR RMSD H3 (Table 2)', '1.83', 'published aggregate, multi-CDR design track',
     'NOT RUN', 'NOT RUN', 'out of scope: task forbids six-CDR design without a separate declared track'],
    ['Full-atom RMSD/TM/lDDT/DockQ (Table 2)', '1.102 / 0.9707 / 0.8151 / 0.431', 'published aggregate, full-atom design track',
     'NOT RUN', 'NOT RUN', 'out of scope: separate evaluation track (multi_cdr/full-atom design)'],
]
with open(BUNDLE / 'benchmark_comparison.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['metric', 'published_value', 'published_scope',
                'this_run_5bv7_1shot', 'this_run_5bv7_pool_n32', 'comparability_decision'])
    w.writerows(rows)

# ---------------------------------------------------------------- structures + raw
for label, run in [('abflow_1shot_seed2023', 'gen_1shot'), ('abflow_g30_seed20261114', 'gen_g30')]:
    src = BASE / run
    for p in src.glob('*.pdb'):
        shutil.copy2(p, BUNDLE / 'structures' / f'{label}__{p.name}')
    for fn in ['generation_freeze.json', 'freeze_record.json', 'shortlist_frozen.csv', 'candidates.csv', 'metrics_per_candidate.json']:
        shutil.copy2(src / fn, BUNDLE / 'raw' / f'{label}__{fn}')
shutil.copy2(BASE / 'reference' / 'native_5bv7.pdb', BUNDLE / 'structures' / 'native_5bv7_reference.pdb')
shutil.copy2(BASE / 'reference' / 'freeze_manifest.json', BUNDLE / 'raw' / 'reference_freeze_manifest.json')
shutil.copy2(BASE / 'reference' / 'native_5bv7.json', BUNDLE / 'raw' / 'native_5bv7_dataset_entry.json')
shutil.copy2(BASE / 'metrics_summary.json', BUNDLE / 'raw' / 'metrics_summary.json')

# checksum manifest
manifest = {}
for p in sorted(BUNDLE.rglob('*')):
    if p.is_file():
        manifest[str(p.relative_to(BUNDLE))] = sha256(p)
with open(BUNDLE / 'CHECKSUMS.sha256', 'w') as f:
    for k, v in manifest.items():
        f.write(f'{v}  {k}\n')
print('packaged', len(manifest), 'files into', BUNDLE)
