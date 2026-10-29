import copy

import pytest

from enzyme_research.contracts import ResearchError, candidate_record, digest, task_contract


def measured_task(task):
    task = copy.deepcopy(task)
    task["evidence_track"] = "protected_measured_library"
    members = [{"member_id": "reference", "sequence": task["parent"]["sequence"]},
               {"member_id": "measured_variant", "sequence": "AGCAAAAAAA"}]
    task["candidate_library"] = {"library_id": "synthetic_library_contract_test",
                                 "members": members, "members_sha256": digest(members)}
    return task


def test_protected_track_without_library_fails(task):
    task["evidence_track"] = "protected_measured_library"
    with pytest.raises(ResearchError, match="frozen public candidate library"):
        task_contract(task)


def test_tool_row_alias_maps_to_frozen_public_member(task, store):
    task = measured_task(task)
    campaign = store.start(task, "base")
    records = store.add_candidates(campaign, [{"candidate_id": "tool_row_42", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    record = records[0]
    assert record["library_member_id"] == "measured_variant"
    assert record["library_members_sha256"] == task["candidate_library"]["members_sha256"]
    assert store.status(campaign)["candidates"][0]["library_member_id"] == "reference"


def test_new_unmeasured_design_rejected_before_registration(task, store):
    campaign = store.start(measured_task(task), "specialist")
    with pytest.raises(ResearchError, match="Novel sequences"):
        store.add_candidates(campaign, [{"candidate_id": "new_design", "parent_id": "parent", "sequence": "AGDAAAAAAA"}])
    assert len(store.status(campaign)["candidates"]) == 1


@pytest.mark.parametrize("change", ["hash", "duplicate_id", "duplicate_sequence", "missing_parent", "catalytic_change", "nonstandard", "assay_value", "length"])
def test_bad_library_rejected(task, change):
    task = measured_task(task)
    library = task["candidate_library"]
    if change == "hash": library["members_sha256"] = "0" * 64
    elif change == "duplicate_id": library["members"][1]["member_id"] = "reference"
    elif change == "duplicate_sequence": library["members"][1]["sequence"] = task["parent"]["sequence"]
    elif change == "missing_parent": library["members"] = library["members"][1:]
    elif change == "catalytic_change": library["members"][1]["sequence"] = "AACAAAAAAA"
    elif change == "nonstandard": library["members"][1]["sequence"] = "AGXAAAAAAA"
    elif change == "assay_value": library["members"][1]["measured_kcat"] = 100
    elif change == "length": library["members"][1]["sequence"] = "AGCAAAAAA"
    if change != "hash": library["members_sha256"] = digest(library["members"])
    with pytest.raises(ResearchError): task_contract(task)


def test_computational_track_does_not_accept_measured_library(task):
    task = measured_task(task)
    task["evidence_track"] = "computational"
    with pytest.raises(ResearchError, match="only to the protected-library track"):
        task_contract(task)


def test_computational_design_still_allows_novel_substitution(task):
    task["evidence_track"] = "computational"
    record = candidate_record(task, {"candidate_id": "new_design", "parent_id": "parent", "sequence": "AGDAAAAAAA"})
    assert "library_member_id" not in record
