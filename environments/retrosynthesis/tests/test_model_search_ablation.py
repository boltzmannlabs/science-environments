"""Predictor availability ablation keeps search inputs and policy fixed."""
import pytest
from synthesis_route_gym import model_search_ablation as ablation
from synthesis_route_gym import development_runner as runner
from test_core import make_task
from test_public_yield_integration import Predictor, candidate


def test_plan_pairs_same_inputs_and_main_policy(tmp_path):
    inputs = tmp_path/'inputs'
    inputs.mkdir()
    for task_id in ('a','b'):
        runner.write_once(inputs/(task_id+'.json'),make_task(task_id=task_id).model_dump(mode='json'))
    manifest = tmp_path/'model.json'
    manifest.write_text('{}')
    selection = {'groups':[{'group_id':'g','task_ids':['a','b']}],
                 'screen_group_ids':['g'],'confirmation_group_ids':[]}
    runtime = {'reaction_yield_model_manifest':str(manifest)}
    plan = ablation.make_model_search_plan(selection,inputs,runtime)
    assert len(plan['runs']) == 4
    for task_id in ('a','b'):
        pair = [row for row in plan['runs'] if row['task_id']==task_id]
        assert {row['model_enabled'] for row in pair} == {False,True}
        assert all(row['arm']=='main' and row['regime']=='budgeted' for row in pair)
    assert len({row['run_id'] for row in plan['runs']}) == 4
    assert plan['final_labels_opened'] is False
    assert plan['runtime']['model_manifest_sha256'] == runner.digest(manifest)


@pytest.mark.parametrize('enabled',[False,True])
def test_execution_changes_only_predictor_availability(tmp_path,monkeypatch,enabled):
    loaded = []
    def loader(path):
        loaded.append(path)
        return Predictor()
    monkeypatch.setattr(ablation,'load_predictor',loader)
    def agent(task,row,runtime,folder,env):
        response = env.dispatch('predict_reaction_yield',{'candidates':[candidate()]})
        assert response['status'] == ('ok' if enabled else 'unavailable')
        env.dispatch('submit',{'route_ids':[]})
        return {'agent':{'completed':True},'episode':env.export()}
    monkeypatch.setattr(runner,'_execute_agent',agent)
    task = make_task()
    row = {'arm':'main','seed':0,'model_enabled':enabled}
    manifest = tmp_path/'model.json'
    manifest.write_text('{}')
    runtime = {'expansion_top_k':10,'reaction_yield_model_manifest':str(manifest),
               'model_manifest_sha256':runner.digest(manifest)}
    result = ablation.execute_model_search(task,row,runtime,tmp_path/'run',expand=lambda **kw: {})
    assert result['episode']['task'] == task.model_dump(mode='json')
    assert bool(loaded) == enabled
    report = result['model_ablation']
    assert report['model_enabled'] == enabled
    assert report['predictor_action_attempts'] == 1
    assert report['scored_predictions'] == (1 if enabled else 0)
    assert report['model_exercised'] == enabled


def test_invalid_variant_is_rejected_before_loading(tmp_path):
    with pytest.raises(ValueError):
        ablation.execute_model_search(make_task(),{'arm':'main','model_enabled':'yes'}, {},tmp_path)


def test_ablation_enforces_same_expansion_width(tmp_path,monkeypatch):
    calls, captured = [], []
    def policy(task,row,runtime,folder,env):
        assert env.dispatch('expand',{'smiles':task.target,'top_k':3})['status'] != 'ok'
        assert not calls
        assert env.dispatch('expand',{'smiles':task.target,'top_k':10})['status']=='ok'
        captured.append(env)
        raise KeyboardInterrupt
    monkeypatch.setattr(runner,'_execute_agent',policy)
    def expand(**kw):
        calls.append(kw)
        return {'status':'ok','predictions':[]}
    with pytest.raises(KeyboardInterrupt):
        manifest = tmp_path/'model.json'
        manifest.write_text('{}')
        ablation.execute_model_search(make_task(),{'arm':'main','seed':0,'model_enabled':False},
            {'expansion_top_k':10,'reaction_yield_model_manifest':str(manifest),
             'model_manifest_sha256':runner.digest(manifest)},tmp_path/'run',expand=expand)
    assert len(calls)==1
    assert captured[0].export()['truncated']
    assert not captured[0].export()['terminated']


def test_pinned_model_and_expansion_adapter_loading(monkeypatch):
    from synthesis_route_gym.public_yield import ReactionT5YieldPredictor
    monkeypatch.setattr(ReactionT5YieldPredictor,'from_manifest',lambda path:('model',path))
    assert ablation.load_predictor('pinned.json') == ('model','pinned.json')
    from synthesis_route_gym.adapters import LocalRetroAdapter
    monkeypatch.setattr(LocalRetroAdapter,'expand',lambda self,**kw:{'root':self.repo_root,**kw})
    fn = ablation._expand({'repo_root':'/local/repo','chemistry_python':'/local/python',
                          'tool_timeout_seconds':60,'expansion_top_k':10},None)
    assert fn('CCO',10)=={'root':'/local/repo','target_smiles':'CCO','top_k':10}


def test_plan_requires_model_identity(tmp_path):
    with pytest.raises(ValueError,match='manifest'):
        ablation.make_model_search_plan({},tmp_path,{})


@pytest.mark.parametrize('enabled',[False,True])
def test_changed_manifest_is_rejected_before_either_variant(tmp_path,monkeypatch,enabled):
    manifest = tmp_path/'model.json'
    manifest.write_text('original')
    runtime = {'reaction_yield_model_manifest':str(manifest),'model_manifest_sha256':runner.digest(manifest)}
    manifest.write_text('changed')
    monkeypatch.setattr(ablation,'load_predictor',lambda path:pytest.fail('changed manifest loaded'))
    with pytest.raises(ValueError,match='integrity'):
        ablation.execute_model_search(make_task(),{'arm':'main','model_enabled':enabled},runtime,tmp_path/'run')
