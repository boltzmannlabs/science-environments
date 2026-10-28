"""Opt-in local impurity inference uses the shared environment."""
import json
from synthesis_route_gym.cli import _parser,execute
from test_core import make_task,make_route


def test_cli_impurity_binding(tmp_path,monkeypatch):
    from synthesis_route_gym.adapters.impurity_local import LocalImpurityAdapter
    calls=[]
    def predict(self,reactants,product,top_k=5):
        calls.append(product);return {'status':'ok','predicted_smiles':['CCO']}
    monkeypatch.setattr(LocalImpurityAdapter,'predict',predict)
    task=tmp_path/'task.json';task.write_text(make_task().model_dump_json())
    actions=tmp_path/'actions.json';actions.write_text(json.dumps([
      {'action':'propose_route','arguments':{'route':make_route().model_dump(mode='json')}},
      {'action':'predict_route_impurities','arguments':{'route_id':'r1','step_id':'ester'}},
      {'action':'application_report','arguments':{'application':'impurity_analysis','route_ids':['r1'],'step_id':'ester'}}]))
    args=_parser().parse_args(['replay','--task',str(task),'--actions',str(actions),'--output',str(tmp_path/'out.json'),
                              '--impurity-model','--repo-root',str(tmp_path),'--chemistry-python','python'])
    result=execute(args)
    assert len(calls)==1 and result['events'][-1]['result']['result']['predicted_impurities']==['CCO']
    assert result['scientific_usage']['predict_impurities']==1


def test_impurity_registry_exposes_host_artifact_identity():
    from synthesis_route_gym.scientific_bindings import build_default_registry
    class Predictor:
        artifact_sha256='a'*64
        model_version='pinned-software-test'
        timeout_seconds=17
        configuration={'snapshot':'software-test'}
        def predict(self,*args):return {'status':'ok','predicted_smiles':[]}
    registry=build_default_registry(make_task(),impurity=Predictor())
    row=registry.invoke('predict_impurities',{'reactants':['CCO','CC(=O)O'],'product':'CCOC(C)=O'})
    assert row['provenance']['binding']['artifact_sha256']=='a'*64
    assert row['provenance']['binding']['model_version']=='pinned-software-test'
    assert row['provenance']['binding']['timeout_seconds']==17
