"""Typed advice derives from bounded host observations, never trusted chemistry."""
import copy
import json
import pytest
from synthesis_route_gym.strategist import StrategistPlan, observer_state, observe, build_context, parse_plan, context_fingerprint
RESOURCES={'remaining_model_calls':4,'remaining_tool_calls':8,'remaining_tokens':10000,'remaining_seconds':90.0}
def result(data=None,status='ok',**extra):
    return {'status':status,'result':data or {},'terminated':False,'truncated':False,'usage':{'expansions':0},**extra}
def initialized():
    return observe(observer_state(),'inspect',{},result({'task':{'target':'CCOC','constraints':{'max_steps':4},'budget':{'max_expansions':12}}}))
def expansion(state,product,reactants=(),status='ok'):
    rows=[{'product':product,'reactants':list(reactants)}] if reactants else []
    return observe(state,'expand',{'smiles':product},result({'predictions':rows},status,usage={'expansions':(state.get('expansions_used') or 0)+1}))
def stalled():
    state=expansion(initialized(),'CCOC',('CCO','C'))
    return expansion(expansion(state,'CCO',status='error'),'CCO',status='error')
def plan(context,**changes):
    return {'schema_version':'srg-strategist-plan-v1','context_sha256':context_fingerprint(context),
            'candidate_route_ids':[],'next_expansion_targets':['C'],'alternative_disconnection_ids':[],
            'relevant_constraint_keys':['max_steps'],'action_allowance':1,
            'rationale':'Inspect the remaining observed branch.','evidence_status':'agent_proposal',**changes}
def test_immutable_observation_without_trigger():
    state=initialized();old=copy.deepcopy(state)
    assert build_context(state,RESOURCES) is None
    expanded=expansion(state,'CCOC',('CCO','C'))
    assert state==old and expanded!=state and build_context(expanded,RESOURCES) is None

def test_failed_expansions_trigger_remaining_frontier():
    context=build_context(stalled(),RESOURCES)
    assert context['trigger']=='stalled_expansion'
    assert context['frontier']==[{'smiles':'C','inventory_status':'unknown'}]
    assert context['constraints']['max_steps']==4 and context['failed_branches']
    assert parse_plan(json.dumps(plan(context)),context)['evidence_status']=='agent_proposal'

def test_inventory_zero_is_unavailable_positive_is_excluded():
    state=stalled()
    missing=observe(state,'inspect',{},result({'inventory_matches':[{'smiles':'C','item':{'smiles':'C','available_mmol':0}}]}))
    assert build_context(missing,RESOURCES)['frontier'][0]['inventory_status']=='unavailable'
    stock=observe(state,'inspect',{},result({'inventory_matches':[{'smiles':'C','item':{'smiles':'C','available_mmol':None}}]}))
    assert build_context(stock,RESOURCES) is None

def test_missing_assessment_triggers_without_copying_agent_claims():
    state=expansion(initialized(),'CCOC',('CCO','C'))
    route={'route_id':'r1','steps':[{'product':'CCOC','reactants':[{'smiles':'CCO'},{'smiles':'C'}]}],'secret_label':99}
    state=observe(state,'propose_route',{'route':route},result({'route_id':'r1','assessment':{'route_id':'r1','unstocked':['CCO'],'weak_steps':['s1']}}))
    context=build_context(state,RESOURCES)
    assert context['trigger']=='inventory_obligation' and context['candidate_route_ids']==['r1']
    assert 'r1:s1' in context['evidence_gaps'] and 'secret_label' not in json.dumps(context)

def test_exact_missing_frontier_inspection_after_two_expansions_triggers():
    state=expansion(expansion(initialized(),'CCOC',('CCO','C')),'CCO',('CO','C'))
    state=observe(state,'inspect',{},result({'inventory_matches':[{'smiles':'CO','item':None}]}))
    assert build_context(state,RESOURCES)['trigger']=='inventory_obligation'

def test_duplicate_route_core_preserves_ids():
    state=expansion(initialized(),'CCOC',('CCO','C'))
    for ident in ('r1','r2'):
        route={'route_id':ident,'steps':[{'product':'CCOC','reactants':[{'smiles':'C'},{'smiles':'CCO'}]}]}
        state=observe(state,'inspect',{'route_ids':[ident]},result({'routes':[route]}))
    context=build_context(state,RESOURCES)
    assert context['trigger']=='equivalent_route' and context['candidate_route_ids']==['r1','r2']

def test_alternative_identity_preserves_multiset_and_host_canonical_identity():
    a=expansion(initialized(),'CCOC',('C','CCO'));b=expansion(initialized(),'CCOC',('CCO','C'))
    c=expansion(initialized(),'CCOC',('CCO','C','C'))
    assert a['alternatives']==b['alternatives'] and a['alternatives'][0]['id']!=c['alternatives'][0]['id']

def test_self_cycle_excluded():
    state=expansion(initialized(),'CCOC',('CCOC','C'))
    assert state['alternatives']==[] and build_context(state,RESOURCES) is None

