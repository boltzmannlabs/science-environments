"""Use the existing workflow executor for immutable scientific segments.

This adapter binds the explicit catalogue directory, adds the current native
upload context, and sends existing connector results to the original observers.
It does not replace the workflow tracker or its artifact parsers.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys

from .contracts import ResearchError, digest


def output_links(value):
    """Read native scalar/list link envelopes without inventing storage URLs."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "download_link":
                if isinstance(item, str):
                    yield item
                elif isinstance(item, list) and all(isinstance(link, str) for link in item):
                    yield from item
                else:
                    raise ResearchError("Native download_link must be a URL string or list of URL strings")
            else:
                yield from output_links(item)
    elif isinstance(value, list):
        for item in value:
            yield from output_links(item)


def load_workflow(source):
    source = Path(source).resolve()
    loaded = sys.modules.get("enzyme_workflow")
    if loaded is not None and Path(loaded.__file__).resolve().parent != source:
        raise ResearchError("A different workflow-plugin source is already loaded")
    sys.path.insert(0, str(source.parent))
    try:
        return tuple(importlib.import_module("enzyme_workflow." + name)
                     for name in ("harness", "state", "contract_registry", "connector"))
    finally:
        sys.path.remove(str(source.parent))


class WorkflowExecutor:
    def __init__(self, research_store, workflow_source, catalogue_root, connector, *, bindings=None, extensions=None):
        harness, state, registry, observers = load_workflow(workflow_source)
        root = research_store.root / "workflow_executor"
        from .stability_workflow import catalogue_extension
        bindings, extensions = catalogue_extension(catalogue_root, bindings, extensions)
        executor = self
        # The existing Harness supports a separately supplied catalogue through
        # its registry loader; no original modules or process globals are patched.
        class CatalogueHarness(harness.Harness):
            def __init__(self):
                self.store = state.Store(root)
                self.registry = registry.load_registry(bindings, extensions, catalog_root=Path(catalogue_root))

            def _ingest(self, db, wid, step, current, tool, state, **kwargs):
                if step["tool"] == "thermompnn":
                    from .stability_workflow import ingest
                    return ingest(executor, self, db, wid, step, current, state,
                                  campaign=kwargs.pop("research_campaign"), **kwargs)
                return super()._ingest(db, wid, step, current, tool, state, **kwargs)
        self.harness = CatalogueHarness()
        self.store = research_store
        self.connector = connector
        self.observers = observers

    def start_segment(self, campaign, specification, *, structure_ids=None):
        research = self.store.status(campaign)
        task = research["task"]
        known = {c["candidate_id"]: c for c in research["candidates"]}
        seed_ids = set()
        needed_structures = set()
        for step in specification.get("steps", []):
            metadata = self.harness.registry.get(step.get("tool"))
            if metadata is None or metadata.get("job_name") not in task["allowed_jobs"]:
                raise ResearchError("Workflow segment includes a tool outside the research task")
            ids = step.get("candidate_ids", [])
            if not isinstance(ids, list) or any(not isinstance(cid, str) for cid in ids) or set(ids) - set(known):
                raise ResearchError("Explicit segment candidate IDs must be registered in this campaign")
            seed_ids.update(ids)
            if set(metadata.get("requires", [])) & {"structure", "all_atom", "ligand", "mapping"}:
                needed_structures.update(ids)
        structure_ids = {} if structure_ids is None else structure_ids
        if (not isinstance(structure_ids, dict) or set(structure_ids) - seed_ids
                or any(not isinstance(value, str) for value in structure_ids.values())):
            raise ResearchError("structure_ids maps only selected candidate IDs to explicit verified coordinate versions")
        from .structures import select_structure
        coordinate_versions = {cid: select_structure(self, campaign, cid, structure_ids.get(cid))
                               for cid in needed_structures | set(structure_ids)}
        for item in specification.get("initial_candidates", []):
            cid = item.get("candidate_id")
            if (cid != task["parent"]["candidate_id"] or item.get("local_path") != task["parent"]["structure"]["path"]):
                raise ResearchError("A supplied parent structure cannot stand in for a mutated candidate; import a verified new structure first")
        result = self.harness.start(specification)
        with self.harness.store.transaction(result["workflow_id"]) as (db, _, state):
            for cid in sorted(seed_ids - set(state["candidates"])):
                candidate = known[cid]
                state["candidates"][cid] = {"candidate_id": cid,
                    "parent_ids": [candidate["parent_id"]] if candidate["parent_id"] else [],
                    "sequence": candidate["sequence"], "capabilities": ["sequence"],
                    "status": candidate["status"], "history": [{"source": "verified_research_candidate",
                        "sequence_sha256": candidate["sequence_sha256"]}]}
            for cid, version in coordinate_versions.items():
                candidate = state["candidates"][cid]
                candidate.update(capabilities=version["capabilities"], mapping=version["mapping"],
                    residue_count=version["residue_count"], structure={"artifact_path": version["artifact"]["path"],
                        "sha256": version["artifact"]["sha256"], "member": version["artifact"]["member"]})
                candidate["history"].append({"source": "verified_research_coordinates", "structure_id": version["structure_id"]})
                if version.get("ligand_identity_verified"):
                    candidate["history"].append({"source": "verified_research_ligand", "structure_id": version["structure_id"],
                                                 "verification": version["ligand_verification"]})
            self.harness.store.event(db, result["workflow_id"], "research_sequences_bound", {"candidate_ids": sorted(seed_ids)})
        with self.store.transaction() as db:
            self.store.event(db, campaign, "workflow_segment_created", {
                "workflow_id": result["workflow_id"], "specification_sha256": digest(specification),
                "structure_ids": {cid: version["structure_id"] for cid, version in coordinate_versions.items()}})
        return result

    def _owned(self, campaign, workflow):
        state = self.store.status(campaign)
        if not any(e["payload"]["event"] == "workflow_segment_created"
                   and e["payload"]["data"]["workflow_id"] == workflow for e in state["events"]):
            raise ResearchError("Workflow segment is not owned by this campaign")

    def dispatch(self, campaign, name, args):
        receipt = self.observers.before(name, args, self.harness.store.root)
        try:
            tracked = self.connector.execute(campaign, name, args)
        except Exception:
            if receipt:
                self.observers.after(name, args, {"error": "Submission outcome unknown", "safe_to_retry": False}, receipt)
            raise
        self.observers.after(name, args, tracked["result"], receipt, root=self.harness.store.root)
        if (receipt and name == "boltzmann_submit" and tracked["status"] == "definite_failure"
                and tracked["result"].get("stage") == "validation"
                and tracked["result"].get("status") in {"not_started", "approval_required"}):
            # The native connector explicitly stopped before contacting the
            # submission endpoint. Preserve its safe_to_retry flag unchanged;
            # a failed validation is not permission to bypass or auto-retry it.
            with self.harness.store.transaction(receipt["workflow_id"]) as (db, _, state):
                current = state["steps"][receipt["step_id"]]
                if current.get("intent_id") == receipt["intent_id"] and not current.get("doc_id"):
                    current["status"] = "failed"
                    db.execute("UPDATE intents SET status='failed' WHERE id=?", (receipt["intent_id"],))
                    self.harness.store.event(db, receipt["workflow_id"], "submission_not_started", {
                        "step_id": receipt["step_id"], "reason": "Native input validation stopped before submission",
                        "automatic_retry_authorized": False})
        return tracked

    def prepare(self, campaign, workflow, step):
        self._owned(campaign, workflow)
        result = self.harness.next(workflow, "prepare", step)
        if result.get("status") == "upload_required":
            report = self.harness.status(workflow)
            definition = next(s for s in report["spec"]["steps"] if s["step_id"] == step)
            metadata = report["state"]["contracts"][definition["tool"]]
            for pending in result["uploads"]:
                # The previously prepared files are still generated/hashed by
                # enzyme_workflow; only native upload validation context is added.
                args = {**pending["call"]["args"], "job_name": metadata["job_name"],
                        "input_field": pending["field"], "experiment_data": definition["inputs"]}
                uploaded = self.dispatch(campaign, "boltzmann_upload", args)
                if uploaded["result"].get("error"):
                    raise ResearchError("Upload did not complete; inspect the original tracked result")
                self.harness.next(workflow, "record_upload", step, field=pending["field"], result=uploaded["result"])
            result = self.harness.next(workflow, "prepare", step)
        return result

    def submit(self, campaign, workflow, step):
        result = self.prepare(campaign, workflow, step)
        if result.get("status") not in (None, "ready") or "call" not in result:
            return result  # A real missing contract/binding remains visible.
        from .request_scope import validate_request_scope
        report = self.harness.status(workflow)
        selected = report["state"]["steps"][step].get("input_candidate_ids", [])
        args = result["call"]["args"]
        try:
            from .results import workflow_bindings
            associations = workflow_bindings(self, campaign, workflow, selected)
            research_ids = [associations[wid]["candidate_id"] for wid in selected]
            definition = next(s for s in report["spec"]["steps"] if s["step_id"] == step)
            adapter = report["state"]["contracts"][definition["tool"]]["adapter"]
            if len(research_ids) != len(set(research_ids)) and adapter not in {"quality", "geometry"}:
                raise ResearchError("This sequence-based stage requires one selected coordinate version per candidate; duplicate sequence rows cannot be inferred as independent variants")
            validate_request_scope(self.store.status(campaign), args["job_name"], args["experiment_data"], list(dict.fromkeys(research_ids)),
                                   structure_ids={a["candidate_id"]: a["structure_id"] for a in associations.values()})
        except ResearchError as exc:
            with self.store.transaction() as db:
                self.store.event(db, campaign, "request_scope_rejected", {
                    "workflow_id": workflow, "step_id": step, "args_sha256": digest(args),
                    "reason": str(exc), "scientific_request_started": False})
            raise
        return self.dispatch(campaign, result["call"]["tool"], result["call"]["args"])

    def poll(self, campaign, workflow, step, submission_call_id):
        self._owned(campaign, workflow)
        report = self.harness.status(workflow)
        current = report["state"]["steps"][step]
        if current["status"] not in {"submitted", "running", "remote_completed"}:
            raise ResearchError("Poll requires the existing accepted workflow job")
        tracked_call = next((c for c in self.store.status(campaign)["calls"] if c["call_id"] == submission_call_id), None)
        if (tracked_call is None or tracked_call["args"].get("job_name") != current["job_name"]
                or (tracked_call.get("result") or {}).get("doc_id") != current["doc_id"]):
            raise ResearchError("Submission receipt belongs to a different workflow job")
        result = self.connector.poll(campaign, submission_call_id)
        args = {"job_name": current["job_name"], "doc_id": current["doc_id"]}
        # The live API may return download_link:[url], while the unchanged
        # workflow observer consumes scalar links. Expose only those exact
        # returned links in its envelope; persist fingerprints, never URLs.
        observed = {**result["result"], "_native_link_envelopes": [
            {"download_link": link} for link in output_links(result["result"])]}
        self.observers.after("boltzmann_status", args, observed, root=self.harness.store.root)
        return result

    def download(self, campaign, workflow, step, link, output_folder):
        self._owned(campaign, workflow)
        # The original observer requires that this exact transient link came
        # from the completed job before it can authorize artifact ingestion.
        report = self.harness.status(workflow)
        current = report["state"]["steps"].get(step)
        if current is None or current["status"] != "remote_completed":
            raise ResearchError("Download requires confirmed completion of the selected workflow step")
        from enzyme_workflow.common import digest as workflow_digest
        with self.harness.store.connection() as db:
            receipt = db.execute("SELECT 1 FROM output_links WHERE fingerprint=? AND workflow_id=? AND step_id=? AND intent_id=?",
                                 (workflow_digest(link), workflow, step, current["intent_id"])).fetchone()
        if receipt is None:
            raise ResearchError("Download link was not returned by this completed job")
        return self.dispatch(campaign, "boltzmann_download", {"download_url": link, "output_folder": str(output_folder)})

    def download_current(self, campaign, workflow, step, submission_call_id, output_folder):
        response = self.poll(campaign, workflow, step, submission_call_id)
        found = list(dict.fromkeys(output_links(response["result"])))
        if len(found) != 1:
            raise ResearchError("Expected one authoritative output link; inspect the tool's output contract before downloading")
        return self.download(campaign, workflow, step, found[0], output_folder)

    def fetch_log(self, campaign, workflow, step, submission_call_id):
        self._owned(campaign, workflow)
        current = self.harness.status(workflow)["state"]["steps"].get(step)
        source = next((c for c in self.store.status(campaign)["calls"] if c["call_id"] == submission_call_id), None)
        if (current is None or source is None or source["tool"] != "boltzmann_submit"
                or source["status"] not in {"accepted", "completed", "definite_failure"}
                or source["args"].get("job_name") != current.get("job_name")
                or not current.get("doc_id") or (source.get("result") or {}).get("doc_id") != current["doc_id"]):
            raise ResearchError("Log lookup requires the existing matching original job receipt")
        return self.dispatch(campaign, "boltzmann_fetch_tool_log", {
            "job_name": current["job_name"], "experiment_id": current["doc_id"]})

    def ingest(self, campaign, workflow, step, local_path, *, bindings=None, member=None):
        self._owned(campaign, workflow)
        return self.harness.next(workflow, "ingest", step, local_path=str(local_path), bindings=bindings, member=member,
                                 research_campaign=campaign)
