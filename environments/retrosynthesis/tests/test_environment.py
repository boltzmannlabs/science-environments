import json
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Budget
from test_core import make_task, make_route


def test_propose_validate_submit_trace_and_input_immutability():
    task = make_task()
    env = SynthesisRouteEnv(task, seed=7)
    initial = env.inspect()
    route = make_route().model_dump(mode="json")
    assert env.dispatch("propose_route", {"route": route})["status"] == "ok"
    route["target"] = "CC"
    result = env.dispatch("validate", {"route_id": "r1"})
    assert result["result"]["graph_valid"]
    assert env.dispatch("submit", {"route_ids": ["r1"]})["terminated"]
    assert len(env.export()["events"]) == 3
    assert initial["routes"] == []
    assert not env.export()["assessments"][0]["solved"]
    assert env.dispatch("propose_route", {"route": route})["status"] == "closed"


def test_invalid_actions_consume_budget_and_reset_cannot_change_task():
    env = SynthesisRouteEnv(make_task(budget=Budget(max_actions=2)))
    assert env.dispatch("reset", {"task": {"target": "CC"}})["status"] == "error"
    assert env.dispatch("nonsense", {})["truncated"]
    assert env.export()["usage"]["actions"] == 2
    assert env.task.target == make_task().target


def test_tool_failure_consumes_expansion_and_no_zero_yield_is_returned():
    def fail(smiles, top_k):
        raise RuntimeError("do not leak private diagnostic")
    env = SynthesisRouteEnv(make_task(budget=Budget(max_expansions=1)), expand=fail)
    result = env.dispatch("expand", {"smiles": "CCOC(C)=O", "top_k": 5})
    assert result["status"] == "error"
    assert result["usage"]["expansions"] == 1
    assert "private diagnostic" not in json.dumps(result)
    assert env.dispatch("expand", {"smiles": "CCO"})["status"] == "budget_exhausted"


def test_wall_deadline_stops_admission_and_late_results_are_discarded():
    now = [0.0]
    def slow(smiles, top_k):
        now[0] = 11.0
        return {"status": "ok", "predictions": []}
    env = SynthesisRouteEnv(make_task(budget=Budget(max_wall_seconds=10)), expand=slow, clock=lambda: now[0])
    result = env.dispatch("expand", {"smiles": "CCO"})
    assert result["status"] == "budget_exhausted" and result["truncated"]


def test_proposals_cannot_modify_evidence_and_incomplete_routes_can_be_reported():
    env = SynthesisRouteEnv(make_task(inventory=()))
    payload = make_route().model_dump(mode="json")
    payload["verified"] = True
    assert env.dispatch("propose_route", {"route": payload})["status"] == "error"
    env.dispatch("propose_route", {"route": make_route().model_dump(mode="json")})
    result = env.dispatch("submit", {"route_ids": ["r1"]})
    assert result["status"] == "ok"
    assert result["result"]["accepted_route_ids"] == []
    assert result["result"]["submitted_route_ids"] == ["r1"]


def test_revision_requires_new_id_and_valid_parent():
    env = SynthesisRouteEnv(make_task())
    route = make_route().model_dump(mode="json")
    assert env.dispatch("propose_route", {"route": route})["status"] == "ok"
    assert env.dispatch("propose_route", {"route": route})["status"] == "error"
    revised = {**route, "route_id": "r2", "parent_route_id": "missing"}
    assert env.dispatch("propose_route", {"route": revised})["status"] == "error"


def test_invalid_target_route_and_nonfinite_action_do_not_poison_export():
    env = SynthesisRouteEnv(make_task(target_amount_mmol=1))
    route = make_route().model_dump(mode="json")
    route["steps"][0]["product"] = "CCO"
    result = env.dispatch("propose_route", {"route": route})
    assert result["status"] == "ok"
    assert not result["result"]["assessment"]["graph_valid"]
    assert env.dispatch("invalid", {"bad": float("nan")})["status"] == "error"
    assert len(env.export()["events"]) == 2


def test_late_submission_does_not_enter_final_shortlist():
    now = [0.0]
    env = SynthesisRouteEnv(make_task(budget=Budget(max_wall_seconds=1)), clock=lambda: now[0])
    env.dispatch("propose_route", {"route": make_route().model_dump(mode="json")})
    original = env._submit
    def late(args):
        result = original(args)
        now[0] = 2.0
        return result
    env._submit = late
    assert env.dispatch("submit", {"route_ids": ["r1"]})["status"] == "budget_exhausted"
    assert env.export()["submitted_route_ids"] == []


def test_scientific_condition_tool_and_route_ranker_are_host_bound():
    class Model:
        metadata = {"model_version": "unit-test-model"}
        def predict(self, rows):
            return [{"predicted_yield_percent": 30, "evidence_status": "predicted"} for row in rows]
    env = SynthesisRouteEnv(make_task(), condition_ranker=Model())
    candidate = {"id": "c1", "aryl halide": "Clc1ccccc1", "ligand": "P", "additive": "O", "base": "N"}
    result = env.dispatch("predict_conditions", {"candidates": [candidate]})
    assert result["result"]["predictions"][0]["id"] == "c1"
    assert result["result"]["predictions"][0]["evidence_status"] == "predicted"
    route = make_route().model_dump(mode="json")
    route["steps"][0]["predicted_yield"] = 0.99
    env.dispatch("propose_route", {"route": route})
    ranks = env.dispatch("rank_routes", {"route_ids": ["r1"]})["result"]["ranking"]
    assert ranks[0]["bottleneck_predicted_yield"] is None
    assert env.dispatch("predict_conditions", {"candidates": [{**candidate,"yield":99}]})["status"] == "error"
def test_invalid_scientific_output_is_logged_without_poisoning_trace():
    env = SynthesisRouteEnv(make_task(), expand=lambda *_: {"status": "ok", "predictions": [], "score": float("nan")})
    result = env.dispatch("expand", {"smiles": "CCO"})
    assert result["status"] == "error"
    assert result["usage"]["expansions"] == 1
    assert env.export()["events"][0]["status"] == "error"

