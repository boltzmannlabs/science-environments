"""Evidence joins and current artifact checks, never invented scientific scores.

Reports do not rank candidates or certify the pinned research milestones.
They preserve sequence and coordinate scopes, missing evidence and failures.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sqlite3

from .contracts import ResearchError, canonical, digest

KINDS = ("activity", "stability", "solubility", "folding", "quality", "geometry", "docking", "sequence_design")


def joined_structure_checks(outcomes, all_atom_ids):
    """Never combine different poses or hide any recorded rejection."""
    shared = set(outcomes["quality"]) & set(outcomes["geometry"])
    nonrejected = {sid for sid in shared & set(all_atom_ids)
                   if all(check["outcome"] in {"measured", "passed"}
                          for kind in outcomes for check in outcomes[kind][sid])}
    validated = {sid for sid in nonrejected
                 if all(check["outcome"] == "passed" and check["execution_mode"] == "validation"
                        for kind in outcomes for check in outcomes[kind][sid])}
    return shared, nonrejected, validated


def _artifact_ok(artifact, cache):
    key = (artifact.get("path"), artifact.get("sha256"))
    if key in cache:
        return cache[key]
    path = Path(key[0]) if isinstance(key[0], str) else None
    try:
        if path is None or path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 512 * 1024**2:
            raise ValueError()
        before = path.stat()
        with path.open("rb") as handle:
            value = hashlib.file_digest(handle, "sha256").hexdigest()
        after = path.stat()
        valid = value == key[1] and (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    except (OSError, ValueError):
        valid = False
    cache[key] = valid
    return valid


def _workflow_steps(store, state):
    """Read only this campaign's saved executor state; no new jobs or repairs."""
    path = store.root / "workflow_executor/state.sqlite"
    expected = {e["payload"]["data"]["workflow_id"]: e["payload"]["data"]["specification_sha256"]
                for e in state["events"] if e["payload"]["event"] == "workflow_segment_created"}
    if not expected:
        return [], []
    if path.is_symlink() or not path.is_file():
        return [], ["Owned workflow receipt database is missing or aliased"]
    records, errors = [], []
    try:
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            for wid, sha in expected.items():
                row = db.execute("SELECT spec,state FROM workflows WHERE id=?", (wid,)).fetchone()
                if row is None:
                    errors.append("Owned workflow receipt is missing: " + wid)
                    continue
                spec, saved = (json.loads(value) for value in row)
                if digest(spec) != sha:
                    errors.append("Owned workflow specification changed: " + wid)
                    continue
                for step in spec["steps"]:
                    current = saved["steps"][step["step_id"]]
                    metadata = saved["contracts"][step["tool"]]
                    kind = {"netsolp": "solubility", "catpred": "activity", "kcat": "activity",
                            "thermompnn": "stability"}.get(step["tool"])
                    if metadata["adapter"] in {"quality", "geometry"}:
                        kind = metadata["adapter"]
                    elif metadata["adapter"] == "sequences":
                        kind = "sequence_design"
                    elif metadata["adapter"] == "structures" and metadata["stage"] in {"folding", "preparation", "docking"}:
                        kind = "docking" if metadata["stage"] == "docking" else "folding"
                    records.append({"workflow_id": wid, "step_id": step["step_id"], "tool_id": step["tool"],
                                    "kind": kind, "current": current, "inputs_sha256": digest(step["inputs"])})
    except (sqlite3.Error, json.JSONDecodeError, KeyError, TypeError):
        return [], ["Owned workflow receipt database could not be verified"]
    return records, errors


