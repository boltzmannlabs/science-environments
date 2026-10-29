"""Software contract fixtures are synthetic; they are not scientific measurements."""
import copy
import csv
import json
from pathlib import Path

import pytest

from synthesis_route_gym.portfolio import (
    assess_impurities, dispatch_portfolio, retrieve_biocatalytic_routes,
    run_condition_task, select_process_routes,
)
from synthesis_route_gym.portfolio_conditions import FiniteConditionStudy


def condition_csv(tmp_path, yields=(10.0, 25.0, 40.0)):
    path = tmp_path / 'software_fixture.csv'
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['ligand', 'base', 'aryl halide', 'yield'])
        writer.writeheader()
        for index, value in enumerate(yields):
            writer.writerow({'ligand': f'L{index}', 'base': 'B', 'aryl halide': 'CCBr', 'yield': value})
    return path


def condition_task(path):
    return {'application': 'condition_optimization', 'dataset_path': str(path),
            'source_url': 'https://example.org/software-test-only',
            'source_locator': 'synthetic software test fixture',
            'substrate': 'CCBr', 'condition_columns': ['ligand', 'base'],
            'budget': 2, 'seed': 4, 'policy': 'fixed_random'}


def test_condition_policy_never_receives_unobserved_yields(tmp_path):
    task = condition_task(condition_csv(tmp_path))
    seen = []
    def choose(view):
        seen.append(copy.deepcopy(view))
        assert all('yield' not in candidate and 'yield_percent' not in candidate
                   for candidate in view['candidates'])
        return view['candidates'][0]['candidate_id']
    result = run_condition_task(task, chooser=choose)
    assert len(seen[0]['observations']) == 0
    assert len(seen[1]['observations']) == 1
    assert len(result['observations']) == 2
    assert result['evidence_kind'] == 'measured_dataset_replay'
    assert result['evaluation']['simple_regret_percent'] == 15.0


def test_condition_unknown_outcomes_do_not_change_first_choice(tmp_path):
    path = condition_csv(tmp_path)
    first = run_condition_task(condition_task(path))['observations'][0]['candidate_id']
    path = condition_csv(tmp_path, yields=(90.0, 2.0, 1.0))
    second = run_condition_task(condition_task(path))['observations'][0]['candidate_id']
    assert first == second


def test_condition_study_observe_is_immutable_and_rejects_repeat(tmp_path):
    task = condition_task(condition_csv(tmp_path))
    study = FiniteConditionStudy.from_task(task)
    candidate = study.view()['candidates'][0]['candidate_id']
    changed = study.observe(candidate)
    assert len(study.view()['observations']) == 0
    assert len(changed.view()['observations']) == 1
    with pytest.raises(ValueError, match='already observed'):
        changed.observe(candidate)
    with pytest.raises(ValueError, match='Unknown candidate'):
        study.observe('missing')


@pytest.mark.parametrize('field,value', [('budget', 0), ('budget', 1.2), ('budget', True), ('policy', 'oracle_best')])
def test_condition_rejects_invalid_task(tmp_path, field, value):
    task = {**condition_task(condition_csv(tmp_path)), field: value}
    with pytest.raises(ValueError):
        run_condition_task(task)


def test_condition_rejects_nonfinite_measurement(tmp_path):
    with pytest.raises(ValueError, match='yield'):
        run_condition_task(condition_task(condition_csv(tmp_path, yields=(float('nan'), 2, 3))))


def test_condition_ucb_exhausts_without_repeats(tmp_path):
    task = {**condition_task(condition_csv(tmp_path)), 'budget': 5, 'policy': 'observed_category_ucb'}
    result = run_condition_task(task)
    assert len(result['observations']) == 3
    assert result['stop_reason'] == 'candidate_space_exhausted'
    assert result['evaluation']['simple_regret_percent'] == 0


def test_impurity_proxy_is_not_measured_truth():
    result = assess_impurities({'predicted_smiles': ['CCO'], 'proxy_impurities': ['CCO']})
    assert result['metrics'] is None
    assert result['evaluation_status'] == 'no_measured_labels'
    assert result['proxy_impurities'] == ['CCO']


def complete_impurity_assay():
    return {'annotation_coverage':'complete_within_assay_scope',
            'assay_method':'synthetic fixture assay', 'assay_scope':'finite fixture identities above reporting limit',
            'reporting_limit':{'value':0.1,'unit':'mass_percent','basis':'fixture sample'}}


