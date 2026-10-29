"""Verify a returned ligand graph against the task and one coordinate version.

Requires a single-molecule 3D SDF in the SAME verified scientific output archive.
No bond inference, atom-order guessing, docking, repair or protonation selection.
RDKit is optional at core installation but required for this operation.
"""
from __future__ import annotations

import hashlib
import io
import math
import re

from .contracts import ResearchError, digest, identifier

VERSION = "same-artifact-ligand-graph-and-coordinates/1"
MAX_SDF_BYTES = 2 * 1024**2


def _reject_explicit_external_links(name, content, selected, selected_serials, aliases):
    """Known covalent/coordination links contradict an isolated organic graph.

    Missing records do not prove the absence of a linkage. CIF reference:
    https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/struct_conn.html
    """
    if name.lower().endswith(".pdb"):
        target = (selected["chain_id"], selected["residue_number"], selected["component_id"], selected["insertion_code"])
        for line in content.decode().splitlines():
            if line.startswith("CONECT"):
                numbers = [int(line[i:i+5]) for i in range(6, len(line), 5) if line[i:i+5].strip()]
                if numbers and any((numbers[0] in selected_serials) != (other in selected_serials) for other in numbers[1:]):
                    raise ResearchError("Selected ligand has an explicit external connection; a separate reviewed chemical-state adapter is required")
            elif line.startswith("LINK  "):
                first = (line[21].strip(), int(line[22:26]), line[17:20].strip(), line[26:27].strip())
                second = (line[51].strip(), int(line[52:56]), line[47:50].strip(), line[56:57].strip())
                if (first == target) != (second == target):
                    raise ResearchError("Selected ligand has an explicit external LINK; isolated molecule identity is insufficient")
        return
    from enzyme_workflow.artifacts import cif_tokens
    tokens = list(cif_tokens(content.decode()))
    rows, singles, i = [], {}, 0
    while i < len(tokens):
        value, quoted = tokens[i]
        if not quoted and value == "loop_":
            i += 1; fields = []
            while i < len(tokens) and not tokens[i][1] and tokens[i][0].startswith("_"):
                fields.append(tokens[i][0]); i += 1
            values = []
            while i < len(tokens):
                v, q = tokens[i]
                if not q and (v.startswith(("_", "data_", "save_")) or v in {"loop_", "stop_"}): break
                values.append(v); i += 1
            if any(f.startswith("_struct_conn.") for f in fields):
                if len(fields) != len(set(fields)) or any(not f.startswith("_struct_conn.") for f in fields) or len(values) % len(fields):
                    raise ResearchError("CIF connection evidence is ambiguous")
                names = [f.split(".", 1)[1] for f in fields]
                rows.extend(dict(zip(names, values[j:j+len(fields)])) for j in range(0, len(values), len(fields)))
        elif not quoted and value.startswith("_struct_conn."):
            field = value.split(".", 1)[1]
            if field in singles or i + 1 >= len(tokens): raise ResearchError("CIF connection evidence is ambiguous")
            singles[field] = tokens[i+1][0]; i += 2
        else: i += 1
    if singles: rows.append(singles)
    for row in rows:
        if row.get("conn_type_id") in {"hydrog", "saltbr"}: continue
        touches = []
        for n in (1, 2):
            def field(kind):
                a = row.get(f"ptnr{n}_auth_{kind}")
                return row.get(f"ptnr{n}_label_{kind}") if a in {None, ".", "?"} else a
            comp, chain, number = field("comp_id"), field("asym_id"), field("seq_id")
            if comp not in aliases["component_id"] or chain not in aliases["chain_id"]:
                touches.append(False); continue
            if number in {None, ".", "?"}:
                raise ResearchError("Selected ligand has an ambiguously numbered explicit connection")
            insertion = row.get(f"pdbx_ptnr{n}_PDB_ins_code", "")
            if insertion in {".", "?"}: insertion = ""
            touches.append(int(number) in aliases["residue_number"] and insertion == selected["insertion_code"])
        if sum(touches) == 1:
            raise ResearchError("Selected ligand has an explicit external CIF connection; separate chemical-state review is required")