def build_report(store, campaign):
    state = store.status(campaign)
    calls = {c["call_id"]: c for c in state["calls"]}
    steps, receipt_errors = _workflow_steps(store, state)
    cache, observation_checks, observations = {}, {}, {}
    for observation in state["observations"]:
        call = calls.get(observation["source_call_id"])
        matching = [step for step in steps if step["current"].get("status") == "complete"
                    and step["kind"] == observation["kind"] and call and call["tool"] == "boltzmann_submit"
                    and call["status"] == "completed" and call["args"].get("job_name") == step["current"].get("job_name")
                    and (call.get("result") or {}).get("doc_id") == step["current"].get("doc_id")
                    and step["current"].get("doc_id")
                    and any(a["sha256"] == step["current"].get("artifact_sha256") for a in observation["artifacts"])]
        artifacts_valid = bool(observation["artifacts"]) and all(_artifact_ok(a, cache) for a in observation["artifacts"])
        valid = len(matching) == 1 and artifacts_valid
        observation_checks[observation["observation_id"]] = {
            "source_job_and_adapter_verified": len(matching) == 1, "artifacts_verified_now": artifacts_valid,
            "usable": valid, "evidence_level": observation["evidence_level"]}
        if valid:
            observations[observation["observation_id"]] = observation
    # A source table may describe scores for a different basis sequence; its
    # derived single-substitution observations retain the original matrix link.
    for oid, observation in list(observations.items()):
        if observation["kind"] != "stability":
            continue
        for cid, metric in observation["metrics"].items():
            source_id = metric.get("source_observation_id") if isinstance(metric, dict) else None
            if source_id is not None and (source_id not in observations or source_id == oid):
                observation_checks[oid]["usable"] = False
                observations.pop(oid, None)
    structures, structure_checks = {}, {}
    for record in state["structures"]:
        call = calls.get(record["source"].get("source_call_id"))
        valid = (bool(call) and call["tool"] == "boltzmann_submit" and call["status"] == "completed"
                 and _artifact_ok(record["artifact"], cache))
        structure_checks[record["structure_id"]] = valid
        if valid:
            structures[record["structure_id"]] = record
    parent = state["task"]["parent"]
    supplied_id = "supplied-" + parent["structure"]["sha256"][:20]
    supplied_valid = _artifact_ok(parent["structure"], cache)
    # The supplied parent is a structure reference, not a prediction or pass.
    structure_checks[supplied_id] = supplied_valid
    if supplied_valid:
        try:
            from types import SimpleNamespace
            from .structures import select_structure
            structures[supplied_id] = select_structure(SimpleNamespace(store=store), campaign, parent["candidate_id"], supplied_id)
        except (ImportError, ResearchError, ValueError):
            # CLI-only core installations may lack the original parser runtime.
            # The file hash remains verified; no atom completeness is invented.
            receipt_errors.append("Supplied parent coordinates could not be reparsed with the original structural parser")
    rows = []
    for candidate in state["candidates"]:
        cid = candidate["candidate_id"]
        sequence = candidate["sequence"]
        sequence_valid = (hashlib.sha256(sequence.encode()).hexdigest() == candidate["sequence_sha256"]
                          and len(sequence) == len(parent["sequence"]))
        catalytic = sequence_valid and all(sequence[s["sequence_position"] - 1] == s["amino_acid"] for s in parent["catalytic_residues"])
        evidence = {kind: [] for kind in KINDS}
        outcomes = {"quality": {}, "geometry": {}}
        matrices, point_scores = [], []
        for oid, observation in observations.items():
            if cid not in observation["candidate_ids"] or cid not in observation["metrics"]:
                continue
            kind, metric = observation["kind"], observation["metrics"][cid]
            reference = {"observation_id": oid, "source_call_id": observation["source_call_id"],
                         "job_name": calls[observation["source_call_id"]]["args"].get("job_name"),
                         "evidence_level": observation["evidence_level"],
                         "context_ref": {"view": "observations", "record_id": oid,
                                         "pointer": "/metrics/" + cid.replace("~", "~0").replace("/", "~1")}}
            if kind in evidence:
                evidence[kind].append(reference)
            if kind in outcomes:
                scope = observation["coordinate_scope"]
                for sid, owner in scope["structure_candidates"].items():
                    if owner == cid and structure_checks.get(sid, False):
                        outcomes[kind].setdefault(sid, []).append({"observation_id": oid,
                            "outcome": scope["outcomes"][sid], "execution_mode": scope["execution_mode"]})
            if kind == "stability" and isinstance(metric, dict):
                matrices.extend(sid for sid, table in metric.get("by_structure", {}).items()
                                if table.get("schema") == "thermompnn-upstream-saturation/1" and structure_checks.get(sid, False))
                if metric.get("source_schema") == "thermompnn-upstream-saturation/1":
                    point_scores.append({"observation_id": oid, "basis_candidate_id": metric["basis_candidate_id"],
                        "basis_structure_id": metric["basis_structure_id"], "sequence_mutation": metric["sequence_mutation"],
                        "ddG_pred": metric["ddG_pred"], "units": metric["units"]})
        versions = [r for r in structures.values() if r["candidate_id"] == cid and r["sequence_sha256"] == candidate["sequence_sha256"]]
        all_atom_ids = {r["structure_id"] for r in versions if "all_atom" in r["capabilities"]}
        shared, nonrejected, validated = joined_structure_checks(outcomes, all_atom_ids)
        counts = {kind: len(refs) for kind, refs in evidence.items()}
        missing = [kind for kind in ("activity", "solubility", "folding") if counts[kind] == 0]
        if cid != parent["candidate_id"] and not any(p["basis_candidate_id"] == parent["candidate_id"] for p in point_scores):
            missing.append("parent_relative_variant_stability")
        if cid == parent["candidate_id"] and not matrices:
            missing.append("stability_reference_matrix")
        if not shared:
            missing.append("quality_and_geometry_on_same_coordinates")
        elif not nonrejected:
            missing.append("nonrejected_quality_and_geometry_on_same_all_atom_coordinates")
        rows.append({"candidate_id": cid, "parent_id": candidate["parent_id"], "sequence_sha256": candidate["sequence_sha256"],
            "sequence_length": len(sequence), "mutation_count": len(candidate["mutations_from_reference"]),
            "sequence_identity_verified_now": sequence_valid, "catalytic_sequence_preserved": catalytic,
            "evidence_counts": counts, "evidence": evidence, "coordinate_versions": [r["structure_id"] for r in versions],
            "all_atom_structure_count": len(all_atom_ids), "structure_outcomes": outcomes,
            "co_checked_structure_ids": sorted(shared), "nonrejected_co_checked_structure_ids": sorted(nonrejected),
            "jointly_validation_passed_structure_ids": sorted(validated),
            "stability_matrix_structure_ids": sorted(set(matrices)), "single_mutation_predictions": point_scores,
            "missing_evidence": missing, "rank": None,
            "boundary": "Available predictions/checks are not experimental outcomes or automatic shortlist approval"})
    submissions = [c for c in state["calls"] if c["tool"] == "boltzmann_submit"]
    ledger = [{"call_id": c["call_id"], "job_name": c["args"].get("job_name"),
               "doc_id": (c.get("result") or {}).get("doc_id"), "status": c["status"],
               "context_ref": {"view": "calls", "record_id": c["call_id"]},
               "experiment_data_sha256": digest(c["args"].get("experiment_data", {}))} for c in submissions]
    feedback = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "decision_observed"]
    reference_selections = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "reference_selection_recorded"]
    ligand_verifications = [{"verification": e["payload"]["data"],
                             "coordinate_artifact_verified_now": structure_checks.get(e["payload"]["data"]["structure_id"], False)}
                            for e in state["events"] if e["payload"]["event"] == "ligand_identity_verified"]
    report = {"schema_version": "enzyme-candidate-evidence-report/1", "campaign_id": campaign,
        "task_sha256": digest(state["task"]), "arm": state["arm"], "status": state["status"],
        "evidence_track": state["task"]["evidence_track"], "candidate_rows": rows,
        "execution_ledger": ledger, "scientific_submission_attempts": len(ledger),
        "unresolved_submission_call_ids": [c["call_id"] for c in submissions if c["status"] not in {"completed", "definite_failure"}],
        "failed_submission_call_ids": [c["call_id"] for c in submissions if c["status"] == "definite_failure"],
        "reported_observation_count": len(observation_checks), "usable_observation_count": len(observations),
        "observation_checks": observation_checks, "structure_checks": structure_checks, "receipt_errors": receipt_errors,
        "observed_decision_feedback": feedback, "reasoning_and_total_resource_accounting": "not_established_by_this_report",
        "live_completion_established": False, "experimental_improvement_established": False,
        "final_selection_status": "fixed_reference_selection_recorded" if reference_selections else "not_recorded",
        "ranking_status": "frozen_reference_selection_available" if reference_selections else "not_applied_no_frozen_ranking_policy",
        "reference_selection_receipts": reference_selections,
        "ligand_verification_records": ligand_verifications,
        "boundary": "Evidence availability only; no silent averaging, cross-pose passes, automatic ranking or complete-plan certification"}
    report["snapshot_sha256"] = digest(report)
    return report


