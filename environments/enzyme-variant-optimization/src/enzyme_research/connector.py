"""Existing native Boltzmann handlers, never a second authenticated HTTP client."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlsplit, parse_qs

from .contracts import ResearchError, strict_load, digest

OPERATIONS = {"boltzmann_upload", "boltzmann_submit", "boltzmann_status", "boltzmann_download", "boltzmann_fetch_tool_log"}


def durable_result(value):
    """Keep signed URLs transient while preserving output storage paths and IDs."""
    if isinstance(value, list):
        return [durable_result(v) for v in value]
    if isinstance(value, dict):
        return {k: durable_result(v) for k, v in value.items() if k.lower() not in
                {"download_url", "download_link", "signed_url", "tokenid", "authorization", "api_key", "token", "password"}}
    if isinstance(value, str) and value.startswith(("https://", "http://")):
        keys = {key.lower() for key in parse_qs(urlsplit(value).query)}
        if keys & {"token", "signature", "sig", "x-goog-signature", "x-amz-signature", "access_token"}:
            return "[transient URL omitted]"
    return value


class NativeConnector:
    def __init__(self, runtime_path):
        runtime = strict_load(runtime_path)
        if not isinstance(runtime, dict) or set(runtime) != {"schema_version", "native_source", "native_revision", "native_python", "profile"}:
            raise ResearchError("Unexpected native connector runtime fields")
        if runtime["schema_version"] != "enzyme-research-connector/1":
            raise ResearchError("Unsupported native connector runtime")
        self.runtime = runtime
        for name in ("native_source", "native_python", "profile"):
            path = Path(runtime[name])
            if not path.is_absolute() or not path.exists():
                raise ResearchError("Native connector paths must exist and be absolute")
        head = subprocess.check_output(["git", "-C", runtime["native_source"], "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", runtime["native_source"], "status", "--porcelain"], text=True)
        if head != runtime["native_revision"] or dirty:
            raise ResearchError("Native Agent-Scientist source must match its pinned clean revision")

    def call(self, name, args):
        if name not in OPERATIONS | {"connector_availability", "connector_service_check", "catalogue_capabilities", "connector_validate_upload", "connector_validate_submission"}:
            raise ResearchError("Unknown native connector operation")
        payload = json.dumps({"runtime": self.runtime, "operation": name, "args": args}, allow_nan=False)
        worker = Path(__file__).with_name("native_connector_worker.py")
        env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1",
               "SCI_HOME": self.runtime["profile"], "CUDA_VISIBLE_DEVICES": "",
               "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2"}
        try:
            result = subprocess.run([self.runtime["native_python"], "-I", "-B", str(worker)],
                input=payload, capture_output=True, text=True, timeout=650, env=env,
                cwd=self.runtime["native_source"])
        except subprocess.TimeoutExpired as exc:
            raise ResearchError("Native connector outcome unknown; do not repeat a submission") from exc
        if result.returncode or len(result.stdout) > 8 * 1024**2:
            raise ResearchError("Native connector failed; no successful operation is confirmed")
        try:
            response = json.loads(result.stdout)
        except ValueError as exc:
            raise ResearchError("Native connector returned an invalid envelope") from exc
        if not isinstance(response, dict):
            raise ResearchError("Native connector response must be an object")
        return response


class TrackedConnector:
    def __init__(self, store, connector, validation_approval=None):
        self.store, self.connector = store, connector
        self.validation_approval = validation_approval

    def _consented_arguments(self, campaign, name, args):
        args = dict(args)
        if name not in {"boltzmann_upload", "boltzmann_submit"}:
            return args
        approval = self.validation_approval
        if not approval:
            if args.get("allow_partial_validation") is True:
                raise ResearchError("Best-effort validation needs recorded operator consent, not a model-supplied flag")
            return args
        state = self.store.status(campaign)
        if (not isinstance(approval, dict) or set(approval) != {"task_sha256", "allowed_warnings", "source"}
                or approval["task_sha256"] != digest(state["task"]) or approval["source"] != "explicit_user_consent"
                or not isinstance(approval["allowed_warnings"], list)
                or any(not isinstance(w, str) or not w for w in approval["allowed_warnings"])):
            raise ResearchError("Validation consent must match this exact frozen task and explicit warning list")
        validation_name = "connector_validate_upload" if name == "boltzmann_upload" else "connector_validate_submission"
        fields = {"job_name", "local_path", "input_field", "experiment_data"} if name == "boltzmann_upload" else {"job_name", "experiment_data"}
        report = self.connector.call(validation_name, {key: value for key, value in args.items() if key in fields})
        if (not isinstance(report, dict) or report.get("error") or report.get("errors")
                or not isinstance(report.get("warnings"), list) or set(report["warnings"]) - set(approval["allowed_warnings"])):
            raise ResearchError("Current native validation has errors or warnings outside the recorded consent; no operation was started")
        args["allow_partial_validation"] = bool(report["warnings"])
        with self.store.transaction() as db:
            self.store.event(db, campaign, "scoped_validation_consent_checked", {
                "operation": name, "task_sha256": approval["task_sha256"],
                "approval_sha256": digest(approval), "current_warnings": report["warnings"]})
        return args

    def execute(self, campaign, name, args, *, operation_key=None):
        if (isinstance(self.connector, NativeConnector)
                and self.store.status(campaign)["task"]["evidence_track"] == "synthetic"):
            raise ResearchError("Synthetic campaigns cannot execute the real native scientific connector")
        args = self._consented_arguments(campaign, name, args)
        call_id, created = self.store.reserve_call(campaign, name, durable_result(args), operation_key=operation_key)
        if not created:
            original = next(c for c in self.store.status(campaign)["calls"] if c["call_id"] == call_id)
            if original["status"] not in {"completed", "definite_failure"}:
                raise ResearchError("This operation was already reserved or sent; reconcile the original call rather than repeating it")
            return {"call_id": call_id, "result": original["result"], "status": original["status"], "reused": True}
        self.store.call_transition(campaign, call_id, "sending")
        try:
            response = self.connector.call(name, args)
        except Exception:
            self.store.call_transition(campaign, call_id, "submit_unknown" if name == "boltzmann_submit" else "operation_unknown",
                                       {"error": "Native operation outcome unknown; inspect the original call"})
            raise
        if not isinstance(response, dict):
            self.store.call_transition(campaign, call_id, "submit_unknown" if name == "boltzmann_submit" else "operation_unknown",
                                       {"error": "Connector returned a malformed result; outcome is unknown"})
            raise ResearchError("Malformed connector result; reconcile the original operation")
        result = durable_result(response)
        validation_stopped = response.get("stage") == "validation" and response.get("status") in {"not_started", "approval_required"}
        if validation_stopped:
            status = "definite_failure"
        elif name == "boltzmann_submit":
            if response.get("job_name", args.get("job_name")) != args.get("job_name"):
                status = "submit_unknown"
            elif isinstance(response.get("doc_id"), str) and response["doc_id"] and not response.get("error"):
                status = "accepted"
            elif response.get("safe_to_retry") is True:
                status = "definite_failure"
            else:
                status = "submit_unknown"
        else:
            status = "operation_unknown" if response.get("error") else "completed"
        self.store.call_transition(campaign, call_id, status, result)
        return {"call_id": call_id, "result": response, "status": status}

    def poll(self, campaign, submission_call_id):
        state = self.store.status(campaign)
        call = next((c for c in state["calls"] if c["call_id"] == submission_call_id), None)
        if call is None or call["tool"] != "boltzmann_submit" or call["status"] not in {"accepted", "completed"}:
            raise ResearchError("Poll requires an accepted tracked original submission")
        response = self.execute(campaign, "boltzmann_status", {"job_name": call["args"]["job_name"], "doc_id": call["result"]["doc_id"]})
        outcome = str(response["result"].get("status", "")).lower()
        failed = outcome in {"failed", "error", "cancelled", "canceled"}
        if call["status"] == "accepted" and (failed or (not response["result"].get("error") and outcome in {"completed", "success", "100%completed"})):
            self.store.call_transition(campaign, submission_call_id,
                "definite_failure" if failed else "completed", {**durable_result(response["result"]),
                    "doc_id": call["result"]["doc_id"], "job_name": call["args"]["job_name"]})
        return response
