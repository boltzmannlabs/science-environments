"""Real environment feedback -> isolated advice -> main-owned metered action."""
import json
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task
from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy
from synthesis_route_gym import route_condition_advice as advice, route_condition_runtime as runtime
from test_route_condition_advice import catalog, RESOURCES
from test_route_condition_runtime import Harness, PROFILE


def environment(tmp_path):
    public=catalog(observed=())
    rows=(('a','O',11.123),('b','N',22.234),('c','F',88.456),('d','I',99.567))
    study=FiniteConditionStudy(tuple(ConditionRecord(k,(('base',r),),v)for k,r,v in rows),(),4,
        public['source_url'],public['source_locator'],public['dataset_sha256'],'CCBr')
    binding={key:public[key]for key in ('study_id','dataset_sha256','source_url','source_locator','reactants','product')}
    binding={**binding,'schema_version':'srg-route-condition-binding-v1',
        'candidates':[{key:row[key]for key in ('candidate_id','conditions','recipe')}for row in public['candidates']]}
    config={'schema_version':'srg-application-config-v1','condition_binding':binding}
    task=Task(task_id='synthetic-condition-advisor-integration',target='CCO',
        inventory=[{'smiles':s}for s in ('CCBr','O','N','F','I')])
    env=SynthesisRouteEnv(task,condition_study=study,application_config=config,
        scientific_limits={'observation_calls':4},store=tmp_path/'episode')
    recipe={**public['candidates'][0]['recipe'],'step_id':'s1'}
    assert env.dispatch('propose_route',{'route':{'route_id':'r1','target':'CCO','steps':[recipe]}})['status']=='ok'
    return env,task,study,config


def test_real_host_feedback_bound_advice_and_main_execution(tmp_path):
    env,task,study,config=environment(tmp_path);h=Harness();args={'route_id':'r1','step_id':'s1'}
    before=env.export()['routes']
    for candidate in ('a','b'):
        query={**args,'candidate_id':candidate};response=env.dispatch('observe_route_condition',query)
        assert response['status']=='ok'
        answer=runtime.after_tool('observe_route_condition',query,response,state=h.state,update=h.update,
            runtime=h.backend,profile=PROFILE,ledger=h.ledger)
    assert len(h.backend.calls)==1
    proposed=answer['route_condition_advice']['recommendation']['next_action']
    assert proposed['arguments']=={**args,'candidate_id':'c'}
    assert '88.456' not in json.dumps(h.state)and'99.567' not in json.dumps(h.state)
    assert env.export()['scientific_usage']['observe_condition']==2
    restored=SynthesisRouteEnv.resume(tmp_path/'episode',expected_task=task,condition_study=study,
        application_config=config,scientific_limits={'observation_calls':4})
    next_result=restored.dispatch(proposed['action'],proposed['arguments'])
    assert next_result['status']=='ok'
    assert next_result['result']['condition_catalog']['observation_resources']['calls_used']==3
    assert restored.export()['routes']==before


def test_real_failed_and_primitive_observations_cannot_create_free_queries(tmp_path):
    env,_,_,_=environment(tmp_path);state=advice.initial_state();args={'route_id':'r1','step_id':'s1'}
    for candidate in ('a','b'):
        query={**args,'candidate_id':candidate}
        state=advice.observe(state,'observe_route_condition',query,env.dispatch('observe_route_condition',query))
    primitive={'candidate_id':'c'}
    state=advice.observe(state,'observe_condition',primitive,env.dispatch('observe_condition',primitive))
    assert advice.build_context(state,RESOURCES)is None
    state=advice.observe(state,'condition_options',args,env.dispatch('condition_options',args))
    ctx=advice.build_context(state,RESOURCES)
    assert ctx['catalog']['observation_count']==2
    assert ctx['catalog']['observation_resources']['calls_used']==3
    assert ctx['catalog']['observation_resources']['attempted_candidate_ids']==['a','b','c']
    assert '88.456'not in json.dumps(ctx)
