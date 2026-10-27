"""Portable serialization and artifact identity; no runtime credentials."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


class WorkflowError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".export-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def identifier(value, name="identifier"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise WorkflowError(f"{name} must contain 1–128 letters, digits, underscores, dots or hyphens")
    return value


def validate_data(value):
    """Prevent credential material from entering durable workflow artifacts."""
    secret_keys = {"tokenid", "token", "api_key", "apikey", "password", "authorization",
                   "download_url", "download_link", "access_token", "secret"}
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key.lower() in secret_keys:
                raise WorkflowError("Workflow data must not contain credentials or signed URLs")
            validate_data(item)
    elif isinstance(value, list):
        for item in value:
            validate_data(item)
    elif isinstance(value, str):
        if re.search(r"(?i)(x-goog-signature=|x-amz-signature=|[?&](token|signature|sig)=|bearer\s+|eyJ[\w-]+\.[\w-]+\.)", value):
            raise WorkflowError("Workflow data must not contain credentials or signed URLs")
    elif isinstance(value, float) and not math.isfinite(value):
        raise WorkflowError("Workflow numbers must be finite")
    elif value is not None and not isinstance(value, (int, float, bool)):
        raise WorkflowError("Workflow data must be JSON serializable")


def scoped_root():
    from sci_constants import get_sci_home
    return get_sci_home() / "enzyme-workflows"
