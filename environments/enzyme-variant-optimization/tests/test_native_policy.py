import json
from pathlib import Path
import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.native_policy import NativeResearchPolicy


class Audit:
    def __init__(self): self.events = []
    def record(self, kind, **data): self.events.append((kind, data))


class Service:
    def __init__(self, store): self.store, self.actions = store, []
    def status(self, campaign): return self.store.status(campaign)
    def next(self, campaign, action, **values):
        self.actions.append(action)
        return {"status": "observed"}
    def report(self, campaign): return {"campaign_id": campaign, "scientific_complete": False}


def policy(store, campaign):
    return NativeResearchPolicy(Service(store), campaign, Audit())


def test_research_tools_not_frozen_predictor_interface(store, campaign):
    p = policy(store, campaign)
    assert p.names == {"enzyme_research_start", "enzyme_research_next", "enzyme_research_status", "enzyme_research_report"}
    assert "benchmark_score" not in p.names


def test_native_step_closes_after_accepted_action(store, campaign):
    p = policy(store, campaign)
    result = p.tool("enzyme_research_next", {"campaign_id": campaign, "action": "complete_decision", "values": {}})
    assert result["research_step_finished"]
    with pytest.raises(ResearchError): p.tool("enzyme_research_status", {"campaign_id": campaign})


@pytest.mark.parametrize("name,args", [("terminal", {}), ("enzyme_research_status", {"campaign_id": "other"}),
    ("enzyme_research_next", {"action": "read_file", "campaign_id": "other"})])
def test_denied_native_operations(store, campaign, name, args):
    p = policy(store, campaign)
    with pytest.raises(ResearchError): p.tool(name, args)
    assert not p.service.actions


def test_arbitrary_local_file_blocked_before_service(store, campaign):
    p = policy(store, campaign)
    with pytest.raises(ResearchError):
        p.tool("enzyme_research_next", {"campaign_id": campaign, "action": "ingest", "values": {"local_path": "/etc/passwd"}})
    assert not p.service.actions


def test_download_directory_cannot_escape(store, campaign, tmp_path):
    p = policy(store, campaign)
    with pytest.raises(ResearchError):
        p.tool("enzyme_research_next", {"campaign_id": campaign, "action": "download", "values": {"output_folder": str(tmp_path)}})


def test_operator_campaign_cannot_be_replaced(store, campaign):
    p = policy(store, campaign)
    with pytest.raises(ResearchError): p.tool("enzyme_research_start", {"task": {}, "arm": "base"})


def test_coordinator_cannot_supply_specialist_critique(store, campaign):
    p = policy(store, campaign)
    assert "investigate" in p.allowed_actions
    assert "propose" not in p.allowed_actions
    with pytest.raises(ResearchError, match="unapproved research action"):
        p.tool("enzyme_research_next", {"campaign_id": campaign, "action": "propose",
                                      "values": {"proposals": [], "critiques": {}}})
    assert not p.service.actions


def test_explicit_allowlist_cannot_reenable_manual_native_critique(store, campaign):
    with pytest.raises(ResearchError, match="dedicated proposer/critic"):
        NativeResearchPolicy(Service(store), campaign, Audit(), allowed_actions={"propose"})


def test_denial_audit_has_diagnostic_fingerprint_not_raw_exception(store, campaign):
    from enzyme_research.contracts import digest
    p = policy(store, campaign)
    with pytest.raises(ResearchError):
        p.tool("enzyme_research_status", {"campaign_id": "other"})
    event, data = p.audit.events[-1]
    assert event == "research_tool_denied"
    assert data["error_message_sha256"] == digest("Research operation refers to another campaign")
    assert "message" not in data and "error" not in data
