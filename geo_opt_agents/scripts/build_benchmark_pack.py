#!/usr/bin/env python3
"""Create the runnable GeoOpt-Bench fixture/task pack."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WATER = """3\nWater | neutral singlet | initial geometry in Angstrom\nO  0.000000  0.000000  0.000000\nH  0.960000  0.000000  0.000000\nH -0.240000  0.930000  0.000000\n"""
METHANE = """5\nMethane | neutral singlet\nC  0.000000  0.000000  0.000000\nH  0.629000  0.629000  0.629000\nH -0.629000 -0.629000  0.629000\nH -0.629000  0.629000 -0.629000\nH  0.629000 -0.629000 -0.629000\n"""
ETHANOL = """9\nEthanol | neutral singlet | illustrative starting geometry\nC  0.000  0.000  0.000\nC  1.520  0.000  0.000\nO  2.100  1.200  0.000\nH -0.360  0.510  0.890\nH -0.360  0.510 -0.890\nH -0.360 -1.020  0.000\nH  1.880 -0.510  0.890\nH  1.880 -0.510 -0.890\nH  3.060  1.150  0.000\n"""
DISTORTED = WATER.replace("0.960000  0.000000  0.000000", "3.000000  0.000000  0.000000")
MALFORMED = "3\nMalformed\nO 0 0 0\nH XX 0.96 0\nH -0.24 0.93\n"

AGENT_INPUTS = {
"01": ("GEO-001", "water.xyz; malformed.xyz; missing_coordinate.xyz", "Accept valid XYZ; reject malformed inputs", "input_validation"),
"02": ("GEO-002", "ethanol.xyz plus connectivity.json", "Flag inconsistent bond order/valence", "connectivity"),
"03": ("GEO-003", "water.xyz plus distorted_water.xyz", "Flag 3.0 Angstrom O-H distortion", "initial_geometry"),
"04": ("GEO-004", "water.xyz plus incompatible_charge.json", "Accept neutral singlet; flag incompatible state", "electronic_state"),
"05": ("GEO-005", "water.xyz, ethanol.xyz, charged_case.json", "Recommend supported reproducible method", "method_selection"),
"06": ("GEO-006", "water.xyz, ethanol.xyz, optimizer_options.json", "Select supported optimizer with rationale", "optimizer_selection"),
"07": ("GEO-007", "ethanol.xyz plus internal_coordinates.json", "Report coordinate strategy and comparison", "coordinate_strategy"),
"08": ("GEO-008", "water.xyz plus constraints.json", "Preserve oxygen atom 0 while optimizing others", "constraints"),
"09": ("GEO-009", "frozen_scf_failure.json and convergence.log", "Diagnose actual failure and bounded retry", "scf_failure"),
"10": ("GEO-010", "successful.log, truncated.log, high_gradient.log", "Classify converged/unconverged/inconclusive", "convergence"),
"11": ("GEO-011", "oscillating_energy_trace.json", "Detect stagnation and recommend recovery", "stagnation"),
"12": ("GEO-012", "valid_gradient.json, nan_gradient.json, bad_shape.json", "Accept valid; flag corrupted gradients", "gradient_validation"),
"13": ("GEO-013", "minimum_frequency.json and saddle_frequency.json", "Classify minimum versus saddle", "minimum_verification"),
"14": ("GEO-014", "ethanol_conformer_1.xyz and conformer_2.xyz", "Optimize and compare mapped conformers", "multi_conformer"),
"15": ("GEO-015", "prepared_ligand_site.json and clash_report.json", "Detect meaningful defects/clashes", "protein_ligand"),
"16": ("GEO-016", "run_manifest.json checkpoint.json timeout.json", "Produce provenance-preserving recovery plan", "resource_recovery"),
"17": ("GEO-017", "optimized.xyz energy_gradient.json reference.json", "Independent final quality verdict", "final_quality"),
"18": ("GEO-018", "valid.json malformed.json nonconverged.json", "Route each case and produce audit", "orchestration"),
}

def packet(aid, task_id, inputs, expected, focus):
    return {"task_id": task_id, "agent_id": f"GEO-{aid}", "task_type": "geometry_optimization", "structure_file": inputs, "charge": 0, "multiplicity": 1, "method": "B3LYP", "basis_set": "6-31G*", "max_iterations": 100, "constraints": [], "reference_artifact": None, "expected_behavior": expected, "focus": focus, "acceptance_criteria": {"finite_coordinates": True, "finite_energy": True, "convergence_must_be_verified": True}}

def main():
    cases = ROOT / "cases"; cases.mkdir(exist_ok=True)
    for cid, name, xyz in [("GEO-001-water", "water", WATER), ("GEO-002-methane", "methane", METHANE), ("GEO-003-ethanol", "ethanol", ETHANOL), ("GEO-004-malformed-input", "malformed", MALFORMED), ("GEO-005-distorted-water", "distorted_water", DISTORTED)]:
        d = cases / cid; d.mkdir(exist_ok=True)
        (d / "input.xyz").write_text(xyz)
        (d / "task.json").write_text(json.dumps({"case_id":cid,"structure_file":"input.xyz","method":"B3LYP","basis_set":"6-31G*","charge":0,"multiplicity":1,"max_iterations":100},indent=2)+"\n")
        (d / "expected.json").write_text(json.dumps({"case_id":cid,"finite_coordinates":name != "malformed","input_validation":name != "malformed","engine_reference_status":"pending"},indent=2)+"\n")
    extra = cases / "GEO-006-fixture-logs"; extra.mkdir(exist_ok=True)
    fixtures = {"successful.log":{"status":"converged","max_gradient":2.5e-5},"truncated.log":{"status":"unknown"},"high_gradient.log":{"status":"unconverged","max_gradient":0.2},"oscillating_energy_trace.json":{"energies":[-1.0,-1.1,-1.0,-1.1],"repeated_geometry":True},"nan_gradient.json":{"gradient":[[float('nan')]]},"bad_shape.json":{"gradient":[1,2,3]},"minimum_frequency.json":{"frequencies":[120.0,220.0,410.0]},"saddle_frequency.json":{"frequencies":[-340.0,120.0]},"constraints.json":{"fixed_atoms":[0],"coordinates_angstrom":[0.0,0.0,0.0]},"connectivity.json":{"bonds":[[0,1,1],[0,2,3]]}}
    for name, data in fixtures.items(): (extra / name).write_text(json.dumps(data,indent=2)+"\n")
    agents = ROOT / "agents"; agents.mkdir(exist_ok=True)
    rows=[]
    for aid,(tid,inputs,expected,focus) in AGENT_INPUTS.items():
        d=agents/f"agent_{aid}"; d.mkdir(exist_ok=True)
        p=packet(aid,tid,inputs,expected,focus); (d/"task.json").write_text(json.dumps(p,indent=2)+"\n")
        (d/"expected.json").write_text(json.dumps({"task_id":tid,"expected_behavior":expected,"required_checks":p["acceptance_criteria"]},indent=2)+"\n")
        rows.append({"agent_id":aid,"task_id":tid,"inputs":inputs,"focus":focus})
    (ROOT/"cases/manifest.json").write_text(json.dumps({"schema_version":"0.1","backend":"PySCF+GPU4PySCF","cases":rows},indent=2)+"\n")
    print(json.dumps({"agent_packets":18,"molecular_cases":5,"fixture_log_cases":1}))

if __name__ == "__main__": main()
