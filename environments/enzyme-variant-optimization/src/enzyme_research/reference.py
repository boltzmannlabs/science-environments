"""Frozen exhaustive-panel reference using the existing scientific executor.

This is an operator-run conventional comparator, not an agent subagent or an
experimental evaluator. Live qualification and the matched comparison remain
separate from its synthetic integration tests.
"""
from __future__ import annotations

import hashlib
import json
import fcntl
import os
from pathlib import Path

from .contracts import ResearchError, candidate_record, canonical, digest, safe_data

STAGES = ("thermompnn", "catpred", "netsolp", "boltz2", "mol_probity", "catalytic_geometry")
FOLDING_TOOLS = {"boltz2", "monomer_prediction"}
COORDINATE_RULES = {"joint_validation", "joint_nonrejected_measurements"}
FILE_FIELDS = {"input_path", "input_csv", "zip_path", "input_file_path", "Protein_Sequences", "DNA_Sequences", "RNA_Sequences", "SMILES"}


def policy_stages(policy):
    """Choose folding explicitly before screening; never silently fail over."""
    if policy.get("schema_version") == "enzyme-fixed-reference/1":
        return STAGES
    if (policy.get("schema_version") == "enzyme-fixed-reference/2"
            and isinstance(policy.get("folding_tool"), str) and policy["folding_tool"] in FOLDING_TOOLS):
        return (*STAGES[:3], policy["folding_tool"], *STAGES[4:])
    raise ResearchError("Reference needs a supported policy version and explicit permitted folding tool")


