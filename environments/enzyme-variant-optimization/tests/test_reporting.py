import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from enzyme_research.contracts import ResearchError, canonical, digest
from enzyme_research.reporting import build_report, export_report, joined_structure_checks, read_report, summary
from test_coordinate_observations import pipeline
from test_observation_semantics import ready_service
from test_stability_handoff import handoff as stability_handoff, complete_matrix
from enzyme_research.stability import match_candidates


def by_id(report, cid):
    return next(row for row in report["candidate_rows"] if row["candidate_id"] == cid)


def test_empty_campaign_reports_missing_science_not_success(store, campaign):
    report = build_report(store, campaign)
    parent = by_id(report, "parent")
    assert parent["catalytic_sequence_preserved"] and parent["rank"] is None
    assert parent["evidence_counts"]["activity"] == 0
    assert "activity" in parent["missing_evidence"]
    assert report["scientific_submission_attempts"] == 0
    assert not report["live_completion_established"] and not report["experimental_improvement_established"]
    assert report["final_selection_status"] == "not_recorded"


def test_existing_property_receipt_joins_exact_candidate(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    service.next(campaign, "ingest", **args)
    report = build_report(store, campaign)
    row = by_id(report, "parent")
    assert row["evidence_counts"]["solubility"] == 1 and row["evidence_counts"]["activity"] == 0
    ref = row["evidence"]["solubility"][0]
    assert ref["context_ref"]["pointer"] == "/metrics/parent"
    assert report["scientific_submission_attempts"] == 1
    assert report["usable_observation_count"] == 1
    assert not report["unresolved_submission_call_ids"]


def test_changed_artifact_no_longer_counts_as_usable_evidence(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    result = service.next(campaign, "ingest", **args)
    initial = build_report(store, campaign)
    Path(result["observation"]["artifacts"][0]["path"]).write_text("changed after ingestion")
    report = build_report(store, campaign)
    assert report["snapshot_sha256"] != initial["snapshot_sha256"]
    assert by_id(report, "parent")["evidence_counts"]["solubility"] == 0
    assert report["reported_observation_count"] == 1 and report["usable_observation_count"] == 0
    assert not report["observation_checks"][result["observation"]["observation_id"]]["artifacts_verified_now"]


def test_pose_rejection_stays_local_and_does_not_imply_geometry_pass(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    report = build_report(service.store, campaign)
    row = by_id(report, "c1")
    assert row["evidence_counts"]["folding"] == 1 and row["evidence_counts"]["quality"] == 1
    outcomes = {sid: checks[0]["outcome"] for sid, checks in row["structure_outcomes"]["quality"].items()}
    assert len(outcomes) == 2 and set(outcomes.values()) == {"passed", "rejected"}
    assert not row["jointly_validation_passed_structure_ids"]
    assert "quality_and_geometry_on_same_coordinates" in row["missing_evidence"]
    assert row["evidence_counts"]["activity"] == 0


def test_parent_relative_stability_is_not_a_matrix_or_an_absolute_score(stability_handoff):
    service, campaign, sid, source = complete_matrix(stability_handoff)
    report = build_report(service.store, campaign)
    assert by_id(report, "parent")["stability_matrix_structure_ids"] == [sid]
    assert not by_id(report, "parent")["single_mutation_predictions"]
    assert "parent_relative_variant_stability" in by_id(report, "c1")["missing_evidence"]
    matched = match_candidates(service, campaign, source["observation_id"], "parent", sid, ["c1"])
    report = build_report(service.store, campaign)
    score = by_id(report, "c1")["single_mutation_predictions"][0]
    assert score["basis_candidate_id"] == "parent" and score["basis_structure_id"] == sid
    assert score["ddG_pred"] == -0.75
    assert "parent_relative_variant_stability" not in by_id(report, "c1")["missing_evidence"]
    assert "parent_relative_variant_stability" in by_id(report, "c2")["missing_evidence"]
    assert report["scientific_submission_attempts"] == 1 and report["usable_observation_count"] == 2


def test_retyped_unrelated_observation_cannot_cover_activity(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    result = service.next(campaign, "ingest", **args)
    observation = copy.deepcopy(result["observation"])
    observation.update(observation_id="wrong-kind", kind="activity")
    store.add_observation(campaign, observation)
    report = build_report(store, campaign)
    assert not report["observation_checks"]["wrong-kind"]["source_job_and_adapter_verified"]
    assert by_id(report, "parent")["evidence_counts"]["activity"] == 0


def test_missing_workflow_database_does_not_erase_recorded_observations(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    result = service.next(campaign, "ingest", **args)
    # Recoverable fixture relocation, not deletion of any real state.
    original = store.root / "workflow_executor/state.sqlite"
    original.rename(original.with_suffix(".saved"))
    report = build_report(store, campaign)
    assert report["reported_observation_count"] == 1 and report["usable_observation_count"] == 0
    assert report["receipt_errors"]
    assert store.status(campaign)["observations"][0] == result["observation"]


def test_polls_do_not_duplicate_submission_accounting(store, campaign):
    call = store.prepare_call(campaign, "boltzmann_submit", {"job_name": "FixtureActivity", "experiment_data": {}})
    store.call_transition(campaign, call, "sending")
    store.call_transition(campaign, call, "accepted", {"doc_id": "fixture-job"})
    for i in range(5):
        poll = store.prepare_call(campaign, "boltzmann_status", {"job_name": "FixtureActivity", "doc_id": "fixture-job"})
        store.call_transition(campaign, poll, "sending")
        store.call_transition(campaign, poll, "completed", {"status": "pending"})
    report = build_report(store, campaign)
    assert report["scientific_submission_attempts"] == 1
    assert report["unresolved_submission_call_ids"] == [call]
    assert report["execution_ledger"][0]["doc_id"] == "fixture-job"
    assert report["reasoning_and_total_resource_accounting"] == "not_established_by_this_report"


def test_native_summary_is_bounded_and_all_candidate_rows_are_readable(store, task):
    task["budget"]["max_unique_candidates"] = 60
    campaign = store.start(task, "base")
    variants = []
    for pos in (0, *range(2, 10)):
        for aa in "CDEFGHIK":
            sequence = list(task["parent"]["sequence"])
            sequence[pos] = aa
            variants.append({"candidate_id": "c" + str(len(variants)), "parent_id": "parent", "sequence": "".join(sequence)})
            if len(variants) == 60: break
        if len(variants) == 60: break
    store.add_candidates(campaign, variants)
    report = build_report(store, campaign)
    compact = summary(report)
    assert compact["candidate_count"] == 61 and len(compact["candidate_index"]) == 20
    assert not compact["candidate_index_complete"] and len(canonical(compact)) < 16384
    rows, offset = [], 0
    while True:
        page = read_report(report, offset=offset, limit=20, snapshot_sha256=report["snapshot_sha256"])
        assert len(canonical(page).encode()) <= 16384
        rows.extend(r["value"] for r in page["items"])
        if page["complete"]: break
        offset = page["next_offset"]
    assert rows == report["candidate_rows"]


def test_page_snapshot_rejects_stale_evidence(store, campaign):
    report = build_report(store, campaign)
    first = read_report(report, limit=1)
    store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    with pytest.raises(ResearchError, match="snapshot changed"):
        read_report(build_report(store, campaign), snapshot_sha256=first["snapshot_sha256"])


@pytest.mark.parametrize("query", [{"view": []}, {"view": "../other"}, {"limit": True}, {"offset": -1},
    {"record_id": "not-a-candidate"}, {"pointer": "/evidence"}])
def test_malformed_report_query_is_rejected(store, campaign, query):
    with pytest.raises(ResearchError): read_report(build_report(store, campaign), **query)


def test_operator_export_preserves_all_rows_and_refuses_overwrite(store, campaign, tmp_path):
    report = build_report(store, campaign)
    output = tmp_path / "joined-report"
    receipt = export_report(report, output)
    saved = json.loads((output / "report.json").read_bytes())
    assert saved == report and receipt["candidate_count"] == 1
    rows = list(csv.DictReader((output / "candidate_summary.csv").open()))
    assert len(rows) == 1 and rows[0]["rank"] == "" and rows[0]["candidate_id"] == "parent"
    assert rows[0]["activity_observation_count"] == "0"
    with pytest.raises(ResearchError): export_report(report, output)
    assert json.loads((output / "report.json").read_bytes()) == report


def test_changed_parent_file_cannot_supply_coordinate_checks(store, campaign):
    parent = Path(store.status(campaign)["task"]["parent"]["structure"]["path"])
    parent.write_text("altered")
    report = build_report(store, campaign)
    sid = next(iter(report["structure_checks"]))
    assert not report["structure_checks"][sid]
    assert by_id(report, "parent")["all_atom_structure_count"] == 0


def test_native_report_reads_remain_nonterminal_without_explicit_selection(store, campaign):
    from enzyme_research.service import ResearchService
    from enzyme_research.native_policy import NativeResearchPolicy
    from test_native_policy import Audit
    service = object.__new__(ResearchService)
    service.store = store
    policy = NativeResearchPolicy(service, campaign, Audit())
    read = policy.tool("enzyme_research_next", {"campaign_id": campaign, "action": "inspect_report",
                       "values": {"record_id": "parent", "pointer": "/missing_evidence"}})
    assert not read["research_step_finished"]
    assert [row["value"] for row in read["result"]["items"]][:2] == ["activity", "solubility"]
    result = policy.tool("enzyme_research_report", {"campaign_id": campaign})
    assert not result["research_step_finished"]
    assert "candidate_rows" not in result["result"] and "candidate_index" in result["result"]
    assert not policy.tool("enzyme_research_report", {"campaign_id": campaign})["research_step_finished"]
    assert policy.accepted_action is None


def check(outcome, mode="validation"):
    return {"outcome": outcome, "execution_mode": mode, "observation_id": "synthetic-check"}


def test_quality_and_geometry_passes_on_different_poses_do_not_combine():
    outcomes = {"quality": {"pose1": [check("passed")]}, "geometry": {"pose2": [check("passed")]}}
    assert joined_structure_checks(outcomes, {"pose1", "pose2"}) == (set(), set(), set())


@pytest.mark.parametrize("second", ["rejected", "invalid"])
def test_any_failure_on_same_pose_remains_visible(second):
    outcomes = {"quality": {"pose1": [check("passed"), check(second)]}, "geometry": {"pose1": [check("passed")]}}
    assert joined_structure_checks(outcomes, {"pose1"}) == ({"pose1"}, set(), set())


def test_measurement_only_is_not_validation_pass():
    outcomes = {"quality": {"pose1": [check("measured", "measurement_only")]}, "geometry": {"pose1": [check("passed")]}}
    assert joined_structure_checks(outcomes, {"pose1"}) == ({"pose1"}, {"pose1"}, set())


def test_all_atom_and_both_explicit_validation_passes_are_required():
    outcomes = {"quality": {"pose1": [check("passed")]}, "geometry": {"pose1": [check("passed")]}}
    assert joined_structure_checks(outcomes, set()) == ({"pose1"}, set(), set())
    assert joined_structure_checks(outcomes, {"pose1"}) == ({"pose1"}, {"pose1"}, {"pose1"})
