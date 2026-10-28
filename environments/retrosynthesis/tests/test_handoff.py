"""Pure handoff feedback never promotes caller claims or performs science calls."""
from copy import deepcopy
import hashlib,json
import pytest
from synthesis_route_gym.handoff import SmallMoleculeHandoff,build_handoff_task,build_handoff_manifest,build_handoff_feedback
from synthesis_route_gym.environment import SynthesisRouteEnv
from test_core import make_route,make_task


def payload(**updates):
    return {'candidate_id':'candidate-1','smiles':'CCOC(C)=O','source_job_id':'job-1','source_tool':'small-molecule',
            'inventory':[{'smiles':'CCO'},{'smiles':'CC(=O)O'}],**updates}


def episode(submit=True,ids=('r1',),**env_options):
    raw=payload();env=SynthesisRouteEnv(build_handoff_task(raw),**env_options)
    env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')})
    if submit:env.dispatch('submit',{'route_ids':list(ids)})
    return build_handoff_manifest(raw),env.export()


def test_legacy_handoff_schema_and_new_provenance_are_bound():
    old=SmallMoleculeHandoff.model_validate(payload(smiles='O=C(OCC)C'))
    assert old.smiles=='CCOC(C)=O'
    richer=payload(source_tool_version='v2',upstream_payload_sha256='a'*64,target_amount_mmol=2)
    manifest=build_handoff_manifest(richer);task=build_handoff_task(richer)
    assert manifest['schema_version']=='srg-small-molecule-manifest-v1'
    assert manifest['handoff']['source_tool_version']=='v2'
    assert manifest['task']==task.model_dump(mode='json') and task.target_amount_mmol==2
    assert manifest['provenance_status']=='caller_supplied_unverified'
    assert manifest['handoff_sha256']!=build_handoff_manifest(payload())['handoff_sha256']
    assert build_handoff_manifest(payload(smiles='O=C(OCC)C'))==build_handoff_manifest(payload())


@pytest.mark.parametrize('updates',[{'seed':True},{'source_tool':' '},{'source_tool_version':' '},
 {'upstream_payload_sha256':'fake'},{'target_amount_mmol':True},{'target_amount_mmol':float('nan')},
 {'inventory':[{'smiles':'CCO'},{'smiles':'OCC'}]},{'api_key':'bad'}])
def test_bad_handoff_requests_fail(updates):
    with pytest.raises(ValueError):SmallMoleculeHandoff.model_validate(payload(**updates))


def test_feedback_preserves_raw_selection_without_claiming_feasibility():
    manifest,export=episode();before=deepcopy((manifest,export))
    result=build_handoff_feedback(manifest,export,episode_id='episode-1')
    assert result['schema_version']=='srg-small-molecule-feedback-v1'
    assert result['candidate_id']=='candidate-1' and result['source_job_id']=='job-1'
    assert result['submission_status']=='submitted_routes'
    assert result['submitted_route_ids']==['r1'] and result['deterministically_eligible_route_ids']==['r1']
    assert result['route_assessments'][0]['source_support_gaps']
    assert result['process_estimates'][0]['status']=='unavailable'
    assert result['resources']['actual_tokens']is None
    assert result['claims_experimental_validation']is False
    assert result['commitment']['durability']=='in_memory_snapshot'
    assert (manifest,export)==before


def test_missing_empty_and_invalid_submissions_remain_distinct():
    manifest,empty=episode(ids=());value=build_handoff_feedback(manifest,empty)
    assert value['submission_status']=='submitted_empty' and value['execution_status']=='completed'
    manifest,missing=episode(submit=False);value=build_handoff_feedback(manifest,missing)
    assert value['submission_status']=='not_submitted' and value['execution_status']=='in_progress'
    raw=payload(inventory=[{'smiles':'CCO'}]);env=SynthesisRouteEnv(build_handoff_task(raw))
    env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')});env.dispatch('submit',{'route_ids':['r1']})
    value=build_handoff_feedback(build_handoff_manifest(raw),env.export())
    assert value['submitted_route_ids']==['r1'] and value['deterministically_eligible_route_ids']==[]


def test_provider_failures_and_unsettled_resources_survive_successful_submission():
    manifest,export=episode()
    agent={'completed':True,'conversation_completed':True,'model':'main-profile-model','provider':'main-provider',
      'provider_request_failures':[{'category':'provider_stream_idle_timeout','exception_type':'TimeoutError','request_id':1}],
      'ledger':{'model_calls':3,'tool_calls':2,'actual_tokens':100,'reserved_tokens':50,'charged_tokens':150,'unsettled_requests':1}}
    result=build_handoff_feedback(manifest,export,agent_run={'agent':agent,'episode':export})
    assert result['execution_status']=='completed' and result['provider_failure_count']==1
    assert result['resources']['actual_tokens']==100 and result['resources']['fully_settled_actual_tokens']is None
    assert result['resources']['reserved_tokens']==50
    assert result['conversation_status']=='completed'


