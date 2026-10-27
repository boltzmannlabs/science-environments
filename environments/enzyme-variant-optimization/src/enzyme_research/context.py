"""Bounded, reconstructable model context over complete campaign records.

This is an access view, not another scientific registry. Full records stay in
the authoritative store/canonical catalogue. Omitted details are explicit and
retrievable by record ID and JSON pointer, never silently truncated.
"""
from __future__ import annotations

import copy

from .connector import durable_result
from .contracts import ResearchError, canonical, digest

PAGE_BYTES = 16384


def operation_contracts():
    """One public action contract for both native arms and dedicated roles.

    These are host operation envelopes, not replacements for the canonical
    scientific input contracts or the executor's validation/approval gates.
    Return fresh objects so an episode cannot mutate another arm's interface.
    """
    text = {"type": "string"}
    strings = {"type": "array", "items": text}
    ids = {**strings, "minItems": 1, "uniqueItems": True}
    mapping = {"type": "object", "additionalProperties": text}
    opaque = {"type": "object", "additionalProperties": True}

    def obj(properties, required=()):
        return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}

    selectors = {"view": text, "record_id": text, "pointer": text,
                 "offset": {"type": "integer", "minimum": 0},
                 "limit": {"type": "integer", "minimum": 1, "maximum": 20}, "snapshot_sha256": text}
    step = obj({"step_id": text, "tool": {**text, "description": "Audited workflow registry tool ID, not a remote job_name."},
        "candidate_ids": ids, "experiment_name": {**text, "maxLength": 200},
        "inputs": {**opaque, "description": "Exact canonical scientific inputs; file references need actual upload/output receipts."},
        "depends_on": strings, "required_gates": strings, "stage": text,
        "expected_count": {"type": "integer", "minimum": 1, "maximum": 10000},
        "max_retries": {"type": "integer", "minimum": 0, "maximum": 3},
        "selection": {"type": "string", "enum": ["all", "passed"]},
        "handoff": {**opaque, "description": "Tool-specific audited handoff, including CatPred endpoint requirements."}},
        ("step_id", "tool", "candidate_ids", "experiment_name", "inputs"))
    specification = obj({"objective": text, "approved": {"type": "boolean", "enum": [True]},
        "steps": {"type": "array", "items": step, "minItems": 1, "maxItems": 100},
        "initial_candidates": {"type": "array", "items": obj({"candidate_id": text, "local_path": text}, ("candidate_id", "local_path"))}},
        ("objective", "approved", "steps"))
    workflow = {"workflow_id": text, "step_id": text}
    receipt = {**workflow, "submission_call_id": text}
    result = {}

    def add(action, properties, required=(), *, read_only=False, requirements):
        result[action] = {"values_schema": obj(properties, required), "read_only": read_only, "requirements": requirements}

    add("inspect", selectors, read_only=True, requirements="Empty values reads the index. Detail reads require view; pointer requires record_id. Carry snapshot_sha256 across pages.")
    add("inspect_report", selectors, read_only=True, requirements="Read verified computational report pages; no scientific action is completed by reading a report.")
    add("investigate", {}, requirements="Only the specialist arm may invoke dedicated proposer/critic roles under the shared model budget. No supplied hypotheses or critiques; context comes from recorded state.")
    add("repair_unsubmitted", {"experiment_data": opaque, "reason": {**text, "maxLength": 2000}}, ("experiment_data", "reason"), requirements="Specialist only: one input-only repair attempt for an approved pending hypothesis before any workflow segment or scientific submission exists. Dedicated critic must approve the exact replacement; job, kind, candidates and round stay unchanged. No invented observations or automatic retries; normal native validation/approval still apply.")
    add("add_candidates", {"candidates": {"type": "array", "minItems": 1, "items": obj({"candidate_id": text, "parent_id": text, "sequence": text}, ("candidate_id", "parent_id", "sequence"))}}, ("candidates",), requirements="Preserve catalytic residues, library membership, unique registered identities and candidate budget.")
    add("prepare_input", {"job_name": text, "candidate_ids": ids, "structure_ids": mapping}, ("job_name", "candidate_ids"), requirements="Use an approved tool's audited conversion adapter and known candidates/verified coordinate versions; does not submit science.")
    add("upload_input", {"input_id": text, "experiment_data": opaque}, ("input_id",), requirements="Upload only an existing hash-checked prepared input. Optional context excludes its file field. Native validation/approval is mandatory; no approval override is accepted.")
    for action in ("sync_sequences", "sync_structures", "sync_metrics"):
        add(action, {**receipt, **({"kind": text} if action == "sync_metrics" else {})}, tuple(receipt), requirements="Import only verified outputs of the matching completed original submission; never invent candidates, structures or metrics.")
    add("verify_ligand", {"candidate_id": text, "structure_id": text, "sdf_member": text,
        "ligand_selector": obj({"chain_id": text, "residue_number": {"type": "integer"}, "component_id": text, "insertion_code": text}, ("chain_id", "residue_number", "component_id"))},
        ("candidate_id", "structure_id", "sdf_member", "ligand_selector"), requirements="Verify exact task ligand graph/coordinates from the same verified output archive; no atom-order guesses or chemical-state substitution.")
    add("match_stability", {"observation_id": text, "basis_candidate_id": text, "structure_id": text, "target_candidate_ids": ids},
        ("observation_id", "basis_candidate_id", "structure_id", "target_candidate_ids"), requirements="Requires an actual stability observation and its exact coordinate basis; predictions are not activity assays.")
    add("plan_segment", {"specification": specification, "structure_ids": mapping,
        "followup": obj({"reason": text, "observation_ids": ids}, ("reason", "observation_ids"))}, ("specification",),
        requirements="Create an immutable approved workflow. Specialist first step must exactly match the pending approved action; additional tools require actual observation-backed followup. Do not set approved without operator approval. Scientific tool schemas remain authoritative.")
    add("submit", workflow, tuple(workflow), requirements="Submit an existing owned workflow step using workflow_id and step_id, NOT job_name/experiment_data. All validation, warning-specific approval and budget gates still apply. Never duplicate pending or ambiguous jobs.")
    add("poll", receipt, tuple(receipt), read_only=True, requirements="Read/reconcile the original accepted submission without claiming scientific progress; reuse submission_call_id, never resubmit while pending.")
    add("logs", receipt, tuple(receipt), read_only=True, requirements="Read the existing matching original job's logs; logs are not scientific observations or successful research progress.")
    add("download", {**receipt, "output_folder": text}, (*receipt, "output_folder"), requirements="Only completed original-job artifacts may be downloaded into allowed_output_folder; use authoritative returned links, not supplied URLs.")
    add("ingest", {**receipt, "local_path": text, "bindings": opaque, "member": text, "kind": text}, (*receipt, "local_path"), requirements="Ingest only a verified downloaded artifact and matching original submission. Bind exact identities; never manufacture an observation.")
    add("complete_decision", {"round": {"type": "integer", "minimum": 1}, "observation_ids": ids}, ("round", "observation_ids"), requirements="Requires actual new observations of the selected scientific action; prior results, reviews, uploads and malformed requests do not complete a decision.")
    # These actions are implemented only by the isolated benchmark service.
    # Keep them in the same schema used by the native worker and host broker;
    # each episode's explicit allowlist still determines authorization.
    add("add_library_candidates", {"member_ids": ids}, ("member_ids",), requirements="Benchmark only: register exact public library member IDs without changing their sequences; parent is already registered.")
    add("checkpoint", {"notes": {**text, "maxLength": 12000}}, ("notes",), requirements="Benchmark only: persist bounded workflow notes across isolated episodes, never experimental labels or invented observations.")
    add("begin_round", {"observation_ids": {**strings, "uniqueItems": True}, "rationale": text}, requirements="Benchmark base arm only: begin at most three optimization rounds. The first may have no observations; later rounds require actual observation IDs.")
    add("seal_selection", {"candidate_ids": {**ids, "minItems": 10, "maxItems": 10}, "rationale": text, "observation_ids": {**strings, "uniqueItems": True}}, ("candidate_ids", "rationale", "observation_ids"), requirements="Benchmark only: irreversibly seal exactly ten distinct registered nonparent public library candidates in ranked order. Cite actual observations, or explicitly disclose prior-only/failed-workflow limitations. Stops all future scientific/model access before independent evaluation.")
    # Internal fixed-reference adapters explicitly pass None for these
    # optional automatic bindings/defaults. Advertise that existing contract.
    nullable = {"ingest": ("bindings", "member", "kind"), "prepare_input": ("structure_ids",),
                "plan_segment": ("structure_ids", "followup"), "upload_input": ("experiment_data",),
                "sync_metrics": ("kind",), "inspect": ("record_id", "snapshot_sha256"),
                "inspect_report": ("record_id", "snapshot_sha256")}
    for action, fields in nullable.items():
        properties = result[action]["values_schema"]["properties"]
        for field in fields:
            schema = properties[field]
            kind = schema["type"]
            properties[field] = {**schema, "type": kind if isinstance(kind, list) else [kind, "null"]}
    return copy.deepcopy(result)


