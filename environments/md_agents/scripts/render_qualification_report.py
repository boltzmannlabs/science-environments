#!/usr/bin/env python3
"""Render a concise, auditable qualification table from harness evidence."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
data = json.loads((ROOT / "results/agent_harness.json").read_text())
lines = ["# MD Agent Qualification Report", "", f"Packets executed: **{data['agent_count']}**", "", "| Agent | Adapter | Qualification | Evidence |", "|---|---|---|---|"]
for r in data["results"]:
    adapter = r.get("adapter", {}).get("adapter_status", "LIVE")
    q = r.get("scientific_evaluation", {}).get("status", "UNAVAILABLE")
    reason = r.get("scientific_evaluation", {}).get("reason", "; ".join(r.get("evidence", [])))
    lines.append(f"| {r['agent_id']} — {r['agent_name']} | {adapter} | {q} | {reason.replace('|', '/') } |")
lines += ["", "## Interpretation", "", "Adapter PASS means the fixture was consumed by the selected software adapter. Qualification PASS is reserved for independently verifiable checks. REVIEW means the required trajectory, reference, sampling, recovery, or provenance evidence is not present; it is not a successful scientific result."]
(ROOT / "results/agent_qualification_report.md").write_text("\n".join(lines) + "\n")
print(ROOT / "results/agent_qualification_report.md")
