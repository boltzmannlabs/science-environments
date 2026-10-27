"""Protein-only CIF -> PDB projection for ProteinMPNN/ThermoMPNN inputs.

Not a ligand converter, structural repair, chemical preparation or geometry
validation. The original complex is retained. Protein coordinates are rounded
only to the representable PDB precision, never optimized or renumbered.

Format references:
https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html
https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/atom_site.html
"""
from __future__ import annotations

import hashlib
import math
import re

from .contracts import ResearchError

PROJECTION_VERSION = "protein-only-cif-pdb/1"


def _atom_rows(content):
    from enzyme_workflow.artifacts import cif_tokens
    lexed = list(cif_tokens(content.decode("utf-8")))
    if sum(not quoted and value.startswith("data_") for value, quoted in lexed) != 1:
        raise ResearchError("Protein projection needs one unambiguous CIF data block")
    i, tables = 0, 0
    rows = []
    while i < len(lexed):
        if lexed[i] != ("loop_", False):
            i += 1; continue
        i += 1
        fields = []
        while i < len(lexed) and not lexed[i][1] and lexed[i][0].startswith("_"):
            fields.append(lexed[i][0]); i += 1
        values = []
        while i < len(lexed):
            value, quoted = lexed[i]
            if not quoted and (value.startswith(("_", "data_", "save_")) or value in {"loop_", "stop_"}):
                break
            values.append(value); i += 1
        if not any(field.startswith("_atom_site.") for field in fields):
            continue
        tables += 1
        if (tables != 1 or len(fields) != len(set(fields)) or not fields
                or any(not field.startswith("_atom_site.") for field in fields) or len(values) % len(fields)):
            raise ResearchError("Protein projection needs exactly one well-formed atom_site table")
        names = [field.split(".", 1)[1] for field in fields]
        required = {"group_PDB", "Cartn_x", "Cartn_y", "Cartn_z", "type_symbol", "occupancy", "B_iso_or_equiv"}
        if not required <= set(names):
            raise ResearchError("Protein projection requires coordinates, elements, occupancy and B-factor fields; missing values are not invented")
        rows = [dict(zip(names, values[j:j+len(names)])) for j in range(0, len(values), len(names))]
    if tables != 1 or not rows:
        raise ResearchError("CIF has no unambiguous atom_site rows")
    return rows


def _number(value, width, precision, field):
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ResearchError("Missing or invalid " + field + " in protein projection") from exc
    if not math.isfinite(number):
        raise ResearchError("Nonfinite " + field + " in protein projection")
    formatted = f"{number:{width}.{precision}f}"
    if len(formatted) != width:
        raise ResearchError(field + " cannot be represented in legacy PDB without changing the structure")
    return number, formatted


