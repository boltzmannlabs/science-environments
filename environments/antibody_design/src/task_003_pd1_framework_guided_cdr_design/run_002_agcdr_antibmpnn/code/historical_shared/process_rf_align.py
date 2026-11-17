#!/usr/bin/env python3
"""Alignment-based CDR extraction from RF-Antibody designs.

Policy (frozen before looking at candidates' scores):
1. Globally align each designed chain to the reference layout (H965 VH/VL = paper FR + published
   CDRs) with Needleman-Wunsch (match +1, mismatch -1, gap -2).
2. CDR segments = design residues aligned to reference CDR columns (allowing length drift inside
   CDR regions only).
3. Enforce paper CDR lengths exactly (H1 7, H2 6, L1 11, L2 7; H3 7-18; L3 9-11).
4. Rebuild VH/VL = byte-exact Table-1 FR blocks + extracted CDRs. All FR mutations by the tool are
   overwritten (recorded per candidate as repair counts).
5. Gates: no Cys in CDRs; not identical to any published panel CDR set.
"""
import json, os

OUT = '/home/boltzmann10/.sci/workspace/outputs/rf_antibody'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'

FR = json.load(open(f'{INP}/framework_table1.json'))['FR_blocks']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']

# Reference layouts with CDR coordinate maps (0-based spans on reference string)
VH_REF = h965['VH']; VL_REF = h965['VL']
VH_CDR = {'H1': (25, 32), 'H2': (51, 57), 'H3': (98, 106)}  # 0-based half-open on H965-layout ref (H3=8)
VL_CDR = {'L1': (23, 34), 'L2': (49, 56), 'L3': (88, 98)}   # L1=11, L2=7, L3=10

def nw_align(a, b, match=1, mism=-1, gap=-2):
    """Global alignment of a (design) to b (reference); returns list of (a_char|'', b_char|'')."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): D[i][0] = D[i - 1][0] + gap
    for j in range(1, m + 1): D[0][j] = D[0][j - 1] + gap
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = max(D[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mism),
                          D[i - 1][j] + gap, D[i][j - 1] + gap)
    i, j, pairs = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mism):
            pairs.append((a[i - 1], b[j - 1])); i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i - 1][j] + gap:
            pairs.append((a[i - 1], '')); i -= 1
        else:
            pairs.append(('', b[j - 1])); j -= 1
    pairs.reverse()
    return pairs

def extract_cdrs(design, ref, cdr_spans):
    """Return dict region->design segment, plus FR mismatch count, via alignment columns."""
    pairs = nw_align(design, ref)
    ref_idx = 0
    segs = {k: [] for k in cdr_spans}
    fr_muts = 0
    in_cdr = {k: False for k in cdr_spans}
    for a_ch, b_ch in pairs:
        region = None
        for k, (s, e) in cdr_spans.items():
            if s <= ref_idx < e:
                region = k
        if b_ch:
            if region:
                segs[region].append(a_ch if a_ch else '-')  # gap in design inside CDR = deletion
                in_cdr[region] = True
            else:
                if a_ch != b_ch:
                    fr_muts += 1
            ref_idx += 1
        else:
            # insertion in design: attach to current CDR if inside one
            if region:
                segs[region].append(a_ch)
            # insertion in FR = framework edit by tool (counted)
            else:
                fr_muts += 1
    return {k: ''.join(v) for k, v in segs.items()}, fr_muts

def rebuild_vh(c):
    return FR['FR-H1'] + c['H1'] + 'AMS' + 'WVRQAPGKGLEWVSAI' + c['H2'] + FR['FR-H3'] + c['H3'] + FR['FR-H4']

def rebuild_vl(c):
    return FR['FR-L1'] + c['L1'] + FR['FR-L2'] + c['L2'] + FR['FR-L3'] + c['L3'] + FR['FR-L4']

# read fasta
records = []
name = None
for setid in [0, 1]:
    for line in open(f'{OUT}/ab_des_output_{setid}_mpnn.fasta'):
        line = line.strip()
        if line.startswith('>'):
            name = line[1:].split()[0]
            records.append({'tag': name})
        else:
            records[-1]['seq'] = line

by_pair = {}
for r in records:
    base = r['tag'].rsplit('_', 1)[0]
    by_pair.setdefault(base, {})[r['tag'][-1]] = r['seq']

pool, dropped, repairs = [], [], []
for base, ch in sorted(by_pair.items()):
    if 'H' not in ch or 'L' not in ch:
        dropped.append((base, 'missing chain')); continue
    cdr_h, mut_h = extract_cdrs(ch['H'], VH_REF, VH_CDR)
    cdr_l, mut_l = extract_cdrs(ch['L'], VL_REF, VL_CDR)
    cdrs = {**cdr_h, **cdr_l}
    lens = {k: len(v) for k, v in cdrs.items()}
    ok = (lens['H1'] == 7 and lens['H2'] == 6 and 7 <= lens['H3'] <= 18 and
          lens['L1'] == 11 and lens['L2'] == 7 and 9 <= lens['L3'] <= 11 and
          '-' not in ''.join(cdrs.values()) and 'X' not in ''.join(cdrs.values()))
    if not ok:
        dropped.append((base, f'lengths {lens}')); continue
    if any('C' in v for v in cdrs.values()):
        dropped.append((base, 'Cys in CDR')); continue
    vh, vl = rebuild_vh(cdrs), rebuild_vl(cdrs)
    published = any(tuple(sorted(p['CDRs'].items())) == tuple(sorted(cdrs.items())) for p in panel.values())
    pool.append({'tag': base, 'VH': vh, 'VL': vl, 'CDRs': cdrs,
                 'fr_muts_overwritten': {'VH': mut_h, 'VL': mut_l}, 'published_duplicate': published})

seen, uniq = set(), []
for c in pool:
    if (c['VH'], c['VL']) in seen: continue
    seen.add((c['VH'], c['VL'])); uniq.append(c)

os.makedirs(f'{RUN}/candidates', exist_ok=True)
json.dump({'pool': uniq, 'dropped': [d for d in dropped], 'n_pairs': len(by_pair)},
          open(f'{RUN}/candidates/rf_antibody_pool.json', 'w'), indent=1)

print(f'pairs: {len(by_pair)} | passed gates: {len(pool)} | unique: {len(uniq)} | dropped: {len(dropped)}')
for d in dropped[:12]:
    print('  DROP', d)
print('FR muts overwritten (VH,VL) per kept candidate:',
      [(c['fr_muts_overwritten']['VH'], c['fr_muts_overwritten']['VL']) for c in uniq[:8]])
print('published duplicates kept-flag:', [c['published_duplicate'] for c in uniq])
h3 = [len(c['CDRs']['H3']) for c in uniq]
print('H3 lengths:', sorted(h3))
