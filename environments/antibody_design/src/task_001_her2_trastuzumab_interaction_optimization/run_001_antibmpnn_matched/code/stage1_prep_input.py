"""Stage 1 prep: build AntiBMPNN input with SEQRES/TER/END records (worker-domain-detection fix).

Diagnosis: three terminal failures 'Expected exactly one heavy/VHH domain; detected 0' on
ATOM-only files; the 1MCP control (full RCSB file with SEQRES) succeeded. The worker's
domain detection requires SEQRES-bearing input. This script emits a complete-format PDB:
REMARK + SEQRES + ATOM + TER + END, chains H=VH, L=VL, A=HER2, sequential numbering.
"""
import hashlib

INP = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs"

ONE2THREE = {v: k for k, v in {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V"}.items()}

VH = "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"
VL = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

# read source atoms from the ter-format complex (A=VH,B=VL,C=HER2) and rename to H,L,A
src = open(f"{INP}/complex_vhvl_her2_ter.pdb").read().splitlines()
atoms = [l for l in src if l.startswith("ATOM")]
by_chain = {}
order = []
for l in atoms:
    ch = l[21]
    if ch not in by_chain:
        by_chain[ch] = []
        order.append(ch)
    by_chain[ch].append(l)
assert order == ["A", "B", "C"], order

rename = {"A": "H", "B": "L", "C": "A"}  # to final H=VH, L=VL, A=HER2

# HER2 SEQRES from 1N8Z chain C
seqres_her2 = []
for ln in open(f"{INP}/1n8z.pdb"):
    if ln.startswith("SEQRES"):
        if ln[11] == "C":
            for i in range(19, len(ln), 4):
                n3 = ln[i:i+3].strip()
                if n3 in ONE2THREE.values():
                    seqres_her2.append(n3)

def seqres_lines(chain, seq3):
    out = []
    for i in range(0, len(seq3), 13):
        chunk = seq3[i:i+13]
        out.append("SEQRES %3d %s %4d  %s" % (i // 13 + 1, chain, len(seq3),
                                              " ".join("%3s" % r for r in chunk)))
    return out

seq = {"H": [ONE2THREE[a] for a in VH], "L": [ONE2THREE[a] for a in VL], "A": seqres_her2}
# verify SEQRES length vs modeled residues for antibody; HER2 modeled < seqres (unresolved)
modeled = {"H": VH, "L": VL, "A": None}

out = []
out.append("REMARK   1 task_001 AntiBMPNN input; source 1N8Z sha256 ed934d36503335c6764b08880f9e50933d99eb13b9bf145339cfcaee150eb21e")
for c in ("H", "L", "A"):
    out.extend(seqres_lines(c, seq[c]))
ser = 0
for ch in order:
    newch = rename[ch]
    for l in by_chain[ch]:
        ser += 1
        # keep original per-chain numbering (1..N per chain already)
        out.append(l[:6] + "%5d" % ser + l[11:21] + newch + l[22:])
    ser += 1
    last = by_chain[ch][-1]
    out.append("TER   %5d      %3s %s%4s%s" % (ser, last[17:20], rename[ch], last[22:26], last[26]))
out.append("END")
with open(f"{INP}/complex_hl_a_seqres.pdb", "w") as f:
    f.write("\n".join(out) + "\n")
h = hashlib.sha256(open(f"{INP}/complex_hl_a_seqres.pdb", "rb").read()).hexdigest()
print("complex_hl_a_seqres.pdb sha256:", h)

# verify: modeled residue identity matches SEQRES for H and L
ONE2THREE_INV = {v: k for k, v in ONE2THREE.items()}
def modeled_seq(lines, ch):
    res = {}
    for l in lines:
        if l.startswith("ATOM") and l[21] == ch:
            res[int(l[22:26])] = l[17:20]
    return "".join(ONE2THREE_INV[res[k]] for k in sorted(res))

lines2 = open(f"{INP}/complex_hl_a_seqres.pdb").read().splitlines()
mh = modeled_seq(lines2, "H")
ml = modeled_seq(lines2, "L")
print("H modeled==VH:", mh == VH, len(mh))
print("L modeled==VL:", ml == VL, len(ml))
ma = modeled_seq(lines2, "A")
her2_1 = "".join({v: k for k, v in ONE2THREE.items()}[r] for r in seqres_her2)
print("A modeled length:", len(ma), "of SEQRES", len(her2_1))
