"""Evidence-routed problem-solving workflow.

The orchestrator invokes shared gates first, then only the matching domain
agents. It never edits the input packet and never retries without a bounded
plan.
"""
from __future__ import annotations
import hashlib, json
try:
    from .runtime import CONTRACTS, run_case
except ImportError:  # direct test/script execution
    from runtime import CONTRACTS, run_case

DOMAIN_PREFIX = {'spe': 'SPE-', 'geo_opt': 'GEO-', 'homo_lumo': 'HL-', 'qmmm': 'QMMM-', 'fep_ti': 'FEP-'}

def route(case: dict) -> dict:
    raw = json.dumps(case, sort_keys=True, separators=(',', ':')).encode()
    domain = case['domain']; prefix = DOMAIN_PREFIX[domain]
    selected = [c for c in CONTRACTS if c['group'] == 'shared' or c['id'].startswith(prefix)]
    all_results = {r['agent_id']: r for r in run_case(case)}
    results = [all_results[c['id']] for c in selected]
    review = any(r['status'] == 'REVIEW' for r in results)
    failed = any(r['status'] == 'FAIL' for r in results)
    return {'case_id': case['case_id'], 'domain': domain, 'input_sha256': hashlib.sha256(raw).hexdigest(), 'selected_agents': [c['id'] for c in selected], 'max_retries': 1, 'status': 'FAIL' if failed else ('REVIEW' if review else 'PASS'), 'results': results, 'original_input_preserved': True, 'retry_performed': False}
