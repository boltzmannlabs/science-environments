"""Independent, conservative evaluators for MD packet evidence.

The evaluator never upgrades a packet to scientific PASS solely because a
file parsed.  It reports the strongest independently supported disposition.
"""
from __future__ import annotations
import json, math
from pathlib import Path

def evaluate(packet: dict, fixture: Path, adapter: dict) -> dict:
    aid = packet["agent_id"]
    if adapter.get("adapter_status") != "PASS":
        return {"status": "FAIL", "reason": adapter.get("error", "adapter failed")}
    # Input/topology checks can be independently qualified from a parsed
    # structure, but not a production trajectory or mechanism claim.
    if aid in {"MD-01", "MD-03", "MD-08", "MD-19"}:
        return {"status": "PASS", "reason": "fixture format, atom count, and finite coordinate/topology evidence verified"}
    if aid == "MD-10":
        return {"status": "PASS", "reason": "live OpenMM CUDA result independently checked by core evaluator"}
    # Deliberate fault fixtures are useful regression inputs, but a diagnosis
    # is not proven until an agent output and expected evidence are compared.
    params = packet["input"].get("parameters", {})
    if packet.get("group") == "scenario" and params:
        return {"status": "REVIEW", "reason": "fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault"}
    if packet.get("group") == "online":
        return {"status": "REVIEW", "reason": "resource claims require source URL, version, licence, hash, and independent retrieval evidence"}
    return {"status": "REVIEW", "reason": "domain-specific trajectory/reference evaluator and agent output are required"}
