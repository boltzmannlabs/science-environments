"""Deterministic evidence-gated runtime for the cross-domain agents."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # environments/
CONTRACT_FILES = [
    Path(__file__).parent/'contracts.json',
    ROOT/'spe_agents/problem_solving/contracts.json',
    ROOT/'geo_opt_agents/problem_solving/contracts.json',
    ROOT/'homo_lumo_agents/problem_solving/contracts.json',
    ROOT/'qmmm_agents/problem_solving/contracts.json',
    ROOT/'fep_ti_agents/problem_solving/contracts.json',
]
CONTRACTS = [item for path in CONTRACT_FILES for item in json.loads(path.read_text())]

def _status(agent_id: str, case: dict) -> tuple[str, str]:
    if not case.get('immutable_inputs') or not case.get('first_failure'):
        return 'FAIL', 'immutable inputs or first failure evidence missing'
    if not case.get('provenance'):
        return 'REVIEW', 'provenance evidence incomplete'
    if agent_id.startswith('FEP-') and not case.get('overlap_evidence'):
        return 'REVIEW', 'FEP overlap evidence intentionally insufficient'
    if agent_id in {'PS-03', 'PS-04'} and not case.get('bounded_plan'):
        return 'REVIEW', 'bounded recovery plan unavailable'
    if agent_id in {'PS-05', 'PS-06'} and not case.get('independent_audit'):
        return 'REVIEW', 'independent audit evidence unavailable'
    if agent_id.startswith('QMMM-') and not case.get('qmmm_boundary_evidence', True):
        return 'REVIEW', 'QM/MM boundary evidence unavailable'
    if agent_id.startswith('GEO-') and case.get('convergence_without_minimum'):
        return 'REVIEW', 'convergence is not minimum verification'
    return 'PASS', 'diagnosis, bounded action, verification, and provenance gates present'

def run_case(case: dict) -> list[dict]:
    rows = []
    for contract in CONTRACTS:
        status, evidence = _status(contract['id'], case)
        rows.append({'agent_id': contract['id'], 'name': contract['name'], 'group': contract['group'], 'case_id': case['case_id'], 'status': status, 'evidence': evidence})
    return rows
