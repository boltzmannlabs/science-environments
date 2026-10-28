import pytest
from synthesis_route_gym.benchmark import check_split, evaluate_episode, review_queue, route_fingerprint
from synthesis_route_gym.environment import SynthesisRouteEnv
from test_core import make_task, make_route


def episode():
    env = SynthesisRouteEnv(make_task())
    env.dispatch("propose_route", {"route": make_route().model_dump(mode="json")})
    env.dispatch("submit", {"route_ids": ["r1"]})
    return env.export()


def test_pending_reviews_never_count_as_feasible_routes():
    result = evaluate_episode(episode(), reviews=[])
    assert result["inventory_complete_top1"]
    assert result["feasible_top1"] is None
    assert result["feasible_at_k"] is None
    assert result["review_coverage"] == 0


def test_llm_review_is_not_independent_chemical_review():
    review = {"route_fingerprint": route_fingerprint(make_route().model_dump(mode="json")),
              "verdict": "accepted", "reviewer_kind": "llm", "reviewer": "critic",
              "independent": True, "source_locators": ["paper:example1"]}
    with pytest.raises(ValueError, match="human"):
        evaluate_episode(episode(), [review])


def test_review_queue_blinds_method_and_binds_chemical_content():
    value = episode()
    queue = review_queue([{"method": "main", "episode": value}, {"method": "specialists", "episode": value}])
    assert len(queue) == 1
    assert "method" not in queue[0]
    review = {"route_fingerprint": queue[0]["route_fingerprint"], "verdict": "accepted",
              "reviewer_kind": "human", "reviewer": "test-reviewer", "independent": True,
              "source_locators": ["https://example.org/paper#example1"]}
    assert evaluate_episode(value, [review])["feasible_at_k"]
    review["route_fingerprint"] = "wrong"
    assert evaluate_episode(value, [review])["feasible_at_k"] is None


def test_group_and_product_leakage_are_rejected():
    train = [{"target": "CCO", "source_family": "patent-family-1"}]
    with pytest.raises(ValueError):
        check_split(train, [{"target": "OCC", "source_family": "different"}])
    with pytest.raises(ValueError):
        check_split(train, [{"target": "CCN", "source_family": "patent-family-1"}])
    assert check_split(train, [{"target": "CCN", "source_family": "different"}])["disjoint"]
def test_review_fingerprint_serializes_frozen_condition_inputs():
    from test_core import make_route
    route = make_route().model_dump(mode="json")
    route["steps"][0]["condition_inputs"] = {"base": "N"}
    assert len(route_fingerprint(route)) == 64


def test_unresolved_source_review_counts_as_reviewed_but_not_as_resolved():
    value = episode()
    review = {"route_fingerprint": route_fingerprint(value["routes"][0]), "verdict": "unresolved",
              "reviewer_kind": "automated_source_audit", "reviewer": "isolated-evidence-audit",
              "independent": True, "source_locators": []}
    result = evaluate_episode(value, [review])
    assert result["review_coverage"] == 1
    assert result["resolved_outcome_coverage"] == 0
    assert result["feasible_top1"] is None

