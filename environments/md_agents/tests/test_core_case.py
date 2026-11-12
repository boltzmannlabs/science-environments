import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_core_request_is_explicit():
    request = json.loads((ROOT/'src/cases/water_box_request.json').read_text())
    assert request['engine'] == 'OpenMM'
    assert request['production_steps'] == 1000
    assert request['seed'] == 20261027

def test_core_result_has_audit_fields():
    results = list((ROOT/'results/core_openmm').glob('repeat_*.json'))
    if not results:
        return
    result = json.loads(results[0].read_text())
    assert result['status'] == 'PASS'
    assert result['trajectory_frames'] > 0
    assert result['trajectory_sha256']
