#!/usr/bin/env python3
"""Select 5 distinct candidates for Boltz2 complex-plausibility screening.

Rule (declared before any complex scores exist): dedupe by CDR sequence; greedy max-min Hamming
distance on the concatenated six CDRs (all candidates share CDR lengths, so Hamming is exact);
seed = candidate with maximum summed distance to pool medoid. H965 added as reference control.
"""
import json

BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'

pool = json.load(open(f'{RUN}/candidates/agcdr_pool.json'))['pool']
print('pool:', len(pool))

def concat(c):
    d = c['CDRs']
    return d['H1'] + d['H2'] + d['H3'] + d['L1'] + d['L2'] + d['L3']

def ham(a, b):
    return sum(x != y for x, y in zip(a, b))

strs = [concat(c) for c in pool]
# medoid = min summed distance
medoid = min(range(len(pool)), key=lambda i: sum(ham(strs[i], strs[j]) for j in range(len(pool))))
# seed selection = farthest from medoid
sel = [max(range(len(pool)), key=lambda i: ham(strs[i], strs[medoid]))]
while len(sel) < 5:
    best, best_d = None, -1
    for i in range(len(pool)):
        if i in sel: continue
        d = min(ham(strs[i], strs[j]) for j in sel)
        if d > best_d:
            best_d, best = d, i
    sel.append(best)

selected = [pool[i] | {'selection_rank': k + 1, 'min_cdr_hamming_to_other_selected': None}
            for k, i in enumerate(sel)]
for k in range(len(selected)):
    others = [j for j in range(len(selected)) if j != k]
    selected[k]['min_cdr_hamming_to_other_selected'] = min(
        ham(strs[sel[k]], strs[sel[j]]) for j in others)

json.dump({'selected': selected, 'control': 'Anti-PD1-H965'},
          open(f'{RUN}/candidates/screening_selection.json', 'w'), indent=1)
for c in selected:
    print(f"rank {c['selection_rank']}: H3={c['CDRs']['H3']} L3={c['CDRs']['L3']} minH={c['min_cdr_hamming_to_other_selected']}")
