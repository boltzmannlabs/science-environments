import re, json
from collections import defaultdict

pdb_path = "/home/boltzmann4/.sci/profiles/ab_task_10/workspace/igdesign_repo/examples/5ngv.pdb"

# Parse ATOM/HETATM records
chains = defaultdict(list)  # chain -> list of (resseq, icode, resname, aa1, hetatm)
aa_map = {
 'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
 'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
 'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'
}
with open(pdb_path) as f:
    for line in f:
        if line.startswith(("ATOM","HETATM")):
            het = line.startswith("HETATM")
            chain = line[21]
            resseq = int(line[22:26])
            icode = line[26]
            resname = line[17:20].strip()
            aa = aa_map.get(resname)
            chains[chain].append((resseq, icode, resname, aa, het))

out = {}
for ch in sorted(chains):
    recs = chains[ch]
    # sequence (canonical AA only, skip non-standard)
    seq = "".join(r[3] for r in recs if r[3])
    residues = [(r[0], r[1], r[2]) for r in recs]
    het_count = sum(1 for r in recs if r[4])
    out[ch] = {
        "n_residue_records": len(recs),
        "canonical_aa_count": len(seq),
        "hetatm_records": het_count,
        "residue_range": [residues[0], residues[-1]] if residues else None,
        "sequence": seq
    }
    print(f"Chain {ch}: {len(recs)} records, {len(seq)} canonical AA, {het_count} HETATM")
    print(f"  range: {residues[0]} .. {residues[-1] if residues else None}")
    print(f"  seq: {seq}")
    print()

with open("/home/boltzmann4/.sci/profiles/ab_task_10/workspace/5ngv_chains.json","w") as f:
    json.dump(out, f, indent=2)
print("Saved 5ngv_chains.json")
