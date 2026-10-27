"""Local interface regressions; no model or scientific endpoint is contacted."""
import copy
import json
from types import SimpleNamespace

import pytest

from enzyme_research.context import compact_context
from enzyme_research.native_policy import NativeResearchPolicy
from enzyme_research.service import ResearchService


class Audit:
    def __init__(self):
        self.events = []

    def record(self, kind, **data):
        self.events.append((kind, data))


def test_native_schema_exposes_action_specific_values_identically_to_both_arms(store, task):
    states = [store.status(store.start(task, arm)) for arm in ("base", "specialist")]
    contexts = [compact_context(state, {}) for state in states]
    assert "operation_contracts" in contexts[0]
    assert contexts[0]["operation_contracts"] == contexts[1]["operation_contracts"]
    operations = contexts[0]["operation_contracts"]
    assert operations["submit"]["values_schema"]["required"] == ["workflow_id", "step_id"]
    assert operations["submit"]["values_schema"]["additionalProperties"] is False
    assert operations["investigate"]["values_schema"]["properties"] == {}
    assert "specialist" in operations["investigate"]["requirements"]
    service = SimpleNamespace(store=store)
    policy = NativeResearchPolicy(service, states[0]["campaign_id"], Audit())
    schema = next(tool for tool in policy.tools if tool["name"] == "enzyme_research_next")
    branches = schema['parameters']['properties']['values']['anyOf']
    advertised = {branch['description'].split(': ', 1)[0]: branch for branch in branches}
    assert set(advertised) == policy.allowed_actions
    for action, entry in operations.items():
        assert advertised[action]['required'] == entry['values_schema']['required']
        assert set(advertised[action]['properties']) == set(entry['values_schema']['properties'])
        assert advertised[action]['additionalProperties'] is False
        assert entry['requirements'] in advertised[action]['description']
    step = advertised["plan_segment"]["properties"]["specification"]["properties"]["steps"]["items"]
    assert {"step_id", "tool", "candidate_ids", "experiment_name", "inputs"} <= set(step["required"])
    assert "approved" in advertised["plan_segment"]["properties"]["specification"]["required"]
    # Caller mutations cannot change the next arm's contract.
    contexts[0]["operation_contracts"]["submit"]["values_schema"]["required"].clear()
    assert compact_context(states[1], {})["operation_contracts"]["submit"]["values_schema"]["required"] == ["workflow_id", "step_id"]


@pytest.mark.parametrize("action,values,path", [
    ("submit", {}, "/values/workflow_id"),
    ("submit", {"workflow_id": "workflow"}, "/values/step_id"),
    ("prepare_input", {"job_name": "FixtureActivity"}, "/values/candidate_ids"),
    ("plan_segment", {"specification": {"objective": "Fixture", "approved": True, "steps": [{}]}}, "/values/specification/steps/0/step_id"),
])
def test_missing_field_diagnostics_survive_service_and_host_audit(store, campaign, tmp_path, action, values, path):
    from enzyme_research.contracts import ResearchError
    catalogue = tmp_path / "tool-contracts.v1.json"
    catalogue.write_text('{"tools": {}}')
    service = object.__new__(ResearchService)
    service.store = store
    service.settings = {"catalogue_root": str(tmp_path)}
    service.workflow = SimpleNamespace(submit=lambda *args: pytest.fail("Malformed operation reached submission"),
                                       harness=SimpleNamespace(registry={}))
    audit = Audit()
    policy = NativeResearchPolicy(service, campaign, audit)
    with pytest.raises(ResearchError) as caught:
        policy.tool("enzyme_research_next", {"campaign_id": campaign, "action": action, "values": values})
    assert str(caught.value) == f"{action}: missing required field at {path}"
    event, data = audit.events[-1]
    assert event == "research_tool_denied"
    assert data["action"] == action
    assert data["argument_keys"] == ["action", "campaign_id", "values"]
    assert data["value_keys"] == sorted(values)
    assert data["diagnostic"] == {"action": action, "code": "missing_required_field", "path": path}
    assert policy.accepted_action is None and store.status(campaign)["calls"] == []


