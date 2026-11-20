#!/usr/bin/env python3
"""ANARCI Chothia CDR mapping for cetuximab VH/VL. Writes _anarci_cdr.json.
Usage: anarci_cdr.py <vh> <vl> <out_json>"""
import json, sys

vh, vl, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
from anarci import run_anarci
res = run_anarci([('VH', vh), ('VL', vl)], scheme='chothia', database='ALL')
CDR = {'H': {'H1': (26, 32), 'H2': (52, 56), 'H3': (95, 102)},
       'L': {'L1': (24, 34), 'L2': (50, 56), 'L3': (89, 97)}}
out = {}
for ci, (name, chain) in enumerate([('VH', 'H'), ('VL', 'L')]):
    dom = vh if name == 'VH' else vl
    numbering, qstart, qend = res[1][ci][0]
    entries = [((n, i.strip()), a) for (n, i), a in numbering]
    got = ''.join(a for _, a in entries)
    assert got == dom, f'{name} numbering mismatch'
    pos = [(f'{ni[0]}{ni[1] if ni[1].isalpha() else ""}', a, idx + 1)
           for idx, (ni, a) in enumerate(entries)]
    out[name] = {'positions': pos}
    for cdr, (lo, hi) in CDR[chain].items():
        sel = [p for p in pos if lo <= int(p[0].rstrip('ABCD') or 0) <= hi]
        out[name][cdr] = {'start': sel[0][2], 'end': sel[-1][2], 'length': len(sel),
                          'segment': ''.join(p[1] for p in sel)}
json.dump(out, open(out_json, 'w'), indent=1)
print('ANARCI CDR map written:', out_json)
