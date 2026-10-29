"""Deterministic orchestration around the existing five remote operations."""

import copy
import json
import shutil
import sqlite3
import uuid
from pathlib import Path

from .artifacts import inspect_artifact, normalize_mapping
from .common import WorkflowError, atomic_json, digest, file_hash, identifier, now, validate_data
from .contract_registry import load_registry, validate_inputs
from .graph import require_capabilities, validate_plan
from .gates import verify_report_policy
from .inputs import build_input
from .state import Store


class Harness:
    def __init__(self, root=None, bindings=None, extensions=None):
        self.store = Store(root)
        self.registry = load_registry(bindings, extensions)

    def start(self, specification):
        spec = copy.deepcopy(specification)
        steps = validate_plan(spec, self.registry)
        wid = "enzyme-" + uuid.uuid4().hex[:16]
        state = {"created_at": now(), "contracts": {s["tool"]: self.registry[s["tool"]] for s in steps.values()},
                 "steps": {name: {"status": "planned", "attempt": 0} for name in steps},
                 "candidates": {}, "uploads": {}, "retry_counts": {}, "status": "in_progress"}
        for item in spec.get("initial_candidates", []):
            cid = identifier(item.get("candidate_id"), "candidate_id")
            if cid in state["candidates"]:
                raise WorkflowError("Duplicate initial candidate ID")
            artifact = inspect_artifact(item["local_path"], "structures")
            if len(artifact["entries"]) != 1:
                raise WorkflowError("Each initial candidate needs one explicit structure")
            entry = artifact["entries"][0]
            source = Path(item["local_path"])
            dest = self.store.root / wid / "artifacts" / artifact["sha256"] / source.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            candidate = {"candidate_id": cid, "parent_ids": [], "capabilities": entry["capabilities"],
                "status": "supplied", "history": [{"source": "user_supplied", "artifact_sha256": artifact["sha256"]}],
                "structure": {"artifact_path": str(dest), "member": entry["member"], "sha256": artifact["sha256"]},
                "residue_count": entry["residue_count"]}
            candidate["sequence"] = entry["structural_sequence"]
            candidate["capabilities"].append("sequence")
            if item.get("mapping"):
                candidate["mapping"] = normalize_mapping(item["mapping"], entry["residues"])
                candidate["capabilities"].append("mapping")
            state["candidates"][cid] = candidate
        with self.store.connection() as db:
            try:
                db.execute("INSERT INTO workflows VALUES(?,?,?)", (wid, json.dumps(spec), json.dumps(state)))
                self.store.event(db, wid, "created", {"steps": list(steps)})
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("Workflow identity already exists") from exc
        return {"workflow_id": wid, "status": "planned", "next": "enzyme_workflow_next"}

    def status(self, workflow_id):
        return self.store.read(workflow_id)

    def next(self, workflow_id, action="inspect", step_id=None, **kwargs):
        identifier(workflow_id, "workflow_id")
        with self.store.transaction(workflow_id) as (db, spec, state):
            steps = {s["step_id"]: s for s in spec["steps"]}
            if action == "inspect":
                result = []
                for name, step in steps.items():
                    current = state["steps"][name]
                    status = current["status"]
                    info = {"step_id": name, "status": status}
                    if status == "planned":
                        info["waiting_for"] = [d for d in step.get("depends_on", []) if state["steps"][d]["status"] != "complete"]
                    elif status in {"submitted", "running", "remote_completed"}:
                        info["call"] = {"tool": "boltzmann_status", "args": {"job_name": current["job_name"], "doc_id": current["doc_id"]}}
                    elif status in {"submitting", "submit_unknown"}:
                        info["warning"] = "Submission outcome is ambiguous. Recover the original job; never resubmit."
                    result.append(info)
                return {"workflow_id": workflow_id, "steps": result}
            if step_id not in steps:
                raise WorkflowError("Unknown step_id")
            step, current = steps[step_id], state["steps"][step_id]
            tool = self.registry[step["tool"]]
            old = state["contracts"][step["tool"]]
            scientific_keys = ("contract_ref", "contract_document", "stage", "adapter", "requires", "tool_id")
            if digest({k: tool.get(k) for k in scientific_keys}) != digest({k: old.get(k) for k in scientific_keys}):
                raise WorkflowError("Scientific contract changed; review a new plan before continuing")
            if action == "prepare":
                return self._prepare(db, workflow_id, step, current, tool, state)
            if action == "record_upload":
                field = kwargs.get("field")
                pending = current.get("pending_uploads", {}).get(field)
                if current["status"] != "planned" or pending is None:
                    raise WorkflowError("No pending upload for this step/field")
                result = kwargs.get("result", {})
                storage_path = result.get("s3_path")
                from .contract_registry import validate_storage_path
                validate_storage_path(storage_path, field)
                if file_hash(pending["local_path"]) != pending["sha256"]:
                    raise WorkflowError("Input changed after upload preparation")
                current.setdefault("resolved_inputs", {})[field] = storage_path
                self.store.event(db, workflow_id, "upload_bound", {"step_id": step_id, "field": field, "path": storage_path})
                return {"status": "upload_recorded", "next": "prepare"}
            if action == "ingest":
                if current["status"] != "remote_completed":
                    raise WorkflowError("Ingest requires confirmed completion of the existing remote job")
                return self._ingest(db, workflow_id, step, current, tool, state, **kwargs)
            if action == "retry":
                if current["status"] != "failed" or current["attempt"] >= step.get("max_retries", 0):
                    raise WorkflowError("Retry is not approved, exhausted, or outcome is not definitely failed")
                current.clear()
                current.update(status="planned", attempt=state["retry_counts"].get(step_id, 0) + 1)
                state["retry_counts"][step_id] = current["attempt"]
                self.store.event(db, workflow_id, "retry_authorized", {"step_id": step_id, "attempt": current["attempt"]})
                return {"status": "planned", "warning": "A new submission is permitted within the approved retry budget"}
            if action == "recover_submission":
                if current["status"] not in {"submitting", "submit_unknown"}:
                    raise WorkflowError("Only an ambiguous submission can be recovered")
                response = kwargs.get("result", {})
                doc_id = response.get("doc_id")
                if not isinstance(doc_id, str) or not doc_id or response.get("job_name") != current["job_name"]:
                    raise WorkflowError("Supply the original connector submit response with doc_id and exact job_name")
                validate_data(response)
                db.execute("UPDATE intents SET status='submitted',doc_id=? WHERE id=?", (doc_id, current["intent_id"]))
                current.update(status="submitted", doc_id=doc_id)
                self.store.event(db, workflow_id, "recovered_original_submission", {"step_id": step_id, "doc_id": doc_id})
                return {"status": "submitted", "doc_id": doc_id}
            raise WorkflowError("Unsupported workflow action")

    def _prepare(self, db, wid, step, current, tool, state):
        if current["status"] == "ready":
            row = db.execute("SELECT args FROM intents WHERE id=?", (current["intent_id"],)).fetchone()
            return {"call": {"tool": "boltzmann_submit", "args": json.loads(row["args"])}}
        if current["status"] != "planned":
            raise WorkflowError("This step already has a submission or result; inspect/poll it instead")
        waiting = [d for d in step.get("depends_on", []) if state["steps"][d]["status"] != "complete"]
        if waiting:
            raise WorkflowError(f"Dependencies are not complete: {waiting}")
        if tool["backend_status"] != "active":
            return {"status": "awaiting_backend_binding", "tool": step["tool"],
                    "message": "This tool is unavailable under the current catalogue or explicit profile binding; no job was submitted"}
        if tool["contract_document"] is None:
            return {"status": "awaiting_authoritative_contract", "tool": step["tool"],
                    "message": "Tool is not documented in the existing Boltzmann catalogue; no job was submitted"}
        selected = require_capabilities(step, tool, state)
        catpred_pairs = None
        if step["tool"] == "catpred":
            from .catpred import requested_pairs
            catpred_pairs = requested_pairs(state, selected, step.get("handoff"))
            if current.get("catpred_inputs") not in (None, catpred_pairs):
                raise WorkflowError("CatPred handoff changed after preparation; review a new approved step")
            current["catpred_inputs"] = catpred_pairs
        inputs = copy.deepcopy(step["inputs"])
        upload_calls = []
        for field, value in inputs.items():
            if isinstance(value, dict) and set(value) == {"from_step", "artifact", "upload_as"}:
                if catpred_pairs is not None and (field != "input_path" or value["artifact"] != "sequences" or value["upload_as"] != "csv"):
                    raise WorkflowError("CatPred handoff requires input_path exported as sequences/csv")
                if field in current.get("resolved_inputs", {}):
                    inputs[field] = current["resolved_inputs"][field]
                else:
                    local = build_input(self.store.root, wid, step["step_id"], field, value, state, selected,
                                        catpred_pairs=catpred_pairs)
                    if isinstance(local, (list, str)):
                        inputs[field] = local
                        continue
                    current.setdefault("pending_uploads", {})[field] = {"local_path": str(local), "sha256": file_hash(local)}
                    upload_calls.append({"field": field, "call": {"tool": "boltzmann_upload", "args": {"local_path": str(local)}}})
        if upload_calls:
            return {"status": "upload_required", "uploads": upload_calls,
                    "next": "record_upload with the actual connector result, then prepare again"}
        validate_inputs(tool, inputs)
        args = {"job_name": tool["job_name"], "experiment_data": inputs, "experiment_name": step["experiment_name"]}
        intent_id = digest({"workflow": wid, "step": step["step_id"], "attempt": current["attempt"], "args": args})
        if current["attempt"]:
            args["experiment_name"] += f" [retry {current['attempt']}]"
        try:
            db.execute("INSERT INTO intents VALUES(?,?,?,?,?,?,?,?)",
                (intent_id, wid, step["step_id"], args["experiment_name"], json.dumps(args), "ready", None, tool["job_name"]))
        except sqlite3.IntegrityError as exc:
            raise WorkflowError("Experiment label already has a tracked intent; inspect it rather than duplicate it") from exc
        current.update(status="ready", intent_id=intent_id, job_name=tool["job_name"], collection_name=tool["collection_name"], input_candidate_ids=selected)
        self.store.event(db, wid, "intent_created", {"step_id": step["step_id"], "intent_id": intent_id})
        return {"status": "ready", "call": {"tool": "boltzmann_submit", "args": args}}

    def _ingest(self, db, wid, step, current, tool, state, local_path=None, bindings=None, member=None, **kwargs):
        if not isinstance(local_path, str):
            raise WorkflowError("A downloaded local artifact path is required")
        path = Path(local_path).expanduser()
        if path.is_symlink():
            raise WorkflowError("Symbolic artifact paths are not accepted")
        source_sha = file_hash(path)
        receipt = db.execute("SELECT local_path FROM downloads WHERE workflow_id=? AND step_id=? AND sha256=? AND intent_id=?",
                             (wid, step["step_id"], source_sha, current["intent_id"])).fetchone()
        if receipt is None:
            raise WorkflowError("Artifact has no matching download receipt from this remote job; poll/download its actual output before ingestion")
        def inspect_output(candidate_path):
            if step["tool"] == "catpred":
                from .catpred import inspect_output as inspect_catpred
                prepared = current.get("pending_uploads", {}).get("input_path")
                if prepared and file_hash(prepared["local_path"]) != prepared["sha256"]:
                    raise WorkflowError("Prepared CatPred input changed after upload; cannot verify result identity")
                return inspect_catpred(candidate_path, current.get("catpred_inputs"))
            return inspect_artifact(candidate_path, tool["adapter"])
        parsed = inspect_output(path) if member is None else None
        if member is not None:
            from .artifacts import read_members
            files = read_members(path)
            if member not in files or Path(member).name != member:
                raise WorkflowError("Select a single top-level authoritative result member")
            selected = self.store.root / wid / "selected" / step["step_id"] / member
            selected.parent.mkdir(parents=True, exist_ok=True)
            selected.write_bytes(files[member])
            parsed = inspect_output(selected)
            path = selected
        entries = parsed["entries"]
        if step["tool"] == "catpred":
            verified_bindings = {entry["label"]: {"candidate_id": entry["label"]} for entry in entries}
            if bindings not in (None, {}) and bindings != verified_bindings:
                raise WorkflowError("CatPred bindings disagree with the verified sequence-SMILES identities")
            bindings = verified_bindings
        verify_report_policy(tool, step["inputs"], entries)
        expected = step.get("expected_count")
        if expected is None:
            sample_field = {"rfd3": "n_samples", "enzycontrol": "n_samples", "genzyme": "num_structures"}.get(step["tool"])
            if sample_field:
                expected = step["inputs"].get(sample_field, 1)
            elif tool["adapter"] in {"geometry", "quality", "report", "pockets"}:
                expected = len(current.get("input_candidate_ids", [])) or None
        if expected is not None and expected != len(entries):
            raise WorkflowError(f"Partial output: expected {expected} candidates, found {len(entries)}")
        mapping = bindings or {}
        if not isinstance(mapping, dict) or set(mapping) - {e["label"] for e in entries}:
            raise WorkflowError("Candidate bindings contain unknown output labels")
        generated = tool["stage"] == "generation"
        if not generated and set(mapping) != {e["label"] for e in entries}:
            raise WorkflowError("Every output label needs an explicit candidate_id or parent_ids binding; never pair by row order")
        dest = self.store.root / wid / "artifacts" / parsed["sha256"] / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.resolve() != path.resolve():
            shutil.copyfile(path, dest)
        if file_hash(dest) != parsed["sha256"]:
            raise WorkflowError("Artifact changed during ingestion")
        accepted_ids = []
        for entry in entries:
            label = entry["label"]
            binding = mapping.get(label, {})
            validate_data(binding)
            if set(binding) - {"candidate_id", "parent_ids", "mapping"}:
                raise WorkflowError("Binding only accepts candidate_id, parent_ids and mapping")
            cid = binding.get("candidate_id")
            parents = binding.get("parent_ids", [])
            if not isinstance(parents, list) or len(set(parents)) != len(parents):
                raise WorkflowError("parent_ids must list unique candidate IDs")
            transforms = tool["adapter"] in {"structures", "sequences"}
            if transforms and cid is not None:
                raise WorkflowError("A coordinate/sequence transformation creates a new child; use parent_ids")
            if not transforms and (cid is None or parents):
                raise WorkflowError("A report attaches to an existing candidate_id, not a new child")
            if cid is not None:
                if cid not in current.get("input_candidate_ids", []):
                    raise WorkflowError("Candidate join is outside this step's selected input set")
                candidate = state["candidates"][cid]
            else:
                if not generated and (not parents or any(p not in current.get("input_candidate_ids", []) for p in parents)):
                    raise WorkflowError("New sequence/structure candidates need explicit parent IDs from this step's inputs")
                cid = "cand-" + digest({"workflow": wid, "step": step["step_id"], "label": label})[:20]
                candidate = {"candidate_id": cid, "parent_ids": parents, "capabilities": [], "history": [], "status": "generated"}
                state["candidates"][cid] = candidate
            if "capabilities" in entry:
                # Sequence replacement invalidates old side-chain/ligand coordinates.
                candidate["capabilities"] = entry["capabilities"]
                if step["tool"] == "enzycontrol":
                    candidate["capabilities"] = [v for v in candidate["capabilities"] if v != "all_atom"]
                    if "backbone_or_incomplete" not in candidate["capabilities"]:
                        candidate["capabilities"].append("backbone_or_incomplete")
                candidate["status"] = "generated"
                if "sequence" in entry:
                    candidate["sequence"] = entry["sequence"]
                    candidate.pop("structure", None)
                    candidate.pop("mapping", None)
                    candidate.pop("gates", None)
                    candidate.pop("metrics", None)
                if "residue_count" in entry:
                    candidate.pop("gates", None)
                    candidate["structure"] = {"artifact_path": str(dest), "member": entry["member"], "sha256": parsed["sha256"]}
                    candidate["residue_count"] = entry["residue_count"]
                    parent_sequences = [state["candidates"][p].get("sequence") for p in parents]
                    if parent_sequences and all(parent_sequences) and ":".join(parent_sequences) != entry["structural_sequence"]:
                        raise WorkflowError("Prepared/predicted structure sequence does not match the explicitly bound parent sequence")
                    if tool["stage"] != "generation":
                        candidate["sequence"] = entry["structural_sequence"]
                        candidate["capabilities"].append("sequence")
                    if binding.get("mapping") is not None:
                        candidate["mapping"] = normalize_mapping(binding["mapping"], entry["residues"])
                    elif "mapping" in entry:
                        candidate["mapping"] = entry["mapping"]
                    else:
                        candidate.pop("mapping", None)
                    if candidate.get("mapping") and "mapping" not in candidate["capabilities"]:
                        candidate["capabilities"].append("mapping")
            if "status" in entry:
                candidate["status"] = entry["status"]
                candidate.setdefault("gates", {})[step["step_id"]] = entry["status"]
            if "metrics" in entry:
                candidate.setdefault("metrics", {})[step["step_id"]] = entry["metrics"]
            candidate["history"].append({"step_id": step["step_id"], "tool": step["tool"], "output_label": label,
                                           "artifact_sha256": parsed["sha256"], "doc_id": current["doc_id"]})
            accepted_ids.append(cid)
        if len(set(accepted_ids)) != len(accepted_ids):
            raise WorkflowError("Multiple output rows map to the same candidate; resolve identity explicitly")
        current.update(status="complete", candidate_ids=accepted_ids, artifact_path=str(dest), artifact_sha256=parsed["sha256"])
        self.store.event(db, wid, "output_validated", {"step_id": step["step_id"], "count": len(entries), "sha256": parsed["sha256"]})
        if all(s["status"] == "complete" for s in state["steps"].values()):
            state["status"] = "complete"
        return {"status": "complete", "candidate_ids": accepted_ids, "artifact_path": str(dest)}

    def report(self, workflow_id):
        report = self.status(workflow_id)
        report["scientific_boundary"] = "Computational measurements and supplied acceptance criteria only; not experimental evidence of catalysis, affinity or activity."
        steps = {s["step_id"]: s for s in report["spec"]["steps"]}
        evidence = {}
        for cid, candidate in report["state"]["candidates"].items():
            gates = candidate.get("gates", {})
            stages = {report["state"]["contracts"][steps[s]["tool"]]["stage"] for s, status in gates.items() if status == "passed"}
            evidence[cid] = {"geometry_validation_passed": "geometry" in stages,
                             "quality_validation_passed": "quality" in stages,
                             "experimental_validation": "not_established"}
        report["candidate_evidence"] = evidence
        directory = self.store.root / workflow_id / "report"
        atomic_json(directory / "workflow_report.json", report)
        import csv
        with (directory / "candidates.csv").open("w", newline="", encoding="utf-8") as handle:
            fields = ["candidate_id", "status", "parent_ids", "capabilities", "gates", "metrics"]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for candidate in report["state"]["candidates"].values():
                writer.writerow({f: json.dumps(candidate.get(f)) if isinstance(candidate.get(f), (dict, list)) else candidate.get(f) for f in fields})
        lines = ["Enzyme workflow report", f"Workflow: {workflow_id}", f"Objective: {report['spec']['objective']}",
                 f"Execution status: {report['state']['status']}", "", "Step results:"]
        for name, current in report["state"]["steps"].items():
            lines.append(f"- {name}: {current['status']}; {len(current.get('candidate_ids', []))} output candidates")
        lines.extend(["", f"Tracked candidates: {len(report['state']['candidates'])}", report["scientific_boundary"]])
        (directory / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"workflow_id": workflow_id, "status": report["state"]["status"], "report_path": str(directory / "workflow_report.json"),
                "summary_path": str(directory / "report.txt"), "candidates_path": str(directory / "candidates.csv"),
                "candidate_count": len(report["state"]["candidates"])}
