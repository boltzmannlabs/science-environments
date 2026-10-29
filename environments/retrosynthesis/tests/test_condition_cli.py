"""CLI condition selection uses the same private replay boundary as Python."""
import json
import pytest
from synthesis_route_gym.cli import _parser, execute, main
from test_condition_io import files

def argv(tmp_path,command='condition-agent'):
    base=[command,'--study',str(tmp_path/'study.json'),'--outcomes',str(tmp_path/'labels.json'),
          '--predictions',str(tmp_path/'predictions.json'),'--output',str(tmp_path/'result.json')]
    if command=='condition-agent':
        base+=['--scientist-python','/trusted/python','--scientist-source','/trusted/scientist',
               '--profile-home',str(tmp_path/'profile')]
    return base

def test_mode_explicit_and_no_model_override(tmp_path):
    parser=_parser();assert parser.parse_args(argv(tmp_path)).method=='main'
    assert parser.parse_args(argv(tmp_path)+['--method','main_condition_scientist']).method=='main_condition_scientist'
    with pytest.raises(SystemExit):parser.parse_args(argv(tmp_path)+['--condition-scientist-model','other'])

@pytest.mark.parametrize('policy',['fixed_order','random','public_model_rank','gp_expected_improvement'])
def test_fixed_cli_real_episode(tmp_path,policy):
    files(tmp_path)
    assert main(argv(tmp_path,'condition-plan')+['--policy',policy])==0
    result=json.loads((tmp_path/'result.json').read_text())
    assert result['episode']['submission']=={'status':'selected','candidate_id':'b'}
    assert result['episode']['resources']['new_observations_used']==1
    assert 'dataset_optimum' not in json.dumps(result)
    assert str(tmp_path/'labels.json') not in json.dumps(result)

def test_agent_cli_and_completed_resume(tmp_path,monkeypatch):
    from synthesis_route_gym import condition_session
    files(tmp_path);(tmp_path/'profile').mkdir()
    (tmp_path/'profile/config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n')
    calls=[]
    def bridge(prompt,executor,**kw):
        calls.append(kw)
        assert kw['mode']=='main_condition_scientist'
        assert kw['budget'].max_model_calls==24 and kw['budget'].max_total_tokens==350000
        assert 'labels.json' not in prompt
        kw['checkpoint']({'fixture':'complete'})
        executor('inspect',{});executor('observe_condition',{'candidate_id':'b'})
        executor('submit',{'candidate_id':'b'})
        return {'completed':True}
    monkeypatch.setattr(condition_session,'run_agent_scientist_bridge',bridge)
    arguments=argv(tmp_path)+['--method','main_condition_scientist']
    assert main(arguments)==0 and main(arguments+['--resume'])==0
    assert len(calls)==1
    assert json.loads((tmp_path/'result.json').read_text())['submission_status']=='selected'

def test_existing_episode_not_overwritten(tmp_path):
    files(tmp_path);arguments=argv(tmp_path,'condition-plan')
    execute(_parser().parse_args(arguments))
    with pytest.raises(FileExistsError):execute(_parser().parse_args(arguments))


def test_missing_condition_submission_reports_failure(tmp_path,monkeypatch):
    import synthesis_route_gym.cli as cli
    monkeypatch.setattr(cli,'execute',lambda args:{'episode':{'submission':{'status':'not_submitted'}},
                                                 'agent':{'completed':False}})
    assert cli.main(argv(tmp_path))==1
    assert (tmp_path/'result.json').exists()
