import json
from pathlib import Path
import pytest

from enzyme_research.plugin import register, SCHEMAS
from enzyme_research.contracts import ResearchError
from enzyme_research.service import ResearchService


class Context:
    def __init__(self): self.tools, self.skills = {}, {}
    def register_tool(self, **kw): self.tools[kw["name"]] = kw
    def register_skill(self, name, path, **kw): self.skills[name] = path
    def get_config(self, name, default=None): return default


def test_additive_tool_registration_and_auth_gate():
    ctx = Context()
    register(ctx, check_fn=lambda: False)
    assert len(ctx.tools) == 4
    assert not ctx.skills
    for tool in ctx.tools.values():
        assert tool["toolset"] == "enzyme_research"
        result = json.loads(tool["handler"]({}))
        assert result["authorization_required"]
        assert result["scientific_jobs_submitted"] == 0


def test_authorized_skill_registered_without_starting_a_job():
    ctx = Context()
    register(ctx, check_fn=lambda: True)
    assert ctx.skills["enzyme-research"].is_file()
    assert all("parameters" in s and "input_schema" not in s for s in SCHEMAS)


def test_service_does_not_invent_missing_runtime():
    with pytest.raises(ResearchError): ResearchService({})
