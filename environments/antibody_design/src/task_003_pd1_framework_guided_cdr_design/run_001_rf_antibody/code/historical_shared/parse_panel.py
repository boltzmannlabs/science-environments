#!/usr/bin/env python3
"""Parse Supplementary Table 7 (PD-1 panel) directly from moesm1.txt.

Sequences are extracted programmatically from the downloaded supplementary PDF text
(never retyped), line wraps joined, then validated against Table 1 FR block layout.
"""
import json, re, os

SRC = '/home/boltzmann10/.sci/cache/scratch/task003_paper'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'

FR = {
    'FR-H1': 'EVQLLESGGGLVQPGGSLRLSCAAS',
    'FR-H2a': 'AMSWVRQAPGKGLEWVSAI',
    'FR-H3': 'TYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK',
    'FR-H4': 'WGQGTLVTVSS',
    'FR-L1': 'DIQMTQSPSTLSASVGDRVTITC',
    'FR-L2': 'WYQQKPGKAPKLLIY',
    'FR-L3': 'GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC',
    'FR-L4': 'FGQGTKVEIK',
}
AA = set('ACDEFGHIKLMNPQRSTVWY')

raw = open(f'{SRC}/moesm1.txt').read()
# Locate Supplementary Table 7 section
# Table N's caption follows its data block: PD-1 panel rows live between Table 6 and Table 7 captions
m = re.search(r'Supplementary Table 6:.*?\n(.*?)(?:Supplementary Table 7:|\Z)', raw, re.S)
assert m, 'Table 7 data section not found'
sec = m.group(1)
# Pull token stream: names, sequence fragments (long uppercase AAcid tokens), KD numbers
tokens = re.findall(r'[A-Z]{2,}|\d+\.\d+|Anti-PD1-H\w+', sec)
rows, cur = [], None
for tok in tokens:
    if tok.startswith('Anti-PD1-'):
        cur = {'name': tok, 'frags': [], 'kd': None}
        rows.append(cur)
    elif cur is not None and re.fullmatch(r'\d+\.\d+', tok):
        cur['kd'] = float(tok)
    elif cur is not None and set(tok) <= AA:
        cur['frags'].append(tok)

panel = {}
for r in rows:
    vh_joined = ''.join(f for f in r['frags'] if f.startswith('EVQLL'))
    vl_joined = ''.join(f for f in r['frags'] if f.startswith('DIQMT'))
    # robust: reconstruct by order — frags alternate VH pieces then VL pieces
    # VH pieces: from EVQLL up to first WGQGTLVTVSS-containing frag; VL: DIQMT start
    vh_parts, vl_parts, mode = [], [], None
    for f in r['frags']:
        if f.startswith('EVQLL'):
            mode = 'H'
        elif f.startswith('DIQMT'):
            mode = 'L'
        if mode == 'H':
            vh_parts.append(f)
        else:
            vl_parts.append(f)
    vh = ''.join(vh_parts)
    vl = ''.join(vl_parts)
    panel[r['name']] = {'VH': vh, 'VL': vl, 'KD_nM': r['kd']}

def decompose_vh(vh):
    assert vh.startswith(FR['FR-H1']), 'FR-H1'
    i = 25
    h1 = vh[i:i+7]; i += 7
    assert vh[i:i+3] == 'AMS', f'AMS anchor got {vh[i:i+5]}'
    i += 3
    assert vh[i:i+16] == 'WVRQAPGKGLEWVSAI', 'FR-H2 rest'
    i += 16
    h2 = vh[i:i+6]; i += 6
    assert vh[i:i+41] == FR['FR-H3'], 'FR-H3'
    i += 41
    k = vh.find(FR['FR-H4'], i)
    assert k > 0, 'FR-H4 anchor'
    h3 = vh[i:k]
    assert vh[k:] == FR['FR-H4']
    return {'H1': h1, 'H2': h2, 'H3': h3}

def decompose_vl(vl):
    assert vl.startswith(FR['FR-L1']), 'FR-L1'
    i = 23
    l1 = vl[i:i+11]; i += 11
    assert vl[i:i+15] == FR['FR-L2'], f'FR-L2 got {vl[i:i+15]}'
    i += 15
    l2 = vl[i:i+7]; i += 7
    assert vl[i:i+32] == FR['FR-L3'], f'FR-L3 got {vl[i:i+32]}'
    i += 32
    k = vl.find(FR['FR-L4'], i)
    assert k > 0, 'FR-L4 anchor'
    l3 = vl[i:k]
    assert vl[k:] == FR['FR-L4']
    return {'L1': l1, 'L2': l2, 'L3': l3}

out = {}
deviations = []
for name, rec in panel.items():
    d = {'VH': rec['VH'], 'VL': rec['VL'], 'KD_nM': rec['KD_nM'],
         'CDRs': {**decompose_vh(rec['VH']), **decompose_vl(rec['VL'])}}
    if not (7 <= len(d['CDRs']['H3']) <= 18):
        deviations.append(f'{name}: H3 len {len(d["CDRs"]["H3"])} outside Table-1 range 7-18')
    if not (9 <= len(d['CDRs']['L3']) <= 11):
        deviations.append(f'{name}: L3 len {len(d["CDRs"]["L3"])} outside Table-1 declared range 9-11 (published as-is)')
    out[name] = d

assert len(out) == 10, f'expected 10 panel members, got {len(out)}'
assert 'Anti-PD1-H965' in out

with open(f'{INP}/pd1_panel_published.json', 'w') as f:
    json.dump({'panel': out, 'published_data_deviations': deviations}, f, indent=1)
with open(f'{INP}/h965_and_pd1_panel.fasta', 'w') as f:
    for name, d in out.items():
        tag = name.replace('Anti-PD1-', '')
        f.write(f'>{tag}_VH|{name}|KD={d["KD_nM"]}nM|published_control\n{d["VH"]}\n')
        f.write(f'>{tag}_VL|{name}|KD={d["KD_nM"]}nM|published_control\n{d["VL"]}\n')

print(f'Parsed {len(out)} panel members, all validated against Table 1 FR layout.')
for name, d in out.items():
    c = d['CDRs']
    print(f"{name}: KD={d['KD_nM']} H3={c['H3']}({len(c['H3'])}) L3={c['L3']}({len(c['L3'])})")
