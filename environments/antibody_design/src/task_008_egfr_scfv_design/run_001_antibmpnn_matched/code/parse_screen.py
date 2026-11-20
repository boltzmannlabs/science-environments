#!/usr/bin/env python3
"""run_001_antibmpnn_matched stage 3a: parse AntiBMPNN results, verify CDR-only design, screen liabilities,
compute scFv records, and emit the shortlist for Boltz2 evaluation.
Outputs -> results/task_008_egfr_scfv_design/run_001_antibmpnn_matched/candidates.csv (+ shortlist.csv)
"""
import csv, hashlib, json, os, subprocess, sys

ENV = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{ENV}/src/task_008_egfr_scfv_design/run_001_antibmpnn_matched'
RAW = f'{RUN}/inputs/execution_records/raw/antibmpnn_out'
RES = f'{ENV}/results/task_008_egfr_scfv_design/run_001_antibmpnn_matched'
os.makedirs(RES, exist_ok=True)

REF = json.load(open(f'{RUN}/inputs/shared/reference.json'))
VH_REF, VL_REF, LINKER = REF['vh'], REF['vl'], REF['linker']
CDR_H = [(26, 32), (52, 56), (98, 108)]
CDR_L = [(24, 34), (50, 56), (89, 97)]
CDR_POS = (sorted(p for lo, hi in CDR_H for p in range(lo, hi + 1))
           + sorted(134 + p for lo, hi in CDR_L for p in range(lo, hi + 1)))  # scFv numbering
CANON_CYS = REF['canonical_cys_scfv']

gen = {r['sample']: r for r in csv.DictReader(open(f'{RAW}/antibmpnn_generation_metrics.csv'))}
rows = list(csv.DictReader(open(f'{RAW}/antibmpnn_results.csv')))
assert len(rows) == 20, len(rows)

def nxst_new(s, ref):
    def f(x): return {i + 1 for i in range(len(x) - 2) if x[i] == 'N' and x[i+1] != 'P' and x[i+2] in 'ST'}
    return sorted(f(s) - f(ref))

cands = []
seen = {}
for i, r in enumerate(rows, 1):
    vh, vl = r['heavy_chain'], r['light_chain']
    assert len(vh) == 119 and len(vl) == 107
    # framework preservation check
    fw_h_bad = [p for p in range(1, 120) if vh[p-1] != VH_REF[p-1] and not any(lo <= p <= hi for lo, hi in CDR_H)]
    fw_l_bad = [p for p in range(1, 108) if vl[p-1] != VL_REF[p-1] and not any(lo <= p <= hi for lo, hi in CDR_L)]
    assert not fw_h_bad and not fw_l_bad, f'sample {i} framework mutated: {fw_h_bad} {fw_l_bad}'
    scfv = vh + LINKER + vl
    muts_h = [(p, VH_REF[p-1], vh[p-1]) for p in range(1, 120) if vh[p-1] != VH_REF[p-1]]
    muts_l = [(134 + p, VL_REF[p-1], vl[p-1]) for p in range(1, 108) if vl[p-1] != VL_REF[p-1]]
    cys = [j + 1 for j, a in enumerate(scfv) if a == 'C']
    noncanon = [c for c in cys if c not in CANON_CYS]
    key = scfv
    dup = key in seen
    seen.setdefault(key, []).append(i)
    cands.append({
        'candidate_id': f'cet_008_r1_s{i:02d}', 'sample': i, 'duplicate_of': seen[key][0] if dup and seen[key][0] != i else '',
        'scfv': scfv, 'vh': vh, 'vl': vl,
        'antibmpnn_score': float(gen[str(i)]['score']),
        'antibmpnn_global_score': float(gen[str(i)]['global_score']),
        'antibmpnn_seq_recovery': float(gen[str(i)]['seq_recovery']),
        'n_mutations': len(muts_h) + len(muts_l),
        'mutations': ' '.join(f'{a}{p}{b}' for p, a, b in muts_h + muts_l),
        'mutations_in_cdr': all(any(lo <= (p if p <= 119 else p - 134) <= hi
                                    for lo, hi in (CDR_H if p <= 119 else CDR_L)) for p, _, _ in muts_h + muts_l),
        'cdr_recovery': 1 - (len(muts_h) + len(muts_l)) / len(CDR_POS),
        'full_recovery': sum(a == b for a, b in zip(scfv, REF['reference_scfv'])) / len(scfv),
        'nxst_new': ';'.join(map(str, nxst_new(scfv, REF['reference_scfv']))),
        'noncanonical_cys': ';'.join(map(str, noncanon)),
        'sha256_12': hashlib.sha256(scfv.encode()).hexdigest()[:12],
    })

# peptide properties (pI, MW) in igdesign env
tmp_in, tmp_out, calc = f'{RUN}/_pep_in.json', f'{RUN}/_pep_out.json', f'{RUN}/_pep_calc.py'
json.dump([{'id': c['candidate_id'], 'seq': c['scfv']} for c in cands], open(tmp_in, 'w'))
open(calc, 'w').write('''
import json, peptides, sys
items = json.load(open(sys.argv[1])); out = {}
for it in items:
    p = peptides.Peptide(it["seq"])
    out[it["id"]] = {"pI": p.isoelectric_point(), "MW_da": p.molecular_weight()}
json.dump(out, open(sys.argv[2], "w"))
''')
rp = subprocess.run(['/home/boltzmann10/anaconda3/envs/igdesign/bin/python', calc, tmp_in, tmp_out],
                    capture_output=True, text=True, timeout=600)
if rp.returncode != 0:
    print('peptides FAILED:', rp.stderr[-300:]); sys.exit(1)
pep = json.load(open(tmp_out))
for c in cands:
    c.update(pep[c['candidate_id']])

# ---- candidates.csv ----
cols = ['candidate_id', 'sample', 'duplicate_of', 'n_mutations', 'mutations', 'mutations_in_cdr',
        'cdr_recovery', 'full_recovery', 'antibmpnn_score', 'antibmpnn_global_score',
        'antibmpnn_seq_recovery', 'pI', 'MW_da', 'nxst_new', 'noncanonical_cys', 'sha256_12', 'vh', 'vl', 'scfv']
with open(f'{RES}/candidates.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    for c in cands:
        w.writerow(c)

# ---- shortlist: unique, clean (no new NxST, no noncanonical Cys), best antibmpnn score ----
uniq = [c for c in cands if not c['duplicate_of']]
clean = [c for c in uniq if not c['nxst_new'] and not c['noncanonical_cys']]
pool = clean if len(clean) >= 6 else uniq  # fall back to all uniques if too few clean
pool = sorted(pool, key=lambda c: c['antibmpnn_score'])[:6]
with open(f'{RES}/shortlist.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    for c in pool:
        w.writerow(c)

print(f'20 samples parsed; all framework-preserving; CDR-only confirmed: {all(c["mutations_in_cdr"] for c in cands)}')
print(f'unique: {len(uniq)}, clean: {len(clean)}')
print('shortlist (best antibmpnn score):')
for c in pool:
    print(f"  {c['candidate_id']} score {c['antibmpnn_score']:.3f} muts {c['n_mutations']} "
          f"cdr_rec {c['cdr_recovery']:.3f} pI {c['pI']:.2f} nxst={c['nxst_new'] or '-'} cys={c['noncanonical_cys'] or '-'}")