def summary(report):
    """Bounded native response; complete evidence remains explicitly pageable."""
    keys = ("schema_version", "campaign_id", "task_sha256", "arm", "status", "evidence_track", "snapshot_sha256",
            "scientific_submission_attempts", "reported_observation_count", "usable_observation_count",
            "live_completion_established", "experimental_improvement_established", "final_selection_status", "ranking_status", "boundary")
    rows = report["candidate_rows"]
    return {**{key: report[key] for key in keys}, "candidate_count": len(rows),
        "candidate_index": [{"candidate_id": row["candidate_id"], "evidence_counts": row["evidence_counts"],
                             "missing_evidence": row["missing_evidence"]} for row in rows[:20]],
        "candidate_index_complete": len(rows) <= 20, "unresolved_submission_call_ids": report["unresolved_submission_call_ids"],
        "failed_submission_call_ids": report["failed_submission_call_ids"],
        "detail_access": {"action": "inspect_report", "values": {"snapshot_sha256": report["snapshot_sha256"], "view": "candidate_rows"}}}


def read_report(report, *, view="candidate_rows", record_id=None, pointer="", offset=0, limit=10, snapshot_sha256=None):
    from .context import read_records
    if snapshot_sha256 is not None and snapshot_sha256 != report["snapshot_sha256"]:
        raise ResearchError("Report snapshot changed; begin a new evidence review")
    views = {"candidate_rows": [(row["candidate_id"], row) for row in report["candidate_rows"]],
             "execution_ledger": [(row["call_id"], row) for row in report["execution_ledger"]],
             "observation_checks": list(report["observation_checks"].items()),
             "structure_checks": list(report["structure_checks"].items()),
             "ligand_verifications": [(r["verification"]["verification_id"], r) for r in report["ligand_verification_records"]],
             "report": [("report", {key: value for key, value in report.items() if key != "candidate_rows"})]}
    if not isinstance(view, str) or view not in views:
        raise ResearchError("Unknown report view")
    rows = [{"record_id": rid, "value": value} for rid, value in views[view]]
    value = read_records(report["campaign_id"], view, rows, record_id=record_id, pointer=pointer, offset=offset, limit=limit)
    value["records_sha256"] = value["snapshot_sha256"]
    value["snapshot_sha256"] = report["snapshot_sha256"]
    return value


