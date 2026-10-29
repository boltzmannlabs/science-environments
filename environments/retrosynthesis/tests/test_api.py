"""HTTP contract tests using real environment transitions and isolated identities."""
import json
import pytest
from fastapi.testclient import TestClient
from synthesis_route_gym.api import create_app

KEY_A = "test-only-token-alice"
KEY_B = "test-only-token-bob"


def headers(key=KEY_A):
    return {"Authorization": f"Bearer {key}"}


def task():
    return {"task_id": "test", "target": "CCOC(C)=O", "inventory": [
        {"smiles": "CCO"}, {"smiles": "CC(=O)O"}]}


def route():
    return {"route_id": "r1", "target": "CCOC(C)=O", "steps": [{
        "step_id": "s1", "product": "CCOC(C)=O",
        "reactants": [{"smiles": "CCO"}, {"smiles": "CC(=O)O"}],
        "source_tool": "test-fixture", "source_version": "1"}]}


@pytest.fixture
def client():
    return TestClient(create_app({KEY_A: "alice", KEY_B: "bob"}))


def test_all_endpoints_require_authentication(client):
    for path in ("/v1/health", "/v1/openapi.json", "/v1/episodes/missing"):
        response = client.get(path)
        assert response.status_code == 401
        assert response.json()["success"] is False
    assert client.post("/v1/episodes", json={"task": task()}, headers=headers("wrong")).status_code == 401


def test_auth_configuration_fails_closed():
    for value in ({}, {"": "owner"}, {"key": ""}):
        with pytest.raises(ValueError):
            create_app(value)


def test_real_assessment_keeps_unknowns_and_review_pending(client):
    response = client.post("/v1/routes/assess", json={"task": task(), "route": route()}, headers=headers())
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["inventory_complete"]
    assert result["cost"]["total"] is None
    assert result["solved"] is False and result["review_status"] == "pending"


def test_episode_route_submit_and_export_end_to_end(client):
    response = client.post("/v1/episodes", json={"task": task(), "seed": 2}, headers=headers())
    assert response.status_code == 201
    episode_id = response.json()["data"]["episode_id"]
    url = f"/v1/episodes/{episode_id}/actions"
    assert client.post(url, json={"action": "propose_route", "arguments": {"route": route()}}, headers=headers()).status_code == 200
    submitted = client.post(url, json={"action": "submit", "arguments": {"route_ids": ["r1"]}}, headers=headers())
    assert submitted.json()["data"]["terminated"]
    exported = client.get(f"/v1/episodes/{episode_id}", headers=headers()).json()["data"]
    assert exported["episode"]["submitted_route_ids"] == ["r1"]
    assert len(exported["episode"]["events"]) == 2


def test_owners_cannot_read_act_on_or_delete_other_episodes(client):
    episode_id = client.post("/v1/episodes", json={"task": task()}, headers=headers()).json()["data"]["episode_id"]
    path = f"/v1/episodes/{episode_id}"
    assert client.get(path, headers=headers(KEY_B)).status_code == 404
    assert client.post(path + "/actions", json={"action": "inspect", "arguments": {}}, headers=headers(KEY_B)).status_code == 404
    assert client.delete(path, headers=headers(KEY_B)).status_code == 404
    assert client.delete(path, headers=headers()).status_code == 200
    assert client.get(path, headers=headers()).status_code == 404


def test_malformed_science_and_unrecognized_fields_are_rejected(client):
    invalid = {**task(), "target": "invalid smiles"}
    assert client.post("/v1/episodes", json={"task": invalid}, headers=headers()).status_code == 422
    response = client.post("/v1/episodes", json={"task": task(), "file_path": "/etc/passwd"}, headers=headers())
    assert response.status_code == 422
    assert "/etc/passwd" not in response.text