def project_protein_pdb(name, content):
    from enzyme_workflow.artifacts import inspect_structure
    if not name.lower().endswith((".cif", ".mmcif")):
        raise ResearchError("Protein projection accepts CIF/mmCIF, not a renamed or unsupported file")
    if not isinstance(content, bytes) or not 0 < len(content) <= 50 * 1024**2:
        raise ResearchError("CIF projection input must be bounded, nonempty bytes")
    try:
        original = inspect_structure(name, content)
        rows = _atom_rows(content)
    except (UnicodeError, ValueError) as exc:
        raise ResearchError("CIF projection needs a prepared single-model structure: " + str(exc)) from exc
    if ":" in original["structural_sequence"]:
        raise ResearchError("Protein projection currently requires one exact-sequence protein chain")
    lines, residues, hetero, rounds = [], {}, 0, []

    def label(row, auth, fallback):
        value = row.get(auth)
        if value in {None, ".", "?"}: value = row.get(fallback)
        if value in {None, ".", "?"}:
            raise ResearchError("Projection cannot infer missing structural labels")
        return value

    for row in rows:
        if row["group_PDB"] != "ATOM":
            hetero += 1
            continue
        serial = len(lines) + 1
        if serial > 99999:
            raise ResearchError("Protein projection exceeds the legacy PDB atom-serial limit")
        atom = label(row, "auth_atom_id", "label_atom_id")
        residue = label(row, "auth_comp_id", "label_comp_id")
        chain = label(row, "auth_asym_id", "label_asym_id")
        raw_number = label(row, "auth_seq_id", "label_seq_id")
        insertion = row.get("pdbx_PDB_ins_code", "")
        if insertion in {"?", "."}: insertion = ""
        if (not re.fullmatch(r"[A-Za-z0-9]{1,4}", atom) or not re.fullmatch(r"[A-Z]{3}", residue)
                or not re.fullmatch(r"[A-Za-z]", chain) or not re.fullmatch(r"-?\d+", raw_number)
                or not re.fullmatch(r"[A-Za-z]?", insertion)):
            raise ResearchError("Projection labels cannot be represented unambiguously in legacy PDB")
        number = int(raw_number)
        if not -999 <= number <= 9999:
            raise ResearchError("Residue number cannot fit PDB; automatic renumbering is not permitted")
        element = row["type_symbol"].upper()
        initial = atom.lstrip("0123456789")[:1].upper()
        if element not in {"C", "N", "O", "S", "H", "D"} or (element != initial and not {element, initial} <= {"H", "D"}):
            raise ResearchError("Protein atom name and supplied element disagree or require unsupported chemistry")
        xyz = [_number(row["Cartn_" + axis], 8, 3, "coordinate") for axis in "xyz"]
        occupancy, occ = _number(row["occupancy"], 6, 2, "occupancy")
        bfactor, bf = _number(row["B_iso_or_equiv"], 6, 2, "B factor")
        if not 0 <= occupancy <= 1 or bfactor < 0:
            raise ResearchError("Projection occupancy/B factor is outside the supported physical range")
        charge = row.get("pdbx_formal_charge", "?")
        if charge not in {"?", ".", ""}:
            if not re.fullmatch(r"[+-]?\d+", charge) or abs(int(charge)) > 9:
                raise ResearchError("Protein formal charge cannot be represented in PDB")
            charge = f"{abs(int(charge))}{'+' if int(charge) > 0 else '-'}" if int(charge) else "  "
        else:
            charge = "  "
        atom_field = atom.ljust(4) if len(atom) == 4 or atom[0].isdigit() else (" " + atom.ljust(3))
        line = (f"ATOM  {serial:5d} {atom_field} {residue:>3} {chain}{number:4d}{insertion or ' '}   "
                + "".join(field for _, field in xyz) + occ + bf + "          " + f"{element:>2}{charge}")
        if len(line) != 80:
            raise ResearchError("Projection produced a noncanonical PDB record")
        lines.append(line)
        residues.setdefault((chain, number, insertion), set()).add(atom)
        rounds.extend(abs(raw - float(field)) for raw, field in xyz)
    if not lines or any(not {"N", "CA", "C", "O"} <= atoms for atoms in residues.values()):
        raise ResearchError("Protein projection requires existing N, CA, C and O at every residue; no missing atoms are filled")
    result = ("\n".join(lines) + "\nEND\n").encode()
    projected = inspect_structure("protein.pdb", result)
    if (projected["structural_sequence"] != original["structural_sequence"] or projected["residues"] != original["residues"]
            or projected["atom_count"] != len(lines) or ("all_atom" in projected["capabilities"]) != ("all_atom" in original["capabilities"])):
        raise ResearchError("Projection changed protein sequence, numbering or atom completeness")
    return result, {"protocol": PROJECTION_VERSION, "source_member_sha256": hashlib.sha256(content).hexdigest(),
        "projected_pdb_sha256": hashlib.sha256(result).hexdigest(), "protein_atoms": len(lines),
        "removed_hetero_atoms": hetero, "ligands_preserved": False, "residues_renumbered": False,
        "atoms_added": 0, "max_coordinate_rounding_angstrom": max(rounds, default=0.0),
        "purpose": "ProteinMPNN/ThermoMPNN protein-only input; never a ligand or catalytic-geometry replacement"}