@pytest.mark.parametrize('change',[{'candidate_route_ids':['invented']},{'next_expansion_targets':['N']},
    {'next_expansion_targets':['CCO']},{'alternative_disconnection_ids':['invented']},
    {'relevant_constraint_keys':['relax_safety']},{'action_allowance':3},{'action_allowance':True},
    {'action_allowance':0},{'evidence_status':'measured'},{'context_sha256':'0'*64},
    {'schema_version':'wrong'},{'yield':99},{'next_expansion_targets':['C','C']},{'rationale':' '}])
def test_forged_or_unbounded_plans_rejected(change):
    context=build_context(stalled(),RESOURCES)
    with pytest.raises(ValueError):parse_plan(json.dumps(plan(context,**change)),context)

def test_allowance_and_empty_plan():
    context=build_context(stalled(),{**RESOURCES,'remaining_tool_calls':1})
    with pytest.raises(ValueError):parse_plan(json.dumps(plan(context,action_allowance=2)),context)
    assert parse_plan(json.dumps(plan(context,next_expansion_targets=[],action_allowance=0)),context)['action_allowance']==0

def test_fingerprint_is_order_independent_but_resource_bound():
    context=build_context(stalled(),RESOURCES)
    assert context_fingerprint(context)==context_fingerprint(dict(reversed(list(context.items()))))
    changed={**context,'resources':{**context['resources'],'remaining_seconds':89}}
    assert context_fingerprint(context)!=context_fingerprint(changed)

@pytest.mark.parametrize('text',['```json\n{}\n```','{"x":1,"x":2}','NaN','[]','x'*20001])
def test_strict_json_only(text):
    with pytest.raises(ValueError):parse_plan(text,build_context(stalled(),RESOURCES))

def test_closed_uninitialized_and_invalid_resources():
    assert build_context(observer_state(),RESOURCES) is None
    assert build_context(observe(stalled(),'submit',{},result({},terminated=True)),RESOURCES) is None
    for value in (float('nan'),True,-1):
        with pytest.raises(ValueError):build_context(stalled(),{**RESOURCES,'remaining_seconds':value})

def test_bounds_and_truncation():
    state=initialized();rows=[{'product':'CCOC','reactants':['C'*i]}for i in range(1,70)]
    state=observe(state,'expand',{'smiles':'CCOC'},result({'predictions':rows}))
    state=expansion(expansion(state,'C',status='error'),'C',status='error')
    context=build_context(state,RESOURCES)
    assert len(json.dumps(state).encode())<=20000 and len(json.dumps(context).encode())<=20000
    assert state['truncated'] and context['truncated']
    assert len(context['frontier'])<=24 and len(context['alternatives'])<=12

def test_plan_frozen():
    parsed=StrategistPlan.model_validate(plan(build_context(stalled(),RESOURCES)))
    with pytest.raises(ValueError):parsed.action_allowance=2


def test_successful_expansion_uses_host_identity_not_caller_alias():
    state=expansion(initialized(),'CCOC',('CCO','C'))
    state=observe(state,'expand',{'smiles':'OCC'},result({'predictions':[{'product':'CCO','reactants':['CO','C']}]}))
    state=expansion(expansion(state,'CCO',status='error'),'CCO',status='error')
    context=build_context(state,RESOURCES)
    assert 'CCO' not in [r['smiles']for r in context['frontier']]
    assert 'OCC' not in json.dumps(context)

def test_unrelated_failed_caller_text_is_not_observed_chemistry():
    before=initialized()
    after=observe(before,'expand',{'smiles':'invented caller assertion'},result(status='error'))
    assert after==before

def test_proposal_arguments_cannot_seed_chemistry_or_duplicate_identity():
    state=initialized()
    forged={'route':{'route_id':'invented','steps':[{'product':'N','reactants':[{'smiles':'O'}]}]}}
    state=observe(state,'propose_route',forged,result({'route_id':'r1','assessment':{'route_id':'r1','unstocked':[]}}))
    assert state['route_cores']=={} and state['frontier']==['CCOC']
    assert state['candidate_route_ids']==['r1']

def test_module_imports_without_rdkit():
    import subprocess,sys
    code="import sys; sys.modules['rdkit']=None; import synthesis_route_gym.strategist; print('ok')"
    run=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
    assert run.returncode==0,run.stderr


def test_inventory_lookup_before_frontier_is_retained():
    state=observe(initialized(),'inspect',{},result({'inventory_matches':[{'smiles':'CCO','item':None},{'smiles':'C','item':{'smiles':'C'}}]}))
    state=expansion(state,'CCOC',('CCO','C'))
    state=expansion(state,'CCOC',('CCO','C'))
    context=build_context(state,RESOURCES)
    assert context['frontier']==[{'smiles':'CCO','inventory_status':'unavailable'}]
    assert context['trigger']=='inventory_obligation'

def test_failed_invalid_expand_without_identity_is_observer_noop():
    state=initialized()
    assert observe(state,'expand',{},result(status='error'))==state

