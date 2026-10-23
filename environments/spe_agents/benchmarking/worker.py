"""Isolated local-Boltzmann attempt worker used to enforce wall-clock timeouts."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Mapping

from spe_agents.adapters import AdapterExecutionError, Atom, SPERequest
from spe_agents.local_module_adapter import LocalBoltzmannSPEAdapter


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--module-root", type=Path, default=None)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        payload = json.loads(args.request.read_text(encoding="utf-8"))
        request = SPERequest(
            task_id=str(payload["task_id"]),
            atoms=tuple(Atom(**item) for item in payload["atoms"]),
            coordinate_unit=str(payload["coordinate_unit"]),
            charge=int(payload["charge"]),
            multiplicity=int(payload["multiplicity"]),
            method=str(payload["method"]),
            basis=str(payload["basis"]),
            requested_properties=tuple(payload["requested_properties"]),
            settings=dict(payload.get("settings", {})),
        )
        kwargs: dict[str, Any] = {"artifact_root": args.artifact_root}
        if args.module_root is not None:
            kwargs["module_root"] = args.module_root
        adapter = LocalBoltzmannSPEAdapter(**kwargs)
        job_id = adapter.submit(request)
        try:
            result = adapter.result(job_id)
            energy = result.outputs["total_energy"]
            response = {
                "status": "completed",
                "job_id": job_id,
                "wall_seconds": time.perf_counter() - started,
                "engine_seconds": result.outputs.get("engine_wall_time_seconds"),
                "energy_hartree": energy["value"],
                "converged": result.converged,
                "artifacts": [
                    {
                        "name": artifact.name,
                        "uri": artifact.uri,
                        "sha256": artifact.sha256,
                        "media_type": artifact.media_type,
                    }
                    for artifact in result.artifacts
                ],
                "engine_name": result.engine_name,
                "engine_version": result.engine_version,
                "outputs": _plain(result.outputs),
                "warnings": list(result.warnings),
            }
        except AdapterExecutionError as exc:
            response = {
                "status": "failed",
                "job_id": job_id,
                "wall_seconds": time.perf_counter() - started,
                "failure_class": exc.failure.failure_class.value,
                "failure_message": exc.failure.message,
                "retryable": exc.failure.retryable,
            }
    except Exception as exc:
        response = {
            "status": "failed",
            "wall_seconds": time.perf_counter() - started,
            "failure_class": "worker_error",
            "failure_message": str(exc),
            "retryable": False,
        }
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(response, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if response["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
