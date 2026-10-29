"""Public task projection, private labels and committed-decision evaluation."""
import hashlib
import json
import pytest
from synthesis_route_gym.dataset_bundle import (
    build_bundle, commit_decision, load_public_task, score_decision, verify_bundle,
)


def condition_task(partition="development"):
    return {"task_id": "conditions-01", "track": "measured_conditions", "partition": partition,
            "target": "CCO", "candidates": [
                {"candidate_id": "c1", "reactants": ["CCBr"], "conditions": {"base": "N"}},
                {"candidate_id": "c2", "reactants": ["CCBr"], "conditions": {"base": "CN"}}]}


def provenance():
    return {"sources": [{"source_id": "fixture", "url": "https://example.org/data.csv",
                         "sha256": "1" * 64, "license": "CC0-1.0"}],
            "baseline_protocol_sha256": "2" * 64}


def build(tmp_path, *, tasks=None, labels=None):
    tasks = [condition_task()] if tasks is None else tasks
    labels = [{"task_id": tasks[0]["task_id"], "outcomes": {"c1": 12.0, "c2": 85.0},
               "source_locator": "private-row-7"}] if labels is None else labels
    return build_bundle(tmp_path / "public", tmp_path / "private", tasks=tasks, labels=labels,
                        provenance=provenance(), inventory=["CCBr", "N", "CN", "O"],
                        assignments=[{"task_id": t["task_id"], "group_id": "private-group"} for t in tasks])


def test_condition_decision_commit_then_private_evaluation_end_to_end(tmp_path):
    report = build(tmp_path)
    public = load_public_task(tmp_path / "public", "conditions-01")
    assert public["candidates"][0]["candidate_id"] == "c1"
    assert "outcomes" not in json.dumps(public) and "private-row" not in json.dumps(report)
    decision = tmp_path / "decision.json"
    digest = commit_decision(decision, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    assert digest == hashlib.sha256(decision.read_bytes()).hexdigest()
    scored = score_decision(tmp_path / "public", tmp_path / "private", decision, digest)
    assert scored["selected_measured_yield_percent"] == 12.0
    assert scored["simple_regret_percent"] == 73.0
    assert scored["scope"] == "retrospective_reference_comparison_not_new_experimental_validation"
    assert verify_bundle(tmp_path / "public", tmp_path / "private")["verified"] is True


@pytest.mark.parametrize("task_id", ["../private/labels", "/tmp/escape", "..", "x/y", "x\\y"])
def test_malformed_ids_rejected_before_writes(tmp_path, task_id):
    with pytest.raises(ValueError):
        build(tmp_path, tasks=[{**condition_task(), "task_id": task_id}])
    assert not (tmp_path / "public").exists()


@pytest.mark.parametrize("inject", [
    lambda t: {**t, "source_locator": "hidden"},
    lambda t: {**t, "outcomes": {"c1": 12}},
    lambda t: {**t, "candidates": [{**t["candidates"][0], "yield": 12}]},
    lambda t: {**t, "candidates": [{**t["candidates"][0], "conditions": {"outcomes": "CCO"}}]},
])
def test_accidental_nested_labels_are_rejected(tmp_path, inject):
    with pytest.raises(ValueError):
        build(tmp_path, tasks=[inject(condition_task())])
    assert not (tmp_path / "public").exists()


def test_write_once_private_permissions_and_no_public_label_files(tmp_path):
    build(tmp_path)
    assert (tmp_path / "private").stat().st_mode & 0o777 == 0o700
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in (tmp_path / "private").rglob("*") if p.is_file())
    public_bytes = b"".join(p.read_bytes() for p in (tmp_path / "public").rglob("*") if p.is_file())
    assert b'"outcomes"' not in public_bytes and b'private-row-7' not in public_bytes
    with pytest.raises(ValueError):
        build(tmp_path)
    decision = tmp_path / "decision.json"
    commit_decision(decision, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError):
        commit_decision(decision, {"task_id": "conditions-01", "selected_candidate_id": "c2"})


@pytest.mark.parametrize("mutation", ["missing", "extra", "tamper"])
def test_public_integrity_detects_missing_extra_and_tampered_files(tmp_path, mutation):
    build(tmp_path)
    target = tmp_path / "public" / "tasks" / "conditions-01.json"
    if mutation == "missing":
        target.unlink()
    elif mutation == "extra":
        (tmp_path / "public" / "accidental-labels.json").write_text('{"outcome":99}')
    else:
        target.write_text(target.read_text() + " ")
    with pytest.raises(ValueError):
        verify_bundle(tmp_path / "public")
    with pytest.raises(ValueError):
        load_public_task(tmp_path / "public", "conditions-01")