def test_impurity_measured_precision_recall_deduplicates():
    result = assess_impurities({**complete_impurity_assay(), 'predicted_smiles': ['CCO', 'OCC', 'CC=O'],
        'measured_impurities': ['CCO'], 'measurement_source': {'url': 'https://example.org/test', 'locator': 'test fixture'}})
    assert result['metrics']['precision'] == 0.5
    assert result['metrics']['recall'] == 1.0
    assert result['metrics']['true_positives'] == 1
    assert result['evidence_kind'] == 'measured_impurity_annotations'


def test_impurity_unknown_and_confirmed_empty_are_different():
    with pytest.raises(ValueError, match='measurement_source'):
        assess_impurities({'predicted_smiles': [], 'measured_impurities': []})
    result = assess_impurities({'predicted_smiles': [], 'measured_impurities': [],
        'measurement_source': {'url': 'https://example.org/test', 'locator': 'test fixture'}})
    assert result['metrics']['recall'] is None
    assert result['metrics']['precision'] is None


def test_impurity_rejects_invalid_smiles():
    with pytest.raises(ValueError, match='SMILES'):
        assess_impurities({'predicted_smiles': ['not a molecule']})


def test_process_pareto_keeps_tradeoffs_and_unknowns():
    task = {'routes': [
        {'route_id': 'cheap', 'material_cost': 10, 'steps': 4, 'cost_currency': 'USD'},
        {'route_id': 'short', 'material_cost': 20, 'steps': 2, 'cost_currency': 'USD'},
        {'route_id': 'dominated', 'material_cost': 25, 'steps': 5, 'cost_currency': 'USD'},
        {'route_id': 'unknown', 'material_cost': None, 'steps': 1, 'cost_currency': 'USD'},
    ]}
    original = copy.deepcopy(task)
    result = select_process_routes(task)
    assert result['pareto_route_ids'] == ['cheap', 'short']
    assert result['unranked_route_ids'] == ['unknown']
    assert task == original
    assert result['evidence_kind'] == 'supplied_route_estimates'


def test_process_rejects_mixed_currencies():
    with pytest.raises(ValueError, match='currency'):
        select_process_routes({'routes': [
            {'route_id': 'a', 'material_cost': 1, 'steps': 1, 'cost_currency': 'USD'},
            {'route_id': 'b', 'material_cost': 1, 'steps': 1, 'cost_currency': 'EUR'},
        ]})


def bio_record():
    return {'record_id': 'rhea58148', 'reactants': ['CCOC(C)=O', 'O'],
        'products': ['CCO', 'CC(=O)[O-]', '[H+]'], 'enzyme_name': 'ethyl acetate hydrolase',
        'enzyme_class': '3.1.1.113', 'source_url': 'https://www.rhea-db.org/rhea/58148',
        'source_locator': 'RHEA:58148 reaction participants', 'evidence_kind': 'curated_database'}


def test_biocatalytic_exact_retrieval_retains_evidence_and_inventory():
    task = {'target_smiles': 'OCC', 'inventory_smiles': ['CCOC(C)=O', 'O'], 'records': [bio_record()]}
    result = retrieve_biocatalytic_routes(task)
    candidate = result['candidates'][0]
    assert candidate['match_kind'] == 'exact_product'
    assert candidate['inventory_complete'] is True
    assert candidate['supports_query_transformation'] is False
    assert candidate['supports_recorded_product_identity'] is True
    assert candidate['evidence_kind'] == 'curated_database'
    assert candidate['experimental_yield'] is None
    assert result['claims_experimental_validation'] is False


def test_biocatalytic_missing_reactant_is_unsolved():
    result = retrieve_biocatalytic_routes({'target_smiles': 'CCO', 'inventory_smiles': ['O'], 'records': [bio_record()]})
    assert result['candidates'][0]['inventory_complete'] is False
    assert result['candidates'][0]['missing_reactants'] == ['CCOC(C)=O']


@pytest.mark.parametrize('inventory', [[], ['COC(C)=O', 'O'], ['CCOC(C)=O', 'O'],
                                     ['CCOC(C)=O', 'O', 'COC(C)=O']])
def test_legacy_biocatalysis_inventory_does_not_bind_query_substrates(inventory):
    result = retrieve_biocatalytic_routes({'target_smiles': 'CCO',
        'inventory_smiles': inventory, 'records': [bio_record()]})
    candidate = result['candidates'][0]
    assert candidate['supports_query_transformation'] is False
    assert candidate['supports_recorded_product_identity'] is True
    assert candidate['query_reaction_binding'] == 'not_supplied_product_only_query'


