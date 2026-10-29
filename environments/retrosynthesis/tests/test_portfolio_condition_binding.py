"""Route-bound condition catalogs expose only admitted, source-matching outcomes."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import pytest
from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy
from synthesis_route_gym.portfolio_condition_binding import (
    RouteConditionBinding, build_condition_report, condition_catalog,
    condition_recipe_digest, validate_binding, validate_step_binding,
)


def sample():
    rows = tuple(ConditionRecord(key, (('base', reagent),), value)
                 for key, reagent, value in [('a', 'O', 12.25), ('b', 'N', 87.75)])
    study = FiniteConditionStudy(rows, (), 2, 'https://example.org/study', 'table 1', 'a' * 64, 'CCBr')
    def recipe(key, reagent):
        return {'step_id': key, 'reactants': [{'smiles': 'CCBr'}], 'product': 'CCO',
                'reagents': [{'smiles': reagent}], 'conditions': ['base=' + reagent],
                'source_tool': 'public_study', 'source_version': '1', 'conditions_complete': False}
    binding = {'schema_version': 'srg-route-condition-binding-v1', 'study_id': 'study',
               'dataset_sha256': study.dataset_sha256, 'source_url': study.source_url,
               'source_locator': study.source_locator, 'reactants': ['CCBr'], 'product': 'CCO',
               'candidates': [{'candidate_id': row.candidate_id, 'conditions': dict(row.conditions),
                               'recipe': recipe(row.candidate_id, dict(row.conditions)['base'])} for row in rows]}
    return study, binding, recipe('stored-step', 'O')


def observed(study, key='a'):
    row = next(row for row in study._records if row.candidate_id == key)
    digest = hashlib.sha256(json.dumps(key, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'candidate_id': key, 'conditions': dict(row.conditions), 'yield_percent': row.yield_percent,
            'source_record_id': f'study:{study.dataset_sha256}:{digest[:20]}',
            'dataset_sha256': study.dataset_sha256, 'evidence_kind': 'measured_dataset_replay',
            'new_experiment_performed': False}


def test_public_catalog_is_outcome_free_until_observation():
    study, binding, step = sample()
    view = condition_catalog(step, study, binding)
    assert view['schema_version'] == 'srg-route-condition-catalog-v1'
    assert len(view['candidates']) == 2 and view['observations'] == []
    assert 'yield_percent' not in json.dumps(view)
    assert '87.75' not in json.dumps(view) and '12.25' not in json.dumps(view)
    assert view['candidates'][0]['recipe_matches_current_step'] is True
    assert view['candidates'][1]['recipe_matches_current_step'] is False
    assert validate_step_binding(step,study,binding)['product']=='CCO'


def test_catalog_shows_only_supplied_successful_observations():
    study, binding, step = sample()
    result = condition_catalog(step, study, binding, observations=[observed(study)])
    assert result['observations'][0]['yield_percent'] == 12.25
    assert '87.75' not in json.dumps(result)
    assert result['observations'][0]['recipe_matches_current_step'] is True
    assert result['observation_count'] == 1


def test_initial_ids_are_not_implicitly_revealed():
    study, binding, step = sample(); study = replace(study, observed_ids=('b',))
    assert condition_catalog(step, study, binding)['observations'] == []


def test_report_alternative_measurement_not_transferred_to_current_step():
    study, binding, step = sample()
    result = build_condition_report(step, study, binding, observations=[observed(study, 'b')], selected_candidate_id='b')
    assert result['schema_version'] == 'srg-condition-application-report-v1'
    assert result['selected_observation']['yield_percent'] == 87.75
    assert result['selected_observation']['recipe_matches_current_step'] is False
    assert result['route_step_yield_percent'] is None
    assert result['best_observed_candidate_id'] == 'b'
    assert result['claims_experimental_validation'] is False


def test_report_without_observations_has_no_optimum_or_result():
    study, binding, step = sample(); report = build_condition_report(step, study, binding)
    assert report['best_observed_candidate_id'] is None and report['selected_observation'] is None
    assert report['route_step_yield_percent'] is None and '87.75' not in json.dumps(report)
    assert 'optimum' not in report


def test_same_recipe_keeps_candidate_endpoint_separate():
    study, binding, step = sample()
    report = build_condition_report(step, study, binding, observations=[observed(study)], selected_candidate_id='a')
    assert report['selected_observation']['recipe_matches_current_step'] is True
    assert report['route_step_yield_percent'] is None


@pytest.mark.parametrize('field,value', [('product','CCN'), ('reactants',[{'smiles':'CCCBr'}]),
                                         ('reactants',[{'smiles':'CCBr'},{'smiles':'CCBr'}])])
def test_step_reaction_mismatch_rejected(field, value):
    study, binding, step = sample()
    with pytest.raises(ValueError, match='reaction'): condition_catalog({**step, field: value}, study, binding)


@pytest.mark.parametrize('patch', [{'dataset_sha256':'b'*64}, {'source_url':'https://example.org/other'},
    {'source_locator':'table 2'}, {'product':'CCN'}, {'reactants':['CCBr','CCBr']},
    {'schema_version':'unknown'}, {'extra':'no'}, {'source_url':'file:///private'}])
def test_invalid_binding(patch):
    study, binding, _ = sample()
    with pytest.raises(ValueError): validate_binding(study, {**binding, **patch})


@pytest.mark.parametrize('mutation', ['missing','duplicate','condition_mismatch','recipe_product','recipe_reactants','outcome_factor','wrong_recipe_id'])
def test_candidate_bindings_rejected(mutation):
    study, binding, _ = sample(); binding = deepcopy(binding)
    if mutation == 'missing': binding['candidates'] = binding['candidates'][:1]
    if mutation == 'duplicate': binding['candidates'][1] = binding['candidates'][0]
    if mutation == 'condition_mismatch': binding['candidates'][0]['conditions'] = {'base':'C'}
    if mutation == 'recipe_product': binding['candidates'][0]['recipe']['product'] = 'CCN'
    if mutation == 'recipe_reactants': binding['candidates'][0]['recipe']['reactants'] = [{'smiles':'CBr'}]
    if mutation == 'outcome_factor': binding['candidates'][0]['conditions'] = {'yield_percent':'12.25'}
    if mutation == 'wrong_recipe_id': binding['candidates'][0]['recipe']['step_id'] = 'b'
    with pytest.raises(ValueError): validate_binding(study, binding)


@pytest.mark.parametrize('patch', [{'candidate_id':'unknown'}, {'yield_percent':87.75},
    {'dataset_sha256':'b'*64}, {'source_record_id':'other'}, {'conditions':{'base':'N'}},
    {'yield_percent':True}, {'new_experiment_performed':True}, {'evidence_kind':'predicted'}, {'extra':'bad'}])
def test_forged_or_misbound_observation_rejected(patch):
    study, binding, step = sample()
    with pytest.raises(ValueError): condition_catalog(step, study, binding, observations=[{**observed(study), **patch}])


def test_duplicate_observations_are_not_new_measurements():
    study, binding, step = sample()
    with pytest.raises(ValueError, match='Duplicate'):
        condition_catalog(step, study, binding, observations=[observed(study), observed(study)])


def test_unobserved_selection_rejected():
    study, binding, step = sample()
    with pytest.raises(ValueError, match='observed'): build_condition_report(step, study, binding, selected_candidate_id='b')


def test_outcome_changes_do_not_change_public_input_identity():
    study, binding, _ = sample()
    other = replace(study, _records=tuple(replace(row,yield_percent=50) for row in study._records))
    assert validate_binding(study,binding) == validate_binding(other,binding)


def test_model_objects_and_defensive_copies():
    study, binding, step = sample(); before=deepcopy(binding); model = RouteConditionBinding.model_validate(binding)
    with pytest.raises(TypeError): model.candidates[0].conditions['base']='C'
    first=validate_binding(study,model); first['candidates'][0]['conditions']['base']='C'
    assert validate_binding(study,model)['candidates'][0]['conditions']['base']=='O' and binding==before


def test_recipe_digest_ignores_proposal_metadata_but_not_operating_inputs():
    _, _, step = sample(); digest=condition_recipe_digest(step)
    assert condition_recipe_digest({**step,'step_id':'revision','predicted_yield':0.9,'evidence_ids':['claimed']})==digest
    for field,value in [('reagents',[{'smiles':'N'}]),('conditions',['other']),('operations',['heat']),
        ('required_equipment',['reactor']),('product_amount_mmol',2),('condition_inputs',{'base':'O'})]:
        assert condition_recipe_digest({**step,field:value})!=digest


def test_chemistry_identity_preserves_stereo_and_isotopes():
    study,binding,step=sample()
    for product in ['[13CH3]CO','C[C@H](O)F','C[C@@H](O)F']:
        changed=deepcopy(binding); changed['product']=product
        for row in changed['candidates']: row['recipe']['product']=product
        assert condition_catalog({**step,'product':product},study,changed)['product']
        with pytest.raises(ValueError,match='reaction'): condition_catalog(step,study,changed)


def test_bounds_and_invalid_host_study():
    study,binding,step=sample()
    for invalid in (None, {}, replace(study, dataset_sha256='invalid')):
        with pytest.raises(ValueError): validate_binding(invalid,binding)
    with pytest.raises(ValueError): condition_catalog(step,study,binding,observations='bad')


@pytest.mark.parametrize('mutation', ['budget_bool','empty','bad_record','bad_pairs','duplicate_factors','outcome',
    'duplicate_id','duplicate_settings','mixed_factors','unknown_initial','duplicate_initial','blank_locator',
    'none_url','unhashable_factor','unhashable_initial'])
def test_malformed_host_metadata_is_rejected_cleanly(mutation):
    study,binding,_=sample(); rows=study._records
    if mutation=='budget_bool': study=replace(study,budget=True)
    if mutation=='empty': study=replace(study,_records=())
    if mutation=='bad_record': study=replace(study,_records=({},))
    if mutation=='bad_pairs': study=replace(study,_records=(replace(rows[0],conditions=('base',)),rows[1]))
    if mutation=='duplicate_factors': study=replace(study,_records=(replace(rows[0],conditions=(('base','O'),('base','N'))),rows[1]))
    if mutation=='outcome': study=replace(study,_records=(replace(rows[0],conditions=(('yield','12.25'),)),rows[1]))
    if mutation=='duplicate_id': study=replace(study,_records=(rows[0],replace(rows[1],candidate_id='a')))
    if mutation=='duplicate_settings': study=replace(study,_records=(rows[0],replace(rows[1],conditions=rows[0].conditions)))
    if mutation=='mixed_factors': study=replace(study,_records=(rows[0],replace(rows[1],conditions=(('solvent','N'),))))
    if mutation=='unknown_initial': study=replace(study,observed_ids=('unknown',))
    if mutation=='duplicate_initial': study=replace(study,observed_ids=('a','a'))
    if mutation=='blank_locator': study=replace(study,source_locator=' ')
    if mutation=='none_url': study=replace(study,source_url=None)
    if mutation=='unhashable_factor': study=replace(study,_records=(replace(rows[0],conditions=((['base'],'O'),)),rows[1]))
    if mutation=='unhashable_initial': study=replace(study,observed_ids=(['a'],))
    with pytest.raises(ValueError): validate_binding(study,binding)


def test_public_fingerprint_binds_observation_allowance():
    study,binding,_=sample()
    assert validate_binding(study,binding)['binding_sha256'] != validate_binding(replace(study,budget=1),binding)['binding_sha256']


def test_public_binding_does_not_inspect_unqueried_outcome_values():
    study,binding,_=sample()
    masked=replace(study,_records=tuple(replace(row,yield_percent=object())for row in study._records))
    assert validate_binding(masked,binding)==validate_binding(study,binding)


def test_excess_observations_do_not_bypass_declared_study_allowance():
    study,binding,step=sample(); study=replace(study,budget=1)
    with pytest.raises(ValueError,match='allowance'):
        condition_catalog(step,study,binding,observations=[observed(study,'a'),observed(study,'b')])


def test_bounded_public_recipe_and_condition_factors():
    study,binding,_=sample(); empty=deepcopy(binding); empty['candidates'][0]['conditions']={}
    with pytest.raises(ValueError): validate_binding(study,empty)
    large=deepcopy(binding);large['candidates'][0]['recipe']['conditions']=['x'*256001]
    with pytest.raises(ValueError,match='bounded size'): validate_binding(study,large)


def test_best_observed_ties_use_stable_id():
    study,binding,step=sample()
    study=replace(study,_records=tuple(replace(row,yield_percent=50)for row in study._records))
    result=build_condition_report(step,study,binding,observations=[observed(study,'b'),observed(study,'a')])
    assert result['best_observed_candidate_id']=='a'


@pytest.mark.parametrize('mutation', ['contradictory_input','contradictory_tag','contradictory_both',
    'missing_tag_and_input','duplicate_tag','duplicate_conflicting_tag','wrong_material','nonchemical_prose'])
def test_condition_recipe_factor_mismatch_cannot_receive_measurement(mutation):
    study,binding,step=sample();binding=deepcopy(binding);candidate=binding['candidates'][0]
    if mutation=='contradictory_input':candidate['recipe']['condition_inputs']={'base':'N'}
    if mutation=='contradictory_tag':candidate['recipe']['condition_inputs']={'base':'O'};candidate['recipe']['conditions']=['base=N']
    if mutation=='contradictory_both':candidate['recipe']['condition_inputs']={'base':'N'};candidate['recipe']['conditions']=['base=N'];candidate['recipe']['reagents']=[{'smiles':'N'}]
    if mutation=='missing_tag_and_input':candidate['recipe']['conditions']=[]
    if mutation=='duplicate_tag':candidate['recipe']['conditions']=['base=O','base=O']
    if mutation=='duplicate_conflicting_tag':candidate['recipe']['conditions']=['base=O','base=N']
    if mutation=='wrong_material':candidate['recipe']['reagents']=[{'smiles':'N'}]
    if mutation=='nonchemical_prose':
        study=replace(study,_records=tuple(replace(row,conditions=(('temperature',str(70+i)+' degC'),))for i,row in enumerate(study._records)))
        for i,row in enumerate(binding['candidates']):
            row['conditions']={'temperature':str(70+i)+' degC'};row['recipe']['conditions']=['run at '+str(70+i)+' degrees']
    with pytest.raises(ValueError,match='factor|material'):
        condition_catalog(step,study,binding,observations=[observed(study)])


def test_explicit_operating_parameter_tags_can_bind_without_chemical_inference():
    study,binding,step=sample();binding=deepcopy(binding)
    study=replace(study,_records=tuple(replace(row,conditions=(('temperature',str(70+i)+' degC'),))for i,row in enumerate(study._records)))
    for i,row in enumerate(binding['candidates']):
        row['conditions']={'temperature':str(70+i)+' degC'};row['recipe']['conditions']=['temperature='+str(70+i)+' degC']
    assert len(condition_catalog(step,study,binding,observations=[observed(study)])['observations'])==1


def test_explicit_chemical_inputs_can_replace_tags_and_use_equivalent_smiles():
    study,binding,step=sample();binding=deepcopy(binding)
    for row in binding['candidates']:
        row['recipe']['condition_inputs']={'base':row['conditions']['base']}
        row['recipe']['conditions']=[]
    binding['candidates'][0]['recipe']['condition_inputs']['base']='[OH2]'
    assert len(condition_catalog(step,study,binding)['candidates'])==2


def test_bad_nonchemical_factor_in_chemical_mapping_rejected():
    study,binding,step=sample();binding=deepcopy(binding)
    study=replace(study,_records=(replace(study._records[0],conditions=(('temperature','70 degC'),)),
                                replace(study._records[1],conditions=(('temperature','71 degC'),))))
    for i,row in enumerate(binding['candidates']):
        row['conditions']={'temperature':str(70+i)+' degC'}
        row['recipe']['conditions']=['temperature='+str(70+i)+' degC']
        row['recipe']['condition_inputs']={'temperature':'O'}
    with pytest.raises(ValueError,match='factor'):validate_binding(study,binding)
