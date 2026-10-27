"""Strict ThermoMPNN saturation-table identity adapter.

Output convention inspected at Kuhlman-Lab/ThermoMPNN revision
370f76ec62bd929f7425e311d8df04a0d094990f, analysis/custom_inference.py
and analysis/SSM.py. This is not a replacement model or API schema.
The deployed wrapper still needs a real-output compatibility check.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import math
from pathlib import Path
import re

from .contracts import AMINO_ACIDS, ResearchError

LAYOUT_VERSION = "thermompnn-integer-auth-gap-index/1"
OUTPUT_VERSION = "thermompnn-upstream-saturation/1"
UPSTREAM_REVISION = "370f76ec62bd929f7425e311d8df04a0d094990f"
MAX_PREDICTION_ROWS = 100000


def input_layout(content, sequence):
    """Map gap-filled ZERO-based model positions to actual sequence/auth labels.

    No repairs, sequence normalization, implicit chain switching or insertion
    code interpretation. N/CA/C/O are required, not all side-chain atoms.
    """
    from enzyme_workflow.artifacts import inspect_structure, ONE_LETTER, STANDARD
    try:
        parsed = inspect_structure("input.pdb", content)
        text = content.decode("utf-8")
    except (ValueError, UnicodeError) as exc:
        raise ResearchError("ThermoMPNN needs prepared PDB coordinates: " + str(exc)) from exc
    if parsed["structural_sequence"] != sequence or ":" in sequence:
        raise ResearchError("ThermoMPNN input must contain one exact candidate protein chain")
    residues, chains = {}, []
    for line in text.splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        chain, resname = line[21:22], line[17:20].strip()
        if chain not in chains:
            chains.append(chain)
        if line.startswith("HETATM"):
            if resname in STANDARD | {"MSE"}:
                raise ResearchError("ThermoMPNN hetero-coded protein residues need reviewed preparation; no silent MSE conversion")
            continue
        raw = line[22:26].strip()
        if line[26:27] not in {" ", ""} or not re.fullmatch(r"-?\d{1,4}", raw):
            raise ResearchError("ThermoMPNN input currently requires integer author numbering without insertion codes")
        key = (chain, int(raw))
        residue = residues.setdefault(key, {"wildtype": ONE_LETTER[resname], "atoms": set()})
        if residue["wildtype"] != ONE_LETTER[resname]:
            raise ResearchError("ThermoMPNN input has conflicting residue identities")
        residue["atoms"].add(line[12:16].strip())
    keys = list(residues)
    chain = keys[0][0]
    if any(key[0] != chain for key in keys) or [n for _, n in keys] != sorted(n for _, n in keys):
        raise ResearchError("ThermoMPNN requires one chain in increasing author-number order")
    if any(not {"N", "CA", "C", "O"} <= value["atoms"] for value in residues.values()):
        raise ResearchError("ThermoMPNN requires N, CA, C and O coordinates for every modeled residue")
    first, last = keys[0][1], keys[-1][1]
    if last - first + 1 > 2000:
        raise ResearchError("ThermoMPNN gap-filled sequence exceeds the research envelope")
    positions = [{"model_position": number - first, "sequence_position": i,
                  "chain": chain, "residue_number": number, "wildtype": residues[(chain, number)]["wildtype"]}
                 for i, (_, number) in enumerate(keys, 1)]
    return {"version": LAYOUT_VERSION, "chain": chain, "first_file_chain": chains[0],
            "pdb_sha256": hashlib.sha256(content).hexdigest(),
            "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
            "gap_filled_length": last - first + 1, "positions": positions}


def _bounded_layouts(layouts):
    if not layouts:
        raise ResearchError("ThermoMPNN needs explicit input residue layouts")
    if sum(len(layout["positions"]) * 20 for layout in layouts.values()) > MAX_PREDICTION_ROWS:
        raise ResearchError("ThermoMPNN matrix exceeds the bounded adapter envelope; split the structure inputs into smaller jobs")


def validate_context(layouts, data):
    _bounded_layouts(layouts)
    chain = data.get("chain")
    if chain is not None and not isinstance(chain, str):
        raise ResearchError("ThermoMPNN chain selection must follow the canonical string contract")
    if data.get("model_path") not in (None, ""):
        raise ResearchError("This audited stability adapter uses the documented default checkpoint, not a custom model")
    for layout in layouts.values():
        selected = chain if chain else layout["first_file_chain"]
        if selected != layout["chain"]:
            raise ResearchError("ThermoMPNN selected/default first chain differs from the verified candidate protein chain")


def prepared_for_request(state, data, candidate_ids, structure_ids=None):
    """Require actual campaign upload bytes and exact coordinate associations."""
    uploads = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_uploaded"]
    matching = [r for r in uploads if r["job_name"] == "Thermal_MPNN" and r["input_field"] == "zip_path"
                and r["storage_path"] == data.get("zip_path") and set(r["candidate_ids"]) == set(candidate_ids)]
    prepared = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_prepared"]
    values = [p for p in prepared for r in matching if p["input_id"] == r["input_id"]
              and p["sha256"] == r["sha256"] and p.get("stability_layouts")
              and (structure_ids is None or p.get("structure_ids") == structure_ids)]
    if not values or any(value != values[0] for value in values):
        raise ResearchError("ThermoMPNN needs an unambiguous prepared/uploaded ZIP for the exact candidates and coordinates")
    value = values[0]
    path = Path(value["path"])
    if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != value["sha256"]:
        raise ResearchError("ThermoMPNN prepared input changed after upload")
    validate_context(value["stability_layouts"], data)
    return value


def _position(value):
    try:
        number = Decimal(value)
        if not number.is_finite() or number < 0 or number >= 2000 or number != number.to_integral_value():
            raise ValueError()
        return int(number)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ResearchError("ThermoMPNN position must be a finite zero-based gap-filled integer index") from exc


def parse_output(path, layouts, *, member=None):
    """Accept complete 20-AA grids only; use exact Dataset, not broken pdb.strip."""
    from enzyme_workflow.artifacts import read_members, csv_rows
    _bounded_layouts(layouts)
    if member is not None and not isinstance(member, str):
        raise ResearchError("ThermoMPNN selected output member must be a string")
    files = read_members(path)
    if member is not None and member not in files:
        raise ResearchError("Selected ThermoMPNN output member is absent")
    selected = {name: content for name, content in files.items()
                if name == member or member is None and name.lower().endswith(".csv")}
    if not selected or any(not name.lower().endswith(".csv") for name in selected):
        raise ResearchError("ThermoMPNN output needs an authoritative CSV saturation table")
    grids = {cid: {} for cid in layouts}
    position_maps = {cid: {p["model_position"]: p for p in layout["positions"]} for cid, layout in layouts.items()}
    for name, content in selected.items():
        rows = csv_rows(content, ("Model", "Dataset", "ddG_pred", "position", "wildtype", "mutation"))
        for row_number, row in enumerate(rows, 2):
            cid = row["Dataset"]
            if (cid not in layouts or row["Model"] != "ThermoMPNN"
                    or "chain" in row and row["chain"] != layouts[cid]["chain"]):
                raise ResearchError("ThermoMPNN output model/Dataset/chain does not identify the exact submitted PDB")
            index = _position(row["position"])
            residue = position_maps[cid].get(index)
            if residue is None or row["wildtype"] != residue["wildtype"] or row["mutation"] not in AMINO_ACIDS:
                raise ResearchError("ThermoMPNN mutation row disagrees with the input residue/index mapping")
            try:
                ddg = float(row["ddG_pred"])
            except (TypeError, ValueError) as exc:
                raise ResearchError("ThermoMPNN ddG prediction is not numeric") from exc
            if not math.isfinite(ddg):
                raise ResearchError("ThermoMPNN ddG prediction must be finite")
            key = (index, row["mutation"])
            if key in grids[cid]:
                raise ResearchError("Duplicate ThermoMPNN prediction; no averaging or row-order joins")
            grids[cid][key] = {**residue, "mutation": row["mutation"], "ddG_pred": ddg,
                               "chain_metadata_source": "output_column" if "chain" in row else "verified_input_layout",
                               "source_member": name, "source_row": row_number}
    output = {}
    for cid, layout in layouts.items():
        expected = {(p["model_position"], aa) for p in layout["positions"] for aa in AMINO_ACIDS}
        if set(grids[cid]) != expected:
            raise ResearchError("Partial ThermoMPNN output: every input residue needs all 20 amino-acid predictions")
        output[cid] = {"schema": OUTPUT_VERSION, "upstream_revision": UPSTREAM_REVISION,
            "prediction_scope": "single_substitution_relative_to_input_sequence_and_structure",
            "index_convention": "zero_based_gap_filled_author_numbering",
            "units": "upstream_ddG_pred_scale_not_independently_calibrated",
            "absolute_stability_or_Tm": "not_predicted", "multi_mutation_aggregation": "unsupported",
            "input_layout": layout, "predictions": [grids[cid][key] for key in sorted(grids[cid])]}
    return output


def lookup_single_mutation(matrix, basis, target):
    """Direct lookup, not an additive approximation for combined mutations."""
    if matrix.get("schema") != OUTPUT_VERSION or hashlib.sha256(basis.encode()).hexdigest() != matrix["input_layout"]["sequence_sha256"]:
        raise ResearchError("Stability matrix does not belong to the declared basis sequence")
    if len(basis) != len(target):
        raise ResearchError("This ThermoMPNN matrix does not score insertions or deletions")
    differences = [(i, a, b) for i, (a, b) in enumerate(zip(basis, target), 1) if a != b]
    if len(differences) != 1:
        raise ResearchError("A direct ThermoMPNN lookup needs exactly one substitution; no absolute WT or multi-mutant score is inferred")
    position, wt, mutation = differences[0]
    rows = [p for p in matrix["predictions"] if p["sequence_position"] == position
            and p["wildtype"] == wt and p["mutation"] == mutation]
    if len(rows) != 1:
        raise ResearchError("No unique source prediction exists for this exact substitution")
    return {**rows[0], "sequence_mutation": f"{wt}{position}{mutation}",
            "basis_sequence_sha256": hashlib.sha256(basis.encode()).hexdigest(),
            "target_sequence_sha256": hashlib.sha256(target.encode()).hexdigest(),
            "prediction_scope": matrix["prediction_scope"], "units": matrix["units"]}


def match_candidates(service, campaign, observation_id, basis_candidate_id, structure_id, target_candidate_ids):
    """Record direct single-mutant lookups with the original matrix provenance.

    All requested variants must be supported; no hidden partial-success table.
    The matrix is checked against its downloaded raw bytes again on resume.
    """
    from .contracts import digest
    state = service.store.status(campaign)
    candidates = {c["candidate_id"]: c for c in state["candidates"]}
    if (basis_candidate_id not in candidates or not isinstance(target_candidate_ids, list) or not target_candidate_ids
            or any(not isinstance(cid, str) or cid not in candidates for cid in target_candidate_ids)
            or len(target_candidate_ids) != len(set(target_candidate_ids))):
        raise ResearchError("Stability matching requires known basis and unique registered target candidates")
    source = next((o for o in state["observations"] if o["observation_id"] == observation_id), None)
    if not source or source["kind"] != "stability" or basis_candidate_id not in source["candidate_ids"]:
        raise ResearchError("Stability matching requires the original basis-candidate matrix observation")
    matrix = source["metrics"].get(basis_candidate_id, {}).get("by_structure", {}).get(structure_id)
    if not matrix or matrix.get("schema") != OUTPUT_VERSION:
        raise ResearchError("Select the exact verified coordinate version of the original saturation matrix")
    call = next((c for c in state["calls"] if c["call_id"] == source["source_call_id"]), None)
    if not call or call["tool"] != "boltzmann_submit" or call["status"] != "completed" or call["args"].get("job_name") != "Thermal_MPNN":
        raise ResearchError("Stability matching requires the completed original ThermoMPNN submission")
    ids = source["candidate_ids"]
    source_versions = {}
    for cid in ids:
        versions = source["metrics"].get(cid, {}).get("by_structure", {})
        if len(versions) != 1:
            raise ResearchError("Source matrix must retain one coordinate version per basis candidate")
        source_versions[cid] = next(iter(versions))
    prepared = prepared_for_request(state, call["args"]["experiment_data"], ids, source_versions)
    if len(source["artifacts"]) != 1:
        raise ResearchError("Stability matching needs the original single downloaded artifact receipt")
    artifact = source["artifacts"][0]
    path = Path(artifact["path"])
    if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
        raise ResearchError("The original ThermoMPNN result artifact is missing or changed")
    # Read the exact originally selected member(s), not another CSV added later.
    source_members = {p["source_member"] for cid in ids
                      for group in source["metrics"][cid]["by_structure"].values() for p in group["predictions"]}
    if not source_members:
        raise ResearchError("ThermoMPNN source table provenance is empty")
    # Normal multi-input jobs require every grid; an explicit member selection
    # is valid only when that member contains all those grids.
    selected_member = next(iter(source_members)) if len(source_members) == 1 else None
    verified = parse_output(path, prepared["stability_layouts"], member=selected_member)
    if verified[basis_candidate_id] != matrix:
        raise ResearchError("Stored ThermoMPNN matrix differs from the raw source predictions")
    metrics = {}
    for cid in sorted(target_candidate_ids):
        hit = lookup_single_mutation(matrix, candidates[basis_candidate_id]["sequence"], candidates[cid]["sequence"])
        metrics[cid] = {**hit, "basis_candidate_id": basis_candidate_id, "basis_structure_id": structure_id,
                        "source_observation_id": observation_id, "source_schema": OUTPUT_VERSION}
    value = {"observation_id": "stability-match-" + digest({"source": observation_id, "basis": basis_candidate_id,
                 "structure": structure_id, "targets": sorted(target_candidate_ids)})[:16],
        "kind": "stability", "candidate_ids": sorted(target_candidate_ids), "evidence_level": source["evidence_level"],
        "metrics": metrics, "artifacts": source["artifacts"], "source_call_id": source["source_call_id"]}
    return {"observation": service.store.add_observation(campaign, value),
            "boundary": "Direct single-substitution predictions only; no absolute stability, multi-mutant additivity or experimental improvement"}