class ActionInterfaceError(ResearchError):
    """Safe machine-readable diagnostics containing schema paths, not values."""
    def __init__(self, action, code, path):
        self.diagnostic = {"action": action, "code": code, "path": path}
        label = "missing required field" if code == "missing_required_field" else "invalid action fields"
        super().__init__(f"{action}: {label} at {path}")


def validate_action_values(action, values):
    """Validate the envelope before dereferencing fields or inspecting paths.

    Scientific input validation and approval still belong to the executor. Only
    known schema property names enter diagnostics; arbitrary supplied keys and
    their values are never echoed into an error or audit.
    """
    contract = operation_contracts().get(action)
    if contract is None:
        return  # The service still rejects unknown actions; propose is fixture-only.

    def check(value, schema, path):
        kind = schema.get("type")
        if isinstance(kind, list):
            if value is None and "null" in kind:
                return
            kind = next(item for item in kind if item != "null")
        if kind == "object":
            if not isinstance(value, dict):
                raise ActionInterfaceError(action, "invalid_fields", path)
            for key in schema.get("required", []):
                if key not in value:
                    raise ActionInterfaceError(action, "missing_required_field", path + "/" + key)
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False and set(value) - set(properties):
                if action == "verify_ligand" and path == "/values":
                    raise ResearchError("Ligand verification takes only candidate_id, structure_id, sdf_member and ligand_selector")
                raise ActionInterfaceError(action, "invalid_fields", path)
            for key, child in properties.items():
                if key in value:
                    check(value[key], child, path + "/" + key)
        elif kind == "array":
            if not isinstance(value, list):
                raise ActionInterfaceError(action, "invalid_fields", path)
            for i, item in enumerate(value):
                check(item, schema.get("items", {}), path + "/" + str(i))
        elif (kind == "string" and not isinstance(value, str)
              or kind == "integer" and type(value) is not int
              or kind == "boolean" and type(value) is not bool):
            raise ActionInterfaceError(action, "invalid_fields", path)

    check(values, contract["values_schema"], "/values")


