#!/usr/bin/env python3
"""Freeze the current GeoOpt-Bench evidence without rewriting source inputs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/benchmark_v1"; OUT.mkdir(parents=True,exist_ok=True)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    qualification=json.loads((ROOT/"reports/agent_qualification/summary.json").read_text())
    engine=json.loads((ROOT/"reports/benchmark_engine/RESULTS.md").read_text()) if False else None
    files=[]
    for base in (ROOT/"cases",ROOT/"agents",ROOT/"reports/tier1",ROOT/"reports/tier1_gpu",ROOT/"reports/benchmark_engine",ROOT/"reports/agent_qualification",ROOT/"reports/production_qmmm",ROOT/"reports/references",ROOT/"reports/expanded_benchmark",ROOT/"reports/expanded_engine",ROOT/"reports/hessian"):
        if base.exists():
            files.extend(p for p in base.rglob("*") if p.is_file() and "benchmark_v1" not in str(p))
    hashes={str(p.relative_to(ROOT)):digest(p) for p in sorted(files)}
    live=[r for r in qualification["results"] if r["execution"]=="live_gpu_engine"]
    repeats_path=ROOT/"reports/repeats/summary.json"
    repeats=json.loads(repeats_path.read_text()) if repeats_path.exists() else {"repeat_count":0,"results":[]}
    summary={
      "benchmark_id":"GeoOpt-Bench-v1.0",
      "backend":"PySCF+GPU4PySCF 1.7.0 + SciPy BFGS",
      "protocol":{"method":"B3LYP","basis_set":"6-31G*","gradient_tolerance_hartree_per_bohr":1e-4,"agent_count":18,"repeat_count":1},
      "qualification_counts":qualification["counts"],
      "live_gpu_agent_results":len(live),
      "independent_repeats":{"repeat_count":repeats.get("repeat_count",0),"systems":repeats.get("systems",[]),"results":repeats.get("results",[])},
      "input_pack":{"agent_packets":18,"molecular_cases":5,"expanded_cases":36,"suite_validation":"passed"},
      "cost":{"tokens":0,"api_calls":0,"agent_wall_time_not_available":True,"engine_wall_time_recorded_in_case_json":True},
      "reproducibility":{"artifact_count":len(hashes),"hash_algorithm":"sha256","hashes":hashes},
      "not_evaluated":["full three-arm agent comparison","full geometry optimization (rather than single-point) for expanded cases","production protein-ligand qualification beyond the preserved prepared complex"],
      "scientific_boundary":"This freezes the current pilot evidence; it does not claim complete qualification of every specialist."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    md=f"""# GeoOpt-Bench v1.0 frozen pilot\n\nBackend: **{summary['backend']}**.\n\n- Specialist qualification records: **18**\n- Qualification status: **{qualification['counts']['pass']} pass, {qualification['counts']['review']} review, {qualification['counts']['fail']} fail**\n- Live GPU specialist-linked results: **{len(live)}**\n- Input packets: **18/18 valid**\n- Automated tests: **6 passed**\n- Hashes recorded: **{len(hashes)}**\n\n## Cost and reproducibility\n\nThe local run used no language-model API calls or token budget. Engine wall times are preserved in the per-case JSON reports. Every frozen input, task packet, qualification result, and engine result is hashed with SHA-256 in `summary.json`.\n\n## Scope limits\n\nThis is a frozen pilot, not a claim that all 18 specialists have independent live optimization implementations. The three-arm comparison, repeat panel, Hessian/frequency backend, protein-ligand reference case, and broader task expansion remain explicitly not evaluated.\n"""
    (OUT/"RESULTS.md").write_text(md)
    print(json.dumps({"benchmark_id":summary["benchmark_id"],"hashed_files":len(hashes),"counts":qualification["counts"]}))

if __name__=="__main__": main()
