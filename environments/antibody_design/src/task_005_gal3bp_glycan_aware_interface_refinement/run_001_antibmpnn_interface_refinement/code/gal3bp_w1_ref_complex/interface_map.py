#!/usr/bin/env python3
"""Interface map for the ternary reference complex.
Definition: antibody-antigen residue pair if any CA-CA distance < 6 A (same
definition for reference and candidates). Antibody residues classified CDR vs
framework by IMGT numbering (from ANARCI run on the supplied sequences).
Outputs JSON: epitope residues (antigen), paratope (CDR vs FR), region stats.
"""
import json, sys
import numpy as np
from collections import defaultdict

pdb = sys.argv[1]
out = sys.argv[2]

# IMGT CDR ranges (from ANARCI numbering of BDBV-43, 1-based Fv index computed here)
# ANARCI output (anarci_out) gave IMGT positions; mapping to 1-based index was computed:
VH_CDR = {  # 1-based position in supplied VH sequence
    "H1": list(range(27, 38)),   # IMGT 27-38 -> after alignment (see index map)
    "H2": list(range(56, 65)),
    "H3": list(range(105, 117)),
}
VL_CDR = {
    "L1": list(range(27, 38)),
    "L2": list(range(55, 62)),
    "L3": list(range(105, 113)),
}
# NOTE: exact mapping recomputed below from the ANARCI file instead of hardcoding.

def load_anarci_cdr_index(anarci_path):
    """Map IMGT CDR positions to 1-based sequence index for H and L."""
    cdr = {"H": {}, "L": {}}
    cur = None; idx = 0
    for line in open(anarci_path):
        if line.startswith("# BDBV43_VH"):
            cur = "H"; idx = 0; continue
        if line.startswith("# BDBV43_VL"):
            cur = "L"; idx = 0; continue
        if line.startswith("//"):
            cur = None; continue
        parts = line.split()
        if len(parts) >= 3 and parts[0] in ("H","L") and not line.startswith("H 111") :
            pass
        if parts and parts[0] == cur and len(parts) >= 2:
            idx += 1
            try:
                imgt_pos = int(parts[1])
            except ValueError:
                continue  # insertion codes like '111 A'
            cdr[cur][imgt_pos] = idx
    return cdr

def imgt_cdr_positions():
    a = load_anarci_cdr_index("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/gal3bp_w1_ref_complex/inputs/anarci_out")
    def idxmap(chain, lo, hi):
        return sorted(v for k,v in a[chain].items() if lo <= k <= hi)
    return {
        "H1": idxmap("H",27,38), "H2": idxmap("H",56,65), "H3": idxmap("H",105,117),
        "L1": idxmap("L",27,38), "L2": idxmap("L",55,61), "L3": idxmap("L",105,113),
    }

CDRS = imgt_cdr_positions()

def parse(p):
    res = {}
    for l in open(p):
        if l.startswith("ATOM"):
            ch=l[21]; rs=int(l[22:26]); nm=l[12:16].strip()
            res.setdefault((ch,rs),{})[nm]=np.array([float(l[30:38]),float(l[38:46]),float(l[46:54])])
    return res

res = parse(pdb)
ab = [(k,v) for k,v in res.items() if k[0] in "AB"]
ag = [(k,v) for k,v in res.items() if k[0]=="C"]

pairs = []
for (k1,v1) in ab:
    ca1 = v1.get("CA")
    if ca1 is None: continue
    for (k2,v2) in ag:
        ca2 = v2.get("CA")
        if ca2 is None: continue
        d = float(np.linalg.norm(ca1-ca2))
        if d < 6.0:
            pairs.append({"ab": k1, "ag": k2, "ca_dist": round(d,2)})

ab_res = sorted({p["ab"] for p in pairs}, key=lambda k:(k[0],k[1]))
ag_res = sorted({p["ag"] for p in pairs}, key=lambda k:k[1])

def classify(k):
    ch, rs = k
    for name, positions in CDRS.items():
        if (name.startswith("H") and ch=="A") or (name.startswith("L") and ch=="B"):
            if rs in positions: return name
    return "FR"

paratope = [{"residue": f"{ch}{rs:03d}", "chain": "VH" if ch=="A" else "VL", "region": classify((ch,rs))} for ch,rs in ab_res]
epitope = [f"C{rs:03d}" for _,rs in ag_res]
from collections import Counter
region_counts = Counter(p["region"] for p in paratope)
# antigen region annotation: mature construct position -> domain (full numbering +18)
def domain(mature_pos):
    full = mature_pos + 18
    if full <= 152: return "SRCR(24-152)"
    if full <= 259: return "BTB(153-259)"
    if full <= 360: return "BACK(260-360)"
    return "C-term(361-585)"
dom_counts = Counter(domain(rs) for _,rs in ag_res)

result = {
    "definition": "antibody-antigen residue pair if CA-CA < 6.0 A; same definition for reference and candidates",
    "n_contact_pairs": len(pairs),
    "n_paratope_residues": len(paratope),
    "n_epitope_residues": len(epitope),
    "paratope_region_counts": dict(region_counts),
    "paratope_residues": paratope,
    "epitope_residues": epitope,
    "epitope_domain_counts": dict(dom_counts),
    "epitope_mature_range": [min(r for _,r in ag_res), max(r for _,r in ag_res)] if ag_res else None,
    "cdr_position_map_1based": {k:v for k,v in CDRS.items()},
    "caveat": "epitope mapped on the computational ternary assembly (Boltz2 pair models), not on the study's unavailable reference model; paper-defined E1 could not be verified (NEEDS_INPUT)",
}
json.dump(result, open(out,"w"), indent=2)
print(json.dumps({k:result[k] for k in ("n_contact_pairs","n_paratope_residues","n_epitope_residues","paratope_region_counts","epitope_domain_counts","epitope_mature_range")}, indent=2))
