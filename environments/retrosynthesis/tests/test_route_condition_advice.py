"""Exact host catalogs, real query allowances and evidence-bound one-step advice."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import subprocess
import sys
import pytest
from synthesis_route_gym import route_condition_advice as module

RESOURCES={'remaining_model_calls':6,'remaining_tool_calls':10,'remaining_tokens':200000,'remaining_seconds':300.0}


def catalog(*, observed=('a','b'), attempted=None, used=None, limit=4):
    from synthesis_route_gym.portfolio_conditions import ConditionRecord,FiniteConditionStudy
    from synthesis_route_gym.portfolio_condition_binding import condition_catalog
    from synthesis_route_gym.schemas import ReactionStep
    def recipe(key,reagent):
        return ReactionStep.model_validate({'step_id':key,'reactants':[{'smiles':'CCBr'}],
            'product':'CCO','reagents':[{'smiles':reagent}],'conditions':['base='+reagent],
            'source_tool':'synthetic','source_version':'1'}).model_dump(mode='json')
    rows=[('a','O',11.123),('b','N',22.234),('c','F',88.456),('d','I',99.567)]
    study=FiniteConditionStudy(tuple(ConditionRecord(k,(('base',r),),v)for k,r,v in rows),(),4,
        'https://example.org/source','synthetic table','a'*64,'CCBr')
    binding={'schema_version':'srg-route-condition-binding-v1','study_id':'study','dataset_sha256':'a'*64,
        'source_url':study.source_url,'source_locator':study.source_locator,'reactants':['CCBr'],'product':'CCO',
        'candidates':[{'candidate_id':k,'conditions':{'base':r},'recipe':recipe(k,r)}for k,r,v in rows]}
    observations=[{'candidate_id':k,'conditions':{'base':r},'yield_percent':v,
        'dataset_sha256':study.dataset_sha256,'source_record_id':f'study:{study.dataset_sha256}:{_sha(k)[:20]}',
        'evidence_kind':'measured_dataset_replay','new_experiment_performed':False}for k,r,v in rows if k in observed]
    result=condition_catalog(recipe('s1','O'),study,binding,observations=observations)
    used=len(observed)if used is None else used
    return {**result,'route_step_reference':{'route_id':'r1','route_sha256':'b'*64,'parent_route_id':None,
        'step_id':'s1','step_sha256':'c'*64},'application_configuration_sha256':'d'*64,
        'offset':0,'candidate_count':4,'next_offset':None,
        'observation_resources':{'schema_version':'srg-route-observation-resources-v1','calls_used':used,
            'call_limit':limit,'remaining_calls':max(0,limit-used),
            'attempted_candidate_ids':list(observed)if attempted is None else list(attempted)}}


def _sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def response(value,**patch):
    return {'status':'ok','result':value,'terminated':False,'truncated':False,**patch}


def ingest(value=None,state=None,**patch):
    return module.observe(module.initial_state()if state is None else state,'condition_options',
        {'route_id':'r1','step_id':'s1','offset':0,'limit':20},response(catalog()if value is None else value,**patch))


def context(value=None):return module.build_context(ingest(value),RESOURCES)


def plan(ctx,**patch):
    return {'schema_version':'srg-route-condition-plan-v1','context_sha256':module.context_fingerprint(ctx),
        'decision':'observe','next_candidate_id':'c','cited_observation_ids':[ctx['catalog']['observations'][0]['source_record_id']],
        'rationale':'Compare another registered condition after the revealed measurements.',
        'evidence_status':'agent_proposal',**patch}


def test_real_step10_catalog_binds_available_candidate_without_hidden_outcomes():
    ctx=context();assert ctx['schema_version']=='srg-route-condition-context-v1'
    assert '88.456'not in json.dumps(ctx)and'99.567'not in json.dumps(ctx)
    selected=module.parse_plan(json.dumps(plan(ctx)),ctx);hydrated=module.hydrate_plan(selected,ctx)
    assert hydrated['next_action']=={'action':'observe_route_condition','arguments':{'route_id':'r1','step_id':'s1','candidate_id':'c'}}
    assert hydrated['selected_candidate']['candidate_id']=='c'
    assert hydrated['supporting_observations'][0]['yield_percent']==11.123
    assert hydrated['evidence_status']=='agent_proposal'


@pytest.mark.parametrize('value',[{'observed':()},{'observed':('a',)}, {'used':4},
    {'attempted':('a','b','c','d'),'used':3}, {'observed':('a','b','c','d'),'used':4}])
def test_ineligible_feedback_or_exhausted_queries(value):
    assert module.build_context(ingest(catalog(**value)),RESOURCES)is None


def test_resource_counts_include_failed_and_initial_attempted_candidates():
    ctx=context(catalog(attempted=('a','b','c','initial-other'),used=3))
    assert module.parse_plan(json.dumps(plan(ctx,next_candidate_id='d')),ctx)['next_candidate_id']=='d'
    with pytest.raises(ValueError):module.parse_plan(json.dumps(plan(ctx)),ctx)


@pytest.mark.parametrize('field,value',[('application_configuration_sha256','e'*64),('current_recipe_sha256','e'*64),
    ('binding_sha256','e'*64),('study_id','other'),('candidate_count',5)])
def test_changed_context_fails_closed(field,value):
    first=ingest();changed={**catalog(),field:value}
    with pytest.raises(ValueError):ingest(changed,state=first)


@pytest.mark.parametrize('mutation',['route','step','recipe','factor','recipe_hash','recipe_match','observed_value',
    'observed_conditions','observed_source','observed_recipe','observed_missing','calls_reset','allowance_reset','remaining_fake','attempt_reset','unknown_field'])
def test_invalid_or_rewritten_public_evidence_rejected(mutation):
    first=ingest();changed=deepcopy(catalog())
    if mutation=='route':changed['route_step_reference']['route_id']='r2'
    if mutation=='step':changed['route_step_reference']['step_sha256']='e'*64
    if mutation=='recipe':changed['candidates'][2]['recipe']['product']='CCN'
    if mutation=='factor':changed['candidates'][2]['conditions']['base']='O'
    if mutation=='recipe_hash':changed['candidates'][2]['recipe_sha256']='e'*64
    if mutation=='recipe_match':changed['candidates'][2]['recipe_matches_current_step']=True
    if mutation=='observed_value':changed['observations'][0]['yield_percent']=70
    if mutation=='observed_conditions':changed['observations'][0]['conditions']={'base':'N'}
    if mutation=='observed_source':changed['observations'][0]['source_record_id']='invented'
    if mutation=='observed_recipe':changed['observations'][0]['recipe']['reagents']=[{'smiles':'N','amount_mmol':None}]
    if mutation=='observed_missing':changed['observations']=changed['observations'][1:];changed['observation_count']=1
    if mutation=='calls_reset':changed['observation_resources']['calls_used']=1;changed['observation_resources']['remaining_calls']=3
    if mutation=='allowance_reset':changed['observation_resources']['call_limit']=3;changed['observation_resources']['remaining_calls']=1
    if mutation=='remaining_fake':changed['observation_resources']['remaining_calls']=3
    if mutation=='attempt_reset':changed['observation_resources']['attempted_candidate_ids']=['a']
    if mutation=='unknown_field':changed['private_optimum']=99
    with pytest.raises(ValueError):ingest(changed,state=first)


def test_paginated_catalog_requires_complete_exact_bound_merge():
    full=catalog();first={**full,'candidates':full['candidates'][:2],'next_offset':2}
    state=module.observe(module.initial_state(),'condition_options',{'route_id':'r1','step_id':'s1','offset':0,'limit':2},response(first))
    assert module.build_context(state,RESOURCES)is None
    second={**full,'candidates':full['candidates'][2:],'offset':2}
    state=module.observe(state,'condition_options',{'route_id':'r1','step_id':'s1','offset':2,'limit':2},response(second))
    assert module.build_context(state,RESOURCES)['catalog']['candidates']==full['candidates']
    assert module.validate_state(state)==state


def test_conflicting_paginated_slot_rejected():
    full=catalog();first={**full,'candidates':full['candidates'][:2],'next_offset':2}
    args={'route_id':'r1','step_id':'s1','offset':0,'limit':2}
    state=module.observe(module.initial_state(),'condition_options',args,response(first))
    changed=deepcopy(first);changed['candidates'][0],changed['candidates'][1]=changed['candidates'][1],changed['candidates'][0]
    with pytest.raises(ValueError):module.observe(state,'condition_options',args,response(changed))


def test_latest_wrapper_catalog_includes_new_measurement():
    state=ingest(catalog(observed=('a',)))
    wrapped={'route_step_reference':catalog()['route_step_reference'],'condition_catalog':catalog()}
    updated=module.observe(state,'observe_route_condition',{'route_id':'r1','step_id':'s1','candidate_id':'b'},response(wrapped))
    assert module.build_context(updated,RESOURCES)is not None


def test_failed_wrapper_with_catalog_still_accounts_for_failed_attempt():
    state=ingest();updated=module.observe(state,'observe_route_condition',{'route_id':'r1','step_id':'s1','candidate_id':'c'},
        response({'condition_catalog':catalog(attempted=('a','b','c'),used=3)},status='error'))
    ctx=module.build_context(updated,RESOURCES)
    assert module.parse_plan(json.dumps(plan(ctx,next_candidate_id='d')),ctx)
    with pytest.raises(ValueError):module.parse_plan(json.dumps(plan(ctx)),ctx)


@pytest.mark.parametrize('action',['observe_route_condition','observe_condition','condition_observation'])
def test_unknown_new_query_accounting_requires_fresh_catalog(action):
    state=module.observe(ingest(),action,{'candidate_id':'c'},response({},status='error'))
    assert module.build_context(state,RESOURCES)is None
    assert module.build_context(ingest(catalog(attempted=('a','b','c'),used=3),state=state),RESOURCES)is not None


@pytest.mark.parametrize('patch',[{'terminated':True},{'truncated':True}])
def test_closed_episode_never_builds_context(patch):
    assert module.build_context(ingest(**patch),RESOURCES)is None


def test_submit_closes_even_without_a_condition_catalog():
    state=module.observe(ingest(),'submit',{'route_ids':['r1']},response({}))
    assert module.build_context(state,RESOURCES)is None


@pytest.mark.parametrize('patch',[{'context_sha256':'e'*64},{'next_candidate_id':'unknown'},
    {'next_candidate_id':'a'},{'cited_observation_ids':['invented']},{'cited_observation_ids':[]},
    {'decision':'abstain'},{'rationale':''},{'evidence_status':'measured'}, {'extra':'fake yield'},
    {'cited_observation_ids':['same','same']}])
def test_invalid_model_plan_rejected(patch):
    ctx=context()
    with pytest.raises(ValueError):module.parse_plan(json.dumps(plan(ctx,**patch)),ctx)


def test_abstain_is_valid_and_never_gets_an_action():
    ctx=context();value=plan(ctx,decision='abstain',next_candidate_id=None,cited_observation_ids=[])
    assert module.hydrate_plan(value,ctx)['next_action']is None


@pytest.mark.parametrize('text',['{}','not-json','{"decision":"observe","decision":"abstain"}','{"n":NaN}'])
def test_strict_json_contract(text):
    with pytest.raises(ValueError):module.parse_plan(text,context())


def test_contract_is_immutable_and_rejects_changed_resume_state():
    state=ingest();before=deepcopy(state);ctx=module.build_context(state,RESOURCES)
    ctx['catalog']['candidates'][0]['conditions']['base']='N'
    assert state==before
    changed=deepcopy(state);changed['identity_sha256']='e'*64
    with pytest.raises(ValueError):module.validate_state(changed)


def test_isolated_import_has_no_rdkit_dependency():
    script="""import builtins\noriginal=builtins.__import__\ndef guarded(name,*args,**kwargs):\n if name.startswith(('rdkit','synthesis_route_gym.schemas','synthesis_route_gym.portfolio')):raise RuntimeError(name)\n return original(name,*args,**kwargs)\nbuiltins.__import__=guarded\nimport synthesis_route_gym.route_condition_advice\nimport synthesis_route_gym.route_condition_runtime\nprint('pure imports')\n"""
    result=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
