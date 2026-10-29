"""Declared accounting is not reaction feasibility or measured yield."""
from copy import deepcopy
import json
import pytest
from synthesis_route_gym.portfolio_process import build_process_report
from synthesis_route_gym.schemas import Task, RouteCandidate


def fixture():
    task={'task_id':'process','target':'CCOC(C)=O','target_amount_mmol':10,
      'inventory':[dict(smiles=s,available_mmol=100,price_per_mmol=p,currency='USD',
        source='illustrative fixture, not vendor quote',quoted_at='2026-10-26')
        for s,p in [('CC=O',2),('[H][H]',1),('O',0.1),('CCO',5),('CC(=O)O',3)]]}
    def step(i,p,inputs):
        return dict(step_id=i,product=p,product_amount_mmol=10,
          reactants=[dict(smiles=s,amount_mmol=10)for s in inputs],
          source_tool='synthetic_accounting_fixture',source_version='1')
    route={'route_id':'convergent','target':task['target'],'steps':[
      step('alcohol','CCO',['CC=O','[H][H]']),step('acid','CC(=O)O',['CC=O','O']),
      step('couple','CCOC(C)=O',['CCO','CC(=O)O'])]}
    direct={'route_id':'direct','target':task['target'],'steps':[deepcopy(route['steps'][-1])]}
    basis={'purity_basis':'unadjusted declared quantities','exclusions':['labor','utilities','workup'],
           'valuation_date':'2026-10-27','price_evidence_kind':'illustrative'}
    return task,route,direct,basis


def report(task=None,route=None,basis=None):
    t,r,_,b=fixture()
    return build_process_report(task or t,[route or r],basis=b if basis is None else basis)


def test_convergent_amounts_costs_and_pareto():
    t,r,d,b=fixture();before=deepcopy((t,r,d,b));v=build_process_report(t,[r,d],basis=b)
    assert v['schema_version']=='srg-process-report-v1'
    assert not v['claims_manufacturing_savings'] and not v['claims_experimental_validation']
    assert v['pareto_route_ids']==['convergent','direct']
    row=v['routes'][0];assert row['material_cost']==pytest.approx(51)
    assert row['scale_mmol']==10 and row['comparison_eligible']
    lines={x['smiles']:x for x in row['cost_lines']}
    assert lines['CC=O']['required_mmol']==20 and lines['CC=O']['extended_cost']==40
    assert 'CCO' not in lines and 'CC(=O)O' not in lines
    assert row['material_balance']['stoichiometry_status']=='unverified' and row['route_yield'] is None
    assert (t,r,d,b)==before and json.loads(json.dumps(v))==v


def test_models_dicts_and_detachment():
    t,r,_,b=fixture();v=build_process_report(Task.model_validate(t),[RouteCandidate.model_validate(r)],basis=b)
    assert v==build_process_report(t,[r],basis=b)
    v['routes'][0]['cost_lines'][0]['source']='changed';assert t['inventory'][0]['source']!='changed'


def test_shared_intermediate_and_no_yield_multiplication():
    t,r,_,_=fixture();r['steps'][1]['reactants']=[{'smiles':'CCO','amount_mmol':10},{'smiles':'O','amount_mmol':10}]
    r['steps'][0]['predicted_yield']=0.99;row=report(t,r)['routes'][0]
    e=next(x for x in row['material_balance']['internal']if x['smiles']=='CCO')
    assert (e['required_mmol'],e['available_mmol'],e['status'])==(20,10,'insufficient')
    assert not row['comparison_eligible'] and 'quantity_insufficient' in row['ineligible_reasons']
    assert row['route_yield'] is None


@pytest.mark.parametrize('field,value,reason',[
 ('price_per_mmol',None,'missing_price'),('quoted_at',None,'missing_quote_date'),
 ('quoted_at','not-a-date','invalid_quote_date'),('quoted_at','2026-10-28','quote_after_valuation_date'),
 ('source','   ','missing_price_source'),('available_mmol',None,'quantity_unknown'),
 ('available_mmol',1,'quantity_insufficient')])
