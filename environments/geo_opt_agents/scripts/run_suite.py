#!/usr/bin/env python3
"""Validate the complete GeoOpt-Bench input pack and summarize runnable cases."""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=("task_id","agent_id","task_type","structure_file","charge","multiplicity","method","basis_set","max_iterations","acceptance_criteria")

def validate_xyz(path: Path) -> dict:
    lines=path.read_text().splitlines(); n=int(lines[0]); rows=lines[2:]
    valid=len(rows)==n
    for row in rows:
        parts=row.split()
        try:
            row_valid=len(parts)==4 and all(math.isfinite(float(x)) for x in parts[1:])
        except ValueError:
            row_valid=False
        valid &= row_valid
    return {"atoms_declared":n,"rows":len(rows),"valid":bool(valid)}

def main():
    results=[]
    for p in sorted((ROOT/"agents").glob("agent_*/task.json")):
        d=json.loads(p.read_text()); missing=[k for k in REQUIRED if k not in d]
        results.append({"agent_id":d.get("agent_id"),"task_id":d.get("task_id"),"valid_packet":not missing,"missing":missing,"input":d["structure_file"]})
    structures=[]
    for p in sorted((ROOT/"cases").glob("*/input.xyz")):
        structures.append({"case":p.parent.name,"path":str(p.relative_to(ROOT)),**validate_xyz(p)})
    summary={"backend":"PySCF+GPU4PySCF","agent_packets":len(results),"valid_packets":sum(r["valid_packet"] for r in results),"structures":structures,"results":results}
    out=ROOT/"reports"/"suite"; out.mkdir(parents=True,exist_ok=True)
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"agent_packets":summary["agent_packets"],"valid_packets":summary["valid_packets"],"structures":[(x["case"],x["valid"]) for x in structures]}))
    raise SystemExit(0 if summary["valid_packets"]==18 and all(x["valid"] for x in structures if x["case"]!="GEO-004-malformed-input") else 1)

if __name__=="__main__": main()
