"""Transfer A060's two actual atoms into the retained full scene.

Serialization only: no coordinate generation, optimization, hydrogenation or tool
submission. Every original atom-site value, including confidence, is preserved.
"""
import hashlib
import json
from pathlib import Path
import gemmi

R = Path(__file__).resolve().parent
source = R / "structure_evidence/LEH_PARENT/parent_native_primary_pair_no_crystal_symmetry_for_review.cif"
actual = R / "prepared/request4582_parent_OXT_only/native_parent_apo_plus_OXT.pdb"
output = R / "prepared/parent_complete_scene_with_A060_OXT_for_review.cif"
manifest = R / "prepared/parent_complete_scene_with_A060_OXT_handoff.json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source) == "64f6e7053b323d8488b675e0e0045850908b3699b2a2173050e8632aed6c15af"
assert sha(actual) == "91e74772367eda69e6dcbb5485f329b2f2e071763432480be0c4d5934c33eeb9"
assert not output.exists() and not manifest.exists()
actual_atoms = {}
for line in actual.read_text().splitlines():
    if line.startswith("ATOM  "):
        key = (line[21], line[22:26].strip(), line[26].strip(),
               line[17:20].strip(), line[12:16].strip())
        assert key not in actual_atoms
        actual_atoms[key] = tuple(line[i:i+8].strip() for i in (30, 38, 46))

doc = gemmi.cif.read_file(str(source))
block = doc.sole_block()
table = block.find_mmcif_category("_atom_site.")
tags = list(table.tags)
col = {name.split(".", 1)[1]: i for i, name in enumerate(tags)}
original = [list(row) for row in table]
assert len({row[col["id"]] for row in original}) == len(original)
assert not block.find_mmcif_category("_cell.")
assert not block.find_mmcif_category("_symmetry.")


def key(row):
    insertion = row[col["pdbx_PDB_ins_code"]]
    return (row[col["auth_asym_id"]], row[col["auth_seq_id"]],
            "" if insertion in ("?", ".") else insertion,
            row[col["label_comp_id"]], row[col["label_atom_id"]])


next_id = max(int(row[col["id"]]) for row in original) + 1
protein_rows = [row for row in original if row[col["group_PDB"]] == "ATOM"]
assert len(protein_rows) == 2324
for row in protein_rows:
    k = key(row)
    assert k in actual_atoms
    assert tuple(float(row[col[n]]) for n in ("Cartn_x", "Cartn_y", "Cartn_z")) == tuple(float(x) for x in actual_atoms[k])
added = []
for chain in ("A", "B"):
    reference = next(row for row in original if key(row) == (chain, "149", "", "GLY", "C"))
    new = list(reference)
    k = (chain, "149", "", "GLY", "OXT")
    assert not any(key(row) == k for row in original)
    new[col["id"]] = str(next_id)
    next_id += 1
    new[col["type_symbol"]] = "O"
    new[col["label_atom_id"]] = "OXT"
    for name, value in zip(("Cartn_x", "Cartn_y", "Cartn_z"), actual_atoms[k]):
        new[col[name]] = value
    new[col["occupancy"]] = "1"
    new[col["B_iso_or_equiv"]] = "0"
    new[col["pdbx_formal_charge"]] = "?"
    table.loop.add_row(new)
    added.append({"author_selector": list(k), "label_chain": new[col["label_asym_id"]],
                  "xyz_A": [float(x) for x in actual_atoms[k]],
                  "confidence": None, "formal_charge": None})
serialized = doc.as_string()
check = gemmi.cif.read_string(serialized).sole_block().find_mmcif_category("_atom_site.")
rows = [list(row) for row in check]
assert rows[:len(original)] == original
assert len(rows) == len(original) + 2
assert len({row[col["id"]] for row in rows}) == len(rows)
assert len({key(row) for row in rows}) == len(rows)
assert sorted((row[col["label_comp_id"]], row[col["label_asym_id"]], row[col["auth_seq_id"]])
              for row in rows if row[col["group_PDB"]] != "ATOM") == sorted(
                  (row[col["label_comp_id"]], row[col["label_asym_id"]], row[col["auth_seq_id"]])
                  for row in original if row[col["group_PDB"]] != "ATOM")
output.write_text(serialized)
record = {"purpose": "Full original parent scene plus only the two actual A060-generated OXT atoms; review input, not reactive preparation",
          "source": str(source), "source_sha256": sha(source),
          "A060_native_output": str(actual), "A060_output_sha256": sha(actual),
          "output": str(output), "output_sha256": sha(output),
          "original_atom_site_rows": len(original), "output_atom_site_rows": len(rows),
          "all_original_atom_site_values_preserved": True,
          "all_original_ligand_water_and_confidence_values_preserved": True,
          "added_atoms": added, "new_atom_confidence_unknown": True,
          "new_atom_formal_charge_unknown": True,
          "new_hydrogens": 0, "new_scientific_preparation_dispatches": 0,
          "native_algorithm_repeated": False, "uploaded": False, "submitted": False,
          "no_new_coordinates_computed": True, "full_reactive_state_verified": False}
manifest.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
