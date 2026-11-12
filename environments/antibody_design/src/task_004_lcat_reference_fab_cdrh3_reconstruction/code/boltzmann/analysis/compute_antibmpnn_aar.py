#!/usr/bin/env python3
"""Compute AAR for AntiBMPNN designed VH sequences vs native CDR-H3."""
import csv

native_vh = "VQLVESGGGVVQPGRSLRLSCAASGFTFSSYGMHWVRQAPGKGLEWVAVIWYDGSNKFYEDSVKGRFTISRDNSKNTLYLQMDSLRAEDTAVYYCAREGAAVRSFYYSYYGMDVWGQGTTVTVSSA"
cdr_start, cdr_end = 95, 114  # 0-indexed [95:114] = positions 96-114
native_cdrh3 = native_vh[cdr_start:cdr_end]
print(f"Native CDR-H3 ({len(native_cdrh3)}): {native_cdrh3}")

rows = []
with open('antibmpnn_results/antibmpnn_results.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)
print(f"Num designed: {len(rows)}")

results = []
for i, r in enumerate(rows):
    seq = r['heavy_chain']
    gen_cdrh3 = seq[cdr_start:cdr_end]
    matches = sum(1 for a, b in zip(native_cdrh3, gen_cdrh3) if a == b)
    aar = matches / len(native_cdrh3)
    results.append({'id': i, 'pdb': r['pdb_name'], 'cdrh3': gen_cdrh3, 'matches': matches, 'aar': aar})

results.sort(key=lambda x: -x['aar'])
aars = [r['aar'] for r in results]
print(f"\nMean AAR: {sum(aars)/len(aars):.3f}")
print(f"Best AAR: {max(aars):.3f}")
print(f"Top 10:")
for r in results[:10]:
    print(f"  {r['pdb']} [{r['id']}] {r['cdrh3']} | AAR {r['aar']:.3f}")

import json
with open('antibmpnn_aar.json','w') as f:
    json.dump(results, f, indent=2)
print("\nSaved antibmpnn_aar.json")
