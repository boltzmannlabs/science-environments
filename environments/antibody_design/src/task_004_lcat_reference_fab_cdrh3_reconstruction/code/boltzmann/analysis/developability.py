#!/usr/bin/env python3
"""Local developability metrics for CDR-H3 sequences (open-source, no GPU)."""
import json

# Standard amino acid properties
GRAVY = {'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'Q':-3.5,'E':-3.5,'G':-0.4,
         'H':-3.2,'I':4.5,'L':3.8,'K':-3.9,'M':1.9,'F':2.8,'P':-1.6,'S':-0.8,
         'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}
INSTAB = {'A':8.6,'R':10.8,'N':3.6,'D':5.1,'C':10.8,'Q':4.4,'E':4.8,'G':0.0,
          'H':8.0,'I':4.3,'L':3.8,'K':11.3,'M':16.2,'F':8.0,'P':5.3,'S':5.7,
          'T':5.1,'W':11.4,'Y':7.2,'V':4.8}
AROMA = set('WFY')
CHARGE = {'R':1,'K':1,'H':0.5,'D':-1,'E':-1}
HYDRO = set('AILMVWF')

def metrics(seq):
    n = len(seq)
    gravy = sum(GRAVY[a] for a in seq)/n
    instability = sum(INSTAB[a] for a in seq)/n
    aroma = sum(a in AROMA for a in seq)/n
    charge = sum(CHARGE.get(a,0) for a in seq)/n
    hydro = sum(a in HYDRO for a in seq)/n
    # CDR-length penalty (long CDR-H3 > 15 can be a liability)
    return {'len': n, 'gravy': round(gravy,3), 'instability_index': round(instability,2),
            'aromatic_frac': round(aroma,3), 'net_charge': round(charge,2),
            'hydrophobic_frac': round(hydro,3)}

# Native
native = "AREGAAVRSFYYSYYGMDV"
print("Native CDR-H3:", metrics(native))

# CDR_Generator top 5 by AAR
with open('cdr_generator_aar.json') as f:
    cdr_gen = json.load(f)
cdr_gen.sort(key=lambda x: -x['aar'])
print("\nCDR_Generator top 5:")
for r in cdr_gen[:5]:
    m = metrics(r['cdrh3'])
    print(f"  {r['cdrh3']} AAR={r['aar']:.3f} | {m}")

# Save all developability
out = {'native': metrics(native)}
for r in cdr_gen:
    out[f"cdr_gen_{r['id']}"] = metrics(r['cdrh3'])
with open('developability_cdr_gen.json','w') as f:
    json.dump(out, f, indent=2)
print("\nSaved developability_cdr_gen.json")
