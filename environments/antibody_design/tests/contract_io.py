"""Strict local JSON and artifact integrity helpers shared by contract validators."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

def require(condition, message):
    if not condition:
        raise ValueError(message)

def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result

def read_json(path):
    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=_unique_keys,
                      parse_constant=invalid_constant)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _finite(value):
    if isinstance(value, float):
        require(math.isfinite(value), "Non-finite numeric value")
    elif isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)

def _artifact_entries(value):
    if isinstance(value, dict):
        if {"path", "sha256"} <= set(value):
            yield value
            return
        for child in value.values():
            yield from _artifact_entries(child)
    elif isinstance(value, list):
        for child in value:
            yield from _artifact_entries(child)

def artifact_path(artifact, root):
    root = Path(root).resolve()
    relative = Path(artifact["path"])
    require(not relative.is_absolute() and ".." not in relative.parts,
            "Artifact paths must stay beneath their declared root")
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "Artifact symlink escapes the declared root")
    require(path.is_file(), f"Missing artifact: {artifact['path']}")
    require(sha256(path) == artifact["sha256"], f"Artifact hash mismatch: {artifact['path']}")
    return path
