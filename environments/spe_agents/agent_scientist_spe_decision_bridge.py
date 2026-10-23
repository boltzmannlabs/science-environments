#!/usr/bin/env python3
"""JSON bridge from the SPE benchmark to Agent Scientist's tool-free one-shot LLM."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Agent Scientist returned no JSON object")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Agent Scientist response is not a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agent-scientist-command",
        default="agent-sci",
    )
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    stdin_payload = sys.stdin.read()
    encoded = stdin_payload or os.environ.get("BOLTZMANN_SPE_DECISION_PAYLOAD", "")
    if not encoded:
        raise SystemExit("decision payload is missing from stdin and environment fallback")
    payload = json.loads(encoded)
    if not isinstance(payload, dict):
        raise SystemExit("stdin must contain one JSON object")
    instructions = (
        "You are making one bounded scientific workflow decision for a controlled SPE benchmark. "
        "Use only the supplied diagnostic evidence and action space. Never request a reference answer, "
        "change the geometry, charge, multiplicity, method, or basis, or claim that a calculation ran. "
        "Return exactly one JSON object matching response_schema, without Markdown."
    )
    prompt = instructions + "\n\nDecision context:\n" + json.dumps(payload, indent=2, sort_keys=True)
    with tempfile.TemporaryDirectory(prefix="spe-agent-scientist-decision-") as temp:
        usage_path = Path(temp) / "usage.json"
        try:
            completed = subprocess.run(
                [
                    args.agent_scientist_command,
                    "-z",
                    prompt,
                    "--usage-file",
                    str(usage_path),
                    "--ignore-rules",
                ],
                text=True,
                capture_output=True,
                timeout=args.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SystemExit(f"Agent Scientist invocation failed: {exc}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise SystemExit(
                f"Agent Scientist exited {completed.returncode}: {detail[:4000]}"
            )
        decision = _parse_json_response(completed.stdout)
        if usage_path.is_file():
            try:
                decision["agent_scientist_usage"] = json.loads(
                    usage_path.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                decision["agent_scientist_usage"] = {"status": "unreadable"}
    print(json.dumps(decision, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
