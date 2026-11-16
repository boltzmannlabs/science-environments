#!/usr/bin/env python3
"""Evaluate epitope_abgen design outputs: parse candidate PDBs/CSV, compute
framework fidelity, CDR content, epitope engagement vs the declared epitope
(hotspots 37/39/41/96/98 + neighbor shell), and summarize. Run after
epitope_abgen_raw/ is populated."""
import glob
import json
import os
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, '/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/code')
from prep_design_inputs import parse_protein, THREE2ONE  # noqa: E402

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
RAW = f'{SCRATCH}/epitope_abgen_raw'
CDRS = {'H1': (26, 33), 'H2': (51, 58), 'H3': (97, 109),
        'L1': (24, 29), 'L2': (50, 55), 'L3': (89, 97)}
HOTSPOTS = [37, 39, 41, 96, 98]


def cdr_positions(seq, chain):
    out = {}
    for name, (a, b) in CDRS.items():
        if name[0] == chain:
            out[name] = seq[a-1:b]
    return out


def main():
    pdbs = sorted(glob.glob(f'{RAW}/**/*.pdb', recursive=True))
    csvs = sorted(glob.glob(f'{RAW}/**/*.csv', recursive=True))
    print('candidate PDBs:', len(pdbs))
    for c in csvs:
        print('csv:', c, os.path.getsize(c), 'bytes')
    if not pdbs:
        print('no structures yet — nothing to evaluate')
        return
    epitope = json.load(open(f'{SCRATCH}/epitope_residues.json'))
    spec = epitope if isinstance(epitope, list) else epitope.get('residues', [])
    epi_res = set(int(str(x).split(':')[0]) for x in spec)
    print('epitope residues:', sorted(epi_res))

    report = []
    for p in pdbs:
        try:
            st = parse_protein(p)
        except Exception as e:
            print('skip', p, e)
            continue
        chains = OrderedDict()
        for (ch, rs), r in st.items():
            chains.setdefault(ch, {})[rs] = r
        seqs = {c: ''.join(THREE2ONE[r['resn']] for _, r in sorted(v.items()))
                for c, v in chains.items()}
        info = {
            'file': os.path.basename(p),
            'chains': {c: len(v) for c, v in chains.items()},
            'seqs': seqs,
        }
        cdrs = {}
        for c, s in seqs.items():
            if len(s) in (119, 120, 121):
                cdrs.update(cdr_positions(s, 'H'))
            elif len(s) in (106, 107, 108):
                cdrs.update(cdr_positions(s, 'L'))
        if cdrs:
            info['cdrs'] = cdrs
        ag = next((c for c, s in seqs.items() if 112 <= len(s) <= 117), None)
        if ag is not None:
            ag_atoms = [np.array(x) for r in chains[ag].values()
                        for n, x in r['atoms'].items() if not n.startswith('H')]
            contacts = set()
            for c, rdict in chains.items():
                if c == ag:
                    continue
                for rs, r in rdict.items():
                    hit = False
                    for n, x in r['atoms'].items():
                        if n.startswith('H'):
                            continue
                        x = np.array(x)
                        for y in ag_atoms:
                            if (x - y).dot(x - y) <= 25.0:
                                hit = True
                                break
                        if hit:
                            break
                    if hit:
                        contacts.add((c, rs))
            epi_hit = sorted({rs for c, rs in contacts if rs in epi_res})
            info['epitope_contacts'] = dict(
                n_residue_contacts=len(contacts),
                n_epitope_contacts=len(epi_hit),
                epitope_coverage=round(len(epi_hit) / len(epi_res), 3))
        report.append(info)
    out = f'{SCRATCH}/design_candidates_report.json'
    json.dump(report, open(out, 'w'), indent=1)
    print(f'wrote {out} ({len(report)} candidates)')
    for r in report[:20]:
        print(r['file'], r['chains'], r.get('epitope_contacts'))


if __name__ == '__main__':
    main()
