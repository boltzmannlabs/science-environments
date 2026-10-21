#!/usr/bin/env python3
"""One-shot Agent Scientist bridge for specialist artifact analysis."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in response")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("response is not an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-scientist-command", default="agent-sci")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()
    payload = json.loads(sys.stdin.read())
    instructions = (
        "You are participating in a blinded, controlled scientific benchmark. "
        "Analyze only the supplied public case. The evaluator reference is hidden. "
        "Return exactly one JSON object matching response_schema, without Markdown, "
        "extra keys, tool calls, or invented calculation results."
    )
    prompt = instructions + "\n\n" + json.dumps(payload, indent=2, sort_keys=True)
    with tempfile.TemporaryDirectory(prefix="spe-specialist-analysis-") as temp:
        usage_path = Path(temp) / "usage.json"
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
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise SystemExit(f"Agent Scientist failed ({completed.returncode}): {detail[:4000]}")
        response = parse_response(completed.stdout)
        if usage_path.is_file():
            response["agent_scientist_usage"] = json.loads(
                usage_path.read_text(encoding="utf-8")
            )
    print(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
