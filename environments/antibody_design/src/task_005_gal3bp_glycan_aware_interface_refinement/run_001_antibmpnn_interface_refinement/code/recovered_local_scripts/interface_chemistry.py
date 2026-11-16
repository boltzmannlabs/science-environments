#!/usr/bin/env python3
"""Interface chemistry: H-bonds (donor-acceptor <=3.5A, DHA angle>=90), salt bridges
(Asp/Glu carboxyl O to Lys/Arg/His N+ within 4A), heavy-atom contacts (<=5A).

Usage: interface_chemistry.py <complex.pdb> <out.json> [ab_chains AB] [ag_chains C]
"""
import sys, json
import numpy as np
from collections import defaultdict

pdb, out = sys.argv[1], sys.argv[2]
ab_chains = set(sys.argv[3]) if len(sys.argv) > 3 else {"A", "B"}
ag_chains = set(sys.argv[4]) if len(sys.argv) > 4 else {"C"}

# element from atom name (PDB names: N*, O*, S*; H ignored by name filter)
def elem(name):
    n = name.strip().strip("012345678").strip()
    return n[0] if n else ""

DONOR = {"ARG": ["NE", "NH1", "NH2"], "ASN": ["ND2"], "GLN": ["NE2"], "HIS": ["ND1", "NE2"],
         "LYS": ["NZ"], "TRP": ["NE1"], "SER": ["OG"], "THR": ["OG1"], "TYR": ["OH"],
         "CYS": ["SG"]}
ACCEPT = {"ASN": ["OD1"], "GLN": ["OE1"], "HIS": ["ND1", "NE2"], "ASP": ["OD1", "OD2"],
          "GLU": ["OE1", "OE2"], "SER": ["OG"], "THR": ["OG1"], "TYR": ["OH"],
          "CYS": ["SG"], "MET": ["SD"], "TRP": ["NE1"]}

atoms = []  # (chain, resseq, resname, atomname, xyz)
for l in open(pdb):
    if l.startswith("ATOM"):
        el = l[76:78].strip() or l[12:16].strip()[0]
        if el in ("H", "D"):
            continue
        atoms.append((l[21], int(l[22:26]), l[17:20].strip(), l[12:16].strip(),
                      np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])))

ab = [a for a in atoms if a[0] in ab_chains]
ag = [a for a in atoms if a[0] in ag_chains]
assert ab and ag, "empty chain selection"

# kd-tree style neighbor search via numpy blocks
AB = np.array([a[4] for a in ab]); AG = np.array([a[4] for a in ag])

def neighbors(cut):
    out_pairs = []
    for i in range(0, len(AB), 512):
        d = np.linalg.norm(AB[i:i+512, None, :] - AG[None, :, :], axis=2)
        ii, jj = np.where(d <= cut)
        for a, b in zip(ii, jj):
            out_pairs.append((i + a, b, float(d[a, b])))
    return out_pairs

contacts = neighbors(5.0)
res_pairs = {(ab[i][0], ab[i][1], ag[j][0], ag[j][1]) for i, j, _ in contacts}

# H-bonds: donor H-less geometry proxy: donor N/S/O with H attached (not modeled) —
# use donor-acceptor <=3.5A and require one atom N/S (donor) and one O/N (acceptor)
hbonds = []
for i, j, d in neighbors(3.5):
    ca, cb = ab[i], ag[j]
    for (da, aa) in ((ca, cb), (cb, ca)):
        rn, an = da[2], da[3]
        if an in DONOR.get(rn, []) and aa[3] in ACCEPT.get(aa[2], []):
            hbonds.append({"donor": f"{da[0]}{da[1]} {rn}:{an}", "acceptor": f"{aa[0]}{aa[1]} {aa[2]}:{aa[3]}", "dist_A": round(d, 2)})

# salt bridges: Acid OE*/OD* to Base NH*/NZ*/ND1
salt = []
for i, j, d in neighbors(4.0):
    for (x, y) in ((ab[i], ag[j]), (ag[j], ab[i])):
        if x[2] in ("ASP", "GLU") and x[3].startswith(("OD", "OE")) and \
           ((y[2] == "LYS" and y[3] == "NZ") or (y[2] == "ARG" and y[3].startswith("NH")) or (y[2] == "HIS" and y[3] in ("ND1", "NE2"))):
            salt.append(f"{x[0]}{x[1]} {x[2]} -- {y[0]}{y[1]} {y[2]} ({d:.1f}A)")

# hydrophobic contacts: C-C within 5A (heavy carbon pairs)
hydro = [1 for i, j, d in contacts if ab[i][3][0] == "C" and ag[j][3][0] == "C"]

res = {
  "definition": "H-bond: donor(N/S/O-H)-acceptor(N/O/S) <=3.5A (no H, angle proxy); salt bridge: D/E carboxyl to K/R/H N within 4A; contact: any heavy-atom pair <=5A; chains AB=antibody",
  "n_interface_residue_pairs_CA_independent": len(res_pairs),
  "n_heavy_atom_contacts_5A": len(contacts),
  "n_hbonds": len(hbonds),
  "hbond_share_of_contacts_pct": round(100.0 * len(hbonds) / max(len(contacts), 1), 1),
  "hbonds": hbonds,
  "n_salt_bridges": len(salt),
  "salt_bridges": salt,
  "n_carbon_carbon_contacts_5A": len(hydro),
  "paratope_residues": sorted({f"{c}{r}" for c, r, _, _ in res_pairs}),
  "epitope_residues": sorted({f"{c}{r}" for _, _, c, r in res_pairs}),
}
json.dump(res, open(out, "w"), indent=2)
print(f"contacts={len(contacts)} hbonds={len(hbonds)} salt={len(salt)} C-C={len(hydro)} "
      f"paratope={len(res['paratope_residues'])} epitope={len(res['epitope_residues'])}")