def selector(value):
    if (not isinstance(value, dict) or not {"chain_id", "residue_number", "component_id"} <= set(value)
            or set(value) - {"chain_id", "residue_number", "component_id", "insertion_code"}
            or not isinstance(value["chain_id"], str) or not re.fullmatch(r"[A-Za-z0-9]{1,16}", value["chain_id"])
            or type(value["residue_number"]) is not int
            or not isinstance(value["component_id"], str) or not re.fullmatch(r"[A-Za-z0-9]{1,8}", value["component_id"])
            or not isinstance(value.get("insertion_code", ""), str)
            or not re.fullmatch(r"[A-Za-z]?", value.get("insertion_code", ""))):
        raise ResearchError("Ligand selector requires explicit chain_id, integer residue_number, component_id and optional insertion_code")
    return {**value, "insertion_code": value.get("insertion_code", "")}


def coordinate_atoms(name, content, selected):
    """Select by exact author labels, not component name or file/atom ordering."""
    rows, serials = [], set()
    aliases = {key: {selected[key]} for key in ("component_id", "chain_id", "residue_number")}
    try:
        if name.lower().endswith(".pdb"):
            for line in content.decode("utf-8").splitlines():
                if not line.startswith("HETATM"): continue
                if (line[21].strip(), int(line[22:26]), line[17:20].strip(), line[26:27].strip()) != (
                        selected["chain_id"], selected["residue_number"], selected["component_id"], selected["insertion_code"]):
                    continue
                rows.append({"name": line[12:16].strip(), "element": line[76:78].strip().upper(),
                    "xyz": [float(line[i:i+8]) for i in (30, 38, 46)],
                    "occupancy": float(line[54:60]), "alt": line[16:17].strip()})
                serials.add(int(line[6:11]))
        elif name.lower().endswith((".cif", ".mmcif")):
            from .protein_projection import _atom_rows
            def label(row, auth, fallback):
                value = row.get(auth)
                if value in {None, ".", "?"}: value = row.get(fallback)
                if value in {None, ".", "?"}: raise ResearchError("Ligand atom has missing structural labels")
                return value
            for row in _atom_rows(content):
                if row["group_PDB"] != "HETATM": continue
                insertion = row.get("pdbx_PDB_ins_code", "")
                if insertion in {".", "?"}: insertion = ""
                identity = (label(row, "auth_asym_id", "label_asym_id"), int(label(row, "auth_seq_id", "label_seq_id")),
                            label(row, "auth_comp_id", "label_comp_id"), insertion)
                if identity != (selected["chain_id"], selected["residue_number"], selected["component_id"], selected["insertion_code"]): continue
                for key, field in (("component_id", "label_comp_id"), ("chain_id", "label_asym_id"), ("residue_number", "label_seq_id")):
                    value = row.get(field)
                    if value not in {None, ".", "?"}: aliases[key].add(int(value) if key == "residue_number" else value)
                rows.append({"name": label(row, "auth_atom_id", "label_atom_id"), "element": row["type_symbol"].upper(),
                    "xyz": [float(row["Cartn_" + axis]) for axis in "xyz"], "occupancy": float(row["occupancy"]),
                    "alt": row.get("label_alt_id", ".")})
        else:
            raise ResearchError("Ligand identity currently supports prepared PDB/CIF/mmCIF coordinates")
        _reject_explicit_external_links(name, content, selected, serials, aliases)
    except ResearchError:
        raise
    except (UnicodeError, ValueError, IndexError, KeyError) as exc:
        raise ResearchError("Ligand coordinate labels, elements, occupancy or coordinates are invalid") from exc
    if (not rows or len(rows) > 512 or len({r["name"] for r in rows}) != len(rows)
            or any(not r["name"] or not r["element"] or r["occupancy"] != 1.0 or r["alt"] not in {"", ".", "?"}
                   or any(not math.isfinite(x) for x in r["xyz"]) for r in rows)):
        raise ResearchError("Selected ligand needs unique atoms, complete occupancy and unambiguous finite coordinates")
    return rows


