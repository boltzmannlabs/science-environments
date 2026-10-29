"""Public-only selection and evaluator-only error/retention scoring."""
from copy import deepcopy
import json
import pytest
from synthesis_route_gym import critic_benchmark as benchmark
from synthesis_route_gym.evidence_contracts import SourceRecord, public_projection
from synthesis_route_gym.schemas import Task, RouteCandidate
from synthesis_route_gym.validation import assess_route


def fixture():
    task=Task.model_validate({'task_id':'case-one','target':'CCO','inventory':[{'smiles':'CC=O'},{'smiles':'CO'}],
        'budget':{'max_actions':80,'max_expansions':6,'max_wall_seconds':600,'max_llm_tokens':350000,'top_k':3}})
    def route(ident,reactants):
        return RouteCandidate.model_validate({'route_id':ident,'target':'CCO','steps':[{'step_id':'step-one',
            'product':'CCO','reactants':[{'smiles':v}for v in reactants],
            'source_tool':'fixture','source_version':'1','evidence_ids':['source-one']}]})
    routes=[route('r-control',['CC=O']),route('r-hard',['CC=O','O']),route('r-unsupported',['CO'])]
    source=SourceRecord(record_id='source-one',document_id='document-one',source_url='https://example.org/source',
        locator='record 1',reactants=('CC=O',),product='CCO',claim_kind='proxy',
        retrieved_at='2020-01-01T00:00:00Z',source_content_sha256='a'*64)
    packet={'schema_version':'srg-route-review-v1','routes':[r.model_dump(mode='json')for r in routes],
        'assessments':[assess_route(task,r).model_dump(mode='json')for r in routes],
        'sources':[public_projection(source)],'facts':[]}
    public={'schema_version':'srg-critic-development-case-v1','case_id':'case-one',
        'data_role':'previously_used_development','task':task.model_dump(mode='json'),
        'routes':packet['routes'],'sources':[source.model_dump(mode='json')],
        'source_family':'fixture','source_case_id':'source-case','source_provenance':[],
        'limitations':['Synthetic software fixture.']}
    public['case_inputs_sha256']=benchmark.case_digest(public)
    labels={'schema_version':'srg-critic-labels-v1','case_id':public['case_id'],
        'case_inputs_sha256':public['case_inputs_sha256'],'routes':{},'label_basis':'Frozen synthetic fixture.'}
    for key,hard,source_ok,errors,reviews in [
        ('r-control',True,True,[],['incomplete_conditions']),
        ('r-hard',False,False,['missing_materials'],[]),
        ('r-unsupported',True,False,[],['unsupported_transformation'])]:
        labels['routes'][key]={'hard_valid':hard,'source_consistent':source_ok,'retain':hard and source_ok,
            'expected_categories':errors+reviews,'expected_error_categories':errors,
            'expected_review_categories':reviews,'mutation_kind':'synthetic'}
    return public,labels,packet


def decision(ids,status=None):
    return {'case_id':'case-one','submitted_route_ids':ids,
        'submission_status':status or ('submitted_routes'if ids else 'submitted_empty')}


def test_direct_keeps_incomplete_source_consistent_control_without_mutation():
    _,_,packet=fixture();before=deepcopy(packet)
    assert benchmark.select_review_routes(packet)==['r-control']
    assert packet==before


def test_direct_keeps_multiple_controls_without_measured_authority():
    _,_,packet=fixture();clone=deepcopy(packet['routes'][0]);clone['route_id']='r-second'
    assessment=deepcopy(packet['assessments'][0]);assessment['route_id']='r-second'
    packet['routes']=[clone,packet['routes'][0]];packet['assessments']=[assessment,packet['assessments'][0]]
    assert benchmark.select_review_routes(packet)==['r-control','r-second']


@pytest.mark.parametrize('change',[lambda p:p.update(schema_version='wrong'),
    lambda p:p['routes'].append(p['routes'][0]),lambda p:p.update(assessments=[]),
    lambda p:p['assessments'][0].update(graph_valid='true')])
def test_policy_rejects_malformed_packet(change):
    _,_,packet=fixture();change(packet)
    with pytest.raises(ValueError):benchmark.select_review_routes(packet)


def test_reactant_multiplicity_not_erased():
    _,_,packet=fixture();packet['sources'][0]['reactants']=['CC=O','CC=O']
    assert benchmark.select_review_routes(packet)==[]


def test_raw_invalid_and_unsupported_are_separate():
    public,labels,_=fixture();score=benchmark.score_critic_decision(public,labels,decision(['r-control','r-hard','r-unsupported']))
    assert score['invalid_submitted_count']==1 and score['unsupported_submitted_count']==1
    assert score['source_controls_retained']==1 and score['source_control_retention']==1
    assert score['invalid_submitted_fraction']==pytest.approx(1/3)
    assert score['strict_selection_success']is False


