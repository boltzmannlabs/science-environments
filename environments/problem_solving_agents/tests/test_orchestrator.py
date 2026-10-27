import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from orchestrator import route

def test_routing_is_domain_specific_and_bounded():
    cases = json.loads((Path(__file__).parents[1]/'cases/fixtures.json').read_text())
    for case in cases:
        result = route(case)
        assert result['original_input_preserved'] is True
        assert result['max_retries'] == 1
        assert all(a.startswith('PS-') or a.startswith({'spe':'SPE-','geo_opt':'GEO-','homo_lumo':'HL-','qmmm':'QMMM-','fep_ti':'FEP-'}[case['domain']]) for a in result['selected_agents'])
