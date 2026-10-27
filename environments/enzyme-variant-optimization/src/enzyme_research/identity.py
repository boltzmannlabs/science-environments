"""Transfer verified sequence-design results into scientific candidate tracking."""
from __future__ import annotations

import hashlib
from pathlib import Path

from .contracts import ResearchError, candidate_record, digest


def sync_sequences(service, campaign, workflow, step, submission_call_id):
    service.workflow._owned(campaign, workflow)
    state = service.store.status(campaign)
    report = service.workflow.harness.status(workflow)
    current = report["state"]["steps"].get(step)
    definition = next((s for s in report["spec"]["steps"] if s["step_id"] == step), None)
    if (current is None or definition is None or current["status"] != "complete"
            or report["state"]["contracts"][definition["tool"]]["adapter"] != "sequences"):
        raise ResearchError("Sequence transfer requires a validated completed sequence-design artifact")
    call = next((c for c in state["calls"] if c["call_id"] == submission_call_id), None)
    if (call is None or call["tool"] != "boltzmann_submit" or call["status"] != "completed"
            or call["args"].get("job_name") != current.get("job_name")
            or (call.get("result") or {}).get("doc_id") != current.get("doc_id")):
        raise ResearchError("Sequence transfer needs the matching completed original job receipt")
    path = Path(current["artifact_path"])
    if (path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 512 * 1024**2
            or hashlib.sha256(path.read_bytes()).hexdigest() != current["artifact_sha256"]):
        raise ResearchError("Validated sequence artifact is missing, empty or changed")
    source_key = digest({"workflow": workflow, "step": step, "submission": submission_call_id,
                         "artifact_sha256": current["artifact_sha256"]})
    prior = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "sequence_output_imported"
             and e["payload"]["data"].get("source_key") == source_key]
    if prior:
        imported = prior[-1]
    else:
        known = {c["candidate_id"]: c for c in state["candidates"]}
        sequences = {c["sequence"] for c in known.values()}
        accepted, rejected = [], []
        for cid in current["candidate_ids"]:
            candidate = report["state"]["candidates"][cid]
            parents = candidate.get("parent_ids", [])
            try:
                if len(parents) != 1 or parents[0] not in current["input_candidate_ids"] or parents[0] not in known:
                    raise ResearchError("Each designed sequence needs one explicit known parent from this job's inputs")
                if not any(h.get("step_id") == step and h.get("doc_id") == current["doc_id"]
                           and h.get("artifact_sha256") == current["artifact_sha256"] for h in candidate.get("history", [])):
                    raise ResearchError("Candidate provenance does not match this job's validated artifact")
                proposed = {"candidate_id": cid, "parent_id": parents[0], "sequence": candidate.get("sequence")}
                candidate_record(state["task"], proposed)
                if cid in known or proposed["sequence"] in sequences:
                    raise ResearchError("Duplicate candidate identity or sequence; not counted as a new design")
                accepted.append(proposed)
                sequences.add(proposed["sequence"])
            except ResearchError as exc:
                rejected.append({"workflow_candidate_id": cid, "reason": str(exc)})
        imported = {"source_key": source_key, "workflow_id": workflow, "step_id": step,
                    "source_call_id": submission_call_id, "artifact_sha256": current["artifact_sha256"],
                    "accepted_ids": [c["candidate_id"] for c in accepted], "rejected": rejected}
        if accepted:
            service.store.add_candidates(campaign, accepted, provenance=imported)
        else:
            with service.store.transaction() as db:
                service.store.event(db, campaign, "sequence_output_imported", imported)
    # Keep raw validated rows and rejection reasons, but downstream DAG steps
    # may consume only the sequences accepted by the research identity gate.
    with service.workflow.harness.store.transaction(workflow) as (db, _, wfstate):
        wfstep = wfstate["steps"][step]
        if not wfstep.get("research_identity_bound"):
            raw_ids = list(wfstep["candidate_ids"])
            if set(imported["accepted_ids"]) | {r["workflow_candidate_id"] for r in imported["rejected"]} != set(raw_ids):
                raise ResearchError("Research sequence selection does not account for every original output row")
            wfstep["raw_candidate_ids"] = raw_ids
            wfstep["candidate_ids"] = list(imported["accepted_ids"])
            wfstep["research_identity_bound"] = True
            for rejected in imported["rejected"]:
                candidate = wfstate["candidates"][rejected["workflow_candidate_id"]]
                candidate["status"] = "rejected_by_research_identity"
                candidate.setdefault("gates", {})["research_sequence_identity"] = "rejected"
            for cid in imported["accepted_ids"]:
                wfstate["candidates"][cid].setdefault("gates", {})["research_sequence_identity"] = "passed"
            service.workflow.harness.store.event(db, workflow, "research_sequence_selection", {
                "step_id": step, "raw_count": len(raw_ids), "accepted_ids": imported["accepted_ids"], "rejected": imported["rejected"]})
    observation_id = "observation-sequences-" + source_key[:16]
    state = service.store.status(campaign)
    observation = next((o for o in state["observations"] if o["observation_id"] == observation_id), None)
    if observation is None:
        ids = imported["accepted_ids"] or current["input_candidate_ids"]
        metrics = ({cid: {"protected_sequence_identities_preserved": True, "requires_new_structure": True}
                    for cid in imported["accepted_ids"]} if imported["accepted_ids"] else
                   {cid: {"accepted_sequence_count": 0, "rejected_sequence_count": len(imported["rejected"])} for cid in ids})
        observation = service.store.add_observation(campaign, {
            "observation_id": observation_id, "kind": "sequence_design", "candidate_ids": ids,
            "evidence_level": "synthetic_fixture" if state["task"]["evidence_track"] == "synthetic" else "computational_prediction",
            "metrics": metrics, "artifacts": [{"path": str(path), "sha256": current["artifact_sha256"]}],
            "source_call_id": submission_call_id})
    return {**imported, "observation": observation,
            "boundary": "Sequence identity and catalytic-residue preservation only; folding and catalytic geometry are not established"}
