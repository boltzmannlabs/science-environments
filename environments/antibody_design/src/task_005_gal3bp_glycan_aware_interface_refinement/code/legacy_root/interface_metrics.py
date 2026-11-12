#!/usr/bin/env python
"""Task 005: matched-conditions interface metrics — BDBV-43 reference vs
designed CDR-H3 candidates, each bound to full-length LGALS3BP (Boltz2 model 0).

Contact definitions (heavy-atom PDBs, no H):
  - Interface residue pair: Cα–Cα distance < 8.0 Å
  - vdW contact: any heavy-atom pair < 4.5 Å
  - Hydrogen bond: N/O donor–acceptor pair < 3.5 Å (heavy-atom proxy;
    no explicit H in Boltz2 PDB output)
Antibody = chains A (VH) + B (VL); antigen = chain C (LGALS3BP).
"""
import sys, os, json, glob, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import metrics as m

BASE = "/home/boltzmann10/shared_metric_tools/results/task005_boltz2"
TAGS = ["ref_bdbv43", "cand11", "cand7", "cand17"]
CA_CA = 8.0; VDW = 4.5; HBOND = 3.5
DON_ACC = set("NO")

def atoms_of(atoms, chains):
    return [a for a in atoms if a[0] in chains]

def vec(a): return (a[4], a[5], a[6])

def ca_dict(atoms):
    d = {}
    for a in atoms:
        if a[3] == "CA": d.setdefault(a[0], {})[a[1]] = vec(a)
    return d

def dist(x1, x2):
    return math.sqrt(sum((x1[i]-x2[i])**2 for i in range(3)))

def analyze(tag):
    pat = f"{BASE}/boltz_results_task005_{tag}/predictions/task005_{tag}/task005_{tag}_model_0.pdb"
    if not glob.glob(pat): return None
    atoms = m.parse_pdb(glob.glob(pat)[0])
    ab = atoms_of(atoms, "AB"); ag = atoms_of(atoms, "C")
    # interface residue pairs via Cα-Cα
    caa, cag = ca_dict(ab), ca_dict(ag)
    iface_pairs = set()
    for ch in ("A","B"):
        for rr, ca in caa[ch].items():
            for rg, cb in cag["C"].items():
                if dist(ca, cb) < CA_CA: iface_pairs.add((ch, rr, rg))
    # vdW + H-bond atom pairs
    vdw, hb = set(), set()
    ab_list, ag_list = ab, ag
    for a1 in ab_list:
        v1 = vec(a1)
        for a2 in ag_list:
            d = dist(v1, vec(a2))
            if d < VDW: vdw.add((a1[0],a1[1],a1[3],a2[1],a2[3]))
            if d < HBOND and a1[3][0] in "NO" and a2[3][0] in "NO":
                hb.add((a1[0],a1[1],a1[3],a2[1],a2[3]))
    # confidence
    cpat = f"{BASE}/boltz_results_task005_{tag}/predictions/task005_{tag}/confidence_task005_{tag}_model_0.json"
    conf = json.load(open(glob.glob(cpat)[0]))
    return {
        "tag": tag,
        "ipTM": round(float(conf["iptm"]),3),
        "pLDDT": round(float(conf["complex_plddt"]),3),
        "pDE": round(float(conf["complex_pde"]),3),
        "interface_residue_pairs": len(iface_pairs),
        "vdw_atom_pairs": len(vdw),
        "hbond_atom_pairs": len(hb),
        "hbond_share_of_contacts": round(len(hb)/(len(vdw)) if vdw else 0, 4),
        "antigen_residues_in_interface": len({x[2] for x in iface_pairs}),
    }

out = [analyze(t) for t in TAGS]
out = [o for o in out if o]
for o in out: print(json.dumps(o))
json.dump({"definitions": {"ca_ca": CA_CA, "vdw": VDW, "hbond": HBOND, "note": "heavy-atom PDBs, no explicit H; hbond = N/O pair <3.5A proxy"}, "results": out},
          open("/home/boltzmann10/shared_metric_tools/results/task005_interface_metrics.json","w"), indent=1)
