#!/usr/bin/env python3
"""Bounded geometry/clash checks for the prepared demo ligand-site fixture."""
from __future__ import annotations
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def distance(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def main():
    d=json.loads((ROOT/"cases/GEO-015-protein-ligand/ligand_site.json").read_text()); ligand=d["ligand"]["atoms"]; site=d["site"]["atoms"]; threshold=d["reference"]["hard_clash_threshold_angstrom"]
    contacts=[]; clashes=[]
    for la in ligand:
        for sa in site:
            dist=distance(la["xyz"],sa["xyz"])
            contacts.append({"ligand_element":la["element"],"residue":sa["residue"],"distance_angstrom":dist})
            if dist < threshold: clashes.append(contacts[-1])
    out={"case":"GEO-015-protein-ligand","status":"pass" if not clashes else "review","topology_present":bool(d.get("topology")),"contacts":contacts,"clashes":clashes,"note":"Demo prepared geometry; not a production protein/QM-MM qualification."}
    p=ROOT/"reports/protein_ligand"; p.mkdir(parents=True,exist_ok=True); (p/"summary.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out))
if __name__=="__main__": main()
