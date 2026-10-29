import copy

import pytest

from enzyme_research.context import PAGE_BYTES, collections, compact_context, read_context
from enzyme_research.contracts import ResearchError, canonical, digest


def large_state(store, task):
    campaign = store.start(task, "base")
    state = store.status(campaign)
    state["candidates"] = [{"candidate_id": f"c{i}", "parent_id": "parent", "sequence": "A" * 2000,
                             "sequence_sha256": "a" * 64, "structure_status": "requires_new_structure"}
                            for i in range(61)]
    state["observations"] = [{"observation_id": f"o{i}", "kind": "activity", "candidate_ids": [f"c{j}" for j in range(61)],
                               "evidence_level": "synthetic_fixture", "source_call_id": f"call{i}",
                               "metrics": {f"c{j}": {"prediction": j / 10, "raw_details": "x" * 1000} for j in range(61)}}
                              for i in range(60)]
    state["calls"] = [{"call_id": f"call{i}", "tool": "boltzmann_status", "status": "completed",
                       "args": {}, "result": {"verbose_output": "x" * 5000}} for i in range(200)]
    return state


def test_full_sized_state_has_small_explicitly_paged_model_index(store, task):
    state = large_state(store, task)
    contracts = {"FixtureActivity": {"request_schema": {"properties": {"sequences": {"type": "array"}}}}}
    context = compact_context(state, contracts)
    assert len(canonical(context).encode()) < 65536
    assert len(context["candidates"]) == len(context["observations"]) == len(context["calls"]) == 20
    views = context["context_access"]["views"]
    assert views["candidates"]["count"] == 61 and not views["candidates"]["index_complete"]
    assert views["observations"]["count"] == 60 and views["calls"]["count"] == 200
    assert "raw_details" not in canonical(context)
    # Full sequence and metrics have not disappeared: explicit identity-based reads.
    sequence = read_context(state, contracts, view="candidates", record_id="c60", pointer="/sequence")
    assert sequence["items"][0]["value"] == "A" * 2000
    metrics = read_context(state, contracts, view="observations", record_id="o59", pointer="/metrics/c60")
    assert metrics["items"][0]["value"]["prediction"] == 6


def test_pages_reconstruct_every_record_with_snapshot_and_hashes(store, task):
    state = large_state(store, task)
    offset, rows, snapshot = 0, [], None
    while True:
        page = read_context(state, {}, view="candidates", offset=offset, limit=20, snapshot_sha256=snapshot)
        assert len(canonical(page).encode()) <= PAGE_BYTES
        assert all(digest(r["value"]) == r["value_sha256"] for r in page["items"])
        snapshot = page["snapshot_sha256"]
        rows.extend({"record_id": r["record_id"], "value": r["value"]} for r in page["items"])
        if page["complete"]:
            assert page["next_offset"] is None
            break
        assert page["next_offset"] > offset
        offset = page["next_offset"]
    assert rows == collections(state, {})["candidates"]
    assert digest(rows) == snapshot


def test_changed_page_snapshot_is_not_silently_combined(store, task):
    state = large_state(store, task)
    page = read_context(state, {}, view="candidates", limit=1)
    state["candidates"][0]["sequence"] = "C" * 2000
    with pytest.raises(ResearchError, match="snapshot changed"):
        read_context(state, {}, view="candidates", offset=1, snapshot_sha256=page["snapshot_sha256"])


def test_library_members_are_paged_without_assay_answers(store, task):
    state = large_state(store, task)
    members = [{"member_id": f"v{i}", "sequence": "A" * 1000} for i in range(1000)]
    state["task"]["candidate_library"] = {"library_id": "synthetic_contract_only", "members": members,
                                           "members_sha256": digest(members)}
    context = compact_context(state, {})
    library = context["task"]["candidate_library"]
    assert "members" not in library and library["member_count"] == 1000
    page = read_context(state, {}, **library["members_context_ref"], offset=995, limit=10)
    assert [r["value"] for r in page["items"]] == members[995:]
    assert page["complete"]


@pytest.mark.parametrize("query", [{"view": "../private"}, {"view": "calls", "limit": True},
    {"view": "calls", "limit": 21}, {"view": "calls", "offset": -1}, {"view": "calls", "offset": 201},
    {"view": "calls", "record_id": "other"}, {"view": "calls", "pointer": "/args"},
    {"view": "calls", "record_id": "call0", "pointer": "/absent"},
    {"view": "calls", "record_id": "call0", "pointer": "/args~2"}])
def test_invalid_lookup_is_rejected_cleanly(store, task, query):
    with pytest.raises(ResearchError): read_context(large_state(store, task), {}, **query)


def test_large_record_requires_explicit_field_not_truncation(store, task):
    state = large_state(store, task)
    with pytest.raises(ResearchError, match="select a smaller field"):
        read_context(state, {}, view="observations", record_id="o0")


def test_pointer_escape_targets_data_only(store, task):
    state = large_state(store, task)
    state["calls"][0]["result"] = {"a/b": {"~key": 7}}
    page = read_context(state, {}, view="calls", record_id="call0", pointer="/result/a~1b/~0key")
    assert page["items"][0]["value"] == 7


def test_actual_upload_identity_and_declined_review_survive_context_restart(store, task):
    state = store.status(store.start(task, "specialist"))
    receipt = {"input_id": "prepared", "job_name": "Netsolp", "input_field": "input_path",
               "candidate_ids": ["parent"], "storage_path": "users/fixture/parent.csv",
               "experiment_data": {"prediction_type": "S"}}
    review = {"review_id": "review-1", "status": "hypothesis_review_declined", "proposed_round": 1,
              "approved_for_execution": False, "critiques": {"h1": {"decision": "revise", "critique": "Missing actual input"}}}
    state["events"].extend([{"payload": {"event": event, "data": data}} for event, data in
                            [("input_uploaded", receipt), ("hypothesis_review_declined", review)]])
    indexed = compact_context(state, {})
    assert indexed["confirmed_uploads"][0]["job_name"] == "Netsolp"
    assert indexed["confirmed_uploads"][0]["experiment_data"] == {"prediction_type": "S"}
    assert indexed["hypothesis_reviews"][0]["approved_for_execution"] is False
    detail = read_context(state, {}, view="hypothesis_reviews", record_id="review-1", pointer="/critiques/h1")
    assert detail["items"][0]["value"]["critique"] == "Missing actual input"
    assert not state["observations"] and not state["decisions"]
