#!/usr/bin/env python3
"""Verify AntiBMPNN edit mask + apply frozen gates + dedupe.

Skill-mandated check: for every candidate assert VL/VH byte-identity outside the declared mask
(position-by-position diff vs the submitted scaffold), lengths unchanged, mutations only inside
the mask. Report as N/N.
"""
import csv, json, os

OUT = '/home/boltzmann10/.sci/workspace/outputs/antibmpnn'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'

FR = json.load(open(f'{INP}/framework_table1.json'))['FR_blocks']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']
REF_VH, REF_VL = h965['VH'], h965['VL']  # scaffold submitted to AntiBMPNN = H965-layout Fv
MASK = {'H': [26,27,28,29,30,31,32,52,53,54,55,56,57,99,100,101,102,103,104,105,106],
        'L': [24,25,26,27,28,29,30,31,32,33,34,50,51,52,53,54,55,56,89,90,91,92,93,94,95,96,97,98]}

rows = list(csv.DictReader(open(f'{OUT}/antibmpnn_results.csv')))
print('rows:', len(rows))

n_pass_mask = 0
mask_failures = []
cands = []
for i, r in enumerate(rows):
    vh, vl = r['heavy_chain'].strip(), r['light_chain'].strip()
    ok = True
    if len(vh) != len(REF_VH) or len(vl) != len(REF_VL):
        ok = False; mask_failures.append((i, 'length changed'))
    else:
        for ch, ref, seq in (('H', REF_VH, vh), ('L', REF_VL, vl)):
            for p in range(1, len(ref) + 1):
                if seq[p - 1] != ref[p - 1] and p not in MASK[ch]:
                    ok = False; mask_failures.append((i, f'{ch}{p} mutated outside mask')); break
            if not ok: break
    if ok:
        n_pass_mask += 1
        cdrs = {'H1': vh[25:32], 'H2': vh[51:57], 'H3': vh[98:106],
                'L1': vl[23:34], 'L2': vl[49:56], 'L3': vl[88:98]}
        # framework byte-identity is guaranteed by mask+refs; verify explicitly:
        fr_ok = (vh[:25] == FR['FR-H1'] and vh[32:35] == 'AMS' and vh[35:51] == 'WVRQAPGKGLEWVSAI'
                 and vh[57:98] == FR['FR-H3'] and vh[106:] == FR['FR-H4']
                 and vl[:23] == FR['FR-L1'] and vl[34:49] == FR['FR-L2']
                 and vl[56:88] == FR['FR-L3'] and vl[98:] == FR['FR-L4'])
        assert fr_ok, f'row {i}: framework not byte-identical'
        cys = any('C' in v for v in cdrs.values())
        published = any(tuple(sorted(p['CDRs'].items())) == tuple(sorted(cdrs.items())) for p in panel.values())
        cands.append({'idx': i, 'VH': vh, 'VL': vl, 'CDRs': cdrs,
                      'cys_in_cdr': cys, 'published_duplicate': published})

print(f'edit-mask verification: {n_pass_mask}/{len(rows)}')

uniq, seen = [], set()
for c in cands:
    if (c['VH'], c['VL']) in seen: continue
    seen.add((c['VH'], c['VL'])); uniq.append(c)

eligible = [c for c in uniq if not c['cys_in_cdr'] and not c['published_duplicate']]
print(f'unique: {len(uniq)} | eligible (no Cys, novel): {len(eligible)}')
print('Cys-in-CDR dropped:', sum(c['cys_in_cdr'] for c in uniq),
      '| published duplicates:', sum(c['published_duplicate'] for c in uniq))
h3lens = sorted(len(c['CDRs']['H3']) for c in eligible)
print('H3 lengths:', h3lens)

json.dump({'pool': eligible, 'dropped_cys': [c['idx'] for c in uniq if c['cys_in_cdr']],
           'dropped_published': [c['idx'] for c in uniq if c['published_duplicate']],
           'mask_failures': mask_failures, 'mask_verified': f'{n_pass_mask}/{len(rows)}'},
          open(f'{RUN}/candidates/antibmpnn_pool.json', 'w'), indent=1)