def native_tool_schemas():
    """Identical native-worker and broker schemas without modifying SCI core."""
    from .plugin import SCHEMAS
    schemas = copy.deepcopy(SCHEMAS)
    operations = operation_contracts()
    schema = next(item for item in schemas if item["name"] == "enzyme_research_next")
    schema["description"] = "Choose one research action using its exact values schema below. Read-only inspection/logging does not complete a research step. Canonical scientific contracts and approval remain mandatory."
    schema["parameters"]["properties"]["action"]["enum"] = sorted(operations)
    def portable(value):
        if isinstance(value, list):
            return [portable(item) for item in value]
        if not isinstance(value, dict):
            return value
        value = {key: portable(item) for key, item in value.items()}
        # Native optional fields can be omitted. Internal callers still use the
        # complete nullable operation contract, not this model-wire projection.
        if isinstance(value.get('type'), list):
            concrete = [kind for kind in value['type'] if kind != 'null']
            if len(concrete) == 1:
                value['type'] = concrete[0]
        if value.get('type') == 'object':
            value.setdefault('properties', {})
            value.setdefault('required', [])
        return value
    # The pinned native SCI sanitizer removes root combinators for Codex.
    # Nested value alternatives survive and advertise each action's exact
    # envelope, while validate_action_values enforces the action/value pairing.
    schema['parameters']['properties']['values'] = {
        'type': 'object', 'properties': {}, 'required': [], 'additionalProperties': True,
        'description': 'Choose the values branch for the selected action; the host validates their exact pairing.',
        'anyOf': [{**portable(entry['values_schema']), 'description': action + ': ' + entry['requirements']}
                  for action, entry in operations.items()]}
    return schemas