def graph_coordinate_evidence(name, content, sdf, smiles, selected):
    if not isinstance(sdf, bytes) or not 0 < len(sdf) <= MAX_SDF_BYTES:
        raise ResearchError("Ligand SDF must be a nonempty bounded molecular file")
    # Bound advertised graph allocation before the native parser touches it.
    try:
        sections = sdf.decode("utf-8").split("$$$$")
        if len(sections) > 2 or (len(sections) == 2 and sections[1].strip()):
            raise ResearchError("One SDF molecule is required; multiple records are not inspected")
        lines = sections[0].splitlines(); header = lines[3]
        if "V2000" in header:
            atoms, bonds = int(header[:3]), int(header[3:6])
        elif "V3000" in header:
            counts = [re.fullmatch(r"M\s+V30 COUNTS (\d+) (\d+) .*", line) for line in lines]
            counts = [m for m in counts if m is not None]
            if len(counts) != 1: raise ResearchError("SDF V3000 counts are ambiguous")
            atoms, bonds = int(counts[0][1]), int(counts[0][2])
        else:
            raise ResearchError("SDF needs explicit V2000/V3000 graph counts")
        if not 1 <= atoms <= 256 or not 0 <= bonds <= 1024:
            raise ResearchError("SDF graph counts exceed the supported bounded ligand")
    except (UnicodeError, IndexError, ValueError) as exc:
        if isinstance(exc, ResearchError): raise
        raise ResearchError("SDF has invalid molecular graph counts") from exc
    try:
        from rdkit import Chem, rdBase
    except ImportError as exc:
        raise ResearchError("Ligand identity verification requires the optional RDKit chemistry dependency") from exc
    try:
        records = list(Chem.ForwardSDMolSupplier(io.BytesIO(sdf), sanitize=True, removeHs=False, strictParsing=True))
        reference = Chem.MolFromSmiles(smiles)
        if len(records) != 1 or records[0] is None or reference is None:
            raise ResearchError("One valid SDF molecule and the exact valid task SMILES are required")
        molecule = records[0]
        if molecule.GetNumAtoms() != atoms or molecule.GetNumBonds() != bonds:
            raise ResearchError("SDF declared graph counts disagree with the parsed molecule")
        for mol in (reference, molecule):
            if (not 1 <= mol.GetNumAtoms() <= 256 or len(Chem.GetMolFrags(mol)) != 1
                    or any(a.GetIsotope() or a.HasQuery() or a.GetNumRadicalElectrons()
                           or a.GetAtomicNum() not in {1, 5, 6, 7, 8, 9, 15, 16, 17, 35, 53} for a in mol.GetAtoms())
                    or any(b.HasQuery() for b in mol.GetBonds())):
                raise ResearchError("Ligand graph requires one supported organic molecule without isotopes, queries, metals or radicals")
            for atom in mol.GetAtoms(): atom.SetAtomMapNum(0)
        if molecule.GetNumConformers() != 1 or not molecule.GetConformer().Is3D():
            raise ResearchError("Returned molecular evidence needs one explicitly three-dimensional conformer")
        Chem.AssignStereochemistryFrom3D(molecule, replaceExistingTags=True)
        def canonical(mol): return Chem.MolToSmiles(Chem.RemoveHs(mol), canonical=True, isomericSmiles=True)
        identity = canonical(reference)
        if canonical(molecule) != identity:
            raise ResearchError("Returned ligand graph, stereochemistry or formal protonation/charge does not match the task substrate")
        rows = coordinate_atoms(name, content, selector(selected))
        heavy = [row for row in rows if row["element"] not in {"H", "D"}]
        indices = [atom.GetIdx() for atom in molecule.GetAtoms() if atom.GetAtomicNum() > 1]
        if len(heavy) != len(indices):
            raise ResearchError("Returned molecule and selected structure have different heavy-atom counts")
        # PDB is rounded to 0.001 A and ordinary SDF to 0.0001 A per component.
        tolerance = 0.001 if name.lower().endswith(".pdb") else 0.0002
        mapping, occupied = [], set()
        for index in indices:
            atom = molecule.GetAtomWithIdx(index)
            point = molecule.GetConformer().GetAtomPosition(index)
            xyz = [point.x, point.y, point.z]
            if any(not math.isfinite(v) for v in xyz): raise ResearchError("SDF coordinates must be finite")
            matches = [row for row in heavy if row["element"] == atom.GetSymbol().upper()
                       and math.dist(xyz, row["xyz"]) <= tolerance]
            if len(matches) != 1 or matches[0]["name"] in occupied:
                raise ResearchError("Ligand atoms do not have a unique element-and-coordinate correspondence; no row-order or nearest-pose guess")
            matched = matches[0]; occupied.add(matched["name"])
            mapping.append({"sdf_atom_index": index, "structure_atom_name": matched["name"], "element": matched["element"]})
    except ResearchError:
        raise
    except (ValueError, TypeError, RuntimeError) as exc:
        raise ResearchError("Ligand molecular graph or stereochemical evidence could not be evaluated") from exc
    return {"adapter_version": VERSION, "rdkit_version": rdBase.rdkitVersion, "canonical_isomeric_smiles": identity,
            "task_smiles_sha256": hashlib.sha256(smiles.encode()).hexdigest(), "heavy_atom_count": len(indices),
            "heavy_atom_mapping": mapping, "coordinate_match_tolerance_angstrom": tolerance,
            "identity_scope": "returned molecular graph and selected heavy-atom coordinates match the exact requested representation",
            "hydrogen_coordinate_identity_verified": False, "assay_protonation_validated": False,
            "unselected_hetero_chemistry_verified": False,
            "structural_quality_validated": False, "catalytic_geometry_validated": False}