def test_symlink_and_traversal_access_fail_closed(tmp_path):
    build(tmp_path)
    for task_id in ("../private/manifest", "missing"):
        with pytest.raises(ValueError):
            load_public_task(tmp_path / "public", task_id)
    target = tmp_path / "public" / "tasks" / "conditions-01.json"
    target.unlink()
    target.symlink_to(tmp_path / "private" / "labels" / "conditions-01.json")
    with pytest.raises(ValueError):
        load_public_task(tmp_path / "public", "conditions-01")


def test_wrong_decision_hash_is_checked_before_private_label_access(tmp_path):
    build(tmp_path)
    path = tmp_path / "decision.json"
    commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError, match="[Dd]ecision.*hash"):
        score_decision(tmp_path / "public", tmp_path / "private-does-not-exist", path, "0" * 64)


def test_unknown_condition_candidate_cannot_be_scored(tmp_path):
    build(tmp_path)
    path = tmp_path / "decision.json"
    sha = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "unknown"})
    with pytest.raises(ValueError, match="candidate"):
        score_decision(tmp_path / "public", tmp_path / "private", path, sha)


def test_sealed_final_partition_is_blocked_even_with_correct_commitment(tmp_path):
    build(tmp_path, tasks=[condition_task("sealed_final")])
    path = tmp_path / "decision.json"
    sha = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError, match="sealed_final"):
        score_decision(tmp_path / "public", tmp_path / "private", path, sha)


def test_private_integrity_is_verified_before_evaluation(tmp_path):
    build(tmp_path)
    label = tmp_path / "private" / "labels" / "conditions-01.json"
    label.write_text(label.read_text().replace("85.0", "99.0"))
    path = tmp_path / "decision.json"
    sha = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError):
        score_decision(tmp_path / "public", tmp_path / "private", path, sha)


def test_nested_public_private_directories_and_url_credentials_rejected(tmp_path):
    args = dict(tasks=[condition_task()], labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12, "c2": 85}}],
                provenance=provenance(), inventory=["CCBr"], assignments=[])
    with pytest.raises(ValueError):
        build_bundle(tmp_path / "public", tmp_path / "public" / "private", **args)
    args["provenance"]["sources"][0]["url"] = "https://user:secret@example.org/data"
    with pytest.raises(ValueError):
        build_bundle(tmp_path / "public", tmp_path / "private", **args)


def reference_route(product="CCO", reactant="CCBr"):
    return {"route_id": "ref", "target": product, "steps": [{"step_id": "s1", "product": product,
            "reactants": [{"smiles": reactant}, {"smiles": "O"}], "source_tool": "private-reference", "source_version": "1"}]}


def test_reference_tasks_materialize_shared_inventory_without_source_or_evidence(tmp_path):
    reference = reference_route()
    t = {"task_id": "reference-01", "track": "reference_route", "partition": "smoke", "target": "OCC"}
    build(tmp_path, tasks=[t], labels=[{"task_id": "reference-01", "reference_route": reference}])
    public = load_public_task(tmp_path / "public", "reference-01")
    assert public["target"] == "CCO" and public["evidence"] == []
    assert {item["smiles"] for item in public["inventory"]} == {"CCBr", "N", "CN", "O"}
    assert all(item["available_mmol"] is None and item["source"] is None for item in public["inventory"])
    path = tmp_path / "decision.json"
    sha = commit_decision(path, {"task_id": "reference-01", "routes": [reference]})
    score = score_decision(tmp_path / "public", tmp_path / "private", path, sha)
    assert score["reference_match_at_k"] and score["reference_match_top1"]


def test_hidden_labels_cannot_change_public_observations(tmp_path):
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir(); right.mkdir()
    common_task = {"task_id": "ref", "track": "reference_route", "partition": "development", "target": "CCO"}
    common = [condition_task(), common_task]
    for root, outcome, reactant in ((left, 1, "CCBr"), (right, 99, "CCCl")):
        labels = [{"task_id": "conditions-01", "outcomes": {"c1": outcome, "c2": 85}, "source_locator": f"SECRET_CANARY_{outcome}"},
                  {"task_id": "ref", "reference_route": reference_route(reactant=reactant), "private_canary": "SECRET_CANARY_ROUTE"}]
        build(root, tasks=common, labels=labels)
    for task_id in ("conditions-01", "ref"):
        a, b = load_public_task(left / "public", task_id), load_public_task(right / "public", task_id)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        assert "SECRET_CANARY" not in json.dumps(a)
    files = [p.relative_to(left / "public") for p in (left / "public").rglob("*") if p.is_file()]
    assert all((left / "public" / p).read_bytes() == (right / "public" / p).read_bytes() for p in files)