def _implementation_hash(service):
    package = Path(__file__).parent
    files = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(package.rglob("*.py"))}
    workflow = Path(service.settings["workflow_source"])
    executor = {str(p.relative_to(workflow)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(workflow.glob("*.py"))}
    executor["contracts/tool_registry.json"] = hashlib.sha256((workflow / "contracts/tool_registry.json").read_bytes()).hexdigest()
    return digest({"research_package": files, "original_executor": executor})


def freeze_reference(service, campaign, policy):
    """Freeze before any results/jobs; existing scientific contracts own inputs."""
    safe_data(policy)
    state = service.store.status(campaign)
    fields = {"schema_version", "task_sha256", "candidate_panel", "tool_settings", "selection_count",
              "coordinate_requirement", "methodology_note"}
    if isinstance(policy, dict) and policy.get("schema_version") == "enzyme-fixed-reference/2":
        fields.add("folding_tool")
    if not isinstance(policy, dict) or set(policy) != fields:
        raise ResearchError("Fixed reference needs its complete explicit policy, not tool-input defaults")
    stages = policy_stages(policy)
    if state["arm"] != "fixed" or policy["task_sha256"] != digest(state["task"]):
        raise ResearchError("Reference policy must match this exact fixed-arm task")
    if policy["coordinate_requirement"] not in COORDINATE_RULES or not isinstance(policy["methodology_note"], str) or not policy["methodology_note"].strip():
        raise ResearchError("Reference needs an explicit structural requirement and scientific rationale")
    panel = policy["candidate_panel"]
    if not isinstance(panel, list) or not 1 <= len(panel) <= state["task"]["budget"]["max_unique_candidates"]:
        raise ResearchError("Reference panel must be nonempty and within the shared candidate allowance")
    parsed = [candidate_record(state["task"], row) for row in panel]
    if policy["schema_version"] == "enzyme-fixed-reference/2" and len(panel) + 1 > 60:
        raise ResearchError("The comparison limit is 60 evaluated sequences including the parent reference")
    parent = state["task"]["parent"]
    if (any(r["parent_id"] != parent["candidate_id"] or len(r["mutations_from_reference"]) != 1 for r in parsed)
            or len({r["candidate_id"] for r in parsed}) != len(parsed)
            or len({r["sequence_sha256"] for r in parsed}) != len(parsed)
            or parent["candidate_id"] in {r["candidate_id"] for r in parsed}):
        raise ResearchError("This reference uses unique, catalytic-preserving single-substitution panel members relative to the parent")
    if state["task"]["evidence_track"] == "protected_measured_library":
        members = state["task"]["candidate_library"]["members"]
        expected = {m["sequence"] for m in members} - {parent["sequence"]}
        if {r["sequence"] for r in parsed} != expected:
            raise ResearchError("The exhaustive measured-library baseline must cover the whole declared public library, not a cherry-picked subset")
    count = policy["selection_count"]
    if type(count) is not int or not 1 <= count <= min(10, len(panel)):
        raise ResearchError("Reference selection_count must be explicit and at most ten/panel size")
    if not isinstance(policy["tool_settings"], dict) or set(policy["tool_settings"]) != set(stages):
        raise ResearchError("Reference must specify settings for every required stage; missing tools are not skipped")
    contracts = {}
    for name in stages:
        params = policy["tool_settings"][name]
        if not isinstance(params, dict) or FILE_FIELDS & set(params):
            raise ResearchError("Reference settings contain only non-file scientific parameters; exact inputs come from verified candidates")
        metadata = service.workflow.harness.registry.get(name)
        if (not metadata or metadata.get("backend_status") != "active" or not metadata.get("contract_document")
                or metadata["job_name"] not in state["task"]["allowed_jobs"]):
            raise ResearchError("Reference stage has no permitted active authoritative contract: " + name)
        contracts[name] = digest(metadata)
    if 3 + 3 * (len(panel) + 1) > state["task"]["budget"]["max_scientific_submissions"]:
        raise ResearchError("Full reference screening exceeds the shared scientific-job allowance")
    value = {"policy": policy, "tool_contract_sha256": contracts, "implementation_sha256": _implementation_hash(service),
             "stage_order": list(stages), "ranking_rule": "non_dominated_fronts_then_kcat_desc_ddG_asc_solubility_desc_id",
             "metric_units": {"kcat": "native CatPred kcat column", "ddG_pred": "native ThermoMPNN scale; no physical recalibration",
                              "predicted_solubility": "native NetSolP score"},
             "policy_role": "fixed_reference_only; does_not_force_agent_selection"}
    value["policy_sha256"] = digest(value)
    with service.store.transaction() as db:
        prior = [json.loads(r[0])["data"] for r in db.execute("SELECT payload FROM events WHERE campaign=?", (campaign,))
                 if json.loads(r[0]).get("event") == "fixed_reference_frozen"]
        if prior:
            if prior != [value]:
                raise ResearchError("A frozen reference policy cannot be replaced; review a new campaign")
            return prior[0]
        if (db.execute("SELECT 1 FROM observations WHERE campaign=? LIMIT 1", (campaign,)).fetchone()
                or db.execute("SELECT 1 FROM calls WHERE campaign=? AND tool='boltzmann_submit' LIMIT 1", (campaign,)).fetchone()
                or db.execute("SELECT COUNT(*) FROM candidates WHERE campaign=?", (campaign,)).fetchone()[0] != 1):
            raise ResearchError("Reference policy must be frozen before candidate screening, submissions or observations")
        service.store.event(db, campaign, "fixed_reference_frozen", value)
    return value


def frozen_reference(service, campaign):
    state = service.store.status(campaign)
    values = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "fixed_reference_frozen"]
    if len(values) != 1 or state["arm"] != "fixed":
        raise ResearchError("This campaign has no unique frozen fixed-reference policy")
    value = values[0]
    if value["implementation_sha256"] != _implementation_hash(service):
        raise ResearchError("Reference implementation changed after freezing; do not silently retune the method")
    if value["policy"]["task_sha256"] != digest(state["task"]):
        raise ResearchError("Reference task changed after freezing")
    if any(digest(service.workflow.harness.registry.get(name)) != sha for name, sha in value["tool_contract_sha256"].items()):
        raise ResearchError("Reference scientific contracts changed after freezing")
    return value


def nondominated_order(scores):
    """No fitted weights: kcat/solubility higher, native single-mutant ddG lower."""
    import math
    if not scores:
        raise ResearchError("No scientifically eligible reference candidates remain")
    for cid, row in scores.items():
        if set(row) != {"kcat", "ddG_pred", "predicted_solubility"} or any(type(v) not in {int, float} or not math.isfinite(v) for v in row.values()):
            raise ResearchError("Reference ranking needs finite audited prediction values, not missing metrics or booleans")
    def vector(cid):
        row = scores[cid]
        return row["kcat"], -row["ddG_pred"], row["predicted_solubility"]
    remaining, result, level = set(scores), [], 1
    while remaining:
        front = [cid for cid in remaining if not any(other != cid and all(a >= b for a, b in zip(vector(other), vector(cid)))
                 and any(a > b for a, b in zip(vector(other), vector(cid))) for other in remaining)]
        front.sort(key=lambda cid: (-scores[cid]["kcat"], scores[cid]["ddG_pred"], -scores[cid]["predicted_solubility"], cid))
        previous_count = len(result)
        result.extend({"candidate_id": cid, "pareto_front": level, "rank": previous_count + i + 1} for i, cid in enumerate(front))
        remaining.difference_update(front); level += 1
    return result


