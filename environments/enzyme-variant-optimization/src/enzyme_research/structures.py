"""Verified coordinate versions, residue mappings and structure handoff.

An exact protein sequence establishes sequence-to-residue numbering, not folding
quality or substrate identity. A non-water HETATM is not automatically the task's
substrate. Unknown ligand chemistry therefore cannot unlock catalytic checks.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from .contracts import ResearchError, digest


def coordinate_metadata(parsed, task, candidate):
    if parsed["structural_sequence"] != candidate["sequence"]:
        raise ResearchError("Predicted structure sequence does not match the explicitly bound candidate")
    labels = parsed["residues"]
    matches = [re.fullmatch(r"([A-Za-z])(-?\d+)([A-Za-z]?)", label) for label in labels]
    if (len(labels) != len(candidate["sequence"]) or len(set(labels)) != len(labels)
            or any(m is None for m in matches) or len({m[1] for m in matches}) != 1):
        raise ResearchError("Automatic residue mapping needs one unambiguous exact-sequence protein chain with letter chain labels; supply a reviewed preparation for other structures")
    mapping = {}
    for site in task["parent"]["catalytic_residues"]:
        position = site["sequence_position"]
        if candidate["sequence"][position - 1] != site["amino_acid"]:
            raise ResearchError("Candidate no longer preserves a required catalytic identity")
        target = matches[position - 1]
        mapping[site["chain"] + site["residue"]] = {
            "chain_id": target[1], "residue_number": int(target[2]), "insertion_code": target[3]}
    detected = sorted(set(parsed["capabilities"]))
    capabilities = set(detected) - {"ligand"}
    if "ligand" in detected:
        capabilities.add("ligand_present_unverified")
    capabilities.update({"sequence", "mapping"})
    return {"capabilities": sorted(capabilities), "detected_capabilities": detected,
            "residue_count": parsed["residue_count"], "atom_count": parsed["atom_count"],
            "mapping": mapping, "mapping_method": "exact_single_chain_sequence_identity",
            "ligand_identity_verified": False, "quality_validated": False}


def checked_structure_content(record):
    from enzyme_workflow.artifacts import inspect_structure, read_members, MAX_TOTAL
    from enzyme_workflow.common import file_hash
    source = record["artifact"]
    path = Path(source["path"])
    if (path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_TOTAL
            or file_hash(path) != source["sha256"]):
        raise ResearchError("Coordinate artifact is missing, empty or changed")
    members = read_members(path)
    if source["member"] not in members:
        raise ResearchError("Verified structure member is absent from its coordinate artifact")
    content = members[source["member"]]
    if hashlib.sha256(content).hexdigest() != source["member_sha256"]:
        raise ResearchError("Coordinate member bytes no longer match the registered structure")
    parsed = inspect_structure(source["member"], content)
    if hashlib.sha256(parsed["structural_sequence"].encode()).hexdigest() != record["sequence_sha256"]:
        raise ResearchError("Coordinate sequence no longer matches its registered sequence identity")
    if sorted(set(parsed["capabilities"])) != record["detected_capabilities"]:
        raise ResearchError("Coordinate capabilities changed since registration")
    return content


def select_structure(service, campaign, candidate_id, structure_id=None):
    """Use an explicit version when a candidate has more than one structure."""
    state = service.store.status(campaign)
    candidate = next((c for c in state["candidates"] if c["candidate_id"] == candidate_id), None)
    if candidate is None:
        raise ResearchError("Structure selection refers to an unknown candidate")
    records = [r for r in state["structures"] if r["candidate_id"] == candidate_id
               and (structure_id is None or r["structure_id"] == structure_id)]
    supplied_id = "supplied-" + state["task"]["parent"]["structure"]["sha256"][:20]
    if candidate_id == state["task"]["parent"]["candidate_id"] and structure_id in {None, supplied_id}:
        # The frozen user-supplied parent is not a model output or a quality pass.
        from enzyme_workflow.artifacts import inspect_structure
        source = state["task"]["parent"]["structure"]
        path = Path(source["path"])
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 10 * 1024**2:
            raise ResearchError("Frozen parent structure is not a bounded regular file")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != source["sha256"]:
            raise ResearchError("Frozen parent structure changed")
        metadata = coordinate_metadata(inspect_structure(path.name, content), state["task"], candidate)
        record = {"structure_id": "supplied-" + source["sha256"][:20], "candidate_id": candidate_id,
                  "sequence_sha256": candidate["sequence_sha256"], "artifact": {
                      "path": str(path), "sha256": source["sha256"], "member": path.name, "member_sha256": source["sha256"]},
                  "source": {"kind": "frozen_user_supplied_parent"}, **metadata}
        records.append(record)
    if len(records) != 1:
        raise ResearchError("Select one verified structure_id for this candidate; zero or multiple coordinate versions cannot be guessed")
    checked_structure_content(records[0])
    from .ligands import apply_verification
    return apply_verification(records[0], state)


def sync_structures(service, campaign, workflow, step, submission_call_id):
    """Attach validated folding/docking outputs to their exact input sequence."""
    service.workflow._owned(campaign, workflow)
    state = service.store.status(campaign)
    report = service.workflow.harness.status(workflow)
    current = report["state"]["steps"].get(step)
    definition = next((s for s in report["spec"]["steps"] if s["step_id"] == step), None)
    contract = report["state"]["contracts"].get(definition["tool"]) if definition else None
    if (not current or current["status"] != "complete" or not contract or contract["adapter"] != "structures"
            or contract["stage"] not in {"folding", "preparation", "docking"}):
        raise ResearchError("Structure transfer requires a completed, validated sequence-conditioned folding/preparation/docking output")
    source = next((c for c in state["calls"] if c["call_id"] == submission_call_id), None)
    if (source is None or source["tool"] != "boltzmann_submit" or source["status"] != "completed"
            or source["args"].get("job_name") != current.get("job_name")
            or (source.get("result") or {}).get("doc_id") != current.get("doc_id")):
        raise ResearchError("Structure transfer needs the matching completed original submission receipt")
    from enzyme_workflow.artifacts import inspect_structure, read_members, MAX_TOTAL
    from enzyme_workflow.common import file_hash
    path = Path(current["artifact_path"])
    if (path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_TOTAL
            or file_hash(path) != current["artifact_sha256"]):
        raise ResearchError("Validated coordinate artifact is missing, empty or changed")
    members = read_members(path)
    known = {c["candidate_id"]: c for c in state["candidates"]}
    records = []
    for wid in current["candidate_ids"]:
        generated = report["state"]["candidates"][wid]
        parents = generated.get("parent_ids", [])
        if len(parents) != 1 or parents[0] not in current["input_candidate_ids"] or parents[0] not in known:
            raise ResearchError("Each coordinate output needs one explicit known sequence parent; never associate outputs by row order")
        artifact = generated.get("structure", {})
        if (artifact.get("artifact_path") != str(path) or artifact.get("sha256") != current["artifact_sha256"]
                or artifact.get("member") not in members):
            raise ResearchError("Candidate coordinates do not belong to the validated original artifact")
        history = [h for h in generated.get("history", []) if h.get("step_id") == step
                   and h.get("doc_id") == current["doc_id"] and h.get("artifact_sha256") == current["artifact_sha256"]]
        if len(history) != 1:
            raise ResearchError("Coordinate output lacks an unambiguous original job association")
        candidate = known[parents[0]]
        content = members[artifact["member"]]
        metadata = coordinate_metadata(inspect_structure(artifact["member"], content), state["task"], candidate)
        record = {"candidate_id": candidate["candidate_id"], "sequence_sha256": candidate["sequence_sha256"],
            "artifact": {"path": str(path), "sha256": current["artifact_sha256"], "member": artifact["member"],
                         "member_sha256": hashlib.sha256(content).hexdigest()},
            "source": {"source_call_id": submission_call_id, "workflow_id": workflow, "step_id": step,
                       "workflow_candidate_id": wid, "output_label": history[0]["output_label"]}, **metadata}
        record["structure_id"] = "structure-" + digest(record)[:20]
        records.append(record)
    if not records:
        raise ResearchError("Empty coordinate output cannot establish a folding observation")
    for record in records:
        service.store.add_structure_version(campaign, record)
    kind = "docking" if contract["stage"] == "docking" else "folding"
    observation_id = "observation-structures-" + digest({"workflow": workflow, "step": step, "source": submission_call_id})[:16]
    current_state = service.store.status(campaign)
    observation = next((o for o in current_state["observations"] if o["observation_id"] == observation_id), None)
    if observation is None:
        ids = sorted({r["candidate_id"] for r in records})
        metrics = {cid: {"structure_ids": [r["structure_id"] for r in records if r["candidate_id"] == cid],
                         "all_atom_structure_count": sum("all_atom" in r["capabilities"] for r in records if r["candidate_id"] == cid),
                         "quality_validation": "not_established", "substrate_identity": "not_established"} for cid in ids}
        observation = service.store.add_observation(campaign, {
            "observation_id": observation_id, "kind": kind, "candidate_ids": ids,
            "evidence_level": "synthetic_fixture" if state["task"]["evidence_track"] == "synthetic" else "computational_prediction",
            "metrics": metrics, "artifacts": [{"path": str(path), "sha256": current["artifact_sha256"]}],
            "source_call_id": submission_call_id})
    return {"structure_ids": [r["structure_id"] for r in records], "observation": observation,
            "boundary": "Coordinate identity and atom completeness only; no structural-quality, catalytic-geometry or activity pass is implied"}
