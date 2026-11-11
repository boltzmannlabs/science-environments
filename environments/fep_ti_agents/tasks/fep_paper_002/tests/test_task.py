import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_input_validation():
    d=json.loads((ROOT/'evaluation/input_validation.json').read_text())
    assert d['status']=='PASS' and d['edge']['direction']=='23477->23482'
    assert d['edge']['ddg_kcal_mol']==-1.16
    assert d['protein']['pdb_id']=='2QBS'
def test_config_b_independent():
    d=json.loads((ROOT/'execution/generated_config.json').read_text())
    assert d['provenance']['read_config_A'] is False
    assert d['provenance']['read_reference_answer'] is False
    assert d['status']=='REVIEW'
    assert 'published_ddg_kcal_mol' not in d
def test_qualification_is_conservative():
    d=json.loads((ROOT/'expected_outputs/qualification.json').read_text())
    assert d['required_status']=='REVIEW'

def test_endpoint_parameterization_is_recorded_without_overclaiming():
    d=json.loads((ROOT/'execution/parameterization.json').read_text())
    assert d['status']=='SUPERSEDED_INVALID_CHARGE'
    assert d['qualification']=='REVIEW'
    assert d['force_field']=='GAFF2'
    assert d['charge_method']=='AM1-BCC'
    assert d['validation']['both_endpoints_parameterized'] is True
    assert d['validation']['complex_topology']=='PASS'
    for endpoint in d['endpoints'].values():
        assert (ROOT/endpoint['mol2']).exists()
        assert (ROOT/endpoint['frcmod']).exists()
        assert (ROOT/endpoint['prmtop']).exists()
        assert (ROOT/endpoint['inpcrd']).exists()
    assert d['validation']['standalone_endpoint_topologies'] is True

def test_agent_execution_trace_is_auditable_and_honest():
    d=json.loads((ROOT/'execution/agent_execution_trace.json').read_text())
    assert d['trace_status']=='RECORDED'
    assert d['autonomous_llm_agent_execution'] is False
    assert {e['agent_role'] for e in d['events']} == {'FEP-AG03','FEP-AG05','FEP-AG15'}
    assert d['events'][1]['command'].startswith('tleap')

def test_paper_comparison_and_architecture_matrix_are_conservative():
    comparison=json.loads((ROOT/'evaluation/paper_parameter_comparison.json').read_text())
    matrix=json.loads((ROOT/'evaluation/agent_configuration_comparison.json').read_text())
    assert comparison['qualification']=='REVIEW'
    assert comparison['summary']['missing'] > 0
    assert matrix['experiments']['A_general_agent']['status']=='NOT_EXECUTED'
    assert matrix['experiments']['B_specialist_assisted']['topology_generation']=='STANDALONE_ENDPOINTS_PASS'
    assert matrix['metrics']['scientific_qualification']=='REVIEW'

def test_paper_configuration_matrix_runs_reference_alternative_and_stop_case():
    d=json.loads((ROOT/'execution/config_comparison.json').read_text())
    assert d['benchmark_focus']=='paper-to-environment setup reconstruction'
    assert d['configs']['config_B_agent']['status']=='SETUP_PASS'
    assert d['configs']['config_B_agent']['standalone_endpoint_topologies'] is True
    assert d['configs']['config_C_alternative']['status']=='REVIEW'
    assert d['configs']['config_D_perturbed']['status']=='FAIL'
    assert d['configs']['config_D_perturbed']['execution']=='STOPPED'

def test_protein_preparation_records_charge_and_tleap_validation():
    d=json.loads((ROOT/'execution/protein_preparation.json').read_text())
    assert d['status']=='SETUP_VALIDATED'
    assert d['independent_checks']['tleap_errors']==0
    assert d['independent_checks']['net_charge_before_neutralization']==-7.0
    assert d['independent_checks']['neutralization']=='PASS'

def test_complex_endpoints_are_independently_validated_without_overclaiming():
    d=json.loads((ROOT/'execution/complex_preparation_corrected.json').read_text())
    assert d['status']=='SETUP_VALIDATED'
    assert d['qualification']=='REVIEW'
    assert d['checks']['formal_charge_consistency']=='PASS'
    assert d['checks']['neutralized_endpoint_charge_within_0.01_e']=='PASS'
    assert d['checks']['hybrid_alchemical_topology']=='PASS'
    assert d['checks']['lambda_window_simulation']=='PASS_BOUNDED'
    for endpoint in d['endpoints'].values():
        assert endpoint['tleap_errors']==0
        assert endpoint['sodium_ions']==9
        assert abs(endpoint['net_charge']) <= 0.01
        for key in ('solvated_prmtop','solvated_inpcrd'):
            assert (ROOT/endpoint[key]).exists()

def test_corrected_gpu_run_is_recorded_and_conservative():
    d=json.loads((ROOT/'execution/openfe_bounded_run/run_record.json').read_text())
    assert d['platform']=='OpenCL'
    assert 'NVIDIA GeForce RTX 3060' in d['gpu_backend']
    assert d['legs']['solvent']['setup_ok'] is True
    assert d['legs']['solvent']['simulation_ok'] is True
    assert d['legs']['complex']['setup_ok'] is True
    assert d['legs']['complex']['simulation_ok'] is True
    assert d['qualification']=='REVIEW'

def test_corrected_parameterization_matches_frozen_formal_charge():
    d=json.loads((ROOT/'execution/parameterization_corrected.json').read_text())
    assert d['checks']['formal_charge_consistency']=='PASS'
    assert d['formal_charge_required']==-2
    for endpoint in d['endpoints'].values():
        assert endpoint['formal_charge']==-2
        assert abs(endpoint['partial_charge_sum'] + 2.0) < 0.01

def test_bounded_run_independent_evaluation_rejects_false_convergence():
    d=json.loads((ROOT/'execution/openfe_bounded_run/independent_evaluation.json').read_text())
    assert d['status']=='REVIEW'
    for leg in d['legs'].values():
        assert leg['finite_energies'] is True
        assert leg['production_samples_per_window']==1
        assert leg['convergence']=='INSUFFICIENT_SAMPLES'
        assert leg['uncertainty']=='NOT_ESTIMABLE'

def test_extended_gpu_replica_has_complete_window_execution_but_stays_review():
    run = ROOT/'execution/openfe_production_replica1'
    record = json.loads((run/'run_record.json').read_text())
    evaluation = json.loads((run/'independent_evaluation.json').read_text())
    assert record['platform'] == 'OpenCL'
    assert 'NVIDIA GeForce RTX 3060' in record['gpu_backend']
    assert record['windows'] == 11
    assert record['production_ps'] == 10
    assert record['qualification'] == 'REVIEW'
    for leg in ('solvent', 'complex'):
        assert record['legs'][leg]['setup_ok'] is True
        assert record['legs'][leg]['simulation_ok'] is True
        assert evaluation['legs'][leg]['finite_energies'] is True
        assert evaluation['legs'][leg]['lambda_windows'] == 11
        assert evaluation['legs'][leg]['production_samples_per_window'] == 10
        assert evaluation['legs'][leg]['convergence'] == 'INSUFFICIENT_SAMPLES'
        assert evaluation['legs'][leg]['uncertainty'] == 'NOT_ESTIMABLE'
        assert evaluation['legs'][leg]['qualification'] == 'REVIEW'