class FixedReferenceRunner:
    """Advance at most one scientific stage/request through the original API path.

    The operator explicitly executes each advance. Preview performs no uploads,
    submissions or state repair. An uncertain operation is never resubmitted.
    """
    def __init__(self, service, campaign):
        self.service, self.campaign = service, campaign

    def _record(self, name, value):
        state = self.service.store.status(self.campaign)
        if any(e["payload"]["event"] == name and e["payload"]["data"] == value for e in state["events"]):
            return
        with self.service.store.transaction() as db:
            self.service.store.event(db, self.campaign, name, value)

    def advance(self, *, execute=False):
        path = self.service.store.root / (self.campaign + ".reference.lock")
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ResearchError("Another reference advance is active; no concurrent operation is started") from exc
            return self._advance(execute=execute)
        finally:
            os.close(descriptor)

    def _advance(self, *, execute):
        frozen = frozen_reference(self.service, self.campaign)
        policy = frozen["policy"]
        state = self.service.store.status(self.campaign)
        parent = state["task"]["parent"]["candidate_id"]
        panel = [p["candidate_id"] for p in policy["candidate_panel"]]
        targets = [parent, *panel]
        if not execute:
            return {"status": "preview_only", "policy_sha256": frozen["policy_sha256"], "stage_order": frozen["stage_order"],
                    "panel_candidate_ids": panel, "scientific_jobs_submitted": 0,
                    "scope": "Full panel screening; no fixed-reference live qualification or comparison established"}
        known = {c["candidate_id"]: c for c in state["candidates"]}
        if set(known) - set(targets):
            raise ResearchError("Unexpected candidates outside the frozen exhaustive panel")
        missing = [p for p in policy["candidate_panel"] if p["candidate_id"] not in known]
        if missing:
            if any(c["tool"] == "boltzmann_submit" for c in state["calls"]):
                raise ResearchError("Reference panel changed or was only partly registered after screening began")
            self.service.store.add_candidates(self.campaign, missing)
        for row in policy["candidate_panel"]:
            current = next(c for c in self.service.store.status(self.campaign)["candidates"] if c["candidate_id"] == row["candidate_id"])
            if current["sequence"] != row["sequence"] or current["parent_id"] != row["parent_id"]:
                raise ResearchError("Reference panel identity changed")
        for tool in frozen["stage_order"]:
            groups = [[parent]] if tool == "thermompnn" else [targets] if tool in {"catpred", "netsolp"} else [[cid] for cid in targets]
            for ids in groups:
                key = tool + ":" + (ids[0] if len(ids) == 1 else "panel")
                state = self.service.store.status(self.campaign)
                finished = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "reference_step_complete"
                            and e["payload"]["data"]["stage_key"] == key]
                if finished:
                    continue
                return self._advance_stage(frozen, tool, key, ids)
        return self.rank()

    def _advance_stage(self, frozen, tool, key, ids):
        service, campaign = self.service, self.campaign
        state = service.store.status(campaign)
        bindings = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "reference_step_bound"
                    and e["payload"]["data"]["stage_key"] == key]
        if len(bindings) > 1:
            raise ResearchError("Reference stage has ambiguous workflow bindings; reconcile the original stage")
        if bindings:
            workflow = bindings[0]["workflow_id"]
        else:
            structure_ids = {}
            if tool == "thermompnn":
                structure_ids[ids[0]] = "supplied-" + state["task"]["parent"]["structure"]["sha256"][:20]
            if tool in {"mol_probity", "catalytic_geometry"}:
                fold = [e["payload"]["data"]["workflow_id"] for e in state["events"] if e["payload"]["event"] == "reference_step_bound"
                        and e["payload"]["data"]["stage_key"] == frozen["stage_order"][3] + ":" + ids[0]]
                versions = [r for r in state["structures"] if r["candidate_id"] == ids[0] and r["source"].get("workflow_id") in fold]
                if len(versions) != 1:
                    raise ResearchError("Reference structural checks require exactly one sequence-matched output from their own folding stage")
                structure_ids[ids[0]] = versions[0]["structure_id"]
            job = service.workflow.harness.registry[tool]["job_name"]
            prepared = service.next(campaign, "prepare_input", job_name=job, candidate_ids=ids, structure_ids=structure_ids)
            params = frozen["policy"]["tool_settings"][tool]
            if prepared.get("input_kind") == "inline":
                data = {**params, **prepared["experiment_data"]}
            else:
                uploaded = service.next(campaign, "upload_input", input_id=prepared["input_id"], experiment_data=params)
                if not uploaded.get("uploaded"):
                    return {"status": "input_upload_not_completed", "stage_key": key, "receipt": uploaded}
                data = uploaded["experiment_data"]
            step = {"step_id": "reference", "tool": tool, "candidate_ids": ids, "inputs": data,
                    "expected_count": len(ids), "experiment_name": campaign + "_" + key.replace(":", "_")}
            if tool == "catpred": step["handoff"] = {"smiles": state["task"]["substrate"]["smiles"]}
            spec = {"objective": "Frozen exhaustive reference stage: " + key, "approved": True, "steps": [step]}
            prior = [e["payload"]["data"]["workflow_id"] for e in state["events"] if e["payload"]["event"] == "workflow_segment_created"
                     and e["payload"]["data"]["specification_sha256"] == digest(spec)]
            if len(prior) > 1:
                raise ResearchError("Multiple workflows match a fixed stage; no new submission is started")
            workflow = prior[0] if prior else service.next(campaign, "plan_segment", specification=spec, structure_ids=structure_ids)["workflow_id"]
            self._record("reference_step_bound", {"stage_key": key, "workflow_id": workflow, "policy_sha256": frozen["policy_sha256"]})
        report = service.workflow.harness.status(workflow)
        current = report["state"]["steps"]["reference"]
        if current["status"] in {"planned", "ready"}:
            receipt = service.next(campaign, "submit", workflow_id=workflow, step_id="reference")
            return {"status": "submission_attempted", "stage_key": key, "workflow_id": workflow, "receipt": receipt}
        with service.workflow.harness.store.connection() as db:
            row = db.execute("SELECT args FROM intents WHERE id=?", (current.get("intent_id"),)).fetchone()
        args = json.loads(row[0]) if row else None
        calls = [c for c in service.store.status(campaign)["calls"] if c["tool"] == "boltzmann_submit" and args
                 and all(c["args"].get(k) == args.get(k) for k in ("job_name", "experiment_name", "experiment_data"))]
        if len(calls) != 1:
            raise ResearchError("Reference stage needs its unique original tracked submission; no replacement is permitted")
        source = calls[0]
        if current["status"] in {"submitting", "submit_unknown", "failed"} or source["status"] in {"submit_unknown", "sending", "prepared", "definite_failure"}:
            return {"status": "original_job_requires_review", "stage_key": key, "call_id": source["call_id"], "original_status": source["status"]}
        values = {"workflow_id": workflow, "step_id": "reference", "submission_call_id": source["call_id"]}
        if current["status"] in {"submitted", "running"}:
            service.next(campaign, "poll", **values)
            current = service.workflow.harness.status(workflow)["state"]["steps"]["reference"]
            if current["status"] != "remote_completed":
                return {"status": "awaiting_original_job", "stage_key": key, "call_id": source["call_id"], "doc_id": current.get("doc_id")}
        if current["status"] == "remote_completed":
            with service.workflow.harness.store.connection() as db:
                paths = [r[0] for r in db.execute("SELECT local_path FROM downloads WHERE workflow_id=? AND step_id=? AND intent_id=?",
                                               (workflow, "reference", current["intent_id"]))]
            if not paths:
                service.next(campaign, "download", **values, output_folder=str(service.store.root / campaign / "downloads"))
                with service.workflow.harness.store.connection() as db:
                    paths = [r[0] for r in db.execute("SELECT local_path FROM downloads WHERE workflow_id=? AND step_id=? AND intent_id=?",
                                                   (workflow, "reference", current["intent_id"]))]
            if len(paths) != 1:
                raise ResearchError("Reference output needs one actual authoritative artifact, not guessed file selection")
            from enzyme_workflow.artifacts import inspect_artifact
            local = paths[0]
            output_bindings = None
            if tool not in {"catpred", "thermompnn"}:
                parsed = inspect_artifact(local, service.workflow.harness.registry[tool]["adapter"])
                if tool == "netsolp":
                    from .results import derive_sequence_report_bindings
                    output_bindings = derive_sequence_report_bindings(service, campaign, workflow, "reference", local)
                elif tool in FOLDING_TOOLS:
                    if len(parsed["entries"]) != 1:
                        raise ResearchError("Frozen reference requires one folding pose per request")
                    output_bindings = {e["label"]: {"parent_ids": ids} for e in parsed["entries"]}
                elif len(ids) == len(parsed["entries"]) == 1:
                    output_bindings = {parsed["entries"][0]["label"]: {"candidate_id": ids[0]}}
                else:
                    if {e["label"] for e in parsed["entries"]} != set(ids):
                        raise ResearchError("Batch reference report needs exact candidate identifiers, not row-order joins")
                    output_bindings = {cid: {"candidate_id": cid} for cid in ids}
            result = service.next(campaign, "ingest", **values, local_path=local, bindings=output_bindings)
        else:
            action = "sync_structures" if tool in FOLDING_TOOLS else "sync_metrics"
            result = service.next(campaign, action, **values)
        observation = result["observation"]
        if tool == "thermompnn":
            parent = ids[0]
            sid = next(iter(observation["metrics"][parent]["by_structure"]))
            derived = service.next(campaign, "match_stability", observation_id=observation["observation_id"],
                         basis_candidate_id=parent, structure_id=sid,
                         target_candidate_ids=[p["candidate_id"] for p in frozen["policy"]["candidate_panel"]])
        else:
            derived = None
        self._record("reference_step_complete", {"stage_key": key, "workflow_id": workflow,
                     "source_call_id": source["call_id"], "observation_id": observation["observation_id"],
                     "derived_observation_ids": [derived["observation"]["observation_id"]] if derived else []})
        return {"status": "stage_complete", "stage_key": key, "observation_id": observation["observation_id"]}

    def rank(self):
        from .reporting import build_report
        frozen = frozen_reference(self.service, self.campaign)
        report = build_report(self.service.store, self.campaign)
        state = self.service.store.status(self.campaign)
        known = {c["candidate_id"]: c for c in state["candidates"]}
        observations = {o["observation_id"]: o for o in state["observations"]}
        complete = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "reference_step_complete"]
        ids = [state["task"]["parent"]["candidate_id"], *[p["candidate_id"] for p in frozen["policy"]["candidate_panel"]]]
        expected = {tool + ":" + (ids[0] if tool == "thermompnn" else "panel" if tool in {"catpred", "netsolp"} else cid)
                    for tool in frozen["stage_order"] for cid in (ids if tool in FOLDING_TOOLS | {"mol_probity", "catalytic_geometry"} else [ids[0]])}
        if {r["stage_key"] for r in complete} != expected or len(complete) != len(expected):
            raise ResearchError("Reference ranking requires every original frozen stage to complete")
        approved_calls = {r["source_call_id"] for r in complete}
        if {c["call_id"] for c in state["calls"] if c["tool"] == "boltzmann_submit"} != approved_calls:
            raise ResearchError("Scientific calls outside the frozen reference schedule require review; no compliant comparison is inferred")
        approved_observations = {oid for r in complete for oid in [r["observation_id"], *r.get("derived_observation_ids", [])]}
        rows = {row["candidate_id"]: row for row in report["candidate_rows"]}
        scores, excluded, sources = {}, {}, {}
        for member in frozen["policy"]["candidate_panel"]:
            cid = member["candidate_id"]
            row = rows.get(cid)
            if not row or not row["catalytic_sequence_preserved"]:
                raise ResearchError("Reference ranking requires every frozen panel member and its protected identities")
            if any(row["evidence_counts"][k] == 0 for k in ("activity", "solubility", "folding", "quality", "geometry")):
                raise ResearchError("Full reference screening is incomplete; missing stages cannot be silently removed from the comparison")
            activity = row["evidence"]["activity"]
            solubility = row["evidence"]["solubility"]
            stability = [p for p in row["single_mutation_predictions"] if p["basis_candidate_id"] == state["task"]["parent"]["candidate_id"]]
            if len(activity) != 1 or len(solubility) != 1 or len(stability) != 1:
                raise ResearchError("Reference metrics are missing or ambiguous; no best-replicate selection or matrix-as-variant score")
            if {activity[0]["observation_id"], solubility[0]["observation_id"], stability[0]["observation_id"]} - approved_observations:
                raise ResearchError("Reference metric comes from outside its frozen original stages")
            coordinate_key = "jointly_validation_passed_structure_ids" if frozen["policy"]["coordinate_requirement"] == "joint_validation" else "nonrejected_co_checked_structure_ids"
            if not row[coordinate_key]:
                excluded[cid] = "No coordinate version meets the frozen common structural requirement"
                continue
            try:
                a = observations[activity[0]["observation_id"]]["metrics"][cid]
                s = observations[solubility[0]["observation_id"]]["metrics"][cid]
                scores[cid] = {"kcat": float(a["kcat"]), "ddG_pred": stability[0]["ddG_pred"],
                               "predicted_solubility": float(s["predicted_solubility"])}
            except (KeyError, TypeError, ValueError) as exc:
                raise ResearchError("Actual output is not the frozen scientific prediction schema") from exc
            sources[cid] = [activity[0]["observation_id"], solubility[0]["observation_id"], stability[0]["observation_id"]]
        ordered = nondominated_order(scores)
        count = frozen["policy"]["selection_count"]
        if len(ordered) < count:
            raise ResearchError("Too few structurally eligible candidates for the frozen selection count; no smaller-set advantage")
        activity_ids = {row["evidence"]["activity"][0]["observation_id"] for cid, row in rows.items() if cid in scores}
        solubility_ids = {row["evidence"]["solubility"][0]["observation_id"] for cid, row in rows.items() if cid in scores}
        if len(activity_ids) != 1 or len(solubility_ids) != 1:
            raise ResearchError("Reference requires comparable parent/panel predictions from the same batched stage")
        parent = state["task"]["parent"]["candidate_id"]
        try:
            parent_predictions = {"kcat": float(observations[next(iter(activity_ids))]["metrics"][parent]["kcat"]),
                                  "predicted_solubility": float(observations[next(iter(solubility_ids))]["metrics"][parent]["predicted_solubility"])}
        except (KeyError, ValueError, TypeError) as exc:
            raise ResearchError("Comparable parent reference predictions are missing") from exc
        import math
        if any(not math.isfinite(v) for v in parent_predictions.values()):
            raise ResearchError("Parent reference predictions must be finite")
        comparisons = {cid: {"predicted_kcat_change": metric["kcat"] - parent_predictions["kcat"],
                             "predicted_solubility_change": metric["predicted_solubility"] - parent_predictions["predicted_solubility"],
                             "experimental_improvement_established": False} for cid, metric in scores.items()}
        selected = [{**row, "evaluation_candidate_id": known[row["candidate_id"]].get("library_member_id", row["candidate_id"])} for row in ordered[:count]]
        evidence_basis = digest({key: report[key] for key in ("candidate_rows", "execution_ledger", "observation_checks", "structure_checks")})
        value = {"policy_sha256": frozen["policy_sha256"], "report_snapshot_sha256": report["snapshot_sha256"],
                 "evidence_basis_sha256": evidence_basis,
                 "selection": selected, "ranking": ordered, "scores": scores, "excluded": excluded,
                 "parent_predictions": parent_predictions, "parent_comparisons": comparisons,
                 "evidence_track": state["task"]["evidence_track"],
                 "source_observation_ids": sources, "experimental_improvement_established": False}
        prior = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "reference_selection_recorded"]
        if prior:
            if len(prior) != 1 or {k: v for k, v in prior[0].items() if k != "report_snapshot_sha256"} != {k: v for k, v in value.items() if k != "report_snapshot_sha256"}:
                raise ResearchError("Frozen reference selection cannot be overwritten by later outputs or ranking changes")
            return {"status": "computational_selection_recorded", **prior[0]}
        self._record("reference_selection_recorded", value)
        return {"status": "computational_selection_recorded", **value}
