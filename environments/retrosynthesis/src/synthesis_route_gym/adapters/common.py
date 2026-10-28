"""Small, explicit adapter contracts; model scores are not feasibility evidence."""

from __future__ import annotations

import json
import math
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


# Arm Linux cleanup in the child interpreter, never in a threaded preexec_fn.
# The kernel kills this direct worker if its host dies, including while model
# imports are blocked. Current workers do not spawn scientific descendants;
# this is not a claim of recursive cleanup for arbitrary future backends.
WORKER_BOOTSTRAP = '''import os,sys,signal
if sys.platform.startswith("linux"):
    import ctypes
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(1,signal.SIGKILL,0,0,0) != 0:
        raise OSError(ctypes.get_errno(),"Cannot arm scientific worker cleanup")
    if os.getppid() != int(sys.argv[2]):
        os.kill(os.getpid(),signal.SIGKILL)
import runpy
runpy.run_path(sys.argv[1],run_name="__main__")
'''


def response(status: str, diagnostic: str = "", **extra: Any) -> dict:
    return {"status": status, "predictions": [], "elapsed_seconds": 0.0,
            "diagnostic": diagnostic, **extra}


def canonical_smiles(value: str) -> str:
    from rdkit import Chem, rdBase

    if not isinstance(value, str) or not value or len(value) > 10000:
        raise ValueError("A nonempty SMILES string of at most 10000 characters is required.")
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(value)
    if mol is None or mol.GetNumAtoms() == 0:
        raise ValueError("Invalid SMILES.")
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def validate_request(target: str, top_k: int) -> str:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 100:
        raise ValueError("top_k must be an integer between 1 and 100.")
    return canonical_smiles(target)


def normalise_prediction(value: dict, tool: str, version: str) -> dict:
    reactants = value.get("reactants")
    if not isinstance(reactants, list) or not reactants or len(reactants) > 100:
        raise ValueError("Expected a nonempty reactant list.")
    score = value.get("score")
    if score is not None:
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ValueError("Model score must be finite or null.")
        score = float(score)
    return {
        "reactants": [canonical_smiles(s) for s in reactants],
        "product": canonical_smiles(value.get("product")),
        "score": score,
        "source": {"tool": tool, "version": version},
        "evidence_status": "predicted",
    }


def normalise_result(value: dict, tool: str, top_k: int) -> dict:
    if value.get("status") != "ok":
        return value
    try:
        candidates = value.get("predictions", [])
        if not isinstance(candidates, list) or len(candidates) > 10000:
            raise ValueError("Invalid prediction collection.")
        predictions = [normalise_prediction(p, tool, str(value.get("version", "unknown")))
                       for p in candidates[:top_k]]
    except (ValueError, TypeError, AttributeError):
        return response("error", "Model returned an invalid prediction contract.",
                        elapsed_seconds=value.get("elapsed_seconds", 0.0))
    return {**value, "predictions": predictions}


def run_worker(python_executable: str | Path, payload: dict, timeout_seconds: float) -> dict:
    """Run one offline worker; timeout kills its process group, never uses a shell."""
    started = time.monotonic()
    if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 3600:
        return response("error", "timeout_seconds must be positive and at most 3600.")
    env = {key: value for key, value in os.environ.items() if key in {
        "PATH", "HOME", "LANG", "LC_ALL", "LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES",
    }}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    try:
        process = subprocess.Popen(
            [str(python_executable), "-c", WORKER_BOOTSTRAP,
             str(Path(__file__).with_name("_worker.py")), str(os.getpid())],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, env=env, start_new_session=True,
        )
        try:
            stdout, _ = process.communicate(json.dumps(payload), timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            return response("error", "Inference timed out.", elapsed_seconds=time.monotonic() - started)
    except (OSError, ValueError):
        return response("unavailable", "Configured Python worker could not start.",
                        elapsed_seconds=time.monotonic() - started)
    if process.returncode != 0 or len(stdout) > 8_000_000:
        return response("error", "Inference worker failed or exceeded the output limit.",
                        elapsed_seconds=time.monotonic() - started)
    try:
        result = json.loads(stdout)
        if not isinstance(result, dict) or result.get("status") not in {"ok", "error", "unavailable"}:
            raise ValueError("Invalid worker response.")
    except (ValueError, TypeError):
        return response("error", "Inference worker returned an invalid response.",
                        elapsed_seconds=time.monotonic() - started)
    return {**result, "elapsed_seconds": time.monotonic() - started}
