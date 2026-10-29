import copy

import pytest

from synthesis_route_gym.benchmark_curation import prepare_tasks, load_seen_doyle


def routes():
    return [{"record_id": f"r{i}", "source_keys": [f"p{i}"], "reaction_keys": [f"rxn{i}"],
             "target": target, "route_fingerprint": f"fp{i}", "stock": ["C", "O"],
             "step_count": 1, "has_stereo": False, "convergent": False,
             "reference_route": {"target": target}, "source_locator": f"private#/{i}"}
            for i, target in enumerate(["CC", "CN", "CO", "CF"])]


def condition(identity, target="CCCl", source="paper:new", outcome=20):
    return {"record_id": identity, "target": target, "reactants": ["C", "Cl"],
            "conditions": {"solvent": "O"}, "outcome_yield_percent": outcome,
            "source_family": source, "source_locator": f"private/{identity}"}


def test_preparation_is_outcome_blind_and_keeps_variants_together():
    fresh = [condition("c1"), {**condition("c2"), "conditions": {"solvent": "CO"}}]
    old = [condition("old", "CCBr", "paper:old")]
    before = copy.deepcopy(fresh)
    args = dict(stock=["C", "O", "N", "Cl"], quotas={"smoke": 1, "development": 1, "sealed_final": 1}, seed="fixed")
    first = prepare_tasks(routes(), condition_records=fresh, doyle_records=old, **args)
    changed = [{**r, "outcome_yield_percent": 100-r["outcome_yield_percent"]} for r in fresh]
    second = prepare_tasks(routes(), condition_records=changed, doyle_records=old, **args)
    assert first["tasks"] == second["tasks"]
    assert first["assignments"] == second["assignments"]
    assert first["labels"] != second["labels"]
    assert fresh == before
    assert len(first["tasks"]) == 8  # 3 base + 3 stock variants + 2 condition tasks.
    assert first["report"]["route_targets"] == 3
    for part in ("smoke", "development", "sealed_final"):
        tasks = [t for t in first["tasks"] if t["track"] == "reference_route" and t["partition"] == part]
        assert len(tasks) == 2 and len({t["target"] for t in tasks}) == 1
        assert sum(bool(t["inventory_exclusions"]) for t in tasks) == 1
    assert all("source_locator" not in t and "outcome" not in str(t) for t in first["tasks"])


def test_cross_track_related_routes_excluded_before_selection():
    fresh = [condition("c1", "CC")]
    result = prepare_tasks(routes(), ["C", "O"], fresh, [], quotas={"smoke": 1, "development": 1, "sealed_final": 1}, seed="v1")
    assert "CC" not in {t["target"] for t in result["tasks"] if t["track"] == "reference_route"}
    assert result["report"]["cross_track_excluded_records"] == 1


def test_seen_and_fresh_connected_chemistry_cannot_be_split():
    with pytest.raises(ValueError, match="cross-partition"):
        prepare_tasks(routes(), ["C", "O"], [condition("new")],
                      [condition("old", source="paper:old")], quotas={"smoke": 1}, seed="v1")


def test_duplicate_condition_inputs_cannot_be_optimised_by_replicate_id():
    with pytest.raises(ValueError, match="replicate"):
        prepare_tasks(routes(), ["C", "O"], [condition("one"), condition("two", outcome=90)], [],
                      quotas={"smoke": 1}, seed="v1")


def test_missing_stock_and_bad_length_exclude_reference_group():
    rows = routes()
    rows[0] = {**rows[0], "stock": ["Br"]}
    rows[1] = {**rows[1], "step_count": 100}
    result = prepare_tasks(rows, ["C", "O"], [], [], quotas={"smoke": 1}, seed="v1")
    assert result["report"]["reference_eligibility_excluded_records"] == 2
    assert result["tasks"][0]["target"] in {"CO", "CF"}


def test_seen_doyle_loader_keeps_all_records_in_development(tmp_path):
    path = tmp_path / "doyle.csv"
    path.write_text('aryl halide,ligand,additive,base,rxn,yield\nCBr,N,O,O,CBr.N>>CN,42\n')
    rows = load_seen_doyle(path)
    assert rows[0]["source_family"] == "doi:10.1126/science.aar5169"
    assert rows[0]["outcome_yield_percent"] == 42
    path.write_text('aryl halide,ligand,additive,base,rxn,yield\nCBr,N,O,O,CBr.N>>CN,nan\n')
    with pytest.raises(ValueError):
        load_seen_doyle(path)


def test_available_training_overlap_is_excluded_before_selection():
    result = prepare_tasks(routes(), ["C", "O"], [], [],
                           quotas={"smoke": 1, "development": 1, "sealed_final": 1},
                           seed="v1", training_overlap_record_ids={"r0"})
    assert all(t["target"] != "CC" for t in result["tasks"])
    assert result["report"]["available_training_overlap_excluded_records"] == 1
