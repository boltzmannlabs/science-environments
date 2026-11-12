#!/usr/bin/env python3
"""Compute AAR and CAAR for CDR_Generator output vs native CDR-H3."""
import csv

# Native CDR-H3 (positions 96-114, 1-indexed)
native_vh = "VQLVESGGGVVQPGRSLRLSCAASGFTFSSYGMHWVRQAPGKGLEWVAVIWYDGSNKFYEDSVKGRFTISRDNSKNTLYLQMDSLRAEDTAVYYCAREGAAVRSFYYSYYGMDVWGQGTTVTVSSA"
# CDR-H3 region: 0-indexed 95-113 (1-indexed 96-114)
cdr_start, cdr_end = 95, 114  # 0-indexed slice [95:114]
native_cdrh3 = native_vh[cdr_start:cdr_end]
print(f"Native CDR-H3 ({len(native_cdrh3)} aa): {native_cdrh3}")

# Contact residues: positions in CDR-H3 that contact the antigen
# From the native complex, determine which CDR-H3 positions contact LCAT
# For now, use all positions (CAAR = AAR if no contact info)
# We'll refine with contact info later

# Read CDR_Generator output
rows = []
with open('cdr_generator_output.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

print(f"Num generated: {len(rows)}")

# Compute AAR for each
results = []
for i, r in enumerate(rows):
    seq = r['Sequence']
    # Extract CDR-H3 region
    gen_cdrh3 = seq[cdr_start:cdr_end]
    # AAR: fraction of matching positions
    matches = sum(1 for a, b in zip(native_cdrh3, gen_cdrh3) if a == b)
    aar = matches / len(native_cdrh3)
    results.append({
        'id': i,
        'seq': seq,
        'cdrh3': gen_cdrh3,
        'matches': matches,
        'aar': aar
    })
    print(f"  [{i}] CDR-H3: {gen_cdrh3} | AAR: {aar:.3f} ({matches}/{len(native_cdrh3)})")

# Summary
aars = [r['aar'] for r in results]
print(f"\nMean AAR: {sum(aars)/len(aars):.3f}")
print(f"Best AAR: {max(aars):.3f} (id {results[aars.index(max(aars))]['id']})")
print(f"Worst AAR: {min(aars):.3f}")

# Save results
with open('cdr_generator_aar.json', 'w') as f:
    import json
    json.dump(results, f, indent=2)
print("\nSaved cdr_generator_aar.json")