def test_biocatalytic_analogue_is_not_exact_or_validated():
    result = retrieve_biocatalytic_routes({'target_smiles': 'CCCO', 'inventory_smiles': ['O'],
        'records': [bio_record()], 'analogue_threshold': 0.1})
    assert result['candidates'][0]['match_kind'] == 'product_similarity_analogue'
    assert result['candidates'][0]['supports_query_transformation'] is False


def test_biocatalytic_requires_source_location():
    record = {**bio_record(), 'source_locator': ''}
    with pytest.raises(ValueError, match='source_locator'):
        retrieve_biocatalytic_routes({'target_smiles': 'CCO', 'records': [record]})


def test_dispatch_inventory_uses_validator_and_rejects_unknown():
    result = dispatch_portfolio({'application': 'inventory_planning', 'route': {'id': 1}},
        inventory_validator=lambda task: {'checked': task['route']['id']})
    assert result == {'checked': 1}
    with pytest.raises(ValueError, match='validator'):
        dispatch_portfolio({'application': 'inventory_planning'})
    with pytest.raises(ValueError, match='application'):
        dispatch_portfolio({'application': 'unknown'})


def test_condition_view_mutation_cannot_change_evaluator(tmp_path):
    study = FiniteConditionStudy.from_task(condition_task(condition_csv(tmp_path)))
    view = study.view()
    view['candidates'][0]['conditions']['ligand'] = 'tampered'
    assert study.view()['candidates'][0]['conditions']['ligand'] == 'L0'


def test_condition_budget_cannot_be_exceeded(tmp_path):
    task = {**condition_task(condition_csv(tmp_path)), 'budget': 1}
    study = FiniteConditionStudy.from_task(task)
    ids = [row['candidate_id'] for row in study.view()['candidates']]
    observed = study.observe(ids[0])
    with pytest.raises(ValueError, match='budget exhausted'):
        observed.observe(ids[1])


@pytest.mark.parametrize('change', [
    {'source_url': ''}, {'source_locator': ''}, {'substrate': ''},
    {'substrate': 'not present'}, {'condition_columns': []},
    {'condition_columns': ['ligand', 'ligand']}, {'condition_columns': ['yield']},
    {'condition_columns': ['missing']}, {'seed': True},
])
def test_condition_rejects_incomplete_provenance_and_schema(tmp_path, change):
    with pytest.raises(ValueError):
        run_condition_task({**condition_task(condition_csv(tmp_path)), **change})


def test_condition_rejects_duplicate_measurements_without_aggregation(tmp_path):
    path = condition_csv(tmp_path)
    lines = path.read_text().splitlines()
    path.write_text('\n'.join(lines + [lines[1]]) + '\n')
    with pytest.raises(ValueError, match='replicate aggregation'):
        run_condition_task(condition_task(path))


def test_impurity_zero_hits_preserves_measured_failure():
    result = assess_impurities({**complete_impurity_assay(), 'predicted_smiles': ['CCO'], 'measured_impurities': ['CC=O'],
        'measurement_source': {'url': 'https://example.org/test', 'locator': 'test fixture'}})
    assert result['metrics']['f1'] == 0
    assert result['metrics']['false_positives'] == 1
    assert result['metrics']['false_negatives'] == 1


@pytest.mark.parametrize('predictions', ['', [''], ['CCO', None]])
def test_impurity_rejects_invalid_collection(predictions):
    with pytest.raises(ValueError):
        assess_impurities({'predicted_smiles': predictions})


@pytest.mark.parametrize('routes', [[],
    [{'route_id': '', 'steps': 1}],
    [{'route_id': 'a', 'steps': True}],
    [{'route_id': 'a', 'steps': 1, 'material_cost': float('nan')}],
    [{'route_id': 'a', 'steps': 1, 'material_cost': 4}],
    [{'route_id': 'a', 'steps': 1}, {'route_id': 'a', 'steps': 2}],
])
def test_process_rejects_invalid_estimates(routes):
    with pytest.raises(ValueError):
        select_process_routes({'routes': routes})


def test_biocatalytic_records_path_and_no_match(tmp_path):
    path = tmp_path / 'records.json'
    path.write_text(json.dumps([bio_record()]))
    result = retrieve_biocatalytic_routes({'target_smiles': 'c1ccccc1', 'records_path': str(path),
                                          'analogue_threshold': 1.0})
    assert result['candidates'] == []


