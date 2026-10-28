"""Candidate feedback is authenticated committed-record postprocessing."""
from fastapi.testclient import TestClient
from synthesis_route_gym.api import create_app
from test_api import headers, KEY_A, KEY_B, route, task


def handoff():
    return {'candidate_id': 'candidate-one', 'smiles': 'CCOC(C)=O',
            'source_job_id': 'upstream-job', 'source_tool': 'small-molecule',
            'source_tool_version': 'fixture-v1', 'upstream_payload_sha256': 'a' * 64,
            'inventory': task()['inventory']}


def test_candidate_identity_survives_submission_and_feedback():
    client = TestClient(create_app({KEY_A: 'alice', KEY_B: 'bob'}))
    response = client.post('/v1/handoffs/small-molecule', json=handoff(), headers=headers())
    assert response.status_code == 201, response.text
    created = response.json()['data']; base = '/v1/episodes/' + created['episode_id']
    assert created['handoff']['candidate_id'] == 'candidate-one'
    for action, args in [('propose_route', {'route': route()}), ('submit', {'route_ids': ['r1']})]:
        assert client.post(base + '/actions', json={'action': action, 'arguments': args}, headers=headers()).status_code == 200
    result = client.get(base + '/feedback', headers=headers())
    assert result.status_code == 200, result.text
    feedback = result.json()['data']
    assert feedback['schema_version'] == 'srg-small-molecule-feedback-v1'
    assert 'candidate-one' in str(feedback) and 'upstream-job' in str(feedback)
    assert 'a' * 64 in str(feedback) and 'r1' in str(feedback)
    assert client.get(base + '/feedback', headers=headers(KEY_B)).status_code == 404
    assert client.get(base + '/feedback').status_code == 401


def test_non_handoff_episode_has_no_fabricated_candidate_feedback():
    client = TestClient(create_app({KEY_A: 'alice'}))
    created = client.post('/v1/episodes', json={'task': task()}, headers=headers()).json()['data']
    result = client.get('/v1/episodes/' + created['episode_id'] + '/feedback', headers=headers())
    assert result.status_code == 409


def test_handoff_unknown_metadata_and_bad_digest_fail_boundary():
    client = TestClient(create_app({KEY_A: 'alice'}))
    for extra in ({'upstream_payload_sha256': 'wrong'}, {'source_model_path': '/private/model'}):
        result = client.post('/v1/handoffs/small-molecule', json={**handoff(), **extra}, headers=headers())
        assert result.status_code == 422
