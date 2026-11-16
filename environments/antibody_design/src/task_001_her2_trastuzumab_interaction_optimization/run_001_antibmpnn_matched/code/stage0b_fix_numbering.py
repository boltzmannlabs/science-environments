"""Stage 0b: regenerate prepared PDBs with CORRECT per-residue renumbering.

Bug in stage0 write_pdb: incremented residue counter per ATOM line -> each atom its own
residue number (VH 924 "residues"). AntiBMPNN domain detection failed on these files
('detected 0' heavy domains) while the 1MCP control (proper numbering) succeeded.

This script rewrites all prepared inputs with per-residue numbering, SEQRES, TER, END:
  complex_hl_a_seqres.pdb : H=VH, L=VL, A=HER2 (design input)
  complex_fv_her2.pdb     : H,L,A (renumbered)   (Prodigy input)
  antibody_fv.pdb, antigen_her2.pdb (legacy names refreshed)
Verification: per-chain residue counts, sequence identity, CDR window contents.
"""
import hashlib
from collections import defaultdict

INP = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs"

THREE2ONE = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}

VH = "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"
VL = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

lines = open(f"{INP}/1n8z.pdb").read().splitlines()
atoms = []
for ln in lines:
    if ln.startswith("ATOM"):
        n3 = ln[17:20].strip()
        if n3 in THREE2ONE:
            atoms.append(ln)

# per deposited chain, ordered residue keys
dep_res = {}
for ln in atoms:
    ch = ln[21]
    dep_res.setdefault(ch, [])
    key = (int(ln[22:26]), ln[26])
    if key not in dep_res[ch]:
        dep_res[ch].append(key)
for ch in dep_res:
    dep_res[ch].sort()

num_map = {}  # (dep_chain, reskey) -> new 1-based number within chain or None if cropped
CROP = {"A": len(VL), "B": len(VH)}  # deposited chain -> keep first N residues (variable domain)
for ch in dep_res:
    for i, key in enumerate(dep_res[ch], start=1):
        num_map[(ch, key)] = i if ch not in CROP or i <= CROP[ch] else None

def build(deposit_chains, out_chains, path, with_seqres=True):
    """deposit_chains: list of deposited chain ids in output order; out_chains: new ids."""
    ser = 0
    out = ["REMARK   1 task_001 prepared input; source 1N8Z sha256 ed934d36503335c6764b08880f9e50933d99eb13b9bf145339cfcaee150eb21e"]
    if with_seqres:
        for dch, och in zip(deposit_chains, out_chains):
            seq = []
            if dch == "B":
                seq = [k for k, v in THREE2ONE.items() if v == "X"]  # placeholder replaced below
            # use SEQRES from deposited file for each chain
            seq3 = seqres_of(dch)
            if dch in ("A", "B"):
                # variable-domain crop only for antibody chains
                seq3 = seq3[:len(VL)] if dch == "A" else seq3[:len(VH)]
            for i in range(0, len(seq3), 13):
                out.append("SEQRES %3d %s %4d  %s" % (i//13+1, och, len(seq3),
                           " ".join("%3s" % r for r in seq3[i:i+13])))
    for dch, och in zip(deposit_chains, out_chains):
        last = None
        for ln in atoms:
            if ln[21] != dch:
                continue
            key = (int(ln[22:26]), ln[26])
            n = num_map[(dch, key)]
            if n is None:
                continue
            ser += 1
            new = ln[:6] + "%5d" % ser + ln[11:21] + och + "%4d" % n + ln[26:]
            out.append(new)
            last = (ln[17:20], n, ln[26])
        ser += 1
        out.append("TER   %5d      %3s %s%4d%s" % (ser, last[0], och, last[1], last[2]))
    out.append("END")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def seqres_of(ch):
    s = []
    for ln in lines:
        if ln.startswith("SEQRES") and ln[11] == ch:
            for i in range(19, len(ln), 4):
                n3 = ln[i:i+3].strip()
                if n3 in THREE2ONE:
                    s.append(n3)
    return s

h1 = build(["B", "A", "C"], ["H", "L", "A"], f"{INP}/complex_hl_a_seqres.pdb")
print("complex_hl_a_seqres.pdb", h1)
h2 = build(["B", "A", "C"], ["H", "L", "A"], f"{INP}/complex_fv_her2.pdb", with_seqres=False)
print("complex_fv_her2.pdb", h2)
h3 = build(["B", "A"], ["H", "L"], f"{INP}/antibody_fv.pdb", with_seqres=False)
print("antibody_fv.pdb", h3)
h4 = build(["C"], ["A"], f"{INP}/antigen_her2.pdb", with_seqres=False)
print("antigen_her2.pdb", h4)

# verification
def verify(path):
    res = {}
    for ln in open(path):
        if ln.startswith("ATOM"):
            res.setdefault(ln[21], {}).setdefault(int(ln[22:26]), ln[17:20].strip())
    out = {}
    for ch in res:
        s = "".join(THREE2ONE[res[ch][k]] for k in sorted(res[ch]))
        out[ch] = (len(res[ch]), s)
    return out

for p in ("complex_hl_a_seqres.pdb", "complex_fv_her2.pdb", "antibody_fv.pdb", "antigen_her2.pdb"):
    v = verify(f"{INP}/{p}")
    print(p, {c: n for c, (n, s) in v.items()})
    if "H" in v:
        assert v["H"][1] == VH, "VH mismatch in %s" % p
        assert v["L"][1] == VL, "VL mismatch in %s" % p
        # CDR windows
        h = v["H"][1]; l = v["L"][1]
        print("  H1(31-35):", h[30:35], "H2(50-65):", h[49:65], "H3(95-102):", h[94:102])
        print("  L1(24-34):", l[23:34], "L2(50-56):", l[49:56], "L3(89-97):", l[88:97])
    print("  verified OK")
