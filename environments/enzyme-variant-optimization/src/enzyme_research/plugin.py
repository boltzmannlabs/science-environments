"""Additive native plugin entry point; no original Agent-Scientist edits."""
import json
from pathlib import Path

from .contracts import ResearchError
from .connector import durable_result


SCHEMAS = [
    {"name": "enzyme_research_start", "description": "Start a reviewed enzyme optimization task; does not submit a scientific job.",
     "parameters": {"type": "object", "properties": {"task": {"type": "object", "properties": {}, "required": []}, "arm": {"type": "string", "enum": ["fixed", "base", "specialist"]}}, "required": ["task", "arm"], "additionalProperties": False}},
    {"name": "enzyme_research_next", "description": "Advance a persisted enzyme research campaign through hypothesis, existing workflow execution and verified observations. Load the enzyme-research skill first. For action investigate, omit values or supply {}; task context and dedicated proposer/critic roles are supplied by the host, not by manual hypothesis arguments.",
     "parameters": {"type": "object", "properties": {"campaign_id": {"type": "string"}, "action": {"type": "string"}, "values": {"type": "object", "properties": {}, "required": []}}, "required": ["campaign_id", "action"], "additionalProperties": False}},
    {"name": "enzyme_research_status", "description": "Read the campaign, hypotheses, scientific jobs and verified observations.",
     "parameters": {"type": "object", "properties": {"campaign_id": {"type": "string"}}, "required": ["campaign_id"], "additionalProperties": False}},
    {"name": "enzyme_research_report", "description": "Report computational candidate evidence and incomplete gates without asserting experimental improvement.",
     "parameters": {"type": "object", "properties": {"campaign_id": {"type": "string"}}, "required": ["campaign_id"], "additionalProperties": False}},
]


def register(ctx, check_fn=None):
    if check_fn is None:
        from plugins.boltzmann.auth import available
        check_fn = available

    def dispatch(name, args):
        if not check_fn():
            return json.dumps({"authorization_required": True, "scientific_jobs_submitted": 0})
        try:
            from .service import ResearchService
            service = ResearchService(ctx.get_config("research_runtime", {}))
            method = name.removeprefix("enzyme_research_")
            if method == "next":
                result = service.next(args["campaign_id"], args["action"], **args.get("values", {}))
            else:
                result = getattr(service, method)(**args)
            # Signed URLs stay with the host executor, never in durable reports.
            return json.dumps(durable_result(result), allow_nan=False)
        except Exception as exc:
            message = str(exc) if isinstance(exc, ResearchError) else "Research operation failed; inspect the tracked step before retrying"
            return json.dumps({"error": message, "completion_confirmed": False})

    for schema in SCHEMAS:
        name = schema["name"]
        ctx.register_tool(name=name, toolset="enzyme_research", schema=schema,
            handler=lambda args, _name=name, **kw: dispatch(_name, args), check_fn=check_fn,
            description=schema["description"])
    if check_fn():
        ctx.register_skill("enzyme-research", Path(__file__).parent / "skills/enzyme-research/SKILL.md",
                           description="Optimize enzymes through adaptive scientific tool use and recorded feedback.")
