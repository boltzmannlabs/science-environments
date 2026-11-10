#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from rdkit import Chem
ROOT = Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inp=ROOT/'inputs'; edge_rows=list(csv.DictReader((inp/'ptp1b_edges.csv').open()))
    edge=next(r for r in edge_rows if r['Ligand 1']=='23477' and r['Ligand 2']=='23482')
    mols={}
    for ident in ('23477','23482'):
        p=inp/f'ligand_{ident}.sdf'; m=next(iter(Chem.SDMolSupplier(str(p),removeHs=False)))
        mols[ident]={'present':p.is_file(),'sha256':digest(p),'atoms':m.GetNumAtoms() if m else 0,'valid':m is not None}
    protein=inp/'ptp1b_2QBS_protein.pdb'; atoms=[x for x in protein.read_text().splitlines() if x.startswith(('ATOM','HETATM'))]
    ddg=float(edge['ddG (kcal/mol)'])
    result={'protein':{'pdb_id':'2QBS','present':protein.is_file(),'sha256':digest(protein),'atom_records':len(atoms)},'ligands':mols,'edge':{'ligand_a':edge['Ligand 1'],'ligand_b':edge['Ligand 2'],'ddg_kcal_mol':round(ddg, 2),'direction':'23477->23482'},'status':'PASS' if len(atoms)>0 and all(x['valid'] for x in mols.values()) and abs(ddg + 1.16) < 1e-8 else 'REVIEW','scope':'source identity and edge validation; no production FEP claim'}
    (ROOT/'evaluation').mkdir(exist_ok=True); (ROOT/'evaluation/input_validation.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2)); return result
if __name__=='__main__': main()