def test_task_budgets_have_service_caps_and_cannot_reset(client):
    value = {**task(), "budget": {"max_actions": 1}}
    episode_id = client.post("/v1/episodes", json={"task": value}, headers=headers()).json()["data"]["episode_id"]
    url = f"/v1/episodes/{episode_id}/actions"
    assert client.post(url, json={"action": "reset", "arguments": {}}, headers=headers()).status_code == 422
    result = client.post(url, json={"action": "inspect", "arguments": {}}, headers=headers())
    assert result.json()["data"]["truncated"]
    assert client.post(url, json={"action": "inspect", "arguments": {}}, headers=headers()).status_code == 409
    too_large = {**task(), "budget": {"max_wall_seconds": 99999999}}
    assert client.post("/v1/episodes", json={"task": too_large}, headers=headers()).status_code == 422


def test_request_body_limits_include_streamed_requests():
    client = TestClient(create_app({KEY_A: "alice"}, max_body_bytes=512))
    assert client.post("/v1/episodes", content="x" * 513, headers=headers()).status_code == 413
    streamed = (b"x" * 300 for _ in range(3))
    assert client.post("/v1/episodes", content=streamed, headers=headers()).status_code == 413


def test_rate_limit_is_per_owner_and_applies_to_read_endpoints():
    client = TestClient(create_app({KEY_A: "alice", KEY_B: "bob"}, requests_per_minute=2))
    assert client.get("/v1/health", headers=headers()).status_code == 200
    assert client.get("/v1/health", headers=headers()).status_code == 200
    limited = client.get("/v1/health", headers=headers())
    assert limited.status_code == 429 and limited.headers["retry-after"]
    assert client.get("/v1/health", headers=headers(KEY_B)).status_code == 200


def test_small_molecule_handoff_retains_identity_and_provenance(client):
    payload = {"candidate_id": "small-molecule-001", "smiles": "OCC",
               "source_job_id": "upstream-01", "source_tool": "small-molecule-candidates",
               "inventory": [{"smiles": "CCO"}]}
    response = client.post("/v1/handoffs/small-molecule", json=payload, headers=headers())
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["handoff"]["candidate_id"] == payload["candidate_id"]
    episode = client.get(f"/v1/episodes/{data['episode_id']}", headers=headers()).json()["data"]
    assert episode["episode"]["task"]["target"] == "CCO"
    assert episode["handoff"]["source_job_id"] == "upstream-01"


def test_openapi_contract_is_authenticated_and_versioned(client):
    response = client.get("/v1/openapi.json", headers=headers())
    schema = response.json()
    assert response.status_code == 200
    assert schema["info"]["version"] == "0.1.0"
    assert "/v1/routes/assess" in schema["paths"]
    assert client.get("/openapi.json", headers=headers()).status_code == 404


def test_episode_capacity_is_bounded_per_owner():
    client = TestClient(create_app({KEY_A: "alice", KEY_B: "bob"}, max_episodes_per_owner=1))
    assert client.post("/v1/episodes", json={"task": task()}, headers=headers()).status_code == 201
    assert client.post("/v1/episodes", json={"task": task()}, headers=headers()).status_code == 429
    assert client.post("/v1/episodes", json={"task": task()}, headers=headers(KEY_B)).status_code == 201


def test_nonfinite_action_arguments_are_rejected(client):
    episode_id = client.post("/v1/episodes", json={"task": task()}, headers=headers()).json()["data"]["episode_id"]
    response = client.post(f"/v1/episodes/{episode_id}/actions", content=json.dumps({"action": "expand", "arguments": {"top_k": float("nan")}}), headers={**headers(), "Content-Type": "application/json"})
    assert response.status_code == 422


def test_condition_ranker_endpoint_uses_operator_model_and_preserves_predictions():
    from synthesis_route_gym.ranking import ConditionRanker
    model = ConditionRanker({"schema_version": "condition-ranker.v1", "n_features": 512,
        "trees": [{"left": [-1], "right": [-1], "feature": [-2], "threshold": [-2.0], "value": [20.0]}],
        "metadata": {"model_version": "api-test-fixture"}})
    payload = {"candidates": [{"candidate_id": "condition-1", "aryl halide": "Brc1ccccc1",
                              "ligand": "P", "additive": "O", "base": "N"}]}
    client = TestClient(create_app({KEY_A: "alice"}, condition_ranker=model))
    response = client.post("/v1/conditions/rank", json=payload, headers=headers())
    assert response.status_code == 200
    result = response.json()["data"]["ranked_candidates"][0]
    assert result["candidate_id"] == "condition-1"
    assert result["predicted_yield_percent"] == 20.0
    assert result["evidence_status"] == "predicted"
    payload["model_path"] = "/tmp/other-model"
    assert client.post("/v1/conditions/rank", json=payload, headers=headers()).status_code == 422


