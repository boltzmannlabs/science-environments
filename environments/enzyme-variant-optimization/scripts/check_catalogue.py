#!/usr/bin/env python3
"""Read current catalogue/API descriptions; submit no model or scientific jobs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

from enzyme_research.paths import bundled_workflow_source
from enzyme_research.workflow import load_workflow

NEW_TOOLS = ("enzycontrol", "deepallo", "rfd3", "mol_probity", "catalytic_geometry")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue-root", type=Path, required=True)
    parser.add_argument("--agent-source", type=Path, required=True)
    parser.add_argument("--api-schema-url", default="https://boltproapis.boltzmann.co/openapi.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = (args.catalogue_root / "tool-contracts.v1.json").read_bytes()
    catalogue = json.loads(raw)
    _, _, registry, _ = load_workflow(bundled_workflow_source())
    resolved = registry.load_registry(catalog_root=args.catalogue_root)
    with urllib.request.urlopen(args.api_schema_url, timeout=30) as response:
        api_raw = response.read(16 * 1024**2 + 1)
    if len(api_raw) > 16 * 1024**2:
        raise ValueError("Oversized API schema")
    api = json.loads(api_raw)
    tools = {}
    for name in NEW_TOOLS:
        value = resolved[name]
        entry = catalogue["tools"][value["job_name"]]
        endpoint = entry.get("fastapi_endpoint")
        operation = api.get("paths", {}).get(endpoint, {}).get("post")
        api_required = None
        if operation:
            schema = operation["requestBody"]["content"]["application/json"]["schema"]
            if "$ref" in schema:
                schema = api["components"]["schemas"][schema["$ref"].rsplit("/", 1)[-1]]
            api_required = schema.get("required", [])
        tools[name] = {"job_name": value["job_name"], "collection_name": value.get("collection_name"),
                       "effective_status": value["backend_status"], "extra_activation_required": False,
                       "contract_sha256": value["contract_document"]["sha256"],
                       "required_experiment_fields": entry["request_schema"].get("required", []),
                       "fastapi_endpoint": endpoint, "fastapi_endpoint_published": bool(operation),
                       "fastapi_required_fields": api_required}
    report = {"schema_version": "enzyme-catalogue-check/1",
              "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "agent_scientist_revision": subprocess.check_output(["git", "-C", str(args.agent_source), "rev-parse", "HEAD"], text=True).strip(),
              "catalogue_sha256": hashlib.sha256(raw).hexdigest(),
              "api_schema_url": args.api_schema_url, "api_schema_sha256": hashlib.sha256(api_raw).hexdigest(),
              "registry_tools_resolved": len(resolved),
              "registry_tools_active": sum(v["backend_status"] == "active" for v in resolved.values()),
              "tools": tools, "scientific_jobs_submitted": 0, "model_requests": 0,
              "live_worker_execution_tested": False,
              "scope": "Dated catalogue and published API check; runtime availability continues to follow the current catalogue"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "active_tools": report["registry_tools_active"],
                      "resolved_tools": report["registry_tools_resolved"], "scientific_jobs_submitted": 0}))


if __name__ == "__main__":
    main()
