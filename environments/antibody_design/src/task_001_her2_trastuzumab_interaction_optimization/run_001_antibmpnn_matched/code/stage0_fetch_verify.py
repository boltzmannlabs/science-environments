"""Stage 0: fetch PDB 1N8Z, verify chains/sequences, map CDRs, split inputs.

Deposited layout (verified from header):
  A = trastuzumab Fab light chain (VL+CL, 214 aa, Kabat-consistent)
  B = trastuzumab Fab heavy chain (VH+CH1, 220 aa, Kabat-consistent)
  C = HER2 ECD (PDB 1-607 = UniProt P04626 23-629; 581 modeled, 26 unresolved)
Biological assembly = as-deposited A+B+C (identity BIOMT).

Outputs (inputs/):
  1n8z.pdb                as-deposited file (hash-pinned)
  1n8z_sequence_report.txt verification report
  complex_fv_her2.pdb     Fv(VH+VL) + HER2, renumbered: H=VH 1-120, L=VL 1-107, A=HER2 1-581 (modeled only)
  antibody_fv.pdb         chains H,L in the same frame (for CDR-conditioned design)
  antigen_her2.pdb        chain A (HER2 modeled residues) PDB
  crystal_contacts.csv    deposited-complex contact map (any heavy atom < 6 A)
  reference_sequences.json VH/VL/HER2 construct sequences + hashes
"""
import hashlib
import json
import os
import urllib.request
from collections import defaultdict

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = os.path.join(WORK, "inputs")
os.makedirs(INPUTS, exist_ok=True)

PDB_URL = "https://files.rcsb.org/download/1N8Z.pdb"
OUT_ASIS = os.path.join(INPUTS, "1n8z.pdb")

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

