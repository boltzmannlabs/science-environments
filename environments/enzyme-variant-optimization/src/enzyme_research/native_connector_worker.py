"""Subprocess entrypoint importing the unmodified, authorized native connector.

No credentials are supplied in stdin. Connector output URLs remain transient.
Library diagnostic stdout/stderr is withheld: it can contain private data.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys


def redact_diagnostic(value, safe_detail, credential):
    """Never export credential fields or raw diagnostic exception/log bodies."""
    secret = {"tokenid", "token", "api_key", "apikey", "access_token", "authorization", "password", "secret",
              "download_url", "download_link", "signed_url"}
    if isinstance(value, dict):
        return {key: redact_diagnostic(item, safe_detail, credential) for key, item in value.items() if key.lower() not in secret}
    if isinstance(value, list):
        return [redact_diagnostic(item, safe_detail, credential) for item in value]
    if isinstance(value, str):
        return safe_detail(value, credential)
    return value


def main():
    raw = sys.stdin.read(2 * 1024**2 + 1)
    if len(raw) > 2 * 1024**2:
        raise ValueError("Oversized native request")
    request = json.loads(raw)
    runtime = request["runtime"]
    sys.path.insert(0, runtime["native_source"])
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from plugins.boltzmann.auth import available
        from plugins.boltzmann import tools
        name = request["operation"]
        handlers = {"boltzmann_upload": tools.handle_boltzmann_upload,
                    "boltzmann_submit": tools.handle_boltzmann_submit,
                    "boltzmann_status": tools.handle_boltzmann_status,
                    "boltzmann_download": tools.handle_boltzmann_download,
                    "boltzmann_fetch_tool_log": tools.handle_boltzmann_fetch_tool_log}
        if name == "connector_availability":
            response = {"locally_authorized": available(), "service_checked": False,
                        "credentials_returned": False, "scientific_jobs_submitted": 0}
        elif name == "connector_service_check":
            from plugins.boltzmann.auth import require_authorized
            require_authorized()
            response = {"locally_authorized": True, "service_checked": True, "service_authorization_succeeded": True,
                        "credentials_returned": False, "scientific_jobs_submitted": 0}
        elif name in {"connector_validate_upload", "connector_validate_submission"}:
            from plugins.boltzmann.contracts import ContractStore
            from plugins.boltzmann.file_validation import validate_file
            from plugins.boltzmann.preflight import preflight_submission
            args = request["args"]
            if name == "connector_validate_upload":
                rule = ContractStore().file_rule(args["job_name"], args["input_field"])
                response = validate_file(Path(args["local_path"]), rule, args.get("experiment_data") or {}).as_dict()
            else:
                response = preflight_submission(args["job_name"], args["experiment_data"]).as_dict()
        elif name == "catalogue_capabilities":
            path = Path(runtime["native_source"]) / "plugins/boltzmann/skills/boltzmann-tools/references/tool-contracts.v1.json"
            import hashlib
            source = path.read_bytes()
            document = json.loads(source)
            requested = request["args"].get("job_names", [])
            response = {"catalogue_sha256": hashlib.sha256(source).hexdigest(), "tools": {}}
            for job in requested:
                entry = document.get("tools", {}).get(job)
                response["tools"][job] = {"documented": bool(entry),
                    "catalogue_active": bool(entry and entry.get("status") == "active" and not entry.get("execution_blocked")),
                    "live_verified": False,
                    "request_schema": entry.get("request_schema") if entry else None}
        elif name in handlers:
            response = handlers[name](**request["args"])
            if isinstance(response, str):
                response = json.loads(response)
            if name == "boltzmann_fetch_tool_log":
                from plugins.boltzmann.results import safe_detail
                from plugins.boltzmann.auth import current_key
                response = redact_diagnostic(response, safe_detail, current_key())
        else:
            raise ValueError("Unknown native operation")
    sys.stdout.write(json.dumps(response, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # No raw exception/provider text; a caller cannot infer acceptance.
        sys.stdout.write(json.dumps({"error": "Native connector operation failed", "error_type": type(exc).__name__, "safe_to_retry": False}))
