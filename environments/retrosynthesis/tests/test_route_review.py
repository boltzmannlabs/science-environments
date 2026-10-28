"""Host review facts preserve deterministic authority and source uncertainty."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import pytest
from synthesis_route_gym.schemas import Task, RouteCandidate, MaterialUse
from synthesis_route_gym.validation import assess_route
from synthesis_route_gym.evidence_contracts import SourceRecord, public_projection
from synthesis_route_gym.route_review import build_route_review


def case(**updates):
    task = Task.model_validate({'task_id':'fixture','target':'CCO',
        'inventory':[{'smiles':'CC=O','available_mmol':10}], **updates})
    route = RouteCandidate.model_validate({'route_id':'route-a','target':'CCO','steps':[
        {'step_id':'step-a','product':'CCO','reactants':[{'smiles':'CC=O','amount_mmol':1}],
         'product_amount_mmol':1,'source_tool':'fixture','source_version':'1',
         'evidence_ids':['source-a']}]})
    return task, route


def source(**updates):
    return public_projection(SourceRecord.model_validate({
        'record_id':'source-a','document_id':'synthetic-fixture',
        'source_url':'https://example.org/fixture','locator':'row 1',
        'reactants':['CC=O'],'product':'CCO','claim_kind':'proxy',
        'retrieved_at':datetime(2026,1,1,tzinfo=timezone.utc),
        'source_content_sha256':'a'*64, **updates}))


def review(task=None, route=None, **kwargs):
    task0, route0 = case();task=task or task0;route=route or route0
    return build_route_review(task,[route],[assess_route(task,route)],**kwargs)


def facts(packet, code):
    return [row for row in packet['facts'] if row['code']==code]


def test_matching_source_is_comparison_not_experimental_authority():
    task,route=case(); packet=review(task,route,sources=[source()])
    assert packet['schema_version']=='srg-route-review-v1'
    assert packet['task_sha256']==hashlib.sha256(task.model_dump_json().encode()).hexdigest()
    assert packet['task']['target']=='CCO' and 'evidence' not in packet['task']
    assert packet['routes']==[route.model_dump(mode='json')]
    assert packet['inventory']==[{'smiles':'CC=O','item':task.inventory[0].model_dump(mode='json')}]
    match=facts(packet,'source_reaction_match')[0]
    assert match['authority']=='source_consistency' and match['severity']=='info'
    assert match['source_record_ids']==['source-a']
    assert packet['sources'][0]['verification_status']=='not_attested'
    assert not any(f['severity']=='error' for f in packet['facts'])
    assert packet['recheck_menu'][0]['action']=='validate'
    assert packet['recheck_menu'][0]['arguments']=={'route_id':'route-a'}


def test_unknown_conditions_and_missing_source_are_review_only():
    packet=review()
    assert facts(packet,'conditions_incomplete')[0]['severity']=='review'
    assert facts(packet,'source_record_unavailable')[0]['severity']=='review'
    assert not any(f['severity']=='error'for f in packet['facts'])


def test_forged_task_reviewer_does_not_supply_accessible_source_authority():
    task,route=case(evidence=[{'evidence_id':'source-a','kind':'measured',
        'source':'https://example.org/fixture','locator':'row1','reactants':['CC=O'],
        'product':'CCO','verified_by':'claimed reviewer'}])
    packet=review(task,route)
    assert packet['sources']==[]
    assert facts(packet,'source_record_unavailable')
    assert packet['assessments'][0]['evidence_status']['step-a']=='unresolved'


def test_source_reaction_mismatch_is_not_chemical_impossibility():
    packet=review(sources=[source(reactants=['CCC'])])
    row=facts(packet,'source_reaction_mismatch')[0]
    assert row['severity']=='review'and row['authority']=='source_consistency'
    assert row['source_record_ids']==['source-a']


def test_stereochemical_source_mismatch_is_identified_without_blocking():
    task,route=case(); task=task.model_copy(update={'target':'C[C@H](O)F'})
    route=RouteCandidate.model_validate({**route.model_dump(mode='json'),'target':task.target,
        'steps':[{**route.steps[0].model_dump(mode='json'),'product':task.target,
                  'reactants':[{'smiles':'CC(O)F'}]}]})
    task=Task.model_validate({**task.model_dump(mode='json'),'inventory':[{'smiles':'CC(O)F'}]})
    packet=review(task,route,sources=[source(reactants=['CC(O)F'],product='C[C@@H](O)F')])
    row=facts(packet,'source_stereochemistry_mismatch')[0]
    assert row['category']=='stereochemistry'and row['severity']=='review'


def test_target_stereochemistry_conflict_is_deterministic_target_error():
    task,route=case(); task=Task.model_validate({**task.model_dump(mode='json'),'target':'C[C@H](O)F'})
    route=RouteCandidate.model_validate({**route.model_dump(mode='json'),'target':'C[C@@H](O)F',
        'steps':[{**route.steps[0].model_dump(mode='json'),'product':'C[C@@H](O)F',
                  'reactants':[{'smiles':'CC(O)F'}]}]})
    packet=review(task,route)
    row=facts(packet,'target_stereochemistry_mismatch')[0]
    assert row['severity']=='error'and row['authority']=='deterministic'


@pytest.mark.parametrize('change,code,category',[
    ({'inventory':[]},'material_unavailable','missing_materials'),
    ({'target_amount_mmol':2},'quantity_insufficient','quantity_conflict'),
    ({'constraints':{'require_complete_conditions':True}},'conditions_incomplete','incomplete_conditions'),
    ({'constraints':{'max_steps':0}},'step_limit','constraint_violation'),
])
def test_existing_hard_constraints_remain_errors(change,code,category):
    task,route=case(**change);packet=review(task,route)
    row=facts(packet,code)[0]
    assert row['severity']=='error'and row['category']==category
    assert row['authority']=='deterministic'


def test_unverified_agent_yield_is_not_a_bound_prediction():
    task,route=case();route=route.model_copy(update={'steps':(
        route.steps[0].model_copy(update={'predicted_yield':0.99}),)})
    packet=review(task,route)
    row=facts(packet,'unverified_yield_claim')[0]
    assert row['category']=='model_domain_mismatch'and row['severity']=='review'
    assert packet['tool_results']==[]


def test_ids_deterministic_and_inputs_copied():
    task,route=case();src=source();before=deepcopy(src)
    a=review(task,route,sources=[src]);b=review(task,route,sources=[src])
    assert a==b and src==before
    a['sources'][0]['locator']='changed'
    assert review(task,route,sources=[src])==b
    assert len({f['fact_id']for f in b['facts']})==len(b['facts'])


@pytest.mark.parametrize('tamper',[
    lambda a:{**a,'graph_valid':False},
    lambda a:{**a,'route_id':'unrelated'},
    lambda a:{**a,'findings':[]},
])
def test_stale_or_fabricated_deterministic_assessment_rejected(tamper):
    task,route=case();a=assess_route(task,route).model_dump(mode='json')
    with pytest.raises(ValueError):build_route_review(task,[route],[tamper(a)])


@pytest.mark.parametrize('change',[
    {'record_sha256':'b'*64},{'reaction_sha256':'b'*64},
    {'verification_status':'host_attested'},{'private_outcome':99},
])
def test_invalid_or_private_source_projection_rejected(change):
    with pytest.raises(ValueError):review(sources=[{**source(),**change}])


def test_duplicate_route_or_source_ids_rejected():
    task,route=case();a=assess_route(task,route)
    with pytest.raises(ValueError):build_route_review(task,[route,route],[a,a])
    with pytest.raises(ValueError):review(sources=[source(),source()])


@pytest.mark.parametrize('count',[0,4])
def test_shortlist_bounds(count):
    task,route=case();routes=[route.model_copy(update={'route_id':f'r{i}'})for i in range(count)]
    with pytest.raises(ValueError):build_route_review(task,routes,[assess_route(task,r)for r in routes])


def test_oversized_and_nonfinite_input_rejected():
    task,route=case();raw=route.model_dump(mode='json');raw['steps']*=13
    with pytest.raises(ValueError):build_route_review(task,[raw],[assess_route(task,route)])
    with pytest.raises(ValueError):review(sources=[source(locator='x'*2001)])
    with pytest.raises(ValueError):review(scientific_results=[{'action':'forward_check','arguments':{},'result':{'x':float('nan')}}])


def scientific(action='predict_reaction_yield', *, reactants=None, product='CCO', status='scored'):
    from synthesis_route_gym.tool_registry import ToolBinding,ToolRegistry
    if action=='forward_check':
        args={'reactants':reactants or ['CC=O'],'product':product}
        raw={'status':'ok','predictions':[{'product':product,'score':0.5}]}
    else:
        args={'candidates':[{'id':'prediction-a','reactants':reactants or ['CC=O'],'reagents':[],'product':product}]}
        row={'id':'prediction-a','status':status,'predicted_yield_percent':99.0 if status=='scored'else None,
             'raw_yield_percent':99.0 if status=='scored'else None,'reason':None if status=='scored'else 'outside_domain',
             'domain':'transfer_not_established'}
        raw={'status':'ok','predictions':[row]}
    registry=ToolRegistry({action:ToolBinding(callback=lambda _:raw,version='fixture-v1',model_version='model-v1')})
    return {'action':action,'arguments':args,'result':registry.invoke(action,args)}


def test_bound_yield_is_prediction_and_outside_domain_abstention_remains_unknown():
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0].model_copy(update={'predicted_yield':.99}),)})
    record=scientific();assert record['result']['status']=='ok',record
    packet=review(task,route,scientific_results=[record])
    assert not facts(packet,'unverified_yield_claim')
    assert facts(packet,'yield_model_scope_unverified')[0]['severity']=='review'
    assert packet['tool_results'][0]['result']['data']['predictions'][0]['evidence_status']=='predicted'
    packet=review(task,route,scientific_results=[scientific(status='abstained')])
    assert facts(packet,'yield_model_abstained')and facts(packet,'unverified_yield_claim')


def test_unrelated_prediction_cannot_back_route_claim():
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0].model_copy(update={'predicted_yield':.99}),)})
    assert facts(review(task,route,scientific_results=[scientific(reactants=['CCC'])]),'unverified_yield_claim')


def test_forward_agreement_and_disagreement_are_not_hard_evidence():
    record=scientific('forward_check');assert record['result']['status']=='ok',record
    assert facts(review(scientific_results=[record]),'forward_model_agreement')[0]['severity']=='info'
    other=deepcopy(record);other['result']['data']['predictions']=[];other['result']['data']['target_in_predictions']=False
    assert facts(review(scientific_results=[other]),'forward_model_disagreement')[0]['severity']=='review'
    assert not facts(review(scientific_results=[scientific('forward_check',reactants=['CCC'])]),'forward_model_agreement')


@pytest.mark.parametrize('change',[
    lambda r:r['result']['data']['predictions'][0].update(id='unrequested'),
    lambda r:r['result']['data']['predictions'][0].update(model_version='unbound-model'),
    lambda r:r['result']['provenance']['binding'].update(authority='estimate'),
])
def test_prediction_identity_or_authority_tampering_rejected(change):
    record=scientific();change(record)
    with pytest.raises(ValueError):review(scientific_results=[record])


def test_forward_flag_must_match_prediction_membership():
    record=scientific('forward_check');record['result']['data']['target_in_predictions']=False
    with pytest.raises(ValueError):review(scientific_results=[record])


def test_unavailable_model_and_unbound_success_do_not_supply_predicted_authority():
    from synthesis_route_gym.tool_registry import ToolRegistry
    record=scientific();record['result']=ToolRegistry().invoke(record['action'],record['arguments'])
    assert review(scientific_results=[record])['tool_results'][0]['result']['status']=='unavailable'
    record=scientific();record['result']['provenance']['binding']=None
    assert not facts(review(scientific_results=[record]),'yield_model_scope_unverified')


def test_scientific_record_unknown_extras_and_capability_changes():
    record=scientific()
    invalid=[{**record,'secret_path':'/private'}, {**record,'action':'observe_condition'},
             {**record,'result':{**record['result'],'capability':'forward_check'}}]
    for row in invalid:
        with pytest.raises(ValueError):review(scientific_results=[row])


def test_legacy_scientific_wrapper_is_checked_and_canonicalized():
    record=scientific();raw=record['result'];record['result']={**raw['data'],'tool_result':raw}
    assert review(scientific_results=[record])['tool_results'][0]['result']==raw
    record['result']={**record['result'],'private_label':99}
    with pytest.raises(ValueError):review(scientific_results=[record])


def test_uncertain_source_stereo_and_completeness_claim_are_not_errors():
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0].model_copy(update={'conditions_complete':True}),)})
    p=review(task,route,sources=[source(stereochemistry_scope='not_reported')])
    assert facts(p,'source_stereochemistry_unreported')and facts(p,'condition_completeness_unverified')
    assert not any(f['severity']=='error'for f in p['facts'])


def test_no_citation_quantities_and_acquisition_only_have_explicit_facts():
    task,route=case(target_amount_mmol=1);step=route.steps[0].model_copy(update={'evidence_ids':(),
        'reactants':(route.steps[0].reactants[0].model_copy(update={'amount_mmol':None}),)})
    p=review(task,route.model_copy(update={'steps':(step,)}))
    assert facts(p,'step_support_unresolved')and facts(p,'quantity_unknown')
    task=Task.model_validate({'task_id':'acquire','target':'CCO','inventory':[{'smiles':'CCO'}]})
    route=RouteCandidate.model_validate({'route_id':'route-a','target':'CCO','steps':[]})
    assert facts(review(task,route),'acquisition_only')[0]['severity']=='error'


def test_duplicate_step_ids_refuse_ambiguous_critic_citations():
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0],route.steps[0])})
    with pytest.raises(ValueError):review(task,route)


def test_packet_bound_and_remaining_assessment_bindings():
    task,route=case();assessment=assess_route(task,route).model_dump(mode='json')
    with pytest.raises(ValueError):build_route_review(task,[route],[{**assessment,'weak_steps':['unknown']}])
    with pytest.raises(ValueError):build_route_review(task,[route],[assessment,assessment])
    sources=[source(record_id=f'source-{i}',conditions=['x'*2000]*2)for i in range(30)]
    with pytest.raises(ValueError,match='bounded public context'):review(sources=sources)


def test_host_packet_roundtrips_pure_contract():
    from synthesis_route_gym.route_critic import build_context
    p=review(sources=[source()],scientific_results=[scientific('forward_check'),scientific()])
    context=build_context(p,{'remaining_model_calls':20,'remaining_tool_calls':50,'remaining_tokens':200000,'remaining_seconds':400})
    assert context['packet']==p


def test_scientific_history_filters_irrelevant_calls_and_deduplicates_identical_records():
    relevant=scientific();unrelated=[scientific(reactants=['CCC'])for _ in range(20)]
    p=review(scientific_results=[*unrelated,relevant,relevant])
    assert len(p['tool_results'])==1
    records=[{**relevant,'result':{**relevant['result'],'usage':{**relevant['result']['usage'],'elapsed_seconds':i}}}for i in range(13)]
    with pytest.raises(ValueError,match='scientific'):review(scientific_results=records)


def test_sources_filter_unrelated_history_but_keep_mismatched_citations():
    unrelated=[source(record_id=f'other-{i}',reactants=['CCC'],product='CCCC')for i in range(70)]
    assert len(review(sources=[*unrelated,source()])['sources'])==1
    assert facts(review(sources=[*unrelated,source(reactants=['CCC'])]),'source_reaction_mismatch')
    with pytest.raises(ValueError):review(sources=[source(record_id=f'known-{i}')for i in range(61)])


def test_builder_rejects_values_outside_isolated_runtime_packet_contract():
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0].model_copy(update={'conditions':('x'*2001,)}),)})
    with pytest.raises(ValueError):review(task,route)


@pytest.mark.parametrize('cited_ids',[(),('different-source',)])
def test_uncited_accessible_exact_source_can_be_recommended_without_new_authority(cited_ids):
    import json
    from synthesis_route_gym.route_critic import build_context,context_fingerprint,parse_report,hydrate_report
    task,route=case();route=route.model_copy(update={'steps':(route.steps[0].model_copy(update={'evidence_ids':cited_ids}),)})
    packet=review(task,route,sources=[source()])
    fact=facts(packet,'accessible_source_reaction_match')[0]
    assert fact['route_id']=='route-a'and fact['step_id']=='step-a'
    assert fact['source_record_ids']==['source-a']
    assert fact['severity']=='info'and fact['authority']=='source_consistency'
    assert not facts(packet,'source_reaction_match')
    assert any(f['severity']=='review'and f['category']=='unsupported_transformation'for f in packet['facts'])
    context=build_context(packet,{'remaining_model_calls':20,'remaining_tool_calls':50,'remaining_tokens':200000,'remaining_seconds':400})
    report={'schema_version':'srg-route-critic-report-v1','context_sha256':context_fingerprint(context),
        'findings':[{'route_id':'route-a','step_id':'step-a','category':'unsupported_transformation','severity':'info',
            'supporting_fact_ids':[fact['fact_id']],'source_record_ids':['source-a'],
            'requested_revision':'revise_route','rationale':'Cite the accessible matching source while retaining its scope limits.'}],
        'recommended_recheck_id':None,'evidence_status':'agent_proposal'}
    checked=parse_report(json.dumps(report),context)
    assert hydrate_report(checked,context)['findings'][0]['source_records'][0]['record_id']=='source-a'
    report['findings'][0]['severity']='error'
    with pytest.raises(ValueError,match='deterministic'):parse_report(json.dumps(report),context)


def test_cited_matching_source_does_not_gain_duplicate_accessible_match_fact():
    packet=review(sources=[source()])
    assert len(facts(packet,'source_reaction_match'))==1
    assert not facts(packet,'accessible_source_reaction_match')


def test_source_isotope_difference_is_not_mislabeled_as_stereochemistry():
    packet=review(sources=[source(product='C[13CH2]O')])
    assert facts(packet,'source_reaction_mismatch')
    assert not facts(packet,'source_stereochemistry_mismatch')
    assert not facts(packet,'source_reaction_match')


def test_requested_target_isotope_difference_is_not_stereochemistry():
    task,route=case(target='C[13CH2]O')
    packet=review(task,route)
    assert facts(packet,'wrong_target')
    assert not facts(packet,'target_stereochemistry_mismatch')


def component_case(action):
    from synthesis_route_gym.tool_registry import ToolRegistry,ToolBinding
    task,route=case()
    roles=({'aryl halide':'CC=O','ligand':'P','additive':'N','base':'O'}if action=='predict_conditions'else
           {'aryl':'CC=O','amine':'N','catalyst':'[Pd]','base':'O','solvent':'CO'})
    step=route.steps[0].model_copy(update={'condition_inputs':roles,'predicted_yield':.99,
        'reagents':tuple(MaterialUse(smiles=s)
                         for s in sorted(set(roles.values())-{'CC=O'}))})
    task=Task.model_validate({**task.model_dump(mode='json'),'inventory':[{'smiles':s}for s in sorted(set(roles.values()))]})
    route=RouteCandidate.model_validate({**route.model_dump(mode='json'),'steps':[step.model_dump(mode='json')]})
    row={'id':'component-a',**roles,**({'product':route.target}if action=='score_cn_conditions'else{})}
    args={'candidates':[row]}
    prediction=({'id':row['id'],'predicted_yield_percent':99.0,'domain':'specific_component_yield_domain'}
        if action=='predict_conditions'else{'id':row['id'],'status':'scored','hit_score':.99,'raw_hit_score':.99,
            'reason':None,'domain':'specific_screening_hit_domain','calibration_kind':'uncalibrated_forest_score'})
    registry=ToolRegistry({action:ToolBinding(callback=lambda _:{'status':'ok','predictions':[prediction]},
        version='fixture-v1',model_version='component-model')})
    record={'action':action,'arguments':args,'result':registry.invoke(action,args)}
    assert record['result']['status']=='ok',record
    return task,route,record


@pytest.mark.parametrize('action,code',[
    ('predict_conditions','component_yield_scope_unverified'),
    ('score_cn_conditions','screening_hit_not_yield')])
def test_component_predictions_keep_endpoint_limits_without_justifying_route_yield(action,code):
    task,route,record=component_case(action)
    packet=review(task,route,scientific_results=[record])
    assert facts(packet,code)[0]['category']=='model_domain_mismatch'
    assert facts(packet,code)[0]['severity']=='review'
    assert facts(packet,'unverified_yield_claim')
    assert packet['tool_results'][0]['result']['data']['predictions'][0]['domain']==record['result']['data']['predictions'][0]['domain']
    assert not facts(packet,'yield_model_scope_unverified')


def test_cn_component_abstention_and_product_binding_remain_explicit():
    task,route,record=component_case('score_cn_conditions')
    row=record['result']['data']['predictions'][0]
    record['result']['data']['predictions']=[{**row,'status':'abstained','hit_score':None,'raw_hit_score':None,'reason':'outside_domain'}]
    assert facts(review(task,route,scientific_results=[record]),'screening_model_abstained')
    record['arguments']['candidates'][0]['product']='CCC'
    packet=review(task,route,scientific_results=[record])
    assert packet['tool_results']==[] and not facts(packet,'screening_model_abstained')