@pytest.mark.parametrize('change', [
    {'records': None}, {'analogue_threshold': True}, {'analogue_threshold': float('nan')},
    {'records': [{**bio_record(), 'evidence_kind': 'predicted'}]},
    {'records': [{**bio_record(), 'reactants': []}]},
    {'records': [bio_record(), bio_record()]},
])
def test_biocatalytic_rejects_unverified_record_shapes(change):
    with pytest.raises(ValueError):
        retrieve_biocatalytic_routes({'target_smiles': 'CCO', 'records': [bio_record()], **change})


def test_dispatch_impurity_contract():
    result = dispatch_portfolio({'application': 'impurity_analysis', 'predicted_smiles': []})
    assert result['evaluation_status'] == 'no_measured_labels'


def test_five_portfolio_examples_execute_end_to_end(tmp_path):
    import subprocess
    import sys
    package_root = Path(__file__).resolve().parents[1]
    archive = package_root / 'examples/portfolio'
    if any(not (archive / name).is_file() for name in
           ('run_examples.py', 'doyle_measured_subset.csv')):
        pytest.skip('Optional archived measured portfolio replay is not bundled in the source-only release')
    run = subprocess.run([sys.executable, str(package_root / 'examples/portfolio/run_examples.py'),
                          '--output-dir', str(tmp_path)], cwd=package_root,
                         capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    results = {p.name: json.loads(p.read_text()) for p in tmp_path.glob('*.result.json')}
    assert len(results) == 5
    assert results['conditions.result.json']['evaluations_used'] == 20
    assert results['conditions.result.json']['evidence_kind'] == 'measured_dataset_replay'
    assert results['impurities.result.json']['metrics'] is None
    assert results['biocatalysis.result.json']['claims_experimental_validation'] is False
    assert results['inventory.result.json']['solved'] is False


@pytest.mark.parametrize('coverage',[None,'unknown','partial'])
def test_impurity_unknown_coverage_does_not_invent_negative_labels(coverage):
    task={'predicted_smiles':['CCO','CO'],'measured_impurities':['CCO'],
          'measurement_source':{'url':'https://example.org/test','locator':'synthetic fixture'}}
    if coverage is not None:task={**task,'annotation_coverage':coverage}
    result=assess_impurities(task);m=result['metrics']
    assert m['known_annotation_recall']==1 and m['true_positives']==1
    assert m['precision'] is None and m['recall'] is None and m['f1'] is None
    assert m['false_positives'] is None and m['false_negatives'] is None
    assert m['unlabeled_predictions']==1 and result['claims_experimental_validation'] is False
    assert result['verification_status']=='not_independently_verified'


@pytest.mark.parametrize('change',[{'assay_method':''},{'assay_scope':None},{'reporting_limit':None},
    {'reporting_limit':{'value':True,'unit':'mass_percent','basis':'fixture'}},
    {'annotation_coverage':'exhaustive'}, {'measurement_source':{'url':'file:///private','locator':'fixture'}}])
def test_impurity_complete_metrics_require_valid_assay_scope(change):
    task={**complete_impurity_assay(),'predicted_smiles':['CCO'],'measured_impurities':['CO'],
          'measurement_source':{'url':'https://example.org/test','locator':'synthetic fixture'},**change}
    with pytest.raises(ValueError):assess_impurities(task)


def test_impurity_legacy_complete_metrics_keep_unbound_warning_and_immutability():
    task={**complete_impurity_assay(),'predicted_smiles':['CCO','CO'],'measured_impurities':['CCO'],
          'measurement_source':{'url':'https://example.org/test','locator':'synthetic fixture'}}
    original=copy.deepcopy(task);result=assess_impurities(task)
    assert task==original and result['recipe_binding_status']=='not_bound_legacy_helper'
    assert result['metrics']['scope']=='supplied_finite_assay_identity_set'
    assert result['evidence_status']=='supplied_measurement_claim'
    assert result['claims_experimental_validation'] is False


def test_impurity_partial_metadata_cannot_alias_mutable_values():
    task={'predicted_smiles':['CCO'],'measured_impurities':['CO'],'assay_scope':['mutable'],
          'measurement_source':{'url':'https://example.org/test','locator':'synthetic fixture'}}
    with pytest.raises(ValueError):assess_impurities(task)