def test_inventory_and_constraint_size_bounds_fail_closed():
    entries=[{'smiles':'C'*i,'available_mmol':1}for i in range(300,500)]
    state=observe(initialized(),'inspect',{},result({'inventory_page':entries}))
    assert len(state['inventory'])<=64 and len(json.dumps(state).encode())<=20000
    assert state['truncated']
    oversized=observe(initialized(),'inspect',{},result({'task':{'target':'CCOC',
        'constraints':{'available_equipment':['x'*25000]}}}))
    assert oversized['closed'] and oversized['saturated'] and oversized['truncated']
    assert len(json.dumps(oversized).encode())<=20000
    assert build_context(oversized,RESOURCES) is None

def test_checked_inventory_page_and_alternative_selection():
    state=observe(stalled(),'inspect',{},result({'inventory_page':[{'smiles':'C','available_mmol':0}]}))
    context=build_context(state,RESOURCES)
    proposal=plan(context,alternative_disconnection_ids=[context['alternatives'][0]['id']])
    assert parse_plan(json.dumps(proposal),context)['alternative_disconnection_ids']==proposal['alternative_disconnection_ids']

def test_seen_expansion_saturation_disables_advice():
    state=initialized()
    for i in range(1,40):
        molecule='C'*i
        state={**state,'frontier':[molecule]}
        state=expansion(state,molecule,status='error')
    assert state['saturated'] and state['truncated']
    assert len(state['expanded'])<=32 and build_context(state,RESOURCES) is None

def test_expansion_before_inspect_replays_after_authoritative_target():
    state=expansion(observer_state(),'CCOC',('CCO','C'))
    assert state['target'] is None and state['frontier']==[]
    state=observe(state,'inspect',{},result({'task':{'target':'CCOC','constraints':{'max_steps':4},'budget':{'max_expansions':12}}}))
    assert state['expansion_count']==1
    state=expansion(state,'CCO',('CO','C'))
    state=observe(state,'inspect',{},result({'inventory_matches':[{'smiles':'CO','item':None}]}))
    context=build_context(state,RESOURCES)
    assert context['trigger']=='inventory_obligation' and state['expansion_count']==2
    assert {'C','CO'} <= {r['smiles']for r in context['frontier']}
    state=observe(state,'inspect',{},result({'task':{'target':'CCOC','constraints':{'max_steps':4},'budget':{'max_expansions':12}}}))
    assert state['expansion_count']==2

def test_pending_does_not_infer_target_or_keep_untrusted_metadata():
    state=observe(observer_state(),'expand',{'smiles':'wrong caller alias','private_label':99},result({'predictions':[
        {'product':'CCOC','reactants':['CCO','C'],'yield_percent':99,'evidence_status':'measured','source':'secret'}]}))
    assert state['target'] is None and build_context(state,RESOURCES) is None
    assert all(x not in json.dumps(state)for x in ('private_label','yield_percent','measured','secret','wrong caller alias'))
    state=observe(state,'inspect',{},result({'task':{'target':'N','constraints':{},'budget':{'max_expansions':12}}}))
    assert state['frontier']==['N'] and state['alternatives']==[] and state['expansion_count']==0

def test_pending_follows_reachability_without_double_count():
    state=expansion(observer_state(),'CCOC',('CCO','C'))
    state=expansion(state,'CCO',('CO','C'))
    state=expansion(state,'N',('O',))
    state=observe(state,'inspect',{},result({'task':{'target':'CCOC','constraints':{},'budget':{'max_expansions':12}}}))
    assert state['expansion_count']==2
    assert all(row['product']!='N'for row in state['alternatives'])
    assert state['pending_expansions']==[]

def test_pending_overflow_disables_advice_and_bounds_checkpoint():
    state=observer_state()
    for _ in range(10):state=expansion(state,'CCOC',('CCO','C'))
    assert state['truncated'] and state['saturated']
    assert len(state['pending_expansions'])<=8 and len(json.dumps(state).encode())<=20000

def test_exhausted_expansion_budget_suppresses_advice():
    state=observe(stalled(),'inspect',{},result({'task':{'target':'CCOC','constraints':{},'budget':{'max_expansions':6}}},usage={'expansions':6}))
    assert build_context(state,RESOURCES) is None

def test_plan_allowance_capped_by_actual_remaining_expansions():
    state=observe(stalled(),'inspect',{},result({'task':{'target':'CCOC','constraints':{'max_steps':4},'budget':{'max_expansions':6}}},usage={'expansions':5}))
    context=build_context(state,RESOURCES)
    assert context['resources']['remaining_expansions']==1
    with pytest.raises(ValueError):parse_plan(json.dumps(plan(context,action_allowance=2)),context)

def test_unknown_expansion_budget_suppresses_advice():
    state=expansion(observer_state(),'CCOC',('CCO','C'))
    state=observe(state,'inspect',{},result({'task':{'target':'CCOC','constraints':{}}}))
    state=expansion(expansion(state,'CCO',status='error'),'CCO',status='error')
    assert build_context(state,RESOURCES) is None