def test_incomplete_price_stock(field,value,reason):
    t,r,_,_=fixture();t['inventory'][0][field]=value;v=report(t,r);row=v['routes'][0]
    assert reason in row['ineligible_reasons']
    assert v['unranked_route_ids']==['convergent'] and v['pareto_route_ids']==[]
    if field=='price_per_mmol':assert row['material_cost'] is None


def test_missing_amount_unknown_not_zero():
    t,r,_,_=fixture();r['steps'][0]['reactants'][0].pop('amount_mmol');row=report(t,r)['routes'][0]
    line=next(x for x in row['cost_lines']if x['smiles']=='CC=O')
    assert line['required_mmol'] is None and line['known_required_mmol']==10
    assert line['extended_cost'] is None and row['material_cost'] is None
    assert 'unknown_feed_amount' in row['ineligible_reasons']


def test_mixed_currency_not_added():
    t,r,_,_=fixture();t['inventory'][0]['currency']='EUR';row=report(t,r)['routes'][0]
    assert row['material_cost'] is None and row['known_subtotal'] is None
    assert 'mixed_currencies' in row['ineligible_reasons']


def test_different_route_currencies_not_compared():
    t,r,d,b=fixture()
    for item in t['inventory'][:3]:item['currency']='EUR'
    v=build_process_report(t,[r,d],basis=b)
    assert v['pareto_route_ids']==[] and v['unranked_route_ids']==['convergent','direct']
    assert all('comparison_currency_mismatch' in row['ineligible_reasons']for row in v['routes'])


@pytest.mark.parametrize('change,reason',[
 ('scale_missing','target_scale_unknown'),('scale_mismatch','target_output_scale_mismatch'),
 ('equipment','equipment_unavailable'),('forbidden','excluded_operation'),
 ('zero_stock','material_unavailable'),('wrong_target','wrong_target'),
 ('duplicate_product','duplicate_step'),('element_deficit','element_amount_deficit')])
def test_gates(change,reason):
    t,r,_,_=fixture()
    if change=='scale_missing':t.pop('target_amount_mmol')
    elif change=='scale_mismatch':r['steps'][-1]['product_amount_mmol']=11
    elif change=='equipment':r['steps'][-1]['required_equipment']=['reactor']
    elif change=='forbidden':t['constraints']={'forbidden_operations':['distillation']};r['steps'][-1]['operations']=['distillation']
    elif change=='zero_stock':t['inventory'][0]['available_mmol']=0
    elif change=='wrong_target':r['target']='CCO'
    elif change=='duplicate_product':r['steps']+=[deepcopy(r['steps'][0])]
    elif change=='element_deficit':r['steps'][0]['product_amount_mmol']=200
    row=report(t,r)['routes'][0]
    assert not row['comparison_eligible'] and reason in row['ineligible_reasons']


def test_basis_explicit_no_rescaling():
    t,r,_,b=fixture();v=build_process_report(t,[r])
    assert {'purity_basis_unknown','cost_exclusions_unknown'}<=set(v['routes'][0]['ineligible_reasons'])
    with pytest.raises(ValueError):build_process_report(t,[r],basis={**b,'target_amount_mmol':100})


def test_unknown_or_missing_output():
    t,r,_,_=fixture();r['steps'][-1]['product_amount_mmol']=None
    assert 'target_output_amount_unknown' in report(t,r)['routes'][0]['ineligible_reasons']
    r['steps']=r['steps'][:2];assert 'missing_target_product' in report(t,r)['routes'][0]['ineligible_reasons']


def test_dominated_and_partial_unranked():
    t,r,d,b=fixture();costly=deepcopy(d);costly['route_id']='costly'
    for use in costly['steps'][0]['reactants']:use['amount_mmol']=20
    unknown=deepcopy(d);unknown['route_id']='unknown';unknown['steps'][0]['product_amount_mmol']=None
    v=build_process_report(t,[d,costly,unknown],basis=b)
    assert v['pareto_route_ids']==['direct'] and v['dominated_route_ids']==['costly']
    assert v['unranked_route_ids']==['unknown']


