#!/usr/bin/env python
"""
Graft-based evaluation-model builder for run_002 (DiffAb) — run_003 models already built.

run_002 protocol note: DiffAb (in-context) keeps the native framework/pose and
redesigns the H3 loop (sequence+structure). Its output is Chothia-renumbered and
terminally cropped. Evaluation models = native IMGT complex with the 19-residue
DiffAb H3 block (full atoms, designed coordinates) transplanted at the native
H3 IMGT numbers (1:1 by sequence position; framework is sequence-identical).
All design content (H3 sequence + loop structure + sidechains) is DiffAb's.
"""
import glob
import json
import os
from pathlib import Path

WS = Path('/home/boltzmann10/lcat_task004')
DIFFAB = WS / 'run_5bv7_diffab'

KEYS = ['2','3','4','5','6','7','8','9','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57','58','59','62','63','64','65','66','67','68','69','70','71','72','74','75','76','77','78','79','80','81','82','83','84','85','86','87','88','89','90','91','92','93','94','95','96','97','98','99','100','101','102','103','104','105','106','107','108','109','110','111','111A','111B','111C','112C','112B','112A','112','113','114','115','116','117','118','119','120','121','122','123','124','125','126','127','128','129']
H3_KEYS = KEYS[95:114]

out_root = DIFFAB / 'gen_diffab_grafted'
out_root.mkdir(exist_ok=True)

# native complex lines, split: chain C H3 block vs rest (keep original ordering)
native_lines = open(DIFFAB / 'native_5bv7_complex.pdb').read().splitlines()
h3_keyset = set(H3_KEYS)
# residue order of chain C in the native file
seen = []
c_res = {}
for line in native_lines:
    if line.startswith('ATOM') and line[21] == 'C':
        k = line[22:27].strip()
        if k not in c_res:
            c_res[k] = []
            seen.append(k)
        c_res[k].append(line)
assert seen == KEYS, 'native chain C numbering differs from expected IMGT order'
non_c_h3 = [l for l in native_lines if not (l.startswith('ATOM') and l[21] == 'C' and l[22:27].strip() in h3_keyset)]
c_framework = [l for l in native_lines if l.startswith('ATOM') and l[21] == 'C' and l[22:27].strip() not in h3_keyset]

import hashlib
def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

three2one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

rows = []
srcs = sorted(glob.glob(str(DIFFAB / 'gen_diffab_n32/5bv7_diffab_*.pdb')))
for i, src in enumerate(srcs):
    # parse DiffAb chain C residues in sequence order
    d_res = []
    d_map = {}
    for line in open(src):
        if line.startswith('ATOM') and line[21] == 'C':
            k = line[22:27].strip()
            if k not in d_map:
                d_map[k] = []
                d_res.append(k)
            d_map[k].append(line)
    h3_src = d_res[95:114]
    assert len(h3_src) == 19, (src, len(h3_src))
    # renumber DiffAb H3 residues to native IMGT keys
    block = []
    for newkey, srckey in zip(H3_KEYS, h3_src):
        for line in d_map[srckey]:
            block.append(line[:22] + f'{newkey:>4}' + line[26:])
    cid = f'5bv7_diffab_g{i:03d}'
    p = out_root / f'{cid}.pdb'
    # assemble: native non-H3 lines in original order, but the H3 block must sit
    # inside chain C's position. Rebuild: iterate native lines; when hitting the
    # first H3 residue, emit block; skip other H3 lines.
    emitted_block = False
    out_lines = []
    for line in native_lines:
        if line.startswith('ATOM') and line[21] == 'C' and line[22:27].strip() in h3_keyset:
            if not emitted_block:
                out_lines.extend(block)
                emitted_block = True
            continue
        out_lines.append(line)
    p.write_text('\n'.join(out_lines) + '\n')
    # extract designed H3 sequence for the record
    seq = ''
    for k in h3_src:
        for line in d_map[k]:
            if line[12:16].strip() == 'CA':
                seq += three2one.get(line[17:20].strip(), 'X')
    rows.append({'candidate_id': cid, 'h3_sequence': seq, 'pdb': str(p), 'pdb_sha256': sha256(p)})

json.dump(rows, open(DIFFAB / 'diffab_grafted_manifest.json', 'w'), indent=2)
print('grafted models:', len(rows), '| first H3:', rows[0]['h3_sequence'])
# sanity: framework untouched, H3 replaced
import subprocess
print(subprocess.run(['grep', '-c', '^ATOM', str(out_root / '5bv7_diffab_g000.pdb')], capture_output=True, text=True).stdout.strip(), 'atoms (native:',
      subprocess.run(['grep', '-c', '^ATOM', str(DIFFAB / 'native_5bv7_complex.pdb')], capture_output=True, text=True).stdout.strip() + ')')
