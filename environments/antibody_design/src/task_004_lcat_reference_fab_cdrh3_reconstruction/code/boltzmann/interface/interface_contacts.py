#!/usr/bin/env python3
"""Interface contacts and clashes for AgCDR-Diff CDR-H3 backbones vs antigen."""
import math, glob, os, json

SKIP = ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL')
def heavy_atoms(f, chains, res_range=None):
    out = []
    with open(f) as fh:
        for line in fh:
            if not line.startswith('ATOM'): continue
            resn = line[17:20].strip()
            if resn in SKIP or line[12:16].strip().startswith('H'): continue
            cid = line[21]; rs = int(line[22:26].strip())
            if res_range and not (res_range[0]<=rs<=res_range[1]): continue
            if cid not in chains: continue
            out.append((cid,rs,float(line[30:38]),float(line[38:46]),float(line[46:54])))
    return out

# Native: CDR-H3 = chain C res 97-115, antigen = chain A
# Generated: CDR-H3 = chain A res 97-115, antigen = chain C
def contacts(clist, alist, cutoff):
    n = 0
    for _,_,x,y,z in clist:
        for _,_,ax,ay,az in alist:
            if math.sqrt((x-ax)**2+(y-ay)**2+(z-az)**2) < cutoff:
                n += 1; break
    return n

def min_dist(clist, alist):
    d = 1e9
    for _,_,x,y,z in clist:
        for _,_,ax,ay,az in alist:
            dd = math.sqrt((x-ax)**2+(y-ay)**2+(z-az)**2)
            if dd < d: d = dd
    return d

results = []
for fp in sorted(glob.glob('agcdr_results/generated_structures/generated_sample_*.pdb'),
                key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))))):
    cdr = heavy_atoms(fp, ('A',), (97,115))
    ag = heavy_atoms(fp, ('C',))
    c4 = contacts(cdr, ag, 4.0)
    c5 = contacts(cdr, ag, 5.0)
    md = min_dist(cdr, ag)
    results.append({'sample': os.path.basename(fp), 'contacts_4A': c4, 'contacts_5A': c5, 'min_dist_A': round(md,2)})

results.sort(key=lambda x: -x['contacts_4A'])
print(f"{'Sample':<28} {'C@4A':>5} {'C@5A':>5} {'minD(A)':>8}")
for r in results[:10]:
    print(f"{r['sample']:<28} {r['contacts_4A']:>5} {r['contacts_5A']:>5} {r['min_dist_A']:>8}")
with open('interface_contacts.json','w') as f:
    json.dump(results, f, indent=2)
print(f"\nMean C@4A: {sum(r['contacts_4A'] for r in results)/len(results):.1f}")
print(f"Mean C@5A: {sum(r['contacts_5A'] for r in results)/len(results):.1f}")
