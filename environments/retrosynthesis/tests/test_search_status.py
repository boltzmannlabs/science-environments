from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task, InventoryItem


def test_search_status_is_small_and_tracks_environment_without_actions(monkeypatch):
    env=SynthesisRouteEnv(Task(task_id='status',target='CCO',inventory=(InventoryItem(smiles='O'),)))
    monkeypatch.setattr(env,'inspect',lambda: (_ for _ in ()).throw(AssertionError('full observation copied')))
    status=env.search_status()
    assert set(status)=={'usage','terminated','truncated','capability_fingerprint'}
    assert status['usage']['actions']==0
    status['usage']['actions']=999
    assert env.search_status()['usage']['actions']==0
    env.dispatch('submit',{'route_ids':[]})
    assert env.search_status()['terminated']
    assert env.search_status()['usage']['actions']==1


def test_public_expansion_cache_identity_canonicalizes_and_changes_with_stock():
    first=SynthesisRouteEnv(Task(task_id='one',target='CCO',inventory=()))
    other=SynthesisRouteEnv(Task(task_id='two',target='CCO',inventory=(InventoryItem(smiles='O'),)))
    args={'smiles':'CCO','top_k':3}
    assert first.expansion_cache_identity(args)==first.expansion_cache_identity({'smiles':'OCC','top_k':3})
    assert first.expansion_cache_identity(args)!=other.expansion_cache_identity(args)
    assert first.expansion_cache_identity(args)!=first.expansion_cache_identity({'smiles':'CCO','top_k':4})