def test_public_inventory_exclusions_are_checked_and_applied(tmp_path):
    t = {"task_id": "ref", "track": "reference_route", "partition": "smoke", "target": "CCO", "inventory_exclusions": ["N"]}
    build(tmp_path, tasks=[t], labels=[{"task_id": "ref", "reference_route": reference_route()}])
    observed = load_public_task(tmp_path / "public", "ref")
    assert {item["smiles"] for item in observed["inventory"]} == {"CCBr", "CN", "O"}


def test_incomplete_labels_and_duplicate_candidates_are_rejected(tmp_path):
    with pytest.raises(ValueError):
        build(tmp_path, labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12}}])
    task = condition_task()
    task["candidates"] = [task["candidates"][0], task["candidates"][0]]
    with pytest.raises(ValueError):
        build(tmp_path, tasks=[task])
    with pytest.raises(ValueError):
        build(tmp_path, labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12, "c2": float("nan")}}])
    assert not (tmp_path / "public").exists()


def test_failed_write_cleans_only_new_bundle_directories(tmp_path, monkeypatch):
    import synthesis_route_gym.dataset_bundle as module
    original = module._write
    marker = tmp_path / "existing.txt"
    marker.write_text("preserve")
    def fail_private(path, data, private=False):
        if private:
            raise OSError("injected local write failure")
        return original(path, data, private)
    monkeypatch.setattr(module, "_write", fail_private)
    with pytest.raises(OSError):
        build(tmp_path)
    assert not (tmp_path / "public").exists() and not (tmp_path / "private").exists()
    assert marker.read_text() == "preserve"


def test_manifest_hash_anchor_and_forbidden_paths(tmp_path):
    report = build(tmp_path)
    assert verify_bundle(tmp_path / "public", expected_manifest_sha256=report["public_manifest_sha256"])["verified"]
    with pytest.raises(ValueError, match="manifest hash"):
        verify_bundle(tmp_path / "public", expected_manifest_sha256="0" * 64)
    manifest = tmp_path / "public" / "manifest.json"
    value = json.loads(manifest.read_text())
    value["files"]["../private/labels/conditions-01.json"] = "0" * 64
    manifest.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        verify_bundle(tmp_path / "public")


def test_unknown_public_provenance_fields_cannot_carry_secrets(tmp_path):
    args = dict(tasks=[condition_task()], labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12, "c2": 85}}],
                provenance={**provenance(), "api_token": "SECRET_CANARY"}, inventory=[], assignments=[])
    with pytest.raises(ValueError):
        build_bundle(tmp_path / "public", tmp_path / "private", **args)
    assert not (tmp_path / "public").exists()


def test_decision_payloads_are_strict_and_commitment_detects_modification(tmp_path):
    build(tmp_path)
    path = tmp_path / "decision.json"
    for decision in ({"task_id": "conditions-01", "selected_candidate_id": "c1", "outcome": 99},
                     {"task_id": "conditions-01"}, {"task_id": "conditions-01", "routes": {}},
                     {"task_id": "conditions-01", "routes": [], "selected_candidate_id": "c1"}):
        with pytest.raises(ValueError):
            commit_decision(path, decision)
    digest = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    path.write_text(path.read_text().replace("c1", "c2"))
    with pytest.raises(ValueError, match="Decision hash"):
        score_decision(tmp_path / "public", tmp_path / "private", path, digest)


def test_final_refusal_does_not_require_access_to_private_directory(tmp_path):
    build(tmp_path, tasks=[condition_task("sealed_final")])
    path = tmp_path / "decision.json"
    digest = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError, match="sealed_final"):
        score_decision(tmp_path / "public", tmp_path / "missing-private", path, digest)


def test_private_permissions_and_public_private_pairing_are_checked(tmp_path):
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir(); right.mkdir()
    build(left)
    build(right, tasks=[condition_task("smoke")])
    with pytest.raises(ValueError, match="different public bundle"):
        verify_bundle(left / "public", right / "private")
    file = left / "private" / "assignments.json"
    file.chmod(0o644)
    with pytest.raises(ValueError, match="permissions"):
        verify_bundle(left / "public", left / "private")


def test_inventory_exclusions_cannot_add_or_duplicate_molecules(tmp_path):
    for exclusions in (["CCCl"], ["N", "N"]):
        with pytest.raises(ValueError):
            build(tmp_path, tasks=[{**condition_task(), "inventory_exclusions": exclusions}])


