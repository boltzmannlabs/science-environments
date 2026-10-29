"""Campaign identity/allocation checks, not another scientific API schema.

The original catalogue and native validator still own request types and tool
syntax. These checks ensure a valid request actually concerns the declared
enzyme candidates and cannot expand the approved research allocation.
"""
from __future__ import annotations

from .contracts import ResearchError


def validate_request_scope(state, job, data, candidate_ids, *, structure_ids=None):
    known = {c["candidate_id"]: c for c in state["candidates"]}
    if (not isinstance(candidate_ids, list) or not candidate_ids or any(not isinstance(cid, str) for cid in candidate_ids) or set(candidate_ids) - set(known)
            or len(candidate_ids) != len(set(candidate_ids))):
        raise ResearchError("Scientific execution requires explicit unique candidates from this campaign")
    if job == "Thermal_MPNN":
        from .stability import prepared_for_request
        prepared_for_request(state, data, candidate_ids, structure_ids)
    if job == "Boltz2":
        if len(candidate_ids) != 1 or data.get("Protein_Sequences") != [known[candidate_ids[0]]["sequence"]]:
            raise ResearchError("Boltz2 inputs must describe the one declared candidate sequence, not another protein or a batch of chains")
        if data.get("SMILES") != [state["task"]["substrate"]["smiles"]] or any(data.get(key) for key in ("DNA_Sequences", "RNA_Sequences")):
            raise ResearchError("This enzyme task permits only its declared substrate, not undeclared extra molecules")
    if job in {"enzycontrol", "Enzyme_RFD3"}:
        if len(candidate_ids) != 1:
            raise ResearchError("Scaffold generation requires one declared input candidate per job")
        count = data.get("n_samples", 1)
        remaining = state["task"]["budget"]["max_unique_candidates"] - (len(known) - 1)
        if type(count) is not int or not 1 <= count <= remaining:
            raise ResearchError("Requested scaffold generation exceeds the campaign's remaining candidate allocation")
        if job == "enzycontrol" and data.get("smiles") != state["task"]["substrate"]["smiles"]:
            raise ResearchError("EnzyControl must use the task's declared substrate")
        if state["task"]["evidence_track"] != "synthetic":
            field = "pdb_path" if job == "enzycontrol" else "input_path"
            receipts = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_uploaded"]
            if not any(r["job_name"] == job and r["input_field"] == field
                       and r["storage_path"] == data.get(field) and r["candidate_ids"] == candidate_ids for r in receipts):
                raise ResearchError("Scaffold generation requires the prepared/uploaded structure for its declared candidate")
    if job in {"Solublempnn", "Ligand_MPNN"}:
        field = "num_seq" if job == "Solublempnn" else "num_sequences"
        count = data.get(field)
        if job == "Solublempnn":
            if not isinstance(count, str) or not count.isascii() or not count.isdigit() or not 0 < len(count) <= 8:
                raise ResearchError("Sequence generation allocation must be a positive whole numeric string")
            count = int(count)
        elif type(count) is not int:
            raise ResearchError("Sequence generation allocation must be a positive whole number")
        remaining = state["task"]["budget"]["max_unique_candidates"] - (len(known) - 1)
        if count < 1 or count * len(candidate_ids) > remaining:
            raise ResearchError("Requested sequence generation exceeds the campaign's remaining candidate allocation")
        if state["task"]["evidence_track"] != "synthetic":
            receipts = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_uploaded"]
            matches = [r for r in receipts if r["job_name"] == job and r["input_field"] == "input_path"
                       and r["storage_path"] == data.get("input_path") and set(r["candidate_ids"]) == set(candidate_ids)]
            if not matches:
                raise ResearchError("Sequence generation requires this campaign's prepared/uploaded structures for the exact selected candidates")
