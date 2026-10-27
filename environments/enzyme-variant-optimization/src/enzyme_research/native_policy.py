"""Host policy for native research operations, not a frozen-score-only sandbox."""
from __future__ import annotations

import json
from pathlib import Path
import threading

from .connector import durable_result
from .contracts import ResearchError, canonical, digest, safe_data
from .context import ActionInterfaceError, native_tool_schemas, operation_contracts


class NativeResearchPolicy:
    def __init__(self, service, campaign, audit, allowed_actions=None):
        self.service, self.campaign, self.audit = service, campaign, audit
        self.tools = tuple({"type": "function", **s} for s in native_tool_schemas())
        self.names = frozenset(s["name"] for s in self.tools)
        self.calls = 0
        self.accepted_action = None
        self.lock = threading.RLock()
        self.allowed_actions = set(allowed_actions) if allowed_actions is not None else set(operation_contracts())
        # Manual proposal/critique injection is an offline fixture facility,
        # never an alternative to the specialist's dedicated model roles.
        if "propose" in self.allowed_actions:
            raise ResearchError("Native investigation requires dedicated proposer/critic calls, not supplied critiques")

    def _owned_paths(self, value):
        """The model may reference known structures/downloads, never host files."""
        state = self.service.store.status(self.campaign)
        paths = {state["task"]["parent"]["structure"]["path"]}
        for call in state["calls"]:
            if call["tool"] == "boltzmann_download" and call["status"] == "completed":
                paths.update((call.get("result") or {}).get("output_paths", []))
        storage_paths = set()
        def storage(obj):
            if isinstance(obj, dict):
                for key, item in obj.items():
                    if key in {"s3_path", "path", "outputFilePath"} and isinstance(item, str) and item.startswith(("users/", "users_test/")):
                        storage_paths.add(item)
                    storage(item)
            elif isinstance(obj, list):
                for item in obj: storage(item)
        for call in state["calls"]:
            if call["status"] == "completed" and call["tool"] != "boltzmann_upload": storage(call.get("result"))
        for event in state["events"]:
            if event["payload"]["event"] == "input_uploaded":
                storage_paths.add(event["payload"]["data"]["storage_path"])
        def inspect(obj):
            if isinstance(obj, dict):
                for key, item in obj.items():
                    if key == "local_path" and item not in paths:
                        raise ResearchError("Only this campaign's verified local artifacts may be referenced")
                    if key == "output_folder":
                        target = Path(item).absolute()
                        allowed = self.service.store.root / self.campaign / "downloads"
                        if target.resolve() != target or not target.is_relative_to(allowed):
                            raise ResearchError("Downloads must stay inside the campaign output directory")
                    inspect(item)
            elif isinstance(obj, list):
                for item in obj:
                    inspect(item)
        inspect(value)
        # A model cannot invent a GCP/storage reference just because the API
        # accepts strings. Bind file fields to actual upload/output receipts.
        specification = value.get("specification") if isinstance(value, dict) else None
        if isinstance(specification, dict):
            catalogue = json.loads((Path(self.service.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())
            for step in specification.get("steps", []):
                metadata = self.service.workflow.harness.registry.get(step.get("tool"), {})
                job = metadata.get("job_name")
                fields = catalogue.get("tools", {}).get(job, {}).get("request_schema", {}).get("properties", {})
                for field, item in step.get("inputs", {}).items():
                    kind = fields.get(field, {}).get("x-input-kind")
                    is_file_reference = kind == "file" or (kind == "file_or_value" and isinstance(item, str) and item.startswith(("users/", "users_test/")))
                    if is_file_reference and isinstance(item, str) and item not in storage_paths:
                        raise ResearchError("Scientific file inputs need actual campaign upload/output receipts")

    def tool(self, name, args):
        with self.lock:
            self.calls += 1
            try:
                if name not in self.names or not isinstance(args, dict):
                    raise ResearchError("Only the registered research operations are allowed")
                if self.calls > 40 or self.accepted_action is not None:
                    raise ResearchError("Native step is already closed or its action limit is exhausted")
                if name == "enzyme_research_start":
                    raise ResearchError("The operator already started this exact campaign; no second campaign is allowed")
                required = ("campaign_id", "action") if name == "enzyme_research_next" else ("campaign_id",)
                for field in required:
                    if field not in args:
                        raise ActionInterfaceError(name, "missing_required_field", "/" + field)
                if args.get("campaign_id") != self.campaign:
                    raise ResearchError("Research operation refers to another campaign")
                if name in {"enzyme_research_status", "enzyme_research_report"}:
                    if set(args) != {"campaign_id"}:
                        raise ResearchError("Unexpected research read fields")
                    result = self.context() if name == "enzyme_research_status" else getattr(self.service, "report")(self.campaign)
                    stop = False
                else:
                    if set(args) - {"campaign_id", "action", "values"}:
                        raise ResearchError("Unexpected research action fields")
                    action = args.get("action")
                    if action not in self.allowed_actions:
                        raise ResearchError("Unknown or unapproved research action")
                    values = args.get("values", {})
                    safe_data(values)
                    validator = getattr(self.service, "validate_action", None)
                    if validator is not None:
                        validator(action, values)
                    self._owned_paths(values)
                    # An unqualified inspect returns the bounded index; detail
                    # queries return explicit pages from authoritative records.
                    result = self.context() if action == "inspect" and not values else self.service.next(self.campaign, action, **values)
                    stop = not operation_contracts()[action]["read_only"]
                result = durable_result(result)
                self.audit.record("research_tool", name=name, arguments_sha256=digest(args),
                                  result_sha256=digest(result), allowed=True)
                if stop:
                    self.accepted_action = {"name": name, "arguments_sha256": digest(args), "result_sha256": digest(result)}
                return {"result": result, "research_step_finished": stop}
            except Exception as exc:
                # Persist only known argument names and locally generated schema
                # paths. Never echo scientific payloads or arbitrary exceptions.
                known_keys = {"campaign_id", "action", "values", "task", "arm", "experiment_name"}
                for entry in operation_contracts().values():
                    known_keys.update(entry["values_schema"]["properties"])
                def keys(value):
                    if not isinstance(value, dict):
                        return []
                    return sorted({key if key in known_keys else "<unrecognized>" for key in value})
                details = {"argument_keys": keys(args),
                           "value_keys": keys(args.get("values")) if isinstance(args, dict) else []}
                action = args.get("action") if isinstance(args, dict) else None
                if isinstance(action, str) and action in operation_contracts():
                    details["action"] = action
                if isinstance(exc, ActionInterfaceError):
                    details["diagnostic"] = exc.diagnostic
                self.audit.record("research_tool_denied", name=str(name)[:128], arguments_sha256=digest(args),
                                  error_type=type(exc).__name__,
                                  error_message_sha256=digest(str(exc)) if isinstance(exc, ResearchError) else None,
                                  **details)
                raise

    def context(self):
        state = self.service.store.status(self.campaign)
        from .context import compact_context
        # Read directly from the canonical catalogue, not a second registry.
        path = Path(self.service.settings["catalogue_root"]) / "tool-contracts.v1.json"
        document = json.loads(path.read_bytes())
        contracts = {}
        for job in state["task"]["allowed_jobs"]:
            entry = document.get("tools", {}).get(job)
            if entry is not None:
                contracts[job] = entry
        registry = getattr(getattr(getattr(self.service, "workflow", None), "harness", None), "registry", {})
        context = compact_context(state, contracts, registry)
        context.update(allowed_output_folder=str(self.service.store.root / self.campaign / "downloads"),
                       permitted_actions_for_this_step=sorted(self.allowed_actions))
        return durable_result(context)