def test_condition_source_specific_roles_are_supported(tmp_path):
    task = condition_task()
    task["candidates"] = [{**row, "conditions": {"catalyst": "[Pd]", "reagent_1": "N", "solvent_1": "O"}} for row in task["candidates"]]
    build(tmp_path, tasks=[task])
    observed = load_public_task(tmp_path / "public", "conditions-01")
    assert observed["candidates"][0]["conditions"]["solvent_1"] == "O"


def score_reference_fixture(tmp_path, routes, *, top_k=1, exclusions=(), constraints=None):
    t = {"task_id": "ref", "track": "reference_route", "partition": "development", "target": "CCO",
         "inventory_exclusions": list(exclusions), "budget": {"top_k": top_k}}
    if constraints is not None:
        t["constraints"] = constraints
    report = build(tmp_path, tasks=[t], labels=[{"task_id": "ref", "reference_route": reference_route(),
                                               "reference_inventory_closed": "CCBr" not in exclusions}])
    path = tmp_path / "decision.json"
    digest = commit_decision(path, {"task_id": "ref", "routes": routes})
    return score_decision(tmp_path / "public", tmp_path / "private", path, digest,
                          expected_manifest_sha256=report["public_manifest_sha256"])


def test_reference_recovery_is_limited_to_public_top_k(tmp_path):
    wrong = {**reference_route(reactant="CCCl"), "route_id": "wrong"}
    result = score_reference_fixture(tmp_path, [wrong, reference_route()], top_k=1)
    assert result["evaluated_unique_routes"] == 1
    assert result["reference_recovery"] == {"top1": False, "at_k": False}


def test_duplicate_cores_do_not_consume_multiple_top_k_slots(tmp_path):
    wrong = {**reference_route(reactant="CCCl"), "route_id": "wrong1"}
    duplicate = {**wrong, "route_id": "wrong2", "steps": [
        {**wrong["steps"][0], "proposal_score": 0.99, "conditions": ["different conditions"], "source_tool": "other"}]}
    result = score_reference_fixture(tmp_path, [wrong, duplicate, reference_route()], top_k=2)
    assert result["evaluated_unique_routes"] == 2 and result["duplicate_routes_ignored"] == 1
    assert result["reference_recovery"] == {"top1": False, "at_k": True}


def test_reference_core_match_ignores_proposal_metadata_conditions_and_atom_maps(tmp_path):
    route = reference_route()
    route["steps"] = [{**route["steps"][0], "product": "[CH3:1][CH2:2][OH:3]",
                       "conditions": ["agent-selected alternative"], "predicted_yield": 0.9}]
    result = score_reference_fixture(tmp_path, [route])
    assert result["reference_recovery"]["top1"]
    assert result["inventory_compliant_reference_recovery"]["top1"]


def test_reference_recovery_does_not_claim_inventory_compliance_for_missing_stock(tmp_path):
    result = score_reference_fixture(tmp_path, [reference_route()], exclusions=("CCBr",))
    assert result["reference_recovery"]["at_k"]
    assert not result["inventory_compliant_reference_recovery"]["at_k"]
    assert result["reference_inventory_closed"] is False
    assert result["route_checks"][0]["unstocked"] == ["CCBr"]
    assert result["independent_chemical_review"] == "not_performed"


def test_forbidden_reactants_fail_qualified_recovery(tmp_path):
    result = score_reference_fixture(tmp_path, [reference_route()], constraints={"forbidden_smiles": ["CCBr"]})
    assert result["reference_recovery"]["at_k"]
    assert not result["inventory_compliant_reference_recovery"]["at_k"]
    assert not result["route_checks"][0]["constraint_compliant"]


def test_wrong_target_route_is_retained_as_invalid_and_cannot_match(tmp_path):
    wrong = reference_route(product="CCN", reactant="CCBr")
    result = score_reference_fixture(tmp_path, [wrong])
    assert not result["reference_recovery"]["at_k"]
    assert not result["route_checks"][0]["graph_valid"]


