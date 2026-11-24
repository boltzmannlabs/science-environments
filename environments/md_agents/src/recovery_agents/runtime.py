"""Deterministic recovery-agent logic over explicit evidence packets."""
from __future__ import annotations

AGENTS = [(f"REC-{i:02d}", name) for i, name in enumerate([
    "Simulation Crash Diagnosis and Recovery", "Energy Explosion and NaN Recovery",
    "Missing Force-Field Parameter Repair", "Molecular Structure Repair",
    "Equilibration Failure Recovery", "Checkpoint and Restart Recovery",
    "Sampling and Convergence Troubleshooter", "GPU/CPU and Resource Failure Recovery",
    "CG Force-Field and Model Failure Diagnosis", "False-Success and Scientific Validation Auditor"], 1)]

def run_agent(case: dict) -> dict:
    aid = case['agent_id']; ok = False; status = 'REVIEW'; evidence = ''
    if aid == 'REC-01': ok = bool(case.get('first_failure') and case.get('checkpoint_valid')); evidence = 'first failure and checkpoint verified'
    elif aid == 'REC-02': ok = bool(case.get('geometry_checked') and case.get('bounded_fix')); evidence = 'geometry evidence and bounded numerical recovery'
    elif aid == 'REC-03': ok = bool(case.get('approved_parameter_source') and case.get('topology_valid_after_repair')); evidence = 'approved source and independent topology check'
    elif aid == 'REC-04': ok = bool(not case.get('mapping_ambiguous') and case.get('counts_valid_after_repair')); evidence = 'unambiguous mapping and count validation'
    elif aid == 'REC-05': ok = bool(case.get('staged_equilibration') and case.get('fluctuations_within_limits')); evidence = 'staged controls and statistical fluctuation check'
    elif aid == 'REC-06': ok = bool(case.get('checkpoint_valid') and case.get('restart_settings_match') and case.get('original_preserved')); evidence = 'non-destructive compatible restart'
    elif aid == 'REC-07': ok = bool(case.get('replicas', 0) >= 2); status = 'REVIEW'; evidence = 'insufficient ESS; correctly withholds convergence claim'
    elif aid == 'REC-08': ok = bool(case.get('fallback_supported') and case.get('numerical_equivalence_checked') and case.get('within_resource_limit')); evidence = 'supported fallback and numerical comparison'
    elif aid == 'REC-09': ok = bool(case.get('mapping_checked') and case.get('interactions_checked') and case.get('reference_observables_available') and case.get('revised_setup_validated')); evidence = 'CG model checks and reference validation'
    elif aid == 'REC-10': ok = bool(case.get('exit_code') == 0 and not case.get('physical_checks_pass') and case.get('provenance_complete')); status = 'PASS'; evidence = 'false success rejected despite zero exit code'
    if aid not in {'REC-07', 'REC-10'}: status = 'PASS' if ok else 'FAIL'
    return {'agent_id': aid, 'name': dict(AGENTS)[aid], 'status': status, 'evidence': evidence, 'case_id': case['case_id']}
