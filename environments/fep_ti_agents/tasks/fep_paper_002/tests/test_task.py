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
def test_qualification_is_conservative():
    d=json.loads((ROOT/'expected_outputs/qualification.json').read_text())
    assert d['required_status']=='REVIEW'

def test_endpoint_parameterization_is_recorded_without_overclaiming():
    d=json.loads((ROOT/'execution/parameterization.json').read_text())
    assert d['status']=='SETUP_COMPLETE'
    assert d['qualification']=='REVIEW'
    assert d['force_field']=='GAFF2'
    assert d['charge_method']=='AM1-BCC'
    assert d['validation']['both_endpoints_parameterized'] is True
    assert d['validation']['complex_topology']=='PENDING'
    for endpoint in d['endpoints'].values():
        assert (ROOT/endpoint['mol2']).exists()
        assert (ROOT/endpoint['frcmod']).exists()
