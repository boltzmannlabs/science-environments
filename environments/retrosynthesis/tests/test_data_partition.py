import copy

import pytest

from synthesis_route_gym.data_partition import leakage_components, select_grouped_records, audit_assignments


def record(identity, target, source, **extra):
    return {"record_id": identity, "target": target, "source_keys": [source],
            "reaction_keys": [], "route_fingerprint": identity, **extra}


def records():
    return [record("a", "CCO", "s1"), record("b", "CCN", "s2"),
            record("c", "CCC", "s3"), record("d", "CCCl", "s4")]


def test_source_reaction_and_target_links_are_transitive_and_immutable():
    rows = [record("a", "CCO", "s1", reaction_keys=["reaction"]),
            record("b", "CCN", "s2", reaction_keys=["reaction"]),
            record("c", "CCC", "s2"), record("d", "OCC", "s4")]
    before = copy.deepcopy(rows)
    result = leakage_components(rows)
    assert len(result["groups"]) == 1
    assert set(result["groups"][0]["record_ids"]) == {"a", "b", "c", "d"}
    assert rows == before
    assert {edge["kind"] for edge in result["links"]} >= {"source", "reaction", "target"}


def test_scaffolds_group_analogues_without_combining_all_acyclic_molecules():
    rows = [record("a", "Cc1ccccc1", "s1"), record("b", "Oc1ccccc1", "s2"),
            record("c", "CCO", "s3"), record("d", "CCN", "s4")]
    groups = leakage_components(rows)["groups"]
    assert sorted(len(g["record_ids"]) for g in groups) == [1, 1, 2]


def test_stereo_and_atom_mapping_do_not_split_related_targets():
    rows = [record("a", "C[C@H](O)F", "s1"), record("b", "C[C@@H](O)F", "s2"),
            record("c", "[CH3:1][CH:2]([OH:3])[F:4]", "s3")]
    assert len(leakage_components(rows)["groups"]) == 1


def test_unknown_source_groups_conservatively():
    rows = [record("a", "CCO", "s1"), record("b", "CCN", "s2")]
    rows = [{**r, "source_keys": [], "source_id": "unknown_source"} for r in rows]
    assert len(leakage_components(rows)["groups"]) == 1


def test_cross_track_target_and_produced_intermediate_share_coarse_namespace():
    rows = [record("route", "CCC", "patent", molecule_keys=["CCC", "C[C@H](O)F"]),
            record("condition", "C[C@@H](O)F", "publication")]
    assert len(leakage_components(rows)["groups"]) == 1
    with pytest.raises(ValueError, match="cross-partition"):
        audit_assignments(rows, [{"record_id": "route", "partition": "development"},
                                 {"record_id": "condition", "partition": "sealed_final"}])


def test_selection_is_deterministic_input_order_invariant_and_group_disjoint():
    rows = records()
    quotas = {"smoke": 1, "development": 1, "sealed_final": 1}
    one = select_grouped_records(rows, quotas, seed="v1")
    two = select_grouped_records(reversed(rows), quotas, seed="v1")
    assert one == two
    assert len(one["selected"]) == 3
    assert len({r["group_id"] for r in one["selected"]}) == 3
    assert audit_assignments(rows, one["assignments"])["cross_partition_groups"] == 0


def test_related_variant_and_duplicate_stay_in_same_partition():
    rows = records() + [record("a2", "OCC", "s99", route_fingerprint="a")]
    result = select_grouped_records(rows, {"smoke": 1, "development": 1, "sealed_final": 1}, seed="v1")
    assignment = {r["record_id"]: r for r in result["assignments"]}
    assert assignment["a"]["partition"] == assignment["a2"]["partition"]
    assert sum(r["record_id"] in {"a", "a2"} for r in result["selected"]) <= 1


def test_cross_partition_transitive_leakage_rejected():
    rows = [record("a", "CCO", "s1"), record("b", "CCN", "s1", reaction_keys=["x"]),
            record("c", "CCC", "s3", reaction_keys=["x"])]
    assignments = [{"record_id": "a", "partition": "development"},
                   {"record_id": "b", "partition": "unused"},
                   {"record_id": "c", "partition": "sealed_final"}]
    with pytest.raises(ValueError, match="cross-partition"):
        audit_assignments(rows, assignments)


def test_exclusions_remove_entire_connected_component():
    rows = records() + [record("a2", "CCBr", "s1")]
    result = select_grouped_records(rows, {"smoke": 1, "development": 1, "sealed_final": 1}, seed="v1", excluded_record_ids={"a2"})
    assert all(r["record_id"] not in {"a", "a2"} for r in result["selected"])
    assert result["audit"]["excluded_groups"] == 1


@pytest.mark.parametrize("change", ["duplicate_id", "invalid_target", "missing_id", "string_sources", "empty_key"])
def test_malformed_records_rejected(change):
    rows = records()
    if change == "duplicate_id":
        rows.append(rows[0])
    elif change == "invalid_target":
        rows[0] = {**rows[0], "target": "invalid"}
    elif change == "missing_id":
        rows[0] = {**rows[0], "record_id": ""}
    elif change == "string_sources":
        rows[0] = {**rows[0], "source_keys": "s1"}
    else:
        rows[0] = {**rows[0], "reaction_keys": [""]}
    with pytest.raises(ValueError):
        leakage_components(rows)


def test_insufficient_independent_groups_and_bad_quotas_fail():
    with pytest.raises(ValueError, match="groups"):
        select_grouped_records(records(), {"smoke": 10}, seed="v1")
    for quotas in ({"other": 1}, {"smoke": -1}, {"smoke": True}, {}):
        with pytest.raises(ValueError):
            select_grouped_records(records(), quotas, seed="v1")


def test_audit_rejects_missing_duplicate_unknown_and_bad_partition_assignments():
    assignments = [{"record_id": r["record_id"], "partition": "smoke"} for r in records()]
    invalid = [assignments[:-1], assignments + [assignments[0]],
               assignments + [{"record_id": "unknown", "partition": "smoke"}],
               [{**r, "partition": "invalid"} for r in assignments]]
    for rows in invalid:
        with pytest.raises(ValueError):
            audit_assignments(records(), rows)