# --- fetch -------------------------------------------------------------------
if not os.path.exists(OUT_ASIS):
    req = urllib.request.Request(PDB_URL, headers={"User-Agent": "sci-agent-task001/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(OUT_ASIS, "wb") as fh:
        fh.write(r.read())
print("1n8z.pdb bytes=%d sha256=%s" % (os.path.getsize(OUT_ASIS), sha256(OUT_ASIS)))

lines = open(OUT_ASIS).read().splitlines()

seqres = defaultdict(list)
for ln in lines:
    if ln.startswith("SEQRES"):
        ch = ln[11]
        for i in range(19, len(ln), 4):
            n3 = ln[i:i+3].strip()
            if n3 in THREE2ONE:
                seqres[ch].append(n3)

# ATOM records of standard residues
atoms = []  # (chain, reskey, resname, x, y, z, line)
for ln in lines:
    if ln.startswith("ATOM"):
        n3 = ln[17:20].strip()
        if n3 not in THREE2ONE:
            continue
        atoms.append((
            ln[21], (int(ln[22:26]), ln[26]), n3,
            float(ln[30:38]), float(ln[38:46]), float(ln[46:54]), ln))

chain_res = defaultdict(list)
seen = set()
for ch, rk, n3, x, y, z, ln in atoms:
    if (ch, rk) not in seen:
        seen.add((ch, rk))
        chain_res[ch].append(rk)
for ch in chain_res:
    chain_res[ch].sort()

report = []
report.append("PDB 1N8Z input verification")
report.append("download: %s" % PDB_URL)
report.append("sha256: %s" % sha256(OUT_ASIS))
report.append("chains (COMPND): A=trastuzumab light, B=trastuzumab heavy, C=HER2 ECD")
report.append("DBREF C 1-607 = UniProt P04626 23-629; SSBOND intra-chain only (A23-88, A134-194, B22-96, B147-203)")
report.append("")
for ch in sorted(seqres):
    s = "".join(THREE2ONE[n] for n in seqres[ch])
    modeled = chain_res.get(ch, [])
    gaps = []
    prev = None
    for rk in modeled:
        if prev is not None and rk[1] == " " and rk[0] != prev + 1:
            gaps.append("%d-%d" % (prev + 1, rk[0] - 1))
        prev = rk[0]
    report.append("chain %s: SEQRES %d aa, modeled %d residues (%s-%s)%s" % (
        ch, len(seqres[ch]), len(modeled), modeled[0][0], modeled[-1][0],
        "; unresolved internal: %s" % ", ".join(gaps) if gaps else ""))
    report.append("  SEQRES: %s" % s)

# --- reference sequence identity ---------------------------------------------
TRA_VH = "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"
TRA_VL = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

resname = defaultdict(dict)
for ch, rk, n3, x, y, z, ln in atoms:
    resname[ch][rk] = n3

def obs_seq_chain(ch):
    return "".join(THREE2ONE[resname[ch][rk]] for rk in chain_res[ch])

heavy_obs = obs_seq_chain("B")
light_obs = obs_seq_chain("A")
vh_len, vl_len = len(TRA_VH), len(TRA_VL)
vh_obs = heavy_obs[:vh_len]
vl_obs = light_obs[:vl_len]
report.append("")
report.append("trastuzumab identity checks (variable domains, deposited numbering 1-%d/%d):" % (vh_len, vl_len))
report.append("  chain B[1:%d] vs trastuzumab VH: %d/%d identical (%.1f%%)" % (
    vh_len, sum(a == b for a, b in zip(vh_obs, TRA_VH)), vh_len,
    100 * sum(a == b for a, b in zip(vh_obs, TRA_VH)) / vh_len))
report.append("  chain A[1:%d] vs trastuzumab VL: %d/%d identical (%.1f%%)" % (
    vl_len, sum(a == b for a, b in zip(vl_obs, TRA_VL)), vl_len,
    100 * sum(a == b for a, b in zip(vl_obs, TRA_VL)) / vl_len))
report.append("  chain B VH observed: %s" % vh_obs)
report.append("  chain A VL observed: %s" % vl_obs)

# Kabat anchor checks on deposited numbering
anchors = {
    "B": {22: "CYS", 36: "TRP", 92: "CYS", 96: "CYS", 103: "TRP", 105: "TRP"},
    "A": {23: "CYS", 35: "TRP", 88: "CYS", 98: "PHE"},
}
report.append("")
report.append("Kabat anchor check on deposited numbering:")
for ch, m in anchors.items():
    for pos, want in sorted(m.items()):
        got = resname[ch].get((pos, " "), "?")
        report.append("  chain %s %d: %s (expect %s)%s" % (
            ch, pos, got, want, "" if got == want else "  <-- MISMATCH"))

# --- split PDBs --------------------------------------------------------------
def write_pdb(path, selection, rename):
    """selection: set of (chain,reskey); rename: chain->new id; renumber sequential per chain."""
    counters = defaultdict(int)
    out = []
    for ch, rk, n3, x, y, z, ln in atoms:
        if (ch, rk) not in selection:
            continue
        newch = rename[ch]
        counters[newch] += 1
        newnum = counters[newch]
        out.append(ln[:21] + newch + ("%4d" % newnum) + ln[26:])
    with open(path, "w") as fh:
        fh.write("REMARK   1 task_001 prepared input; source 1N8Z sha256=%s\n" % sha256(OUT_ASIS))
        fh.write("\n".join(out) + "\n")
    lengths = defaultdict(int)
    for ch, rk, n3, x, y, z, ln in atoms:
        if (ch, rk) in selection:
            lengths[rename[ch]] += 1
    res_counts = defaultdict(int)
    for ch, rk in selection:
        res_counts[rename[ch]] += 1
    return len(out), dict(res_counts)

vh_sel = set(("B", rk) for rk in chain_res["B"] if rk[0] <= vh_len)
vl_sel = set(("A", rk) for rk in chain_res["A"] if rk[0] <= vl_len)
ag_sel = set(("C", rk) for rk in chain_res["C"])

complex_sel = vh_sel | vl_sel | ag_sel
n, counts = write_pdb(os.path.join(INPUTS, "complex_fv_her2.pdb"), complex_sel,
                      {"B": "H", "A": "L", "C": "A"})
report.append("")
report.append("complex_fv_her2.pdb: %d atom lines; chain lengths (renumbered 1..N): %s" % (n, counts))
n, counts = write_pdb(os.path.join(INPUTS, "antibody_fv.pdb"), vh_sel | vl_sel, {"B": "H", "A": "L"})
report.append("antibody_fv.pdb: %d atom lines; %s" % (n, counts))
n, counts = write_pdb(os.path.join(INPUTS, "antigen_her2.pdb"), ag_sel, {"C": "A"})
report.append("antigen_her2.pdb: %d atom lines; %s" % (n, counts))

# --- crystal contact map (any heavy atom < 6 A) -------------------------------
ag_atoms = [(x, y, z, rk) for ch, rk, n3, x, y, z, ln in atoms if ch == "C"]
ab_atoms = [(ch, rk, n3, x, y, z) for ch, rk, n3, x, y, z, ln in atoms if ch in ("A", "B")]
contacts = []
for ch, rk, n3, x, y, z in ab_atoms:
    for ax, ay, az, ark in ag_atoms:
        if (x-ax)**2 + (y-ay)**2 + (z-az)**2 < 36.0:
            contacts.append((ch, rk, n3, ark))
            break
ab_contact_res = sorted(set((c, r) for c, r, n, a in contacts))
ag_contact_res = sorted(set(a for c, r, n, a in contacts))
report.append("")
report.append("Deposited-complex contacts (<6 A, any heavy atom):")
report.append("  antibody contact residues (%d): %s" % (len(ab_contact_res), ", ".join(
    "%s%d%s" % (c, r[0], r[1].strip()) for c, r in ab_contact_res)))
report.append("  HER2 contact residues (%d): %s" % (
    len(ag_contact_res), ", ".join(str(r[0]) for r in ag_contact_res)))

with open(os.path.join(INPUTS, "crystal_contacts.csv"), "w") as fh:
    fh.write("chain,residue_pdb,resname,contact_type\n")
    for c, r, n, a in sorted(set(contacts)):
        fh.write("%s,%d%s,%s,antibody-antigen<6A\n" % (c, r[0], r[1].strip(), n))
    for r in ag_contact_res:
        fh.write("A,%d,HER2_contact,antibody-antigen<6A\n" % r[0])

# --- reference sequences json -------------------------------------------------
her2_seqres = "".join(THREE2ONE[n] for n in seqres["C"])
ref = {
    "source": "PDB 1N8Z",
    "source_sha256": sha256(OUT_ASIS),
    "VH": TRA_VH, "VL": TRA_VL,
    "VH_observed_in_1n8z": vh_obs, "VL_observed_in_1n8z": vl_obs,
    "HER2_construct_seqres_607aa": her2_seqres,
    "HER2_uniprot_mapping": "PDB C 1-607 = P04626 23-629",
    "Fv_chains_in_prepared_pdb": {"H": "VH 1-%d" % vh_len, "L": "VL 1-%d" % vl_len, "A": "HER2 modeled 1-%d renumbered" % len(ag_sel)},
}
with open(os.path.join(INPUTS, "reference_sequences.json"), "w") as fh:
    json.dump(ref, fh, indent=2)
for k in ("VH", "VL"):
    print(k, "sha256:", hashlib.sha256(ref[k].encode()).hexdigest())

with open(os.path.join(INPUTS, "1n8z_sequence_report.txt"), "w") as fh:
    fh.write("\n".join(report) + "\n")
print("\n".join(report))
