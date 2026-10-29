"""SynthChem is preferred while other search policies remain selectable."""
import json
import pytest
from synthesis_route_gym.cli import _parser, execute
from synthesis_route_gym.schemas import Task, InventoryItem, Budget


def task_file(tmp_path):
    path = tmp_path / 'task.json'
    task = Task(task_id='search-cli', target='CCO', inventory=(InventoryItem(smiles='C=C'), InventoryItem(smiles='O')),
                budget=Budget(max_actions=10, max_expansions=3, top_k=1))
    path.write_text(task.model_dump_json())
    return path


def test_search_options_prefer_synthchem_portfolio():
    args = _parser().parse_args(['plan','--task','task.json','--output','out.json'])
    assert args.search_policy == 'synthchem_portfolio'
    assert args.expansion_top_k == 10
    assert args.max_frontier_states is None  # Host resolves legacy 10000 only for budgeted tasks.


@pytest.mark.parametrize('policy,algorithm', [('breadth_first','breadth_first_AND_OR'),('best_first','best_first')])
def test_plan_selects_policy_and_passes_limits(tmp_path,monkeypatch,policy,algorithm):
    from synthesis_route_gym.adapters import LocalRetroAdapter
    seen=[]
    def expand(self,smiles,top_k):
        seen.append((smiles,top_k))
        return {'status':'ok','predictions':[{'product':smiles,'reactants':['C=C','O'],
            'score':0.8,'source':{'tool':'fixture','version':'1'}}]}
    monkeypatch.setattr(LocalRetroAdapter,'expand',expand)
    args = _parser().parse_args(['plan','--task',str(task_file(tmp_path)),'--output',str(tmp_path/'out.json'),
            '--search-policy',policy,'--expansion-top-k','3','--max-frontier-states','100'])
    result=execute(args)
    assert algorithm in result['algorithm']
    assert result['expansion_top_k']==3
    assert result['max_frontier_states']==100
    assert seen==[('CCO',3)]
    assert len(result['episode']['submitted_route_ids'])==1


def test_plan_rejects_invalid_search_policy():
    with pytest.raises(SystemExit):
        _parser().parse_args(['plan','--task','t','--output','o','--search-policy','invented'])


def test_best_first_cli_end_to_end_without_model_calls(tmp_path):
    import subprocess
    import sys
    task=Task(task_id='cli-acquisition',target='CCO',inventory=(InventoryItem(smiles='CCO'),))
    path=tmp_path/'task.json';path.write_text(task.model_dump_json())
    output=tmp_path/'result.json'
    completed=subprocess.run([sys.executable,'-m','synthesis_route_gym','plan','--task',str(path),
        '--output',str(output),'--search-policy','best_first','--repo-root',str(tmp_path/'missing-model')],
        capture_output=True,text=True,timeout=20)
    assert completed.returncode==0,completed.stderr
    report=json.loads(output.read_text())
    assert report['episode']['usage']['expansions']==0
    assert report['episode']['terminated']
    assert report['episode']['submitted_route_ids']==[]
