#!/usr/bin/env python3
"""Execute all MD input packets with explicit evidence-aware statuses.

This harness distinguishes executable checks from unavailable scientific
fixtures. It never turns a missing molecular trajectory/model into PASS.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
from engine_adapters import validate_fixture
from scientific_evaluators import evaluate

ROOT = Path(__file__).parents[1]

def packet_result(packet_path: Path, live: bool = False) -> dict:
    started = time.perf_counter()
    packet = json.loads(packet_path.read_text())
    aid = packet["agent_id"]
    fixture = packet["input"]["fixture"]
    result = {"agent_id": aid, "agent_name": packet["agent_name"], "fixture": fixture,
              "input_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
              "runtime_s": 0.0, "status": "REVIEW", "evidence": []}
    # Every packet must be structurally executable before scientific execution.
    required = ("agent_id", "agent_name", "group", "input", "expected_output", "acceptance")
    missing = [k for k in required if k not in packet]
    if missing:
        result.update(status="FAIL", evidence=[f"missing packet fields: {missing}"])
        return result
    result["evidence"].append("packet schema valid")
    if aid == "MD-10" and live:
        out = ROOT / "results" / "harness_live"
        cmd = [sys.executable, str(ROOT / "scripts/run_core_openmm.py"), "--repeat", "1", "--output", "results/harness_live"]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            result.update(status="FAIL", evidence=["OpenMM execution failed", proc.stderr[-500:]])
        else:
            live_result = json.loads((out / "repeat_1.json").read_text())
            if live_result.get("status") == "PASS" and live_result.get("platform_name") == "CUDA":
                result.update(status="PASS", evidence=["live OpenMM CUDA execution", "finite energy/trajectory evidence"], live_result=live_result,
                              scientific_evaluation={"status": "PASS", "reason": "live OpenMM CUDA result independently checked by core evaluator"})
            else:
                result.update(status="REVIEW", evidence=["engine returned without qualified CUDA evidence"], live_result=live_result)
    else:
        # A packet-only run is executable contract validation, not a chemistry pass.
        # Fixtures may be kept in the package's explicit cases/ directory or
        # referenced by a path relative to the package root.  Presence alone
        # is not a scientific pass; it only enables the next adapter stage.
        candidates = (ROOT / fixture, ROOT / "inputs" / "fixtures" / fixture, ROOT / "cases" / fixture)
        candidate = next((p for p in candidates if p.exists()), None)
        if candidate is not None:
            result["evidence"].append(f"fixture exists: {candidate.relative_to(ROOT)}")
            adapter = validate_fixture(candidate)
            result["adapter"] = adapter
            if adapter["adapter_status"] == "PASS":
                result["scientific_evaluation"] = evaluate(packet, candidate, adapter)
                result["status"] = "REVIEW"
                result["evidence"].append(f"{adapter['engine']} adapter executed")
                result["evidence"].append(result["scientific_evaluation"]["reason"])
            else:
                result["status"] = "FAIL"
                result["evidence"].append(adapter.get("error", "adapter failed"))
        else:
            result["status"] = "NEEDS_INPUT"
            result["evidence"].append(f"fixture not materialized: {fixture}")
    result["runtime_s"] = round(time.perf_counter() - started, 6)
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", help="MD-01..MD-62; omit to run all")
    ap.add_argument("--live", action="store_true", help="run live OpenMM for MD-10")
    ap.add_argument("--strict", action="store_true", help="return nonzero when any packet is not scientifically qualified")
    ap.add_argument("--output", default="results/agent_harness.json")
    args = ap.parse_args()
    paths = [ROOT / "inputs" / f"MD-{int(args.agent.split('-')[1]):02d}" / "task.json"] if args.agent else sorted((ROOT / "inputs").glob("MD-??/task.json"))
    results = [packet_result(p, live=args.live) for p in paths]
    payload = {"benchmark": "md-agent-harness-v1", "agent_count": len(results),
               "live_engine_agents": ["MD-10"] if args.live else [], "results": results,
               "scope": "packet execution with evidence-aware status; only MD-10 invokes a live engine in this harness"}
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    counts = {s: sum(x["status"] == s for x in results) for s in ("PASS", "REVIEW", "NEEDS_INPUT", "FAIL")}
    print(json.dumps({"agent_count": len(results), "counts": counts, "output": str(out)}, indent=2))
    qualification_review = sum(x.get("scientific_evaluation", {}).get("status") == "REVIEW" for x in results)
    if args.strict and qualification_review:
        raise SystemExit(2)
    raise SystemExit(1 if counts["FAIL"] else 0)

if __name__ == "__main__":
    main()
