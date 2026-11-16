#!/usr/bin/env python
"""Rebuild run_003 AntiBMPNN evaluation models correctly: native complex with
chain-C H3 residues mutated to the designed sequence (backbone N/CA/C/O + CB),
all other chains and residues byte-identical to native."""
import csv
import glob
import hashlib
import json
from pathlib import Path

WS = Path('/home/boltzmann10/lcat_task004')
DIFFAB = WS / 'run_5bv7_diffab'
BASE = WS / 'run_5bv7_abflow'

KEYS = ['2','3','4','5','6','7','8','9','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57','58','59','62','63','64','65','66','67','68','69','70','71','72','74','75','76','77','78','79','80','81','82','83','84','85','86','87','88','89','90','91','92','93','94','95','96','97','98','99','100','101','102','103','104','105','106','107','108','109','110','111','111A','111B','111C','112C','112B','112A','112','113','114','115','116','117','118','119','120','121','122','123','124','125','126','127','128','129']
H3_KEYS = KEYS[95:114]
h3_keyset = set(H3_KEYS)
one2three = {'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','Q':'GLN','E':'GLU','G':'GLY','H':'HIS','I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE','P':'PRO','S':'SER','T':'THR','W':'TRP','Y':'TYR','V':'VAL'}

native = json.loads(open(BASE / 'reference/native_5bv7.json').read())
vh_n = native['heavy_chain_seq']
native_lines = open(DIFFAB / 'native_5bv7_complex.pdb').read().splitlines()

def sha256(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

rows = list(csv.DictReader(open(DIFFAB / 'antibmpnn_out/antibmpnn_results.csv')))
# model scores from raw FASTA headers (sample=1..32 -> rows order)
import re
scores = {}
for fa in glob.glob(str(DIFFAB / 'antibmpnn_out/antibmpnn_artifacts/model_output/seqs/*.fa')):
    txt = open(fa).read()
    for m in re.finditer(r'>.*?sample=(\d+), score=([\d.]+)', txt):
        scores[int(m.group(1))] = float(m.group(2))

out_root = DIFFAB / 'gen_antibmpnn_n32'
# wipe old broken models
for p in out_root.glob('*.pdb'):
    p.unlink()

out_rows = []
for i, r in enumerate(rows):
    vh = r['heavy_chain']
    h3 = vh[95:114]
    assert len(h3) == 19
    out_lines, emitted = [], False
    for line in native_lines:
        if line.startswith('ATOM') and line[21] == 'C' and line[22:27].strip() in h3_keyset:
            if not emitted:
                # emit the 19 mutated residues in H3_KEYS order
                # collect native lines per key first
                pass
            out_lines.append(line)  # placeholder replaced below
            continue
        out_lines.append(line)
    # simpler correct approach: rebuild by residue blocks
    c_res, c_order = {}, []
    for line in native_lines:
        if line.startswith('ATOM') and line[21] == 'C':
            k = line[22:27].strip()
            if k not in c_res:
                c_res[k] = []; c_order.append(k)
            c_res[k].append(line)
    out_lines, emitted = [], False
    for line in native_lines:
        if line.startswith('ATOM') and line[21] == 'C' and line[22:27].strip() in h3_keyset:
            if not emitted:
                for j, k in enumerate(H3_KEYS):
                    aa3 = one2three[h3[j]]
                    for l in c_res[k]:
                        atom = l[12:16].strip()
                        if atom in ('N','CA','C','O') or (atom == 'CB' and aa3 != 'GLY'):
                            out_lines.append(l[:17] + f'{aa3:>3}' + l[20:])
                emitted = True
            continue
        out_lines.append(line)
    cid = f'5bv7_abmpnn_{i:03d}'
    p = out_root / f'{cid}.pdb'
    p.write_text('\n'.join(out_lines) + '\n')
    full_vh = vh[:114] + vh_n[114:]
    out_rows.append({'candidate_id': cid, 'h3': h3, 'full_vh': full_vh,
                     'model_score': scores.get(i+1), 'pdb_sha256': sha256(p), 'pdb': str(p)})

# frozen ranking: model score ascending, tie-break candidate_id
out_rows.sort(key=lambda r: (r['model_score'], r['candidate_id']))
for rank, r in enumerate(out_rows, 1):
    r['frozen_rank'] = rank
json.dump(out_rows, open(DIFFAB / 'antibmpnn_prep.json', 'w'), indent=2)
print('rebuilt', len(out_rows), 'models | rank1:', out_rows[0]['candidate_id'],
      'score', out_rows[0]['model_score'], 'H3', out_rows[0]['h3'])
# verify parse + chains
import sys
sys.path.insert(0, str(WS / 'AbFlow'))
from Bio.PDB import PDBParser
s = PDBParser(QUIET=True).get_structure('x', str(out_root / '5bv7_abmpnn_000.pdb'))
print('chains:', [c.id for c in s[0]], '| A len:', len(list(s[0]['A'])), '| C len:', len(list(s[0]['C'])), '| B len:', len(list(s[0]['B'])))
