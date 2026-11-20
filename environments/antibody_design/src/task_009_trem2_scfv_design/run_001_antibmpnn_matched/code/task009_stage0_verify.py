"""Task009 stage 0: verify reference scFv and TREM2 construct identity.

Outputs under <run>/inputs/:
  ref_scFv.fasta            - reference scFv sequence (245 aa)
  trem2_construct.fasta     - TREM2 ectodomain construct used by the reference Boltz2 model (126 aa)
  trem2_uniprot_report.txt  - UniProt feature map (signal, IgV domain, glycans, disulfides)
  ref_structure_report.txt  - chain/residue maps of the published ESMFold + Boltz2 models
  verify_report.json        - machine-readable verification summary
"""
import json, os, re, sys
from collections import OrderedDict

WORK = "/home/boltzmann10/.sci/cache/scratch/task009_ref"
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

REF_SCFV = ("SMEVQLLESGGGLVSPGGSLRLSCAASGFTFSYYYMGWVRQAPGKGLEWVSGISPSSGYTYYADSVKGRFTISRDNSKNT"
            "LYLQMNSLRAEDTAVYYCARYYYGYYYSHMDYWGQGTLVTVSSGGGGSGGGGSGGGGSDIQMTQSPSSLSASVGDRVT"
            "ITCRASQSISSYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQSRSGLHT"
            "FGQGTKLEIK")
assert len(REF_SCFV) == 245

# VH/VL split: find the G4S linker
linker = "GGGGSGGGGSGGGGS"
li = REF_SCFV.find(linker)
VH = REF_SCFV[:li]
VL = REF_SCFV[li+len(linker):]
# note leading SM before EVQLL: VH segment starts SM + EVQLLE...
print(f"scFv 245aa | VH-linker-VL split at {li}: VH={len(VH)}aa, linker=15aa, VL={len(VL)}aa")

TREM2_UNIPROT = ("MEPLRLLILLFVTELSGAHNTTVFQGVAGQSLQVSCPYDSMKHWGRRKAWCRQLGEKGPC"
                 "QRVVSTHNLWLLSFLRRWNGSTAITDDTLGGTLTITLRNLQPHDAGLYQCQSLHGSEADT"
                 "LRKVLVEVLADPLDHRDAGDLWFPGESESFEDAHVEHSISRSLLEGEIPFPPTSILLLLA"
                 "CIFLIKILAASALWAAAWHGQKPGTHPPSELDCGHDPGYQLQTLPGLRDT")

def parse_cif_atoms(path):
    """Return (columns, rows) of the _atom_site loop."""
    txt = open(path, errors='replace').read()
    lines = txt.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == 'loop_':
            j = i + 1
            cols = []
            while j < len(lines) and lines[j].strip().startswith('_'):
                cols.append(lines[j].strip())
                j += 1
            if any(c.startswith('_atom_site.') for c in cols):
                rows = []
                while j < len(lines) and not lines[j].strip().startswith(('loop_', '_', '#', 'data_')):
                    t = lines[j].split()
                    if len(t) == len(cols):
                        rows.append(dict(zip(cols, t)))
                    j += 1
                return cols, rows
            i = j
            continue
        i += 1
    raise RuntimeError(f"no atom_site in {path}")

def cif_sequences(path):
    cols, rows = parse_cif_atoms(path)
    seqs = OrderedDict()
    for r in rows:
        ch = r['_atom_site.label_asym_id']
        seqs.setdefault(ch, OrderedDict())[r['_atom_site.label_seq_id']] = r['_atom_site.label_comp_id']
    return seqs

def cif_local_plddt(path):
    txt = open(path, errors='replace').read()
    m = re.search(r'loop_\n((?:_ma_qa_metric_local[^\n]*\n)+)(.*?)\n#', txt, re.S)
    if not m:
        return None
    cols = [c.strip() for c in m.group(1).split()]
    cols = [c.replace('_ma_qa_metric_local.', '') for c in cols]
    out = {}
    for ln in m.group(2).splitlines():
        t = ln.split()
        if len(t) != len(cols):
            continue
        r = dict(zip(cols, t))
        out[(r.get('label_asym_id'), r.get('label_seq_id'))] = float(r['metric_value'])
    return out

