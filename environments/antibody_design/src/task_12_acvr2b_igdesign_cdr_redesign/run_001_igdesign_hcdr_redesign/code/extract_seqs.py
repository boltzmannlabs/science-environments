from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import PPBuilder, is_aa
import warnings, json
warnings.filterwarnings('ignore')

pdb_path = "/home/boltzmann4/.sci/profiles/ab_task_10/workspace/igdesign_repo/examples/5ngv.pdb"
parser = PDBParser(QUIET=True)
structure = parser.get_structure("5ngv", pdb_path)

model = structure[0]
out = {}
for chain in model:
    chid = chain.id
    # Build sequence from residues, canonical AA only
    seq = ""
    resinfo = []
    for res in chain.get_residues():
        resname = res.get_resname()
        if is_aa(resname, standard=True):
            aa3to1 = {
            'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
            'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
            'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
            seq += aa3to1[resname]
            resinfo.append((res.id[1], resname))
    out[chid] = {"length": len(seq), "sequence": seq,
                 "residues": [r[0] for r in resinfo]}
    print(f"=== Chain {chid} ({len(seq)} residues) ===")
    print(seq)
    print()

with open("/home/boltzmann4/.sci/profiles/ab_task_10/workspace/5ngv_sequences.json","w") as f:
    json.dump(out, f, indent=2)
print("Saved 5ngv_sequences.json")
