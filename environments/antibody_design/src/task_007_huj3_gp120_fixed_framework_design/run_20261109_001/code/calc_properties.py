#!/usr/bin/env python3
"""task_007 physicochemical property calculations.

Three properties, calculated identically for the native parent and every
designed candidate:

1. Residue-volume descriptor (sequence-level physical descriptor):
   Residue volume = sum of Bondi van-der-Waals volumes of the side-chain
   heavy atoms (backbone N, CA, C, O excluded). Bondi radii (Angstrom):
   C 1.70, N 1.55, O 1.52, S 1.80; V_atom = 4/3*pi*r^3 (Angstrom^3).
   This is a sequence-based atomic-volume descriptor, NOT a geometric
   molecular-volume calculation (no coordinates used).

2. Hydrophilicity descriptor: Kyte-Doolittle hydropathy index,
   hydrophilicity = -KD (positive = more hydrophilic).

3. Net charge at pH 7.4: Henderson-Hasselbalch with fixed pKa table
   (Berg, Tymoczko, Stryer, Biochemistry):
     side chains: D 3.90, E 4.10, H 6.00, C 8.30, Y 10.50, K 10.50, R 12.50
     termini (whole-antibody only): N-term 8.00, C-term 3.60
   Internal segments carry no terminal groups.

Segments (1-based): CDR1 = 26-33; full CDR3 analysis segment = 94-110.
Design masks: CDR1 26-33; CDR3 {97,101,103,104,105,106}.
Whole-antibody values are labeled separately.
"""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

# ---- tables -------------------------------------------------------------
BONDI_R = {'C': 1.70, 'N': 1.55, 'O': 1.52, 'S': 1.80}
VOLUME_ATOM = {el: 4.0 / 3.0 * math.pi * r ** 3 for el, r in BONDI_R.items()}

# side-chain heavy-atom composition (backbone excluded)
SC_ATOMS = {
    'G': {}, 'A': {'C': 1}, 'R': {'C': 4, 'N': 3}, 'N': {'C': 1, 'N': 1, 'O': 1},
    'D': {'C': 2, 'O': 2}, 'C': {'C': 1, 'S': 1}, 'Q': {'C': 2, 'N': 1, 'O': 1},
    'E': {'C': 3, 'O': 2}, 'H': {'C': 3, 'N': 2}, 'I': {'C': 4}, 'L': {'C': 4},
    'K': {'C': 4, 'N': 1}, 'M': {'C': 3, 'S': 1}, 'F': {'C': 7}, 'P': {'C': 4},
    'S': {'C': 1, 'O': 1}, 'T': {'C': 2, 'O': 1}, 'W': {'C': 9, 'N': 1},
    'Y': {'C': 7, 'O': 1}, 'V': {'C': 3},
}
VOL_RES = {aa: sum(VOLUME_ATOM[el] * n for el, n in comp.items()) for aa, comp in SC_ATOMS.items()}

KD = {'I': 4.5, 'V': 4.2, 'L': 3.8, 'P': 3.4, 'F': 2.8, 'C': 2.5, 'M': 1.9,
      'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8, 'W': -0.9, 'Y': -1.3,
      'H': -3.2, 'E': -3.5, 'D': -3.5, 'N': -3.5, 'Q': -3.5, 'K': -3.9, 'R': -4.5}
HYDROPHILICITY = {aa: -v for aa, v in KD.items()}  # positive = hydrophilic

PH = 7.4
PKA_ACID = {'D': 3.90, 'E': 4.10, 'C': 8.30, 'Y': 10.50}          # XH -> X- + H+
PKA_BASE = {'K': 10.50, 'R': 12.50, 'H': 6.00}                     # XH+ -> X + H+
PKA_NT, PKA_CT = 8.00, 3.60


def charge_aa(aa, ph=PH):
    if aa in PKA_ACID:
        return -1.0 / (1.0 + 10.0 ** (ph - PKA_ACID[aa]))
    if aa in PKA_BASE:
        return 1.0 / (1.0 + 10.0 ** (PKA_BASE[aa] - ph))
    return 0.0


# ---- segment helpers ----------------------------------------------------
SEGMENTS = {'CDR1': (26, 33), 'CDR3_full': (94, 110)}
DESIGN_MASKS = {'CDR1': list(range(26, 34)), 'CDR3': [97, 101, 103, 104, 105, 106]}


def seg_slice(seq, seg):
    lo, hi = SEGMENTS[seg]
    return seq[lo - 1:hi]


