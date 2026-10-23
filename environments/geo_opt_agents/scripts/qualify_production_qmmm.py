#!/usr/bin/env python3
"""Qualify the preserved real QM/MM execution for the Geo-Opt report.

This reads existing evidence; it does not alter the SPE baseline or rerun it.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/boltzmann15/github/science-benchmarking/spe_agents/reports/engine_execution/repairs/agent_15_qualification.json')
def main():
    data=json.loads(SOURCE.read_text()); required=['amber14_topology_created','partition_passed','electronic_embedding_active','nonzero_mm_environment','scf_converged','energy_components_present']; checks=data['checks']; passed=all(checks.get(k) is True for k in required)
    out={"qualification_id":"GEOOPT-QMMM-PRODUCTION-001","status":"pass" if passed else "review","evidence_source":str(SOURCE),"source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),"system":data["system"],"execution":data["execution"],"energies_hartree":data["energies_hartree"],"checks":checks,"scientific_assessment":data["scientific_assessment"],"warnings":data.get("warnings",[]),"scope":"Preserved real electronic QM/MM execution; production qualification is limited to this prepared system and settings."}
    outdir=ROOT/'reports/production_qmmm'; outdir.mkdir(parents=True,exist_ok=True); (outdir/'qualification.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({"status":out["status"],"required_checks":len(required),"source_sha256":out["source_sha256"]}))
if __name__=='__main__': main()