def export_report(report, output):
    """Create a new operator-selected output directory; never overwrite a run."""
    output = Path(output).absolute()
    if output.resolve() != output or output.exists():
        raise ResearchError("Report output must be a new non-aliased directory")
    output.mkdir(parents=True, mode=0o700)
    for name, value in (("report.json", report), ("candidate_evidence.json", report["candidate_rows"]),
                        ("execution_ledger.json", report["execution_ledger"])):
        with (output / name).open("x") as handle:
            handle.write(json.dumps(value, indent=2, allow_nan=False) + "\n")
    if report["reference_selection_receipts"]:
        with (output / "reference_selection.json").open("x") as handle:
            handle.write(json.dumps(report["reference_selection_receipts"], indent=2, allow_nan=False) + "\n")
    if report["ligand_verification_records"]:
        with (output / "ligand_verifications.json").open("x") as handle:
            handle.write(json.dumps(report["ligand_verification_records"], indent=2, allow_nan=False) + "\n")
    with (output / "candidate_summary.csv").open("x", newline="") as handle:
        fields = ["candidate_id", "parent_id", "sequence_sha256", "sequence_length", "mutation_count",
                  "catalytic_sequence_preserved", *[kind + "_observation_count" for kind in KINDS],
                  "all_atom_structure_count", "jointly_validation_passed_structure_count", "missing_evidence", "rank"]
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        for row in report["candidate_rows"]:
            writer.writerow({**{key: row[key] for key in fields if key in row and key != "missing_evidence"},
                **{kind + "_observation_count": row["evidence_counts"][kind] for kind in KINDS},
                "jointly_validation_passed_structure_count": len(row["jointly_validation_passed_structure_ids"]),
                "missing_evidence": ";".join(row["missing_evidence"])})
    return {"output_directory": str(output), "snapshot_sha256": report["snapshot_sha256"], "candidate_count": len(report["candidate_rows"])}
