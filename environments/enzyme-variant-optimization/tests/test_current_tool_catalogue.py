"""Current catalogue controls availability; all responses here are synthetic."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from enzyme_research.paths import bundled_workflow_source
from enzyme_research.workflow import load_workflow
from test_workflow_bridge import fixture_module

JOBS = {"rfd3": "Enzyme_RFD3", "enzycontrol": "enzycontrol", "deepallo": "deepallo",
        "catalytic_geometry": "Catalytic_Geometry", "mol_probity": "Mol_Probity"}


@pytest.mark.parametrize("tool,job", JOBS.items())
def test_deployed_tool_resolves_without_manual_activation(tmp_path, tool, job):
    _, _, registry, _ = load_workflow(bundled_workflow_source())
    catalogue, _ = fixture_module().fixture_catalogue(tmp_path)
    result = registry.load_registry(catalog_root=catalogue)[tool]
    assert result["backend_status"] == "active"
    assert result["job_name"] == job and result["binding_source"] == "catalogue"
    assert result["contract_document"]["entry"] == job
    assert result["collection_name"] is None  # Submission does not need diagnostic metadata.
    assert result["live_verified"] is False  # Resolving a contract is not a worker test.


@pytest.mark.parametrize("job", JOBS.values())
def test_disabled_canonical_tool_is_not_forced_active(tmp_path, job):
    _, _, registry, _ = load_workflow(bundled_workflow_source())
    catalogue, _ = fixture_module().fixture_catalogue(tmp_path)
    path = catalogue / "tool-contracts.v1.json"
    data = json.loads(path.read_text())
    data["tools"][job]["execution_blocked"] = True
    path.write_text(json.dumps(data))
    tool = next(name for name, candidate in JOBS.items() if candidate == job)
    result = registry.load_registry(catalog_root=catalogue)[tool]
    assert result["backend_status"] == "pending" and result["job_name"] == job


def test_explicit_operator_pause_is_retained(tmp_path):
    _, _, registry, _ = load_workflow(bundled_workflow_source())
    catalogue, _ = fixture_module().fixture_catalogue(tmp_path)
    result = registry.load_registry({"enzycontrol": {"backend_status": "pending"}}, catalog_root=catalogue)
    assert result["enzycontrol"]["backend_status"] == "pending"


def test_missing_current_contract_is_reported(tmp_path):
    _, _, registry, _ = load_workflow(bundled_workflow_source())
    catalogue, _ = fixture_module().fixture_catalogue(tmp_path)
    path = catalogue / "tool-contracts.v1.json"
    data = json.loads(path.read_text())
    del data["tools"]["enzycontrol"]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="missing or has conflicting identity"):
        registry.load_registry(catalog_root=catalogue)


@pytest.mark.parametrize("tool,job,field", [("enzycontrol", "enzycontrol", "pdb_path"),
    ("deepallo", "deepallo", "input_path"), ("rfd3", "Enzyme_RFD3", "input_path")])
def test_prepare_reaches_catalogue_job_without_an_activation_gate(tmp_path, task, tool, job, field):
    # This tests routing only; the native connector owns scientific input validation.
    module = fixture_module()
    catalogue, _ = module.fixture_catalogue(tmp_path)
    harness = module.FixtureHarness(tmp_path / "state", catalogue, {})
    plan = {"objective": "Synthetic routing check", "approved": True,
            "initial_candidates": [{"candidate_id": "parent", "local_path": task["parent"]["structure"]["path"]}],
            "steps": [{"step_id": "analysis", "tool": tool, "candidate_ids": ["parent"],
                       "experiment_name": "Synthetic routing only", "inputs": {field: "fixtures/input.pdb"}}]}
    workflow = harness.start(plan)["workflow_id"]
    result = harness.next(workflow, "prepare", "analysis")
    assert result["status"] == "ready"
    assert result["call"]["args"]["job_name"] == job
