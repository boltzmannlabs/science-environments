import json
from Bio.PDB import PDBParser
base="/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results"
parser=PDBParser(QUIET=True)
struct=parser.get_structure("1n8z", base+"/1N8Z_deposited_complex.pdb")
chains={ch.get_id():ch for ch in struct.get_chains()}
three_to_one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
def chain_seq1(ch, n):
    res=[r for r in ch.get_residues() if r.get_id()[0]==' ']
    return ''.join(three_to_one[r.get_resname()] for r in res[:n]), [r.get_id()[1] for r in res[:n]]
vh_seq, vh_ids = chain_seq1(chains['B'], 120)
vl_seq, vl_ids = chain_seq1(chains['A'], 107)
cands=json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json"))["shortlist"]
ref_vh=cands[0]["heavy"]; ref_vl=cands[0]["light"]
print("1N8Z VH (first 120):", vh_seq)
print("cand  VH (AB_08)    :", ref_vh)
print("VH match:", sum(1 for a,b in zip(vh_seq,ref_vh) if a==b), "/", len(vh_seq))
print("1N8Z VL (first 107):", vl_seq)
print("cand  VL (AB_08)    :", ref_vl)
print("VL match:", sum(1 for a,b in zip(vl_seq,ref_vl) if a==b), "/", len(vl_seq))
print("VH residue IDs (first 5):", vh_ids[:5], "last 5:", vh_ids[-5:])
print("VL residue IDs (first 5):", vl_ids[:5], "last 5:", vl_ids[-5:])
