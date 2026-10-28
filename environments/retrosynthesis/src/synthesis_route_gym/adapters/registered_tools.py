"""Use Agent Scientist's registered tool dispatcher, preserving its auth and policy.

Inject model_tools.handle_function_call; this adapter never reads credentials or
constructs HTTP requests. A submitted/completed job is not a validated route.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Callable

from .common import canonical_smiles, response


@dataclass(frozen=True)
class RegisteredPlatformAdapter:
    dispatch: Callable[[str, dict], str | dict] | None = None

    def _invoke(self, name: str, arguments: dict, require_id: bool = True) -> dict:
        started = time.monotonic()
        if self.dispatch is None:
            return response("unavailable", "Agent Scientist registered tool dispatcher is not configured.")
        try:
            raw = self.dispatch(name, dict(arguments))
            value = json.loads(raw) if isinstance(raw, str) else raw
            if not isinstance(value, dict) or value.get("error") or value.get("success") is False:
                raise ValueError("Tool failed.")
            if str(value.get("status", "")).lower() in {"failed", "error", "cancelled"}:
                raise ValueError("Job failed.")
            if require_id and not isinstance(value.get("doc_id"), str):
                raise ValueError("Missing job receipt.")
            if not require_id and not isinstance(value.get("status"), str):
                raise ValueError("Missing job status.")
            job = {key: value.get(key, arguments.get(key))
                   for key in ("doc_id", "job_name", "status", "stage")
                   if key in value or key in arguments}
        except Exception:
            return response("error", "Registered platform tool failed or returned an invalid receipt.",
                            elapsed_seconds=time.monotonic() - started)
        return response("ok", "Job receipt only; predictions require a completed result artifact.",
                        job=job, complete=False, elapsed_seconds=time.monotonic() - started)

    def submit(self, target_smiles: str, experiment_name: str) -> dict:
        try:
            target = canonical_smiles(target_smiles)
            if not isinstance(experiment_name, str) or not 1 <= len(experiment_name) <= 120:
                raise ValueError("experiment_name must contain 1 to 120 characters.")
        except ValueError as error:
            return response("error", str(error))
        return self._invoke("boltzmann_submit", {
            "job_name": "retrosynthesis", "experiment_name": experiment_name,
            "experiment_data": {"target_mol": target, "outname": experiment_name},
        })

    def status(self, doc_id: str) -> dict:
        if not isinstance(doc_id, str) or not 1 <= len(doc_id) <= 256:
            return response("error", "A valid job doc_id is required.")
        return self._invoke("boltzmann_status", {"job_name": "retrosynthesis", "doc_id": doc_id},
                            require_id=False)
