import pandas as pd, re, json, hashlib
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import three_to_index, index_to_one

ROOT = "retained-private-evidence/sun-leh-discoveryrsi"
with open(ROOT + "/inputs/1NWW.pdb") as f:
    pdb = f.read()
sbc = {}
for L in pdb.splitlines():
    if L.startswith("SEQRES"):
        ch = L[11]
        sbc.setdefault(ch, []).append(L)
chains = {}
for ch, ls in sbc.items():
    letters = []
    for L in ls:
        for three in L[19:].split():
            letters.append(index_to_one(three_to_index(three)))
    chains[ch] = "".join(letters)
print("A len:", len(chains["A"]), "first 30:", chains["A"][:30])

structure = PDBParser(QUIET=True).get_structure("x", ROOT + "/inputs/1NWW.pdb")
model = structure[0]
# Map modelpos -> native SEQRES index using PDB resseq labels
modelpos_to_nativepos = {}
for ch in ["A", "B"]:
    res = list(model["" + ch].get_residues())
    for i, r in enumerate(res):
        three = r.get_resname()
        if three in ["ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL"]:
            nativepos = int(r.id[1])
            modelpos_to_nativepos.setdefault(ch, {})[i + 1] = nativepos
print("modelpos 1 A -> native:", modelpos_to_nativepos["A"][1], "(ILE5)")
print("modelpos 5 A -> native:", modelpos_to_nativepos["A"][5])
print("modelpos 101 A -> native:", modelpos_to_nativepos["A"][101])
print("modelpos 101 B -> native:", modelpos_to_nativepos["B"][101])
print("modelpos 55 A -> native:", modelpos_to_nativepos["A"][55])
print("modelpos 55 B -> native:", modelpos_to_nativepos["B"][55])

with open(ROOT + "/results/local/task_005_sun_leh_pythia/parent.fasta", "w") as f:
    for ch, seq in chains.items():
        f.write(f">1NWW_{ch}_LEH\n{seq}\n")

with open(ROOT + "/results/local/task_005_sun_leh_pythia/native_to_model_map.json", "w") as f:
    json.dump({
        "pdb_accession": "1NWW",
        "chains": chains,
        "seqres_length": {ch: len(s) for ch, s in chains.items()},
        "modelpos_to_native_seqres_index": modelpos_to_nativepos,
        "missing_coordinates_native_seqres": {
            ch: [i for i in range(1, 150) if i not in set(modelpos_to_nativepos[ch].values())] for ch in chains
        },
        "note": "Corrected map: model position (1-indexed coordinate order) -> native SEQRES index (PDB resseq label). 1NWW PDB labels match SEQRES indices."
    }, f, indent=2)

# Reconstruct candidates: candidate_id = {chain_int}_{resseq}_{nat}{alt}
# resseq is the PDB label = native SEQRES index for 1NWW
selected = pd.read_csv(ROOT + "/results/local/task_005_sun_leh_pythia/selection.csv")
chainmap = {0: "A", 1: "B"}
def h(s):
    if isinstance(s, bytes):
        return hashlib.sha256(s).hexdigest()
    return hashlib.sha256(s.encode()).hexdigest()
rows = []
with open(ROOT + "/results/local/task_005_sun_leh_pythia/candidates.fasta", "w") as out:
    for _, r in selected.iterrows():
        m = re.match(r"(\d+)_(\d+)_([A-Z])([A-Z])", r["candidate_id"])
        cint, resseq, nat, alt = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
        ch = chainmap[cint]
        nativepos = resseq  # PDB resseq = native SEQRES index for 1NWW
        parent = chains[ch]
        assert parent[nativepos - 1] == nat, (r["candidate_id"], parent[nativepos - 1], nat)
        mutated = parent[:nativepos - 1] + alt + parent[nativepos:]
        out.write(f">{r['candidate_id']}\n{mutated}\n")
        rows.append({"candidate_id": r["candidate_id"], "rank": int(r["rank"]), "sequence_sha256": h(mutated),
                     "chain": ch, "resseq": resseq, "native_seqres_pos": nativepos, "native_aa": nat, "alt_aa": alt})
with open(ROOT + "/results/local/task_005_sun_leh_pythia/selection.csv", "w") as f:
    f.write("candidate_id,rank,sequence_sha256\n")
    for r in rows:
        f.write(f"{r['candidate_id']},{r['rank']},{r['sequence_sha256']}\n")
with open(ROOT + "/results/local/task_005_sun_leh_pythia/selection_seal.json", "w") as f:
    with open(ROOT + "/results/local/task_005_sun_leh_pythia/selection.csv", "rb") as g:
        seal = h(g.read())
    json.dump({"selection_sha256": seal, "selected_count": len(rows),
               "note": "Re-sealed after correcting one-letter encoding and residue mapping; candidate identities and ranks unchanged"}, f, indent=2)
print("unique hashes:", len(set(x["sequence_sha256"] for x in rows)), "of", len(rows))
print("new seal:", seal)
