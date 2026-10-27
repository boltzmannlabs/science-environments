"""Join verified workflow outputs to research sequences and coordinate versions."""
from __future__ import annotations

from pathlib import Path

from .contracts import ResearchError, digest


def sequence_report_bindings(entries, expected_sequences):
    """Join sequence reports by exact sequence, allowing renamed output IDs.

    Without a reported sequence, only an exact submitted ID is acceptable.
    No row-order matching, approximate sequences, or best-replicate choice.
    """
    if (not entries or len(entries) != len(expected_sequences)
            or len(set(expected_sequences.values())) != len(expected_sequences)):
        raise ResearchError("Sequence report must cover unique submitted sequences exactly once")
    by_sequence = {sequence: cid for cid, sequence in expected_sequences.items()}
    bindings, seen = {}, set()
    for entry in entries:
        label, metrics = entry.get("label"), entry.get("metrics", {})
        if not isinstance(label, str) or not label or label in bindings:
            raise ResearchError("Sequence report output labels must be unique and nonempty")
        values = [metrics[key] for key in ("Sequence", "Sequences", "sequence", "sequences") if key in metrics]
        if values:
            if any(not isinstance(value, str) or value not in by_sequence for value in values) or len(set(values)) != 1:
                raise ResearchError("Sequence report has an unknown, changed or contradictory full sequence")
            cid = by_sequence[values[0]]
        elif label in expected_sequences:
            cid = label
        else:
            raise ResearchError("Renamed report identifiers require an exact full-sequence identity")
        if cid in seen:
            raise ResearchError("Duplicate sequence report rows cannot replace a missing candidate")
        bindings[label] = {"candidate_id": cid}; seen.add(cid)
    if seen != set(expected_sequences):
        raise ResearchError("Sequence report is incomplete for the submitted candidates")
    return bindings


def derive_sequence_report_bindings(service, campaign, workflow, step, local_path, *, member=None):
    service.workflow._owned(campaign, workflow)
    report = service.workflow.harness.status(workflow)
    current = report["state"]["steps"].get(step)
    definition = next((s for s in report["spec"]["steps"] if s["step_id"] == step), None)
    if not current or not definition or definition["tool"] != "netsolp":
        raise ResearchError("This sequence-report identity adapter is audited for NetSolP only")
    from enzyme_workflow.artifacts import inspect_artifact, read_members
    ids = current.get("input_candidate_ids", [])
    workflow_bindings(service.workflow, campaign, workflow, ids)
    expected = {cid: report["state"]["candidates"][cid]["sequence"] for cid in ids}
    if member is None:
        entries = inspect_artifact(local_path, "report")["entries"]
    else:
        import tempfile
        files = read_members(local_path)
        if not isinstance(member, str) or Path(member).name != member or member not in files:
            raise ResearchError("Select one exact top-level report member from this artifact")
        with tempfile.TemporaryDirectory(prefix="sequence-report-validation-") as directory:
            selected = Path(directory) / member
            selected.write_bytes(files[member])
            entries = inspect_artifact(selected, "report")["entries"]
    return sequence_report_bindings(entries, expected)


def workflow_bindings(executor, campaign, workflow, candidate_ids, *, require_coordinates=False):
    """Resolve explicit provenance, never output order or nearest sequence."""
    executor._owned(campaign, workflow)
    state = executor.store.status(campaign)
    report = executor.harness.status(workflow)
    known = {c["candidate_id"]: c for c in state["candidates"]}
    versions = state["structures"]
    result = {}
    from .structures import select_structure, checked_structure_content
    from enzyme_workflow.common import file_hash
    for wid in candidate_ids:
        current = report["state"]["candidates"].get(wid)
        if not current or current.get("status") == "rejected_by_research_identity":
            raise ResearchError("Output association refers to an unknown or rejected workflow candidate")
        matching = [v for v in versions if v["source"].get("workflow_id") == workflow
                    and v["source"].get("workflow_candidate_id") == wid]
        if matching:
            if len(matching) != 1:
                raise ResearchError("Workflow coordinate provenance is ambiguous")
            record = matching[0]
            cid = record["candidate_id"]
        elif wid in known:
            cid = wid
            selected = [h["structure_id"] for h in current.get("history", [])
                        if h.get("source") == "verified_research_coordinates"]
            if len(set(selected)) > 1:
                raise ResearchError("A workflow candidate has conflicting selected coordinate versions")
            record = select_structure(executor, campaign, cid, selected[0]) if selected else None
            if record is None and cid == state["task"]["parent"]["candidate_id"] and current.get("structure"):
                supplied = "supplied-" + state["task"]["parent"]["structure"]["sha256"][:20]
                record = select_structure(executor, campaign, cid, supplied)
        else:
            raise ResearchError("Workflow output has no verified association to a research candidate")
        if cid not in known or current.get("sequence") != known[cid]["sequence"]:
            raise ResearchError("Workflow and research sequence identities disagree")
        if record is not None:
            checked_structure_content(record)
            artifact = current.get("structure", {})
            if (artifact.get("sha256") != record["artifact"]["sha256"]
                    or artifact.get("member") != record["artifact"]["member"]
                    or not isinstance(artifact.get("artifact_path"), str)):
                raise ResearchError("Workflow coordinates differ from the selected registered version")
            path = Path(artifact["artifact_path"])
            if path.is_symlink() or not path.is_file() or file_hash(path) != record["artifact"]["sha256"]:
                raise ResearchError("Workflow coordinate artifact is missing or changed")
        if require_coordinates and record is None:
            raise ResearchError("Structural measurements require an explicit verified coordinate version")
        result[wid] = {"candidate_id": cid, "structure_id": record["structure_id"] if record else None}
    return result