def _receipt(record, task, sdf_member, selected):
    from .structures import checked_structure_content
    from enzyme_workflow.artifacts import read_members
    content = checked_structure_content(record)
    if not isinstance(sdf_member, str) or not sdf_member.lower().endswith(".sdf"):
        raise ResearchError("Select an explicit SDF member from this coordinate artifact, not another local path")
    members = read_members(record["artifact"]["path"])
    if sdf_member not in members: raise ResearchError("Selected SDF is absent from the original verified coordinate artifact")
    selected = selector(selected)
    evidence = graph_coordinate_evidence(record["artifact"]["member"], content, members[sdf_member], task["substrate"]["smiles"], selected)
    value = {"structure_id": record["structure_id"], "candidate_id": record["candidate_id"],
        "source_call_id": record["source"].get("source_call_id"), "coordinate_artifact_sha256": record["artifact"]["sha256"],
        "coordinate_member_sha256": record["artifact"]["member_sha256"],
        "sdf_member": sdf_member, "sdf_member_sha256": hashlib.sha256(members[sdf_member]).hexdigest(),
        "ligand_selector": selected, **evidence}
    if not value["source_call_id"]:
        raise ResearchError("Ligand molecular evidence needs a returned, originally receipted scientific output")
    value["verification_id"] = "ligand-" + digest(value)[:20]
    return value


def apply_verification(record, state):
    """Recheck evidence whenever selected; do not mutate immutable coordinates."""
    entries = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "ligand_identity_verified"
               and e["payload"]["data"]["structure_id"] == record["structure_id"]]
    if not entries: return record
    _check_source(record, state)
    if len(entries) != 1 or _receipt(record, state["task"], entries[0]["sdf_member"], entries[0]["ligand_selector"]) != entries[0]:
        raise ResearchError("Ligand identity evidence changed or is ambiguous; do not reuse a prior gate")
    return {**record, "capabilities": sorted(set(record["capabilities"]) | {"ligand"}),
            "ligand_identity_verified": True, "ligand_verification": entries[0]}


def _check_source(record, state):
    call = next((c for c in state["calls"] if c["call_id"] == record["source"].get("source_call_id")), None)
    if call is None or call["tool"] != "boltzmann_submit" or call["status"] != "completed":
        raise ResearchError("Ligand evidence needs its still-completed original scientific submission")


def verify_ligand(service, campaign, candidate_id, structure_id, sdf_member, ligand_selector):
    from .structures import select_structure
    identifier(candidate_id, "candidate_id")
    identifier(structure_id, "structure_id")
    record = select_structure(service, campaign, candidate_id, structure_id)
    state = service.store.status(campaign)
    _check_source(record, state)
    value = _receipt(record, state["task"], sdf_member, ligand_selector)
    with service.store.transaction() as db:
        import json
        entries = [json.loads(row[0])["data"] for row in db.execute("SELECT payload FROM events WHERE campaign=?", (campaign,))
                   if json.loads(row[0]).get("event") == "ligand_identity_verified"
                   and json.loads(row[0])["data"]["structure_id"] == structure_id]
        if entries and entries != [value]: raise ResearchError("A structure's verified substrate selection cannot be replaced")
        if not entries: service.store.event(db, campaign, "ligand_identity_verified", value)
    return {"verification": value, "ligand_identity_verified": True, "scientific_jobs_submitted": 0,
            "boundary": "Exact requested graph and selected heavy-atom coordinates only; no assay state, preparation, quality, catalytic geometry or activity pass"}
