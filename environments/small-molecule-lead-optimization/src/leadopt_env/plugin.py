"""Agent-Scientist adapter; scientific execution remains with the host tools."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3


OPERATIONS = (
    "create", "status", "report", "candidate", "observation", "check", "action",
    "usage", "decision", "freeze", "attach", "detach", "describe",
)

SCHEMA = {
    "name": "leadopt_campaign",
    "description": (
        "Create, inspect and record an advisory lead-optimization campaign. "
        "Load leadopt_env:lead-optimization first. Use check before a costly action, "
        "then choose whether to continue using existing scientific tools. This tool "
        "does not submit jobs, enforce task budgets, or call models. Use describe "
        "to read the environment record contracts without creating campaign state."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": list(OPERATIONS)},
            "campaign_id": {"type": "string"},
            "payload": {"type": "object", "additionalProperties": True},
        },
        "required": ["operation"],
        "additionalProperties": False,
    },
}


def register(ctx):
    """Register local records and instructions without changing host state."""
    def handle(args, session_id=None, **_kwargs):
        def error(message, error_type="record_validation"):
            return json.dumps({"error": message, "error_type": error_type,
                               "host_session_id": session_id, "scientific_jobs_submitted": 0})

        if args.get("operation") == "describe":
            from .contracts import SCHEMAS
            return json.dumps({"schema_version": 1, "record_schemas": SCHEMAS,
                               "host_session_id": session_id}, allow_nan=False)
        db_path = ctx.get_config("db_path")
        if not isinstance(db_path, str) or not Path(db_path).is_absolute():
            return error("Set this plugin's db_path to an absolute local campaign database path.")
        operation = args.get("operation")
        if operation not in OPERATIONS:
            return error("Unknown campaign operation.")
        if not isinstance(args.get("campaign_id"), str) or not args["campaign_id"].strip():
            return error("Supply an explicit campaign_id.")
        payload = args.get("payload", {})
        if not isinstance(payload, dict):
            return error("payload must be an object.")
        payload = dict(payload)
        if operation in {"attach", "detach"} and "session_id" not in payload:
            if not session_id:
                return error("No host session identity is available; supply an explicit session_id.")
            payload["session_id"] = session_id
        try:
            from .core import CampaignStore
            store = CampaignStore(db_path)
            if session_id and operation not in {"create", "status", "report", "attach", "detach"}:
                bound_campaign = store.campaign_for_session(session_id)
                if bound_campaign is not None and bound_campaign != args["campaign_id"]:
                    return error("Host session is attached to another campaign. Detach and attach explicitly "
                                 "before recording mutations under a different campaign.", "session_campaign_mismatch")
            result = store.dispatch(operation, args.get("campaign_id"), payload)
        except (ValueError, KeyError) as exc:
            return error(str(exc))
        except (OSError, sqlite3.Error) as exc:
            return error(f"Local campaign storage failed ({type(exc).__name__}). Inspect the configured "
                         "database before continuing; no operation was retried.", "storage_error")
        return json.dumps({**result, "host_session_id": session_id}, allow_nan=False)

    ctx.register_tool(
        name="leadopt_campaign", toolset="leadopt_env", schema=SCHEMA,
        handler=handle, description=SCHEMA["description"],
    )
    ctx.register_skill(
        "lead-optimization", Path(__file__).parent / "skills/lead-optimization/SKILL.md",
        description="Investigate supplied leads with recorded advice, evidence and comparisons.",
    )
    ctx.register_system_prompt_section(
        "leadopt.environment",
        "For a small-molecule lead-optimization campaign, load "
        "skill_view(name='leadopt_env:lead-optimization'). Use leadopt_campaign "
        "to check planned costly actions and keep evidence records. Advice is "
        "warning-only; the agent chooses its next action through existing tools.",
        max_chars=1000,
    )