def sync_metrics(service, campaign, workflow, step, submission_call_id, kind=None):
    """Derive a restart-safe scientific observation from an ingested artifact."""
    service.workflow._owned(campaign, workflow)
    state = service.store.status(campaign)
    report = service.workflow.harness.status(workflow)
    current = report["state"]["steps"].get(step)
    definition = next((s for s in report["spec"]["steps"] if s["step_id"] == step), None)
    if not current or not definition or current["status"] != "complete":
        raise ResearchError("Metric transfer requires the completed validated original workflow step")
    metadata = report["state"]["contracts"][definition["tool"]]
    if metadata["adapter"] in {"sequences", "structures"}:
        raise ResearchError("Sequence/coordinate outputs use their identity-transfer adapters, not metric transfer")
    observed = {"netsolp": "solubility", "catpred": "activity", "kcat": "activity", "thermompnn": "stability"}.get(definition["tool"])
    if metadata["adapter"] in {"quality", "geometry"}:
        observed = metadata["adapter"]
    if observed is not None and kind not in {None, observed}:
        raise ResearchError("Observation kind does not match the executed scientific capability")
    kind = observed or kind
    if kind is None:
        raise ResearchError("An audited observation kind is required for this report capability")
    source = next((c for c in state["calls"] if c["call_id"] == submission_call_id), None)
    if (source is None or source["tool"] != "boltzmann_submit" or source["status"] != "completed"
            or source["args"].get("job_name") != current.get("job_name")
            or (source.get("result") or {}).get("doc_id") != current.get("doc_id")):
        raise ResearchError("Metric transfer needs the matching completed original scientific job")
    structural = metadata["adapter"] in {"quality", "geometry"}
    bindings = workflow_bindings(service.workflow, campaign, workflow, current["candidate_ids"], require_coordinates=structural)
    metrics, versions, outcomes = {}, {}, {}
    for wid, association in bindings.items():
        cid, sid = association["candidate_id"], association["structure_id"]
        candidate = report["state"]["candidates"][wid]
        raw = candidate.get("metrics", {}).get(step)
        if not raw:
            raise ResearchError("Validated report has no scientific metrics for a selected candidate")
        if not any(h.get("step_id") == step and h.get("doc_id") == current["doc_id"]
                   and h.get("artifact_sha256") == current["artifact_sha256"] for h in candidate.get("history", [])):
            raise ResearchError("Metric row does not belong to this original job's validated artifact")
        if structural:
            if sid in versions:
                raise ResearchError("Multiple rows refer to the same coordinate version; no averaging is inferred")
            versions[sid] = cid
            outcomes[sid] = candidate.get("gates", {}).get(step)
            metrics.setdefault(cid, {"by_structure": {}})["by_structure"][sid] = raw
        else:
            if cid in metrics:
                raise ResearchError("Multiple report rows refer to one sequence; an explicit scientific aggregation is required")
            metrics[cid] = raw
    if not metrics:
        raise ResearchError("Empty metric output cannot create a scientific observation")
    value = {"observation_id": "observation-" + digest({"workflow": workflow, "step": step})[:16],
        "kind": kind, "candidate_ids": list(metrics),
        "evidence_level": "synthetic_fixture" if state["task"]["evidence_track"] == "synthetic" else
                          "structural_measurement" if structural else "computational_prediction",
        "metrics": metrics, "artifacts": [{"path": current["artifact_path"], "sha256": current["artifact_sha256"]}],
        "source_call_id": submission_call_id}
    if structural:
        value["coordinate_scope"] = {"structure_candidates": versions, "outcomes": outcomes,
                                     "execution_mode": definition["inputs"].get("execution_mode", "measurement_only")}
    observation = service.store.add_observation(campaign, value)
    return {"observation": observation,
            "boundary": "Structural results apply only to their recorded coordinate versions; predictions and checks are not assay evidence"}