def test_budget_and_external_interruption_are_explicit():
    raw=payload(budget={'max_actions':1});env=SynthesisRouteEnv(build_handoff_task(raw));env.dispatch('inspect',{})
    result=build_handoff_feedback(build_handoff_manifest(raw),env.export())
    assert result['execution_status']=='budget_exhausted' and result['submission_status']=='not_submitted'
    raw=payload();env=SynthesisRouteEnv(build_handoff_task(raw));env.cancel('external interruption')
    result=build_handoff_feedback(build_handoff_manifest(raw),env.export(),agent_run={'agent':{'completed':False,'stop_reason':'bridge_interrupted'}})
    assert result['execution_status']=='interrupted'


@pytest.mark.parametrize('mutation',['task','seed','manifest','chain','submitted','routes','agent_episode'])
def test_mismatched_feedback_inputs_fail(mutation):
    manifest,export=episode();run=None
    if mutation=='task':export['task']['target']='CCO'
    if mutation=='seed':export['seed']=1
    if mutation=='manifest':manifest['handoff']['source_job_id']='changed'
    if mutation=='chain':export['events'][0]['result']['route_id']='changed'
    if mutation=='submitted':export['submitted_route_ids']=[]
    if mutation=='routes':export['routes'][0]['steps'][0]['product']='CCO'
    if mutation=='agent_episode':run={'episode':{**export,'seed':1},'agent':{}}
    with pytest.raises(ValueError):build_handoff_feedback(manifest,export,agent_run=run)


def test_complete_resource_counts_require_consistent_ledger():
    manifest,export=episode();agent={'completed':False,'ledger':{
      'model_calls':1,'tool_calls':2,'actual_tokens':10,'reserved_tokens':0,'charged_tokens':10,'unsettled_requests':0}}
    value=build_handoff_feedback(manifest,export,agent_run={'agent':agent})
    assert value['resources']['fully_settled_actual_tokens']==10
    agent['ledger']['charged_tokens']=0
    with pytest.raises(ValueError):build_handoff_feedback(manifest,export,agent_run={'agent':agent})


def test_recorded_process_estimates_keep_basis_and_missing_cost_explicit():
    from test_portfolio_process import fixture
    t,r,d,b=fixture()
    raw=payload(inventory=t['inventory'],target_amount_mmol=t['target_amount_mmol'])
    env=SynthesisRouteEnv(build_handoff_task(raw),application_config={'process_basis':b})
    env.dispatch('propose_route',{'route':r});env.dispatch('propose_route',{'route':d})
    response=env.dispatch('application_report',{'application':'process_route_selection','route_ids':['convergent','direct']})
    assert response['status']=='ok'
    env.dispatch('submit',{'route_ids':['convergent','direct']})
    result=build_handoff_feedback(build_handoff_manifest(raw),env.export())
    costs=result['process_estimates']
    assert [x['material_cost'] for x in costs]==[51,80]
    assert all(x['status']=='available_declared_estimate' and x['price_evidence_kind']=='illustrative' for x in costs)
    assert costs[0]['basis']['exclusions']==['labor','utilities','workup']
    assert costs[0]['cost_lines'][0]['source']
    assert not costs[0]['claims_process_savings']
    incomplete=payload(inventory=[{**item,'quoted_at':None}for item in t['inventory']],target_amount_mmol=10)
    env=SynthesisRouteEnv(build_handoff_task(incomplete),application_config={'process_basis':b})
    env.dispatch('propose_route',{'route':r})
    env.dispatch('application_report',{'application':'process_route_selection','route_ids':['convergent']})
    env.dispatch('submit',{'route_ids':['convergent']})
    cost=build_handoff_feedback(build_handoff_manifest(incomplete),env.export())['process_estimates'][0]
    assert cost['material_cost'] is None and cost['reason']=='recorded_process_estimate_ineligible'


def test_explicit_direct_tool_has_no_model_conversation():
    manifest,export=episode()
    run={'method':'direct_tool','agent':{'execution_kind':'deterministic_direct_tool','completed':True,
        'ledger':{'model_calls':0,'tool_calls':2,'actual_tokens':0,'reserved_tokens':0,'charged_tokens':0,'unsettled_requests':0}}}
    result=build_handoff_feedback(manifest,export,agent_run=run)
    assert result['conversation_status']=='not_applicable' and result['resources']['fully_settled_actual_tokens']==0