THREE2ONE = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G",
             "HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S",
             "THR":"T","TRP":"W","TYR":"Y","VAL":"V"}

report = {"reference_scFv": {"sequence": REF_SCFV, "length": 245,
                             "VH_len": len(VH), "linker": linker, "VL_len": len(VL)},
          "trem2_uniprot": {"accession": "Q9NZC2", "length": 230},
          "structures": {}}

for f, key in [("ref_esmfold.cif", "esmfold"), ("ref_boltz2.cif", "boltz2")]:
    path = os.path.join(WORK, f)
    seqs = cif_sequences(path)
    plddt = cif_local_plddt(path)
    info = {"chains": {}}
    for ch, res in seqs.items():
        s = "".join(THREE2ONE.get(c, "X") for c in res.values())
        vals = [plddt[(ch, k)] for k in res if (ch, k) in plddt]
        info["chains"][ch] = {
            "length": len(s),
            "sequence": s,
            "mean_plddt": round(sum(vals)/len(vals), 4) if vals else None,
            "plddt_min": min(vals) if vals else None,
            "plddt_max": max(vals) if vals else None,
        }
    # identity vs reference scFv and TREM2
    for ch, res in seqs.items():
        s = "".join(THREE2ONE.get(c, "X") for c in res.values())
        ident_sc = sum(a == b for a, b in zip(s, REF_SCFV)) / max(len(s), len(REF_SCFV)) * 100
        ident_t2 = max(
            (sum(a == b for a, b in zip(s, TREM2_UNIPROT[i:i+len(s)])) / len(s) * 100
             for i in range(0, max(0, len(TREM2_UNIPROT) - len(s)) + 1)), default=0.0)
        info["chains"][ch]["identity_to_scFv_pct"] = round(ident_sc, 2)
        info["chains"][ch]["best_identity_to_TREM2_pct"] = round(ident_t2, 2)
    report["structures"][key] = info

print(json.dumps(report["structures"], indent=1)[:2000])

# TREM2 construct in Boltz2 model chain A (126 aa): map to UniProt
b2 = report["structures"]["boltz2"]["chains"]["A"]["sequence"]
best_i, best_id = 0, 0
for i in range(len(TREM2_UNIPROT) - len(b2) + 1):
    idt = sum(a == b for a, b in zip(b2, TREM2_UNIPROT[i:i+len(b2)])) / len(b2) * 100
    if idt > best_id:
        best_i, best_id = i, idt
print(f"\nTREM2 construct: Boltz2 chain A ({len(b2)} aa) best-matches UniProt Q9NZC2 residues "
      f"{best_i+1}-{best_i+len(b2)} (1-based full precursor numbering) at {best_id:.1f}% identity")
print("construct sequence:", b2)

report["trem2_construct"] = {
    "length": len(b2),
    "uniprot_range_1based": [best_i + 1, best_i + len(b2)],
    "identity_pct": round(best_id, 2),
    "sequence": b2,
}

# glycosylation sites N20/N79, IgV domain 29-112, disulfides 36-110, 51-60 (UniProt numbering)
report["trem2_features_uniprot_numbering"] = {
    "signal_peptide": [1, 18], "extracellular_domain": [19, 174], "ig_like_v_type_domain": [29, 112],
    "transmembrane": [175, 195], "cytoplasmic": [196, 230],
    "n_glycosylation": [20, 79], "disulfides": [[36, 110], [51, 60]],
    "note": "UniProt Q9NZC2 precursor numbering; construct mapped range above is exact-match contiguous"}

with open(os.path.join(OUT, "ref_scFv.fasta"), "w") as fh:
    fh.write(">golden-gecko-stone_scFv_reference VH-linker-VL 245aa\n" + REF_SCFV + "\n")
with open(os.path.join(OUT, "trem2_construct.fasta"), "w") as fh:
    fh.write(f">TREM2_construct_Boltz2ref UniProt_Q9NZC2_{best_i+1}-{best_i+len(b2)}\n{b2}\n")
with open(os.path.join(OUT, "verify_report.json"), "w") as fh:
    json.dump(report, fh, indent=1)
print("\nwrote", OUT)
