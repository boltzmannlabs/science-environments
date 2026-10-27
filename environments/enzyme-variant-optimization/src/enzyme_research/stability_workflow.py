"""Additive workflow hook for full ThermoMPNN matrices, not scalar CSV rows."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

from .contracts import ResearchError


METADATA = {
    "stage": "properties", "adapter": "report", "requires": ["structure"],
    "contract_ref": {"path": "tool-contracts.v1.json", "entry": "Thermal_MPNN"},
    "adapter_source": "enzyme_research.stability_workflow",
    "notes": "Complete single-substitution matrix; exact Dataset and gap-index mapping; not an absolute/multi-mutant score",
}


def catalogue_extension(catalogue_root, bindings=None, extensions=None):
    bindings, extensions = dict(bindings or {}), dict(extensions or {})
    doc = json.loads((Path(catalogue_root) / "tool-contracts.v1.json").read_bytes())
    if "Thermal_MPNN" not in doc.get("tools", {}):
        return bindings, extensions
    if "thermompnn" in extensions and extensions["thermompnn"] != METADATA:
        raise ResearchError("ThermoMPNN extension conflicts with the audited external matrix adapter")
    supplied = bindings.get("thermompnn", {})
    if (not isinstance(supplied, dict) or supplied.get("job_name", "Thermal_MPNN") != "Thermal_MPNN"
            or supplied.get("contract_ref", METADATA["contract_ref"]) != METADATA["contract_ref"]
            or supplied.get("backend_status", "catalogue") not in {"catalogue", "pending"}):
        raise ResearchError("The audited ThermoMPNN adapter must derive routing/status from its original canonical contract")
    extensions["thermompnn"] = METADATA
    bindings["thermompnn"] = {"backend_status": "catalogue", **supplied}
    return bindings, extensions


def ingest(executor, harness, db, wid, step, current, state, *, campaign,
           local_path=None, bindings=None, member=None):
    from enzyme_workflow.common import file_hash
    from .results import workflow_bindings
    from .stability import prepared_for_request, parse_output
    if not isinstance(local_path, str):
        raise ResearchError("ThermoMPNN ingestion requires the actual downloaded artifact path")
    path = Path(local_path)
    if path.is_symlink() or not path.is_file():
        raise ResearchError("ThermoMPNN result must be a regular downloaded file")
    source_sha = file_hash(path)
    receipt = db.execute("SELECT local_path FROM downloads WHERE workflow_id=? AND step_id=? AND sha256=? AND intent_id=?",
                         (wid, step["step_id"], source_sha, current["intent_id"])).fetchone()
    if receipt is None:
        raise ResearchError("ThermoMPNN artifact has no matching download receipt from this original job")
    associations = workflow_bindings(executor, campaign, wid, current["input_candidate_ids"], require_coordinates=True)
    research = executor.store.status(campaign)
    calls = [c for c in research["calls"] if c["tool"] == "boltzmann_submit" and c["status"] == "completed"
             and c["args"].get("job_name") == "Thermal_MPNN" and (c.get("result") or {}).get("doc_id") == current.get("doc_id")]
    if len(calls) != 1:
        raise ResearchError("ThermoMPNN ingestion requires the unique matching completed source submission")
    data = calls[0]["args"]["experiment_data"]
    if data != step["inputs"]:
        raise ResearchError("ThermoMPNN source submission settings differ from the frozen workflow step")
    ids = [a["candidate_id"] for a in associations.values()]
    versions = {a["candidate_id"]: a["structure_id"] for a in associations.values()}
    if len(ids) != len(set(ids)) or step.get("expected_count", len(ids)) != len(ids):
        raise ResearchError("ThermoMPNN expects one explicit coordinate input per selected sequence")
    prepared = prepared_for_request(research, data, ids, versions)
    matrices = parse_output(path, prepared["stability_layouts"], member=member)
    expected_bindings = {a["candidate_id"]: {"candidate_id": wid_candidate} for wid_candidate, a in associations.items()}
    if bindings not in (None, {}) and bindings != expected_bindings:
        raise ResearchError("ThermoMPNN bindings conflict with the exact Dataset/structure identities")
    destination = harness.store.root / wid / "artifacts" / source_sha / path.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() != path.resolve():
        shutil.copyfile(path, destination)
    if file_hash(destination) != source_sha or file_hash(path) != source_sha:
        raise ResearchError("ThermoMPNN artifact changed during ingestion")
    for wid_candidate, association in associations.items():
        cid = association["candidate_id"]
        candidate = state["candidates"][wid_candidate]
        candidate.setdefault("metrics", {})[step["step_id"]] = {
            "by_structure": {association["structure_id"]: matrices[cid]}}
        candidate["history"].append({"step_id": step["step_id"], "tool": "thermompnn", "output_label": cid,
                                     "artifact_sha256": source_sha, "doc_id": current["doc_id"]})
    current.update(status="complete", candidate_ids=list(associations), artifact_path=str(destination), artifact_sha256=source_sha)
    harness.store.event(db, wid, "output_validated", {"step_id": step["step_id"], "count": len(ids),
        "sha256": source_sha, "adapter": "thermompnn_complete_single_mutation_matrix"})
    if all(item["status"] == "complete" for item in state["steps"].values()):
        state["status"] = "complete"
    return {"status": "complete", "candidate_ids": list(associations), "artifact_path": str(destination)}
