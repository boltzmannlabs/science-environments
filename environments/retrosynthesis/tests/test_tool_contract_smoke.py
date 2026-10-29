"""Reproducible subprocess acceptance for offline scientific contracts."""
import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/run_tool_contract_smoke.py'


def test_tool_contract_smoke_covers_all_capabilities_without_live_science(tmp_path):
    output = tmp_path/'smoke'
    result = subprocess.run([sys.executable,str(SCRIPT),'--output',str(output)],capture_output=True,text=True,timeout=30)
    assert result.returncode == 0, result.stderr
    receipt = json.loads((output/'receipt.json').read_text())
    assert receipt['status'] == 'passed'
    assert receipt['live_llm_calls'] == receipt['scientific_model_inferences'] == 0
    assert receipt['configured_capabilities_tested'] == 8
    assert receipt['synthetic_fixtures_not_experimental_measurements']
    assert receipt['resume']['usage_preserved'] and receipt['resume']['alias_retrieval_quota_enforced']
    assert receipt['evidence']['stale_attestation_remains_unresolved']
    schema = json.loads((output/'tool-contract.v1.json').read_text())
    assert len(schema['capabilities']) == 10
    cn = next(row for row in schema['capabilities'] if row['name'] == 'score_cn_conditions')
    assert cn['availability'] == 'not_configured'
    public_yield = next(row for row in schema['capabilities'] if row['name'] == 'predict_reaction_yield')
    assert public_yield['availability'] == 'not_configured'
    assert all(row['input_schema'] and row['output_schema'] for row in schema['capabilities'])


def test_tool_contract_smoke_refuses_to_overwrite_existing_output(tmp_path):
    output = tmp_path/'existing'; output.mkdir()
    result = subprocess.run([sys.executable,str(SCRIPT),'--output',str(output)],capture_output=True,text=True,timeout=30)
    assert result.returncode != 0
    assert 'exists' in result.stderr.lower()
    assert list(output.iterdir()) == []