def test_condition_model_unavailable_is_explicit(client):
    payload = {"candidates": [{"candidate_id": "condition-1", "aryl halide": "Brc1ccccc1",
                              "ligand": "P", "additive": "O", "base": "N"}]}
    assert client.post("/v1/conditions/rank", json=payload, headers=headers()).status_code == 503


def test_health_reports_local_execution_scope(client):
    data = client.get("/v1/health", headers=headers()).json()["data"]
    assert data["execution_scope"] == "local"
    assert "platform_deployment" not in data


def test_episode_actions_use_configured_model_and_record_budgeted_events():
    class ConfiguredModel:
        def __init__(self):
            self.calls = []
            self.metadata = {"model_version": "api-episode-fixture"}

        def predict(self, rows):
            self.calls.append(rows)
            return [{"predicted_yield_percent": 37.0, "model_version": "api-episode-fixture",
                     "evidence_status": "predicted"} for row in rows]

    model = ConfiguredModel()
    client = TestClient(create_app({KEY_A: "alice"}, condition_ranker=model))
    roles = {"aryl halide": "BrC1=CC=C(C(F)(F)F)C=C1",
             "ligand": "CC(C)C(C=C(C(C)C)C=C1C(C)C)=C1C2=C(P(C(C)(C)C)C(C)(C)C)C(OC)=CC=C2OC",
             "additive": "C1(C2=CC=CC=C2)=CC=NO1", "base": "CC(C)(C)/N=C(N(C)C)/N(C)C"}
    partner = "Cc1ccc(N)cc1"
    catalyst = "O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F"
    value = {"task_id": "condition-episode", "target": "Cc1ccc(Nc2ccc(C(F)(F)F)cc2)cc1", "inventory": [
        {"smiles": s} for s in (*roles.values(), partner, catalyst)], "budget": {"max_actions": 3}}
    episode_id = client.post("/v1/episodes", json={"task": value}, headers=headers()).json()["data"]["episode_id"]
    path = f"/v1/episodes/{episode_id}"
    predicted = client.post(path + "/actions", json={"action": "predict_conditions", "arguments": {
        "candidates": [{"id": "c1", **roles}]}}, headers=headers())
    assert predicted.status_code == 200
    prediction = predicted.json()["data"]["result"]["predictions"][0]
    assert prediction["predicted_yield_percent"] == 37.0
    assert prediction["model_version"] == "api-episode-fixture"
    proposal = {"route_id": "r1", "target": value["target"], "steps": [{
        "step_id": "s1", "product": value["target"], "reactants": [{"smiles": roles["aryl halide"]}, {"smiles": partner}],
        "reagents": [{"smiles": roles[role]} for role in ("ligand", "additive", "base")] + [{"smiles": catalyst}],
        "source_tool": "fixture", "source_version": "1",
        "condition_inputs": roles, "predicted_yield": 0.99}]}
    assert client.post(path + "/actions", json={"action": "propose_route", "arguments": {
        "route": proposal}}, headers=headers()).status_code == 200
    ranked = client.post(path + "/actions", json={"action": "rank_routes", "arguments": {
        "route_ids": ["r1"]}}, headers=headers())
    assert ranked.status_code == 200
    assert ranked.json()["data"]["result"]["ranking"][0]["bottleneck_predicted_yield"] == 0.37
    from synthesis_route_gym.chemistry import canonical_smiles
    assert len(model.calls) == 2 and model.calls[0] == [{k:canonical_smiles(v) for k,v in roles.items()}]
    exported = client.get(path, headers=headers()).json()["data"]["episode"]
    assert len(exported["events"]) == 3
    closed = client.post(path + "/actions", json={"action": "predict_conditions", "arguments": {
        "candidates": [{"id": "c1", **roles}]}}, headers=headers())
    assert closed.status_code == 409 and len(model.calls) == 2