@pytest.mark.parametrize('patch',[{'purity_basis':' '},{'exclusions':['']},{'valuation_date':'tomorrow'},
 {'price_evidence_kind':'experimentally_verified'},{'unexpected':1}])
def test_basis_rejects_invalid(patch):
    t,r,_,b=fixture()
    with pytest.raises(ValueError):build_process_report(t,[r],basis={**b,**patch})


def test_input_bounds():
    t,r,_,b=fixture()
    for routes in ([],[r,r],'bad'):
        with pytest.raises(ValueError):build_process_report(t,routes,basis=b)
    t['target_amount_mmol']=True
    with pytest.raises(ValueError):build_process_report(t,[r],basis=b)
    t,r,_,b=fixture();r['steps'][0]['conditions']=['x'*2_000_001]
    with pytest.raises(ValueError):build_process_report(t,[r],basis=b)


def test_acquisition_not_process():
    t,r,_,_=fixture();t['inventory'].append(dict(smiles=t['target'],available_mmol=100,price_per_mmol=1,currency='USD',source='fixture',quoted_at='2026-10-26'));r['steps']=[]
    row=report(t,r)['routes'][0];assert 'acquisition_only' in row['ineligible_reasons'] and row['route_yield'] is None


@pytest.mark.parametrize('bad',[False,0,[],['purity']])
def test_basis_object_only(bad):
    t,r,_,_=fixture()
    with pytest.raises(ValueError):build_process_report(t,[r],basis=bad)


def test_input_nan_and_unreasonable_scale_fail_before_arithmetic():
    t,r,_,b=fixture()
    for value in (float('nan'),float('inf'),1e13,'10'):
        t['target_amount_mmol']=value
        with pytest.raises(ValueError):build_process_report(t,[r],basis=b)


def test_quote_timestamps_and_duplicate_exclusions():
    t,r,_,b=fixture();t['inventory'][0]['quoted_at']='2026-10-26T14:00:00+00:00'
    assert report(t,r)['routes'][0]['comparison_eligible']
    t['inventory'][0]['quoted_at']='2026-10-26T14:00:00'
    assert 'invalid_quote_date' in report(t,r)['routes'][0]['ineligible_reasons']
    with pytest.raises(ValueError):build_process_report(t,[r],basis={**b,'exclusions':['labor','labor']})


def test_missing_stock_unknown_condition_material_and_free_quotes():
    t,r,_,_=fixture();t['inventory']=t['inventory'][1:]
    assert 'material_unavailable' in report(t,r)['routes'][0]['ineligible_reasons']
    t,r,_,_=fixture();r['steps'][0]['condition_inputs']={'solvent':'CO'}
    row=report(t,r)['routes'][0]
    assert {'undeclared_condition_material','unknown_feed_amount','material_unavailable'}<=set(row['ineligible_reasons'])
    t,r,_,_=fixture()
    for item in t['inventory']:item['price_per_mmol']=0
    row=report(t,r)['routes'][0];assert row['material_cost']==0 and row['comparison_eligible']


def test_reagent_made_elsewhere_still_needs_explicit_external_stock():
    t,r,_,_=fixture();r['steps'][-1]['reagents']=[{'smiles':'CCO','amount_mmol':2}]
    row=report(t,r)['routes'][0];line=next(x for x in row['cost_lines']if x['smiles']=='CCO')
    assert line['required_mmol']==2 and line['uses'][0]['role']=='reagent'
    assert row['material_cost']==61


def test_empty_unstocked_route_does_not_claim_acquisition():
    t,r,_,_=fixture();r['steps']=[];row=report(t,r)['routes'][0]
    assert 'no_synthesis_steps' in row['ineligible_reasons'] and 'acquisition_only' not in row['ineligible_reasons']
