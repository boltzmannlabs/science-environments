import json
import subprocess
import sys
from test_core import make_task, make_route


def test_cli_validate_and_replay_produce_real_artifacts(tmp_path):
    task_path, route_path = tmp_path / "task.json", tmp_path / "route.json"
    task_path.write_text(make_task().model_dump_json())
    route_path.write_text(make_route().model_dump_json())
    output = tmp_path / "assessment.json"
    result = subprocess.run([sys.executable, "-m", "synthesis_route_gym", "validate", "--task", str(task_path),
                             "--route", str(route_path), "--output", str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text())["inventory_complete"]
    actions = tmp_path / "actions.json"
    actions.write_text(json.dumps([
        {"action": "propose_route", "arguments": {"route": make_route().model_dump(mode="json")}},
        {"action": "submit", "arguments": {"route_ids": ["r1"]}}]))
    result = subprocess.run([sys.executable, "-m", "synthesis_route_gym", "replay", "--task", str(task_path),
                            "--actions", str(actions), "--output", str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text())["submitted_route_ids"] == ["r1"]


def test_cli_bad_input_returns_failure_without_overwriting_output(tmp_path):
    task = tmp_path / "invalid.json"
    task.write_text('{"target":"invalid"}')
    result = subprocess.run([sys.executable, "-m", "synthesis_route_gym", "plan", "--task", str(task),
                             "--output", str(tmp_path / "result.json")], capture_output=True, text=True)
    assert result.returncode != 0
    assert not (tmp_path / "result.json").exists()


def test_cli_replay_loads_explicit_host_condition_model(tmp_path, monkeypatch):
    from synthesis_route_gym.cli import _parser, execute
    from synthesis_route_gym.ranking import ConditionRanker
    class Predictor:
        def predict(self, rows):
            return [{"predicted_yield_percent": 12} for row in rows]
    monkeypatch.setattr(ConditionRanker, "load", lambda path: Predictor())
    task = tmp_path / "task.json"
    task.write_text(make_task().model_dump_json())
    actions = tmp_path / "actions.json"
    actions.write_text(json.dumps([{"action": "predict_conditions", "arguments": {"candidates": [
        {"id": "c", "aryl halide": "Clc1ccccc1", "ligand": "P", "additive": "O", "base": "N"}]}}]))
    args = _parser().parse_args(["replay", "--task", str(task), "--actions", str(actions),
                                "--condition-model", "host-model.json", "--output", str(tmp_path / "out.json")])
    assert execute(args)["events"][0]["result"]["predictions"][0]["predicted_yield_percent"] == 12


def test_agent_cli_creates_durable_episode_and_resumes_closed_without_model(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    from synthesis_route_gym.cli import _parser, execute
    from synthesis_route_gym.observation import compact_observation
    task = tmp_path/'task.json'; task.write_text(make_task().model_dump_json())
    def fake(prompt, executor, **kw):
        kw['checkpoint']({'ledger': {'model_calls': 1, 'actual_tokens': 10}})
        kw['action_executor']('submit', {'route_ids': []}, action_id='final')
        return {'completed': True}
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', fake)
    command = ['agent','--task',str(task),'--output',str(tmp_path/'report.json'),
               '--episode-dir',str(tmp_path/'episode'), '--scientist-python', '/trusted/python',
               '--scientist-source', '/trusted/source']
    first = execute(_parser().parse_args(command))
    assert first['submission_status'] == 'submitted_empty'
    assert (tmp_path/'episode'/'environment'/'HEAD.json').exists()
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **k: (_ for _ in ()).throw(AssertionError('unexpected call')))
    resumed = execute(_parser().parse_args(command + ['--resume']))
    assert resumed['episode']['usage']['actions'] == first['episode']['usage']['actions']
    assert resumed['runtime_checkpoint']['ledger']['actual_tokens'] == 10


def test_cli_replay_loads_host_science_config_without_revealing_unqueried_rows(tmp_path):
    from synthesis_route_gym.cli import _parser,execute
    task=tmp_path/'task.json';task.write_text(make_task().model_dump_json())
    config=tmp_path/'science.json'
    config.write_text(json.dumps({'schema_version':'srg-science-config-v1',
      'scientific_limits':{'observation_calls':1},'condition_replay':{
      'data_role':'smoke','substrate':'CCO','source_url':'https://example.org/fixture',
      'source_locator':'synthetic fixtures','dataset_sha256':'a'*64,'budget':1,
      'rows':[{'candidate_id':'one','conditions':{'ligand':'P'},'yield_percent':10},
              {'candidate_id':'two','conditions':{'ligand':'N'},'yield_percent':99}]}}))
    actions=tmp_path/'actions.json';actions.write_text(json.dumps([
      {'action':'inspect','arguments':{'condition_offset':0}},
      {'action':'observe_condition','arguments':{'candidate_id':'one'}},
      {'action':'observe_condition','arguments':{'candidate_id':'two'}}]))
    args=_parser().parse_args(['replay','--task',str(task),'--actions',str(actions),
                              '--science-config',str(config),'--output',str(tmp_path/'result.json')])
    report=execute(args)
    assert report['events'][1]['result']['data']['yield_percent']==10
    assert report['events'][2]['result']['error']['code']=='access_budget_exhausted'
    assert 'yield_percent' not in json.dumps(report['events'][0]['result'])
    assert report['scientific_usage']['observe_condition']==2
