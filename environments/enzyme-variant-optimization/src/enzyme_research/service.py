"""Agent-facing research operations around the existing scientific executor."""
from __future__ import annotations

from pathlib import Path

from .connector import NativeConnector, TrackedConnector, durable_result
from .contracts import ResearchError, canonical, digest, safe_data
import json
from .context import validate_action_values
from .discovery import DiscoveryCoordinator, HypothesisReviewDeclined
from .store import Store
from .workflow import WorkflowExecutor


class ResearchService:
    def __init__(self, settings, *, connector=None):
        required = {"state_root", "upstream_source", "workflow_source", "catalogue_root", "connector_runtime"}
        if not isinstance(settings, dict) or not required <= set(settings):
            raise ResearchError("Configure the separate research state, pinned upstream, workflow source, catalogue and connector runtime")
        self.settings = settings
        self.store = Store(settings["state_root"])
        self.connector = TrackedConnector(self.store, connector or NativeConnector(settings["connector_runtime"]),
                                          validation_approval=settings.get("validation_approval"))
        self.workflow = WorkflowExecutor(self.store, settings["workflow_source"], settings["catalogue_root"], self.connector,
                                         bindings=settings.get("bindings"), extensions=settings.get("extensions"))

    def start(self, task, arm):
        # The original workflow parser independently checks structural identities.
        from enzyme_workflow.artifacts import inspect_structure
        source = Path(task["parent"]["structure"]["path"])
        if task.get("evidence_track") != "synthetic":
            if source.is_symlink() or not source.is_file() or not 0 < source.stat().st_size <= 10 * 1024**2:
                raise ResearchError("Parent structure must be a bounded regular file")
            parsed = inspect_structure(source.name, source.read_bytes())
            if parsed["structural_sequence"] != task["parent"]["sequence"]:
                raise ResearchError("Parent sequence does not match the supplied structure")
            labels = parsed["residues"]
            for site in task["parent"]["catalytic_residues"]:
                position = site["sequence_position"]
                if not 1 <= position <= len(labels) or labels[position - 1] != site["chain"] + site["residue"]:
                    raise ResearchError("Catalytic structural mapping does not match the sequence positions")
        return {"campaign_id": self.store.start(task, arm), "scientific_jobs_submitted": 0}

    def status(self, campaign_id):
        return self.store.status(campaign_id)

    def tool_context(self, state):
        document = json.loads((Path(self.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())
        entries = {job: document["tools"][job] for job in state["task"]["allowed_jobs"] if job in document.get("tools", {})}
        inputs = [event["payload"]["data"] for event in state["events"] if event["payload"]["event"] == "input_prepared"]
        uploads = [c for c in state["calls"] if c["tool"] == "boltzmann_upload" and c["status"] == "completed"]
        return durable_result({"tool_contracts": entries, "prepared_inputs": inputs, "confirmed_uploads": uploads})

    def model_context(self, state):
        from .context import compact_context
        registry = getattr(getattr(getattr(self, "workflow", None), "harness", None), "registry", {})
        return compact_context(state, self.tool_context(state)["tool_contracts"], registry)

    def read_context(self, campaign_id, **query):
        from .context import read_context
        allowed = {"view", "record_id", "pointer", "offset", "limit", "snapshot_sha256"}
        if "view" not in query or set(query) - allowed:
            raise ResearchError("Context lookup requires view and only supported record/pointer/page selectors")
        state = self.store.status(campaign_id)
        return read_context(state, self.tool_context(state)["tool_contracts"], **query)

    def _repair_unsubmitted(self, campaign_id, experiment_data, reason):
        """One reviewed input-only repair, never a new round or a send retry.

        Freeze identity, hypothesis, job, kind and candidate scope. The original
        approved decision remains in append-only provenance. A real dedicated
        critic must approve the exact replacement inputs; native validation and
        operator approval still run at the ordinary execution boundary.
        """
        safe_data({"experiment_data": experiment_data, "reason": reason})
        if not experiment_data or not reason.strip() or len(reason) > 2000:
            raise ResearchError("Input repair needs nonempty experiment_data and a bounded reason")

        def pending(state):
            if state["arm"] != "specialist" or not state["decisions"] or state["decisions"][-1]["status"] != "planned":
                raise ResearchError("Input repair requires a specialist's approved pending hypothesis")
            decision = state["decisions"][-1]
            saved = next(e["seq"] for e in state["events"] if e["payload"]["event"] == "decision_saved"
                         and e["payload"]["data"]["round"] == decision["round"])
            later = [e["payload"] for e in state["events"] if e["seq"] > saved]
            if any(e["event"] == "workflow_segment_created" or e["event"] == "call_prepared"
                   and e["data"]["tool"] == "boltzmann_submit" for e in later):
                raise ResearchError("Input repair is forbidden after a workflow segment or scientific submission exists; reconcile the original operation")
            return decision

        roles = getattr(self, "model_roles", None)
        if roles is None:
            raise ResearchError("Input repair requires the native dedicated critic under the shared model budget")
        with self.store.transaction() as db:
            state = self.store.status(campaign_id)
            decision = pending(state)
            if any(e["payload"]["event"] == "pending_action_repair_requested"
                   and e["payload"]["data"]["round"] == decision["round"] for e in state["events"]):
                raise ResearchError("Pre-submission input repair allowance exhausted for this decision")
            original = decision["value"]
            if experiment_data == original["action"]["experiment_data"]:
                raise ResearchError("Input repair must change the malformed unsubmitted inputs")
            self.store.event(db, campaign_id, "pending_action_repair_requested", {
                "round": decision["round"], "original_decision_sha256": digest(original),
                "replacement_inputs_sha256": digest(experiment_data), "reason": reason,
                "scientific_jobs_submitted": 0})
        revised = json.loads(json.dumps(original))
        revised["action"]["experiment_data"] = json.loads(canonical(experiment_data))
        hypothesis = next(h for h in original["hypotheses"] if h["id"] == original["selected_id"])
        context = self.model_context(state)
        context["pre_submission_repair"] = {"round": decision["round"], "reason": reason,
                                             "original_action": original["action"]}
        review = roles.critique(json.loads(canonical({**hypothesis, "action": revised["action"]})),
                                json.loads(canonical(context)))
        safe_data(review)
        if (not isinstance(review, dict) or set(review) != {"score", "critique", "decision"}
                or type(review.get("score")) not in (int, float) or not 0 <= review["score"] <= 10
                or not isinstance(review.get("critique"), str) or not review["critique"].strip()
                or review.get("decision") != "test"):
            with self.store.transaction() as db:
                self.store.event(db, campaign_id, "pending_action_repair_declined", {
                    "round": decision["round"], "review": review,
                    "original_decision_sha256": digest(original), "scientific_jobs_submitted": 0})
            raise ResearchError("Dedicated critic did not approve the exact input repair; pending decision is unchanged")
        revised["pre_submission_repair"] = {"reason": reason, "critique": review,
                                              "original_decision_sha256": digest(original)}
        with self.store.transaction() as db:
            current = pending(self.store.status(campaign_id))
            if current != decision:
                raise ResearchError("Pending decision changed during input repair; no replacement was saved")
            db.execute("UPDATE decisions SET value=? WHERE campaign=? AND round=? AND status='planned'",
                       (canonical(revised), campaign_id, decision["round"]))
            self.store.event(db, campaign_id, "pending_action_repaired", {
                "round": decision["round"], "original_decision": original,
                "repaired_decision_sha256": digest(revised), "review": review,
                "scientific_jobs_submitted": 0, "molecular_improvement_established": False})
        return {"status": "pending_action_repaired", "round": decision["round"],
                "decision_sha256": digest(revised), "scientific_jobs_submitted": 0,
                "native_validation_still_required": True}

    validate_action = staticmethod(validate_action_values)

    def next(self, campaign_id, action="inspect", **values):
        state = self.store.status(campaign_id)
        validate_action_values(action, values)
        # An explicitly omitted optional binding must retain the executor's
        # automatic derivation/default path, not become a fake supplied value.
        values = {key: value for key, value in values.items() if value is not None}
        if action == "inspect":
            if values:
                return self.read_context(campaign_id, **values)
            return {"campaign_id": campaign_id, "status": state["status"], "decisions": state["decisions"],
                    "calls": state["calls"], "observations": state["observations"]}
        if action == "inspect_report":
            from .reporting import build_report, read_report
            return read_report(build_report(self.store, campaign_id), **values)
        if action == "propose":
            if state["task"]["evidence_track"] != "synthetic":
                raise ResearchError("Supplied proposals/critiques are synthetic fixtures only; use investigate for scientific runs")
            proposals, critiques = values["proposals"], values["critiques"]
            def critic(candidate, context):
                if candidate["id"] not in critiques:
                    raise ResearchError("Critique missing for a proposed hypothesis")
                return critiques[candidate["id"]]
            return DiscoveryCoordinator(self.store, self.settings["upstream_source"]).advance(
                campaign_id, lambda context: proposals, critic)
        if action == "investigate":
            if state["arm"] != "specialist":
                raise ResearchError("Dedicated DiscoveryRSI subagents are available only in the specialist arm")
            roles = getattr(self, "model_roles", None)
            if roles is None:
                raise ResearchError("Use the native research runtime to supply the shared-budget model-role adapter")
            if values:
                raise ResearchError("Investigation context comes from recorded task/results, not supplied answers")
            try:
                return DiscoveryCoordinator(self.store, self.settings["upstream_source"], self.model_context).advance(campaign_id, roles.propose, roles.critique)
            except HypothesisReviewDeclined as declined:
                # A reviewed stop is a completed planning action, never an
                # approved executable decision. plan_segment still requires
                # an actual planned decision and cannot run this proposal.
                return declined.review
        if action == "repair_unsubmitted":
            return self._repair_unsubmitted(campaign_id, values["experiment_data"], values["reason"])
        if action == "add_candidates":
            return {"candidates": self.store.add_candidates(campaign_id, values["candidates"])}
        if action == "prepare_input":
            from .preparation import prepare_input
            return prepare_input(self, campaign_id, values["job_name"], values["candidate_ids"], structure_ids=values.get("structure_ids"))
        if action == "upload_input":
            from .preparation import upload_input
            return upload_input(self, campaign_id, values["input_id"], values.get("experiment_data"))
        if action == "sync_sequences":
            from .identity import sync_sequences
            return sync_sequences(self, campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"])
        if action == "sync_structures":
            from .structures import sync_structures
            return sync_structures(self, campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"])
        if action == "sync_metrics":
            from .results import sync_metrics
            return sync_metrics(self, campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"], values.get("kind"))
        if action == "verify_ligand":
            from .ligands import verify_ligand
            expected = {"candidate_id", "structure_id", "sdf_member", "ligand_selector"}
            if set(values) != expected:
                raise ResearchError("Ligand verification takes only candidate_id, structure_id, sdf_member and ligand_selector")
            return verify_ligand(self, campaign_id, **values)
        if action == "match_stability":
            from .stability import match_candidates
            return match_candidates(self, campaign_id, values["observation_id"], values["basis_candidate_id"],
                                    values["structure_id"], values["target_candidate_ids"])
        if action == "plan_segment":
            specification = values["specification"]
            if state["arm"] == "specialist":
                if not state["decisions"] or state["decisions"][-1]["status"] != "planned":
                    raise ResearchError("Specialist execution requires an approved pending hypothesis")
                chosen = state["decisions"][-1]["value"]["action"]
                steps = specification.get("steps", [])
                first_matches = len(steps) == 1 and (
                    self.workflow.harness.registry.get(steps[0].get("tool"), {}).get("job_name") == chosen["job_name"]
                    and steps[0].get("inputs") == chosen["experiment_data"]
                    and steps[0].get("candidate_ids") == chosen["candidate_ids"])
                if not first_matches:
                    # One optimization round can involve several scientific
                    # tools. A follow-up is not a hidden fourth round: retain
                    # the current hypothesis and justify a new immutable segment
                    # from actual observations obtained during that investigation.
                    followup = values.get("followup")
                    known = {o["observation_id"] for o in state["observations"]}
                    if not isinstance(followup, dict) or set(followup) != {"reason", "observation_ids"}:
                        raise ResearchError("Additional tools in this investigation need an evidence-backed follow-up")
                    refs = followup["observation_ids"]
                    if (not isinstance(followup["reason"], str) or not followup["reason"].strip()
                            or not isinstance(refs, list) or not refs or any(not isinstance(x, str) for x in refs)
                            or set(refs) - known):
                        raise ResearchError("Follow-up must cite actual scientific observations")
                    safe_data(followup)
                    with self.store.transaction() as db:
                        self.store.event(db, campaign_id, "hypothesis_followup_planned", {
                            "hypothesis_id": state["decisions"][-1]["value"]["selected_id"],
                            "specification_sha256": digest(specification), **followup})
            return self.workflow.start_segment(campaign_id, specification, structure_ids=values.get("structure_ids"))
        if action == "submit":
            return self.workflow.submit(campaign_id, values["workflow_id"], values["step_id"])
        if action == "poll":
            return self.workflow.poll(campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"])
        if action == "logs":
            return self.workflow.fetch_log(campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"])
        if action == "download":
            return self.workflow.download_current(campaign_id, values["workflow_id"], values["step_id"], values["submission_call_id"], values["output_folder"])
        if action == "ingest":
            workflow, step = values["workflow_id"], values["step_id"]
            self.workflow._owned(campaign_id, workflow)
            initial_report = self.workflow.harness.status(workflow)
            before = initial_report["state"]["steps"][step]
            tool_id = next(s["tool"] for s in initial_report["spec"]["steps"] if s["step_id"] == step)
            metadata = initial_report["state"]["contracts"][tool_id]
            observed_kind = {"netsolp": "solubility", "catpred": "activity", "kcat": "activity", "thermompnn": "stability"}.get(tool_id)
            if metadata["adapter"] in {"quality", "geometry"}:
                observed_kind = metadata["adapter"]
            if observed_kind is not None and values.get("kind", observed_kind) != observed_kind:
                raise ResearchError("Observation kind must match the executed tool's scientific capability: " + observed_kind)
            source = next((c for c in state["calls"] if c["call_id"] == values["submission_call_id"]), None)
            if (source is None or source["tool"] != "boltzmann_submit" or source["status"] != "completed"
                    or source["args"].get("job_name") != before.get("job_name")
                    or (source.get("result") or {}).get("doc_id") != before.get("doc_id")):
                raise ResearchError("Ingestion requires the matching completed original scientific submission")
            bindings = values.get("bindings")
            if tool_id == "netsolp":
                from .results import derive_sequence_report_bindings
                derived = derive_sequence_report_bindings(self, campaign_id, workflow, step, values["local_path"], member=values.get("member"))
                if bindings is not None and bindings != derived:
                    raise ResearchError("Supplied NetSolP bindings contradict verified sequence/identifier identities")
                bindings = derived
            result = self.workflow.ingest(campaign_id, workflow, step, values["local_path"],
                                           bindings=bindings, member=values.get("member"))
            report = self.workflow.harness.status(workflow)
            current = report["state"]["steps"][step]
            contract = report["state"]["contracts"][next(s["tool"] for s in report["spec"]["steps"] if s["step_id"] == step)]
            if contract["adapter"] == "sequences":
                from .identity import sync_sequences
                return {**result, **sync_sequences(self, campaign_id, workflow, step, values["submission_call_id"])}
            if contract["adapter"] == "structures":
                from .structures import sync_structures
                return {**result, **sync_structures(self, campaign_id, workflow, step, values["submission_call_id"])}
            from .results import sync_metrics
            return {**result, **sync_metrics(self, campaign_id, workflow, step, values["submission_call_id"], values.get("kind"))}
        if action == "complete_decision":
            self.store.decision_observed(campaign_id, values["round"], values["observation_ids"])
            return {"status": "observed"}
        raise ResearchError("Unknown research action")

    def report(self, campaign_id):
        from .reporting import build_report, summary
        return summary(build_report(self.store, campaign_id))
