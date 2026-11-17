#!/usr/bin/env python3
"""Verify agcdr-backbone AntiBMPNN masks + gates; build the combined candidate pool.

Mask check here: framework positions must be byte-identical to the Table-1 template (the
backbones came from agcdr_diff, whose framework was preserved; AntiBMPNN mask then restricts
edits to CDR positions). CDR regions may differ from H965 (new backbones).
"""
import csv, json, os
from collections import Counter

OUT = '/home/boltzmann10/.sci/workspace/outputs/antibmpnn_agcdr'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'

FR = json.load(open(f'{INP}/framework_table1.json'))['FR_blocks']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
published = {tuple(sorted(p['CDRs'].items())) for p in panel.values()}

rows = list(csv.DictReader(open(f'{OUT}/antibmpnn_results.csv')))
pool, fails = [], Counter()
for i, r in enumerate(rows):
    vh, vl = r['heavy_chain'].strip(), r['light_chain'].strip()
    if len(vh) != 117 or len(vl) != 108:
        fails['length'] += 1; continue
    cdrs = {'H1': vh[25:32], 'H2': vh[51:57], 'H3': vh[98:106],
            'L1': vl[23:34], 'L2': vl[49:56], 'L3': vl[88:98]}
    fr_ok = (vh[:25] == FR['FR-H1'] and vh[32:35] == 'AMS' and vh[35:51] == 'WVRQAPGKGLEWVSAI'
             and vh[57:98] == FR['FR-H3'] and vh[106:] == FR['FR-H4']
             and vl[:23] == FR['FR-L1'] and vl[34:49] == FR['FR-L2']
             and vl[56:88] == FR['FR-L3'] and vl[98:] == FR['FR-L4'])
    if not fr_ok:
        fails['framework'] += 1; continue
    if any('C' in v for v in cdrs.values()):
        fails['cys'] += 1; continue
    if tuple(sorted(cdrs.items())) in published:
        fails['published_dup'] += 1; continue
    pool.append({'tag': f"agcdr_{r['pdb_name'].replace('.pdb','')}_{i}", 'track': 'agcdr_diff+AntiBMPNN',
                 'VH': vh, 'VL': vl, 'CDRs': cdrs})

# dedupe
seen, uniq = set(), []
for c in pool:
    if (c['VH'], c['VL']) in seen: continue
    seen.add((c['VH'], c['VL'])); uniq.append(c)

json.dump({'pool': uniq, 'failures': dict(fails), 'n_rows': len(rows)},
          open(f'{RUN}/candidates/agcdr_pool.json', 'w'), indent=1)
print(f"rows {len(rows)} | gates passed {len(pool)} | unique {len(uniq)} | failures {dict(fails)}")
print('H3 length distribution:', Counter(len(c['CDRs']['H3']) for c in uniq))
print('distinct H3 seqs:', len(set(c['CDRs']['H3'] for c in uniq)),
      '| distinct L3:', len(set(c['CDRs']['L3'] for c in uniq)))
