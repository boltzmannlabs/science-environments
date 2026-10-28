import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "reference_constraint_audit", Path(__file__).parents[1] / "scripts/audit_reference_constraints.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def record(identifier="private-record", product="CC=O", reactant="CCO"):
    return {"record_id": identifier, "reference_route": {
        "route_id": identifier, "target": product,
        "steps": [{"step_id": "step-0", "product": product,
                   "reactants": [{"smiles": reactant}], "source_tool": "fixture", "source_version": "1"}]}}


def test_unknown_conditions_and_stoichiometry_do_not_become_hard_failure():
    public, private = audit.audit_records([record()], ["CCO"])
    assert public["deterministically_accepted_records"] == 1
    assert public["quantity_status_records"] == {"not_requested": 1}
    assert public["unknown_finding_records"]["conditions_incomplete"] == 1
    assert private["ineligible_record_ids"] == []
    assert public["scientific_feasibility_established"] is False


def test_missing_element_and_missing_common_stock_are_hard_failures():
    rows = [record("private-a", product="CCN"), record("private-b", reactant="CO")]
    public, private = audit.audit_records(rows, ["CCO"])
    assert public["deterministically_accepted_records"] == 0
    assert public["hard_finding_records"]["missing_element_source"] == 1
    assert public["hard_finding_records"]["material_unavailable"] == 1
    assert private["ineligible_record_ids"] == ["private-a", "private-b"]
    assert "private-a" not in str(public)
    assert "CCN" not in str(public)


def test_step_limit_uses_actual_environment_rule():
    public, private = audit.audit_records([record()], ["CCO"], max_steps=0)
    assert public["hard_finding_records"] == {"step_limit": 1}
    assert private["ineligible_record_ids"] == ["private-record"]


def test_duplicate_record_identifiers_fail_closed():
    with pytest.raises(ValueError, match="Duplicate"):
        audit.audit_records([record(), record()], ["CCO"])