def collections(state, contracts):
    prepared = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_prepared"]
    uploaded = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "input_uploaded"]
    reviews = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "hypothesis_review_declined"]
    views = {
        "task": [("task", state["task"])],
        "candidates": [(c["candidate_id"], c) for c in state["candidates"]],
        "observations": [(o["observation_id"], o) for o in state["observations"]],
        "structures": [(s["structure_id"], s) for s in state["structures"]],
        "ligand_verifications": [(e["payload"]["data"]["verification_id"], e["payload"]["data"])
                                 for e in state["events"] if e["payload"]["event"] == "ligand_identity_verified"],
        "structure_assessments": [(str(i), s) for i, s in enumerate(state["structure_assessments"])],
        "decisions": [(str(d["round"]), d) for d in state["decisions"]],
        "calls": [(c["call_id"], c) for c in state["calls"]],
        "prepared_inputs": [(str(i), item) for i, item in enumerate(prepared)],
        "confirmed_uploads": [(str(i), item) for i, item in enumerate(uploaded)],
        "hypothesis_reviews": [(item["review_id"], item) for item in reviews],
        "tool_contracts": list(contracts.items()),
    }
    return {name: [{"record_id": rid, "value": durable_result(value)} for rid, value in rows]
            for name, rows in views.items()}


def pointer_get(value, pointer):
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")) or len(pointer) > 2048:
        raise ResearchError("pointer must be an empty string or a bounded JSON pointer")
    if not pointer:
        return value
    for raw in pointer[1:].split("/"):
        # RFC 6901 escapes: do not accept an ambiguous unknown escape.
        for i, character in enumerate(raw):
            if character == "~" and (i + 1 == len(raw) or raw[i + 1] not in "01"):
                raise ResearchError("Invalid JSON pointer escape")
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and key.isascii() and key.isdecimal() and (key == "0" or not key.startswith("0")) and int(key) < len(value):
            value = value[int(key)]
        else:
            raise ResearchError("JSON pointer does not identify an available value")
    return value


def read_context(state, contracts, *, view, record_id=None, pointer="", offset=0, limit=10, snapshot_sha256=None):
    """Read complete bounded records, or page a selected record's list field.

    List pointers use item offsets; other fields return one complete value.
    Every response includes a stable snapshot hash. Send it on later pages to
    reject changed state instead of combining pages from different snapshots.
    """
    views = collections(state, contracts)
    if not isinstance(view, str) or view not in views:
        raise ResearchError("Unknown research context view")
    return read_records(state["campaign_id"], view, views[view], record_id=record_id, pointer=pointer,
                        offset=offset, limit=limit, snapshot_sha256=snapshot_sha256)


def read_records(campaign_id, view, rows, *, record_id=None, pointer="", offset=0, limit=10, snapshot_sha256=None):
    """Shared bounded reader for authoritative context and verified report rows."""
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 20:
        raise ResearchError("Context offset must be nonnegative and limit must be 1-20")
    snapshot = digest(rows)
    if snapshot_sha256 is not None and snapshot_sha256 != snapshot:
        raise ResearchError("Context snapshot changed; begin a new page sequence")
    if record_id is not None:
        if not isinstance(record_id, str):
            raise ResearchError("Context record_id must be a string")
        selected = next((row for row in rows if row["record_id"] == record_id), None)
        if selected is None:
            raise ResearchError("Unknown record in this campaign context")
        value = pointer_get(selected["value"], pointer)
        if isinstance(value, list):
            items = [{"item_index": i, "value": item} for i, item in enumerate(value)]
            mode = "list_items"
        else:
            items, mode = [{"record_id": record_id, "value": value}], "field"
        selected_hash = digest(value)
    else:
        if pointer:
            raise ResearchError("A JSON pointer requires an explicit record_id")
        items, mode, selected_hash = rows, "records", snapshot
    if offset > len(items):
        raise ResearchError("Context offset exceeds the selected record count")
    response = {"campaign_id": campaign_id, "view": view, "record_id": record_id,
                "pointer": pointer, "mode": mode, "snapshot_sha256": snapshot,
                "selection_sha256": selected_hash, "total": len(items), "offset": offset,
                "items": [], "next_offset": None, "complete": False}
    for index in range(offset, min(len(items), offset + limit)):
        row = copy.deepcopy(items[index])
        response["items"].append({**row, "value_sha256": digest(row["value"])})
        if len(canonical(response).encode()) > PAGE_BYTES - 128:
            response["items"].pop()
            if not response["items"]:
                raise ResearchError("Context record exceeds the page bound; select a smaller field with a JSON pointer")
            break
    end = offset + len(response["items"])
    response.update(next_offset=end if end < len(items) else None, complete=end == len(items))
    return response