def describe(seq):
    out = {}
    for seg in SEGMENTS:
        s = seg_slice(seq, seg)
        out[seg] = {
            'residue_volume_sum_A3': sum(VOL_RES[a] for a in s),
            'residue_volume_mean_A3_per_res': sum(VOL_RES[a] for a in s) / len(s),
            'hydrophilicity_sum': sum(HYDROPHILICITY[a] for a in s),
            'hydrophilicity_mean': sum(HYDROPHILICITY[a] for a in s) / len(s),
            'net_charge_e': sum(charge_aa(a) for a in s),
        }
    whole = {
        'residue_volume_sum_A3': sum(VOL_RES[a] for a in seq),
        'residue_volume_mean_A3_per_res': sum(VOL_RES[a] for a in seq) / len(seq),
        'hydrophilicity_sum': sum(HYDROPHILICITY[a] for a in seq),
        'hydrophilicity_mean': sum(HYDROPHILICITY[a] for a in seq) / len(seq),
        'net_charge_e': (sum(charge_aa(a) for a in seq)
                         - 1.0 / (1.0 + 10.0 ** (PH - PKA_CT))
                         + 1.0 / (1.0 + 10.0 ** (PH - PKA_NT))),
    }
    out['whole_antibody'] = whole
    return out


def load_fasta(path):
    recs = []
    name = None
    for line in open(path):
        line = line.strip()
        if line.startswith('>'):
            name = line[1:]
        elif name:
            recs.append((name, line.upper()))
    return recs


def main(fasta_path, out_csv, out_json):
    recs = load_fasta(fasta_path)
    parent = next((s for n, s in recs if n.startswith('parent')), None)
    if parent is None:
        raise SystemExit('parent sequence not found in fasta')
    rows = []
    for name, seq in recs:
        tag = 'parent' if name.startswith('parent') else name
        d = describe(seq)
        row = {'candidate_id': tag, 'seq_length': len(seq),
               'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(),
               'scope': 'native_parent' if tag == 'parent' else 'candidate'}
        for seg in list(SEGMENTS) + ['whole_antibody']:
            for k, v in d[seg].items():
                row[f'{seg}.{k}'] = v
        rows.append(row)

    # differences vs parent + predeclared selection rule
    p = rows[0]
    fields = ['residue_volume_sum_A3', 'hydrophilicity_sum', 'net_charge_e']
    for r in rows:
        for seg in SEGMENTS:
            for f in fields:
                r[f'delta_{seg}.{f}'] = r[f'{seg}.{f}'] - p[f'{seg}.{f}']
    # composite: sum of per-property absolute deltas across the two analysis
    # segments, normalized by the campaign maximum, then summed.
    for f in fields:
        key = f'combined_abs_{f}'
        for r in rows:
            r[key] = (abs(r[f'delta_CDR1.{f}']) + abs(r[f'delta_CDR3_full.{f}']))
        mx = max(r[key] for r in rows)
        for r in rows:
            r[f'norm_{key}'] = r[key] / mx if mx else 0.0
    for r in rows:
        r['composite_abs_deviation'] = sum(r[f'norm_combined_abs_{f}'] for f in fields)
    shortlist = sorted([r for r in rows if r['scope'] == 'candidate'],
                       key=lambda r: (r['composite_abs_deviation'], r['candidate_id']))
    short_ids = {r['candidate_id'] for r in shortlist[:10]}

    with open(out_csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with open(out_json, 'w') as fh:
        json.dump({
            'ph_charge': PH, 'pka_acid': PKA_ACID, 'pka_base': PKA_BASE,
            'pka_Nterm': PKA_NT, 'pka_Cterm': PKA_CT,
            'bondi_radii_A': BONDI_R, 'bondi_atom_volumes_A3': VOLUME_ATOM,
            'side_chain_heavy_atom_composition': SC_ATOMS,
            'residue_volume_table_A3': VOL_RES,
            'kyte_doolittle_table': KD,
            'segments': {k: list(v) for k, v in SEGMENTS.items()},
            'design_masks': DESIGN_MASKS,
            'selection_rule': ('rank by composite normalized absolute deviation '
                               'from parent over volume, hydrophilicity and '
                               'charge, summed across CDR1 and CDR3-full '
                               'segments; shortlist = 10 smallest'),
            'shortlist': sorted(short_ids),
            'parent_sha256': p['sequence_sha256'],
        }, fh, indent=2)
    print(f'wrote {out_csv} and {out_json}; {len(rows)-1} candidates, shortlist {len(short_ids)}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