def test_empty_or_missing_cannot_win_by_rejecting_everything():
    public,labels,_=fixture()
    for status in ['submitted_empty','not_submitted']:
        score=benchmark.score_critic_decision(public,labels,decision([],status))
        assert score['false_rejection_count']==1 and score['source_control_retention']==0
        assert score['invalid_submitted_fraction']is None
        assert score['strict_selection_success']is False
        assert score['missing_submission']==(status=='not_submitted')


def test_exact_control_selection_succeeds():
    public,labels,_=fixture();score=benchmark.score_critic_decision(public,labels,decision(['r-control']))
    assert score['strict_selection_success']is True
    assert score['invalid_submitted_count']==score['unsupported_submitted_count']==score['false_rejection_count']==0


@pytest.mark.parametrize('change',[lambda p,l,d:p['routes'][0]['steps'][0].update(product='CO'),
    lambda p,l,d:l.update(case_inputs_sha256='f'*64),lambda p,l,d:l['routes'].pop('r-hard'),
    lambda p,l,d:l['routes']['r-control'].update(retain='true'),
    lambda p,l,d:d.update(submitted_route_ids=['absent']),
    lambda p,l,d:d.update(submitted_route_ids=['r-control','r-control']),
    lambda p,l,d:d.update(submission_status='not_submitted'),
    lambda p,l,d:l['routes']['r-hard'].update(retain=True)])
def test_stale_or_invalid_bindings_rejected(change):
    public,labels,_=fixture();d=decision(['r-control']);change(public,labels,d)
    with pytest.raises(ValueError):benchmark.score_critic_decision(public,labels,d)


def test_unknown_review_is_not_a_negative_chemistry_label():
    public,labels,_=fixture();findings=[
        {'route_id':'r-hard','category':'missing_materials','severity':'error'},
        {'route_id':'r-control','category':'incomplete_conditions','severity':'review'},
        {'route_id':'r-control','category':'stereochemistry','severity':'review'},
        {'route_id':'r-unsupported','category':'unsupported_transformation','severity':'error'}]
    score=benchmark.score_critic_findings(public,labels,findings)
    assert score['true_error_findings']==1 and score['false_error_findings']==1
    assert score['matched_review_findings']==1 and score['unlabeled_review_findings']==1
    assert score['error_category_precision']==.5 and score['error_category_recall']==1


@pytest.mark.parametrize('findings',[[{'route_id':'x','category':'missing_materials','severity':'error'}]])
def test_invalid_finding_references_rejected(findings):
    public,labels,_=fixture()
    with pytest.raises(ValueError):benchmark.score_critic_findings(public,labels,findings)


def test_closed_prompt_and_tools():
    public,_,_=fixture();prompt=benchmark.critic_selection_prompt(public)
    assert 'source-consistent'in prompt and 'uncertainty'in prompt
    assert 'expected_categories'not in prompt and 'mutation'not in prompt
    assert {s['name']for s in benchmark.critic_selection_schemas()}=={'inspect','review_routes','validate','submit'}


def run_fixture(arm='main',ids=None,settled=True):
    public,labels,packet=fixture();ids=['r-control']if ids is None else ids
    agent={}if arm=='direct_tool'else {'model':'main-model','provider':'main-provider',
        'conversation_completed':True,'ledger':{'model_calls':3,'actual_tokens':100,
        'charged_tokens':100 if settled else 120,'reserved_tokens':0 if settled else 20,
        'unsettled_requests':0 if settled else 1},'route_critic_runs':[],
        'route_critic_state':{'consultation':None}}
    return public,labels,{'method':arm,'case_id':public['case_id'],'agent':agent,
        'bootstrap':{'actions':4},'episode':{'task':public['task'],'routes':public['routes'],
        'submitted_route_ids':ids,'terminated':True,'truncated':False,
        'events':[],'usage':{'actions':6,'wall_seconds':2.0}}}


def test_summary_retains_unconfirmed_usage_and_consumed_failed_advice():
    public,labels,run=run_fixture('main_route_critic',settled=False)
    run['agent']['route_critic_state']['consultation']={'status':'failed','report':None}
    run['agent']['route_critic_runs']=[{'completed':False}]
    score=benchmark.score_critic_decision(public,labels,decision(['r-control']))
    row=benchmark.summarize_critic_run(public,run,score,repeat_id=0)
    assert row['actual_tokens']==100 and row['fully_settled_actual_tokens']is None
    assert row['reserved_tokens']==20 and row['critic_status']=='failed'and row['critic_invocations']==1
    assert row['environment_actions']==6 and row['bootstrap_actions']==4 and row['policy_actions']==2