@pytest.mark.parametrize("name,action", [
    ("enzyme_research_status", None), ("enzyme_research_report", None),
    ("enzyme_research_next", "inspect"), ("enzyme_research_next", "inspect_report"),
    ("enzyme_research_next", "logs"), ("enzyme_research_next", "poll"),
])
def test_read_only_operations_never_close_or_claim_research_progress(store, campaign, name, action):
    service = SimpleNamespace(store=store, report=lambda campaign: {"scientific_complete": False},
                              next=lambda *args, **kwargs: {"status": "read"})
    policy = NativeResearchPolicy(service, campaign, Audit())
    policy.context = lambda: {"campaign_id": campaign}
    args = {"campaign_id": campaign}
    if action is not None:
        args.update(action=action, values={})
    result = policy.tool(name, args)
    assert result["research_step_finished"] is False
    assert policy.accepted_action is None
    # A subsequent valid operation is still possible in the same native step.
    assert policy.tool("enzyme_research_next", {"campaign_id": campaign, "action": "prepare_input", "values": {}})["research_step_finished"]


def test_native_and_dedicated_roles_receive_exact_allowed_workflow_tool_bindings(store, campaign, tmp_path):
    (tmp_path / "tool-contracts.v1.json").write_text('{"tools": {"FixtureActivity": {"job_name": "FixtureActivity"}}}')
    service = object.__new__(ResearchService)
    service.store = store
    service.settings = {"catalogue_root": str(tmp_path)}
    registry = {"actual-workflow-id": {"job_name": "FixtureActivity", "stage": "properties", "adapter": "report", "requires": ["sequence"]},
                "outside-task": {"job_name": "not-permitted", "stage": "folding"}}
    service.workflow = SimpleNamespace(harness=SimpleNamespace(registry=registry))
    native = NativeResearchPolicy(service, campaign, Audit()).context()
    roles = service.model_context(store.status(campaign))
    assert native["workflow_tools"] == roles["workflow_tools"] == {"actual-workflow-id": registry["actual-workflow-id"]}
    assert native["operation_contracts"] == roles["operation_contracts"]


@pytest.mark.parametrize("args,path", [({"action": "inspect"}, "/campaign_id"), ({"campaign_id": "placeholder"}, "/action")])
def test_missing_operation_envelope_fields_have_exact_safe_paths(store, campaign, args, path):
    from enzyme_research.contracts import ResearchError
    args = {key: campaign if key == "campaign_id" else value for key, value in args.items()}
    audit = Audit()
    policy = NativeResearchPolicy(SimpleNamespace(store=store), campaign, audit)
    with pytest.raises(ResearchError) as caught:
        policy.tool("enzyme_research_next", args)
    assert str(caught.value) == f"enzyme_research_next: missing required field at {path}"
    assert audit.events[-1][1]["diagnostic"]["path"] == path


@pytest.mark.parametrize("action,values,nullable", [
    ("ingest", {"workflow_id": "w", "step_id": "s", "submission_call_id": "call", "local_path": "fixture.csv", "bindings": None, "member": None, "kind": None}, "bindings"),
    ("prepare_input", {"job_name": "FixtureActivity", "candidate_ids": ["parent"], "structure_ids": None}, "structure_ids"),
    ("upload_input", {"input_id": "prepared", "experiment_data": None}, "experiment_data"),
])
def test_optional_internal_none_preserves_automatic_handoffs(action, values, nullable):
    from enzyme_research.context import operation_contracts, validate_action_values
    validate_action_values(action, values)
    assert "null" in operation_contracts()[action]["values_schema"]["properties"][nullable]["type"]


def test_service_next_remains_callable_for_existing_unbound_adapters(store, campaign, monkeypatch):
    import enzyme_research.results as results
    monkeypatch.setattr(results, "sync_metrics", lambda *args: {"automatic_kind": args[-1]})
    service = SimpleNamespace(store=store)
    assert ResearchService.next(service, campaign, "sync_metrics", workflow_id="w", step_id="s",
                                submission_call_id="call", kind=None) == {"automatic_kind": None}