def test_trusted_manifest_anchor_rejects_rewritten_partition_even_with_rehashed_files(tmp_path):
    report = build(tmp_path, tasks=[condition_task("sealed_final")])
    task_path = tmp_path / "public" / "tasks" / "conditions-01.json"
    task_path.write_text(task_path.read_text().replace("sealed_final", "development"))
    manifest_path = tmp_path / "public" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["tasks"][0]["partition"] = "development"
    manifest["files"]["tasks/conditions-01.json"] = hashlib.sha256(task_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    path = tmp_path / "decision.json"
    digest = commit_decision(path, {"task_id": "conditions-01", "selected_candidate_id": "c1"})
    with pytest.raises(ValueError, match="manifest hash"):
        load_public_task(tmp_path / "public", "conditions-01", expected_manifest_sha256=report["public_manifest_sha256"])
    with pytest.raises(ValueError, match="manifest hash"):
        score_decision(tmp_path / "public", tmp_path / "missing-private", path, digest,
                       expected_manifest_sha256=report["public_manifest_sha256"])


def test_unique_reference_cores_preserve_stereochemistry(tmp_path):
    reference = reference_route(product="C[C@H](O)F", reactant="CC(=O)F")
    other = {**reference_route(product="C[C@@H](O)F", reactant="CC(=O)F"), "route_id": "opposite"}
    task = {"task_id": "stereo", "track": "reference_route", "partition": "smoke",
            "target": reference["target"], "budget": {"top_k": 2}}
    report = build(tmp_path, tasks=[task], labels=[{"task_id": "stereo", "reference_route": reference}])
    path = tmp_path / "decision.json"
    digest = commit_decision(path, {"task_id": "stereo", "routes": [other, reference]})
    result = score_decision(tmp_path / "public", tmp_path / "private", path, digest,
                            expected_manifest_sha256=report["public_manifest_sha256"])
    assert result["evaluated_unique_routes"] == 2 and result["duplicate_routes_ignored"] == 0
    assert result["reference_recovery"] == {"top1": False, "at_k": True}


def test_quantity_free_tasks_do_not_claim_quantitative_sufficiency(tmp_path):
    route = reference_route()
    route["steps"] = [{**route["steps"][0], "reactants": [{"smiles": "CCBr", "amount_mmol": 1}, {"smiles": "O"}]}]
    result = score_reference_fixture(tmp_path, [route])
    assert result["reference_recovery"]["at_k"]
    assert result["route_checks"][0]["quantity_status"] == "not_requested"
    assert "no quantitative sufficiency claim" in result["inventory_scope"]


def test_private_manifest_anchor_detects_labels_and_manifest_rewrite(tmp_path):
    report = build(tmp_path)
    private_hash = report["private_manifest_sha256"]
    label_path = tmp_path / "private" / "labels" / "conditions-01.json"
    label_path.write_text(label_path.read_text().replace("85.0", "99.0"))
    manifest_path = tmp_path / "private" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"]["labels/conditions-01.json"] = hashlib.sha256(label_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="manifest hash"):
        verify_bundle(tmp_path / "public", tmp_path / "private",
                      expected_manifest_sha256=report["public_manifest_sha256"],
                      expected_private_manifest_sha256=private_hash)
    decision = tmp_path / "decision.json"
    digest = commit_decision(decision, {"task_id": "conditions-01", "selected_candidate_id": "c2"})
    with pytest.raises(ValueError, match="manifest hash"):
        score_decision(tmp_path / "public", tmp_path / "private", decision, digest,
                       expected_manifest_sha256=report["public_manifest_sha256"],
                       expected_private_manifest_sha256=private_hash)


def test_private_anchor_and_mixed_record_task_assignments(tmp_path):
    assignments = [{"record_id": "source-01", "group_id": "g1", "partition": "development", "selected": True,
                    "link_audit": {"linked_records": ["source-01"]}},
                   {"task_id": "conditions-01", "group_id": "g1"}]
    report = build_bundle(tmp_path / "public", tmp_path / "private", tasks=[condition_task()],
                          labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12, "c2": 85}}],
                          provenance=provenance(), inventory=["CCBr"], assignments=assignments)
    assert verify_bundle(tmp_path / "public", tmp_path / "private",
                         expected_private_manifest_sha256=report["private_manifest_sha256"])["verified"]
    with pytest.raises(ValueError, match="private"):
        verify_bundle(tmp_path / "public", expected_private_manifest_sha256=report["private_manifest_sha256"])
    assert json.loads((tmp_path / "private" / "assignments.json").read_text()) == assignments


@pytest.mark.parametrize("assignment", [{}, {"record_id": ""}, {"record_id": 3}, {"task_id": "unknown", "record_id": "r"}])
def test_assignment_rows_require_valid_record_or_known_task_identity(tmp_path, assignment):
    with pytest.raises(ValueError):
        build_bundle(tmp_path / "public", tmp_path / "private", tasks=[condition_task()],
                     labels=[{"task_id": "conditions-01", "outcomes": {"c1": 12, "c2": 85}}],
                     provenance=provenance(), inventory=[], assignments=[assignment])
