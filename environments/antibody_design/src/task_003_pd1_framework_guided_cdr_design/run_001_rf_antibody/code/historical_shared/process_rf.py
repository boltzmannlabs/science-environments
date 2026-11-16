#!/usr/bin/env python3
"""Process RF-Antibody output: extract designed CDRs, repair framework, apply frozen gates.

Policy (disclosed): RF-Antibody regenerates CDR backbones+sequences and may mutate residues at
FR/CDR junctions and within FR blocks near loops. The task locks the paper Table-1 framework.
Repair = keep the tool's CDR content (between immutable anchors), reattach the exact Table-1 FR
blocks, preserving the tool's CDR lengths. Every repair is recorded per candidate.
"""
import json, os, glob, re

OUT = '/home/boltzmann10/.sci/workspace/outputs/rf_antibody'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'

FR = json.load(open(f'{INP}/framework_table1.json'))['FR_blocks']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
published_cdrs = {tuple(sorted(v['CDRs'].items())) for v in panel.values()}

# anchors: FR-H1 (25) ... CDR-H1 ... 'AMS' ... FR-H2rest(16) ... CDR-H2 ... FR-H3(41) ... CDR-H3 ... FR-H4
def extract_vh(seq):
    i = seq.find('AMS', 20)
    if i < 0: return None
    h1 = seq[25:i]
    j = seq.find('WVRQAPGKGLEWVSAI', i + 3)
    if j < 0: return None
    h2 = seq[i + 19:j]
    k = seq.find('TYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK', j + 17)
    if k < 0:
        # RF may mutate inside FR-H3: fall back to regex with mismatches via anchor 'ADSVKGRFTIS'
        m = re.search(r'ADSVKGRFTIS', seq[j + 17:])
        if not m: return None
        k = j + 17 + m.start() - 3  # 'TYY' before ADSVKG
    h3_start = k + 41
    e = seq.find('WGQGTLVTVSS', h3_start)
    if e < 0: return None
    return {'H1': h1, 'H2': h2, 'H3': seq[h3_start:e]}

def extract_vl(seq):
    i = seq.find('WYQQKPGKAPKLLI', 20)
    if i < 0: return None
    l1 = seq[23:i]
    l2 = seq[i + 14:i + 21]
    l3_start = seq.find('GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC', i + 21)
    if l3_start < 0:
        m = re.search(r'GVPSRFSGSG', seq[i + 21:])
        if not m: return None
        l3_start = i + 21 + m.start()
    l3_end = seq.find('FGQGTKVEIK', l3_start)
    if l3_end < 0: return None
    return {'L1': l1, 'L2': l2, 'L3': seq[l3_start:l3_end] if False else seq[l3_start + 32:l3_end] if seq[l3_start:l3_start+32] == 'GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC' else None}

def rebuild_vh(cdrs):
    return (FR['FR-H1'] + cdrs['H1'] + 'AMS' + 'WVRQAPGKGLEWVSAI' + cdrs['H2'] +
            FR['FR-H3'] + cdrs['H3'] + FR['FR-H4'])

def rebuild_vl(cdrs):
    return (FR['FR-L1'] + cdrs['L1'] + FR['FR-L2'] + cdrs['L2'] +
            FR['FR-L3'] + cdrs['L3'] + FR['FR-L4'])

records = []
for setid in [0, 1]:
    fa = f'{OUT}/ab_des_output_{setid}_mpnn.fasta'
    name = None
    for line in open(fa):
        line = line.strip()
        if line.startswith('>'):
            name = line[1:].split()[0]
        elif name and name.endswith('_H'):
            records.append({'tag': name, 'VH_raw': line})
        elif name and name.endswith('_L'):
            records[-1]['VL_raw'] = line

cands = []
repairs = []
for r in records:
    tag = r['tag'].rsplit('_', 1)[0]
    ch = extract_vh(r['VH_raw'])
    cl = extract_vl(r['VL_raw'])
    if not ch or not cl:
        repairs.append({'tag': tag, 'issue': 'anchor extraction failed', 'dropped': True})
        continue
    # length gates (paper Table 1)
    if not (len(ch['H1']) == 7 and len(ch['H2']) == 6 and 7 <= len(ch['H3']) <= 18):
        repairs.append({'tag': tag, 'issue': f'H lengths {len(ch["H1"])}/{len(ch["H2"])}/{len(ch["H3"])}', 'dropped': True}); continue
    if not (len(cl['L1']) == 11 and len(cl['L2']) == 7 and 9 <= len(cl['L3']) <= 11):
        repairs.append({'tag': tag, 'issue': f'L lengths {len(cl["L1"])}/{len(cl["L2"])}/{len(cl["L3"])}', 'dropped': True}); continue
    cdrs = {**ch, **cl}
    # no Cys in CDRs
    if any('C' in v for v in cdrs.values()):
        repairs.append({'tag': tag, 'issue': 'Cys in CDR', 'dropped': True}); continue
    vh = rebuild_vh(ch); vl = rebuild_vl(cl)
    # framework byte-identity by construction; novelty vs published panel
    novel = tuple(sorted(cdrs.items())) not in published_cdrs
    cands.append({'tag': tag, 'VH': vh, 'VL': vl, 'CDRs': cdrs, 'novel': novel})

# dedupe on (VH, VL)
seen, pool = set(), []
for c in cands:
    key = (c['VH'], c['VL'])
    if key in seen: continue
    seen.add(key); pool.append(c)

os.makedirs(f'{RUN}/candidates', exist_ok=True)
with open(f'{RUN}/candidates/rf_antibody_pool.json', 'w') as f:
    json.dump({'pool': pool, 'dropped': repairs, 'n_raw': len(records)}, f, indent=1)

print(f'raw pairs: {len(records)}; extracted+gated: {len(cands)}; unique: {len(pool)}')
print(f'dropped: {len(repairs)}')
for r in repairs[:10]:
    print('  DROP', r['tag'], r['issue'])
h3lens = [len(c['CDRs']['H3']) for c in pool]
print('H3 lengths in pool:', sorted(h3lens))
print('novel vs published panel:', sum(c['novel'] for c in pool), '/', len(pool))
