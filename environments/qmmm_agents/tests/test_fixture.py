import json
from pathlib import Path
def test_fixture_contains_all_gates():
    p = Path(__file__).parents[1]/'cases/fixture.json'
    case = json.loads(p.read_text())
    required = ['qm_region_defined','boundary_valid','charge_accounted','embedding_declared','qm_scf_converged','coupling_checked','expanded_regions','checkpoint_compatible','provenance_complete']
    assert all(k in case for k in required)