def compact_context(state, contracts, workflow_registry=None):
    views = collections(state, contracts)
    def refs(name, fields):
        return [{"record_id": row["record_id"], "record_sha256": digest(row["value"]),
                 **{field: row["value"][field] for field in fields if field in row["value"]}}
                for row in views[name][:20]]
    task = copy.deepcopy(state["task"])
    if "candidate_library" in task:
        library = task["candidate_library"]
        task["candidate_library"] = {"library_id": library["library_id"], "members_sha256": library["members_sha256"],
                                     "member_count": len(library["members"]),
                                     "members_context_ref": {"view": "task", "record_id": "task", "pointer": "/candidate_library/members"}}
    context = {"campaign_id": state["campaign_id"], "task": task, "arm": state["arm"],
        "candidates": refs("candidates", ("candidate_id", "parent_id", "sequence_sha256", "structure_status", "library_member_id")),
        "observations": refs("observations", ("observation_id", "kind", "candidate_ids", "evidence_level", "source_call_id")),
        "structures": refs("structures", ("structure_id", "candidate_id", "sequence_sha256", "capabilities")),
        "ligand_verifications": refs("ligand_verifications", ("verification_id", "structure_id", "candidate_id", "heavy_atom_count")),
        "structure_assessments": refs("structure_assessments", ("structure_id", "candidate_id", "kind", "outcome", "execution_mode", "observation_id")),
        "decisions": refs("decisions", ("round", "status")),
        "calls": refs("calls", ("call_id", "tool", "status")),
        "prepared_inputs": refs("prepared_inputs", ("input_id", "job_name", "candidate_ids", "sha256")),
        "confirmed_uploads": refs("confirmed_uploads", ("input_id", "job_name", "input_field", "candidate_ids", "storage_path", "experiment_data")),
        "hypothesis_reviews": refs("hypothesis_reviews", ("review_id", "status", "proposed_round", "approved_for_execution")),
        "operation_contracts": operation_contracts(),
        "workflow_tools": {tool_id: {key: metadata[key] for key in ("job_name", "stage", "adapter", "requires", "backend_status") if key in metadata}
                           for tool_id, metadata in (workflow_registry or {}).items()
                           if metadata.get("job_name") in state["task"]["allowed_jobs"]},
        "tool_contracts": {row["record_id"]: {"context_ref": {"view": "tool_contracts", "record_id": row["record_id"]},
                                            "record_sha256": digest(row["value"])} for row in views["tool_contracts"][:20]},
        "context_access": {"action": "inspect", "values": {"view": "observations", "record_id": "<observation_id>", "pointer": "/metrics", "limit": 10},
            "page_bytes_max": PAGE_BYTES,
            "views": {name: {"count": len(rows), "snapshot_sha256": digest(rows), "index_offset": 0,
                             "indexed_records": min(20, len(rows)), "index_complete": len(rows) <= 20}
                      for name, rows in views.items()},
            "note": "Index includes at most the first 20 records per collection; count and index_complete disclose the remainder. Full records are not embedded. Read inspect views for remaining records, sequences, metrics and tool schemas. Use record_id and JSON pointer for large records; arrays can be paged. Carry snapshot_sha256 across pages. Missing detail never implies a scientific pass."}}
    return durable_result(context)
