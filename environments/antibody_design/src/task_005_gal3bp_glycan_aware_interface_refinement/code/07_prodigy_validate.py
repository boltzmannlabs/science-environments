#!/usr/bin/env python3
"""Open-source Prodigy binding-affinity validation for task_005 (fixed CLI)."""
import subprocess, json, os, re

BASE = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy"
STRUCT = os.path.join(BASE, "structures")
REF = os.path.join(BASE, "evidence/reference/task005_ref_bdbv43.pdb")

targets = {
    "BDBV-43 (reference)": REF,
    "task005_cand11": os.path.join(STRUCT, "task005_cand11_complex.pdb"),
    "task005_cand7": os.path.join(STRUCT, "task005_cand7_complex.pdb"),
    "task005_cand17": os.path.join(STRUCT, "task005_cand17_complex.pdb"),
}

def run_prodigy(pdb):
    try:
        r = subprocess.run(["prodigy", pdb, "--selection", "A,B", "C"], capture_output=True, text=True, timeout=300)
        out = r.stdout
        m = re.search(r"Predicted binding affinity \(kcal\.mol-1\):\s*([-\d.]+)", out)
        dg = float(m.group(1)) if m else None
        m2 = re.search(r"Predicted dissociation constant \(M\)[^:]*:\s*([\d.e+-]+)", out)
        kd = float(m2.group(1)) if m2 else None
        m3 = re.search(r"No\. of intermolecular contacts:\s*(\d+)", out)
        n_contacts = int(m3.group(1)) if m3 else None
        return {"dg_kcal_mol": dg, "kd_M": kd, "n_intermolecular_contacts": n_contacts}
    except Exception as e:
        return {"error": str(e)}

results = {}
for name, pdb in targets.items():
    print(f"Running Prodigy on {name}...")
    results[name] = run_prodigy(pdb)
    print(f"  dG={results[name].get('dg_kcal_mol')} kcal/mol, Kd={results[name].get('kd_M')} M, contacts={results[name].get('n_intermolecular_contacts')}")

outpath = os.path.join(BASE, "evidence/prodigy_validation.json")
with open(outpath,"w") as f:
    json.dump({"tool":"Prodigy (open-source PPI affinity estimator)","selection":"A,B (antibody) vs C (LGALS3BP)","results":results}, f, indent=2)
print(f"Saved: {outpath}")
