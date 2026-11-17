#!/usr/bin/env python
"""Prepare IgDesign input: ref_rank1_clean + proper 3-letter SEQRES records."""
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

one3 = {'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','Q':'GLN','E':'GLU','G':'GLY','H':'HIS',
        'I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE','P':'PRO','S':'SER','T':'THR','W':'TRP',
        'Y':'TYR','V':'VAL'}
SRC = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/gal3bp_w1_ref_complex/ref_rank1_clean.pdb"
DST = "/home/boltzmann10/.sci/cache/scratch/gal3bp_run/igdesign_input_complex.pdb"

s = PDBParser(QUIET=True).get_structure("x", SRC)
hdr = ["REMARK   1 task_005 IgDesign input: ref_rank1_clean + SEQRES 3-letter (A=VH B=VL C=Gal3BP)"]
for ch in s[0]:
    one = "".join(seq1(r.resname) for r in ch if r.id[0] == " ")
    seq3 = [one3[c] for c in one]
    ser = 1
    for i in range(0, len(seq3), 13):
        chunk = seq3[i:i+13]
        hdr.append(f"SEQRES {ser:>3} {ch.id} {len(seq3):>4}  " + " ".join(f"{c:>3}" for c in chunk))
        ser += 1
atoms = [l.rstrip("\n") for l in open(SRC) if l.startswith(("ATOM", "TER", "END"))]
open(DST, "w").write("\n".join(hdr + atoms) + "\n")
print("written", DST, "| SEQRES lines:", len(hdr) - 1)