def test_comparison_includes_all_three_arms_and_failure_retention():
    rows=[]
    for arm in benchmark.ARMS:
        public,labels,run=run_fixture(arm,ids=[]if arm=='main'else None)
        score=benchmark.score_critic_decision(public,labels,decision(run['episode']['submitted_route_ids']))
        rows.append(benchmark.summarize_critic_run(public,run,score,repeat_id=0))
    summary=benchmark.summarize_critic_comparison(rows)
    assert summary['aggregate']['main']['source_control_retention']==0
    assert summary['aggregate']['main']['invalid_submitted_fraction']is None
    assert summary['aggregate']['direct_tool']['model_calls']==0
    assert summary['paired_strict_selection']['wins']==1
    assert summary['promotion_eligible']is False
    with pytest.raises(ValueError):benchmark.summarize_critic_comparison(rows[1:])
    changed=deepcopy(rows);changed[1]['case_inputs_sha256']='b'*64
    with pytest.raises(ValueError):benchmark.summarize_critic_comparison(changed)
    with pytest.raises(ValueError):benchmark.summarize_critic_comparison(rows+[rows[0]])


def test_missing_ledger_is_unknown_not_zero():
    public,labels,run=run_fixture();run['agent']={'completed':False,'model':'main-model','provider':'main-provider'}
    score=benchmark.score_critic_decision(public,labels,decision(['r-control']))
    row=benchmark.summarize_critic_run(public,run,score,repeat_id=0)
    assert row['actual_tokens']is None and row['fully_settled_actual_tokens']is None


def test_summary_rejects_changed_run_pool():
    public,labels,run=run_fixture();score=benchmark.score_critic_decision(public,labels,decision(['r-control']))
    run['episode']['routes']=deepcopy(run['episode']['routes']);run['episode']['routes'][0]['steps'][0]['conditions']=['different']
    with pytest.raises(ValueError):benchmark.summarize_critic_run(public,run,score,repeat_id=0)


def test_matching_uncited_source_does_not_repair_wrong_declared_citation():
    _,_,packet=fixture();packet['routes'][0]['steps'][0]['evidence_ids']=['wrong-source']
    assert benchmark.select_review_routes(packet)==[]


def test_distinct_or_repeated_findings_use_unique_route_category_severity_units():
    public,labels,_=fixture()
    first={'route_id':'r-hard','category':'missing_materials','severity':'error','step_id':'one','supporting_fact_ids':['a']}
    second={**first,'step_id':'two','supporting_fact_ids':['b']}
    score=benchmark.score_critic_findings(public,labels,[first,second,first])
    assert score['true_error_findings']==1 and score['matched_error_categories']==1
    assert score['unit']=='unique_route_category_severity'


@pytest.mark.parametrize('quantity_status,eligible',[
    ('complete',True),('not_requested',True),('unknown',False),('insufficient',False)])
def test_direct_quantity_gate_matches_submission(quantity_status,eligible):
    _,_,packet=fixture()
    packet['assessments'][0]['quantity_status']=quantity_status
    assert benchmark.select_review_routes(packet)==(['r-control']if eligible else [])


@pytest.mark.parametrize('statuses,attempted,completed',[
    ([],False,False),(['error'],True,False),(['error','ok'],True,True),(['ok'],True,True)])
def test_summary_distinguishes_recheck_attempts_and_completion(statuses,attempted,completed):
    public,labels,run=run_fixture('main_route_critic')
    recommendation={'action':'validate','arguments':{'route_id':'r-control'}}
    run['agent']['route_critic_state']['consultation']={'status':'accepted',
        'recommendation':{'recommended_recheck':recommendation}}
    run['episode']['events']=[{'action':'review_routes','status':'ok','arguments':{}}]+[
        {**recommendation,'status':status}for status in statuses]
    score=benchmark.score_critic_decision(public,labels,decision(['r-control']))
    row=benchmark.summarize_critic_run(public,run,score,repeat_id=0)
    assert row['critic_recommended_recheck_attempted']is attempted
    assert row['critic_recommended_recheck_used']is completed
    assert row['rechecks']==len(statuses)
    assert row['completed_rechecks']==statuses.count('ok')


def test_label_category_union_must_match_severity_annotations():
    public,labels,_=fixture()
    labels['routes']['r-hard']['expected_categories']=[]
    with pytest.raises(ValueError,match='union'):
        benchmark.score_critic_decision(public,labels,decision(['r-control']))
