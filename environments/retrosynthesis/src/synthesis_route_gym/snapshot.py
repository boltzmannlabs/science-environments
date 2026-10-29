"""Explicit, write-once local snapshots; verify against an externally pinned hash.

Read-only permissions prevent accidental edits, not changes by the file owner.
This utility never loads model objects or copies directories recursively.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
from typing import Any, Iterable

FORMAT = "srg-baseline-v1"
SECRET_NAMES = frozenset({"auth.json", "credentials.json", "id_rsa", "id_ed25519"})


@dataclass(frozen=True)
class SnapshotInput:
    path: str
    source: Path
    sha256: str | None = None


def _safe_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Invalid snapshot path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in {"", ".", ".."} for p in value.split("/")):
        raise ValueError("Snapshot paths must be normalized relative paths")
    if any(p.lower() in SECRET_NAMES or p.lower().startswith(".env") for p in path.parts):
        raise ValueError("Credential paths cannot enter a baseline")
    return path


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        return digest.hexdigest()


def _check_hash(value: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("Expected a lowercase SHA-256 hash")


def _unique_paths(paths: Iterable[str]) -> None:
    seen: set[PurePosixPath] = set()
    for value in paths:
        path = _safe_path(value)
        if path in seen:
            raise ValueError("Duplicate snapshot path")
        seen.add(path)
    if any(parent in seen for path in seen for parent in path.parents):
        raise ValueError("Snapshot file/directory path conflict")


def _validate_inputs(inputs: tuple[SnapshotInput, ...], output: Path) -> None:
    if not inputs:
        raise ValueError("Cannot create an empty baseline")
    _unique_paths(item.path for item in inputs)
    for item in inputs:
        _safe_path(item.source.name)
        if item.sha256 is not None:
            _check_hash(item.sha256)
        if not stat.S_ISREG(item.source.lstat().st_mode):
            raise ValueError("Snapshot sources must be regular files, not symlinks")
        if output.resolve() in item.source.resolve().parents:
            raise ValueError("Snapshot source cannot be inside its output")


def _copy_item(item: SnapshotInput, output: Path) -> dict[str, Any]:
    target = output / "payload" / item.path
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Copy bytes only: do not carry source permissions or executable flags.
    with item.source.open("rb") as source, target.open("xb") as destination:
        shutil.copyfileobj(source, destination, length=1024 * 1024)
    actual = _sha256(target)
    expected = item.sha256 or _sha256(item.source)
    if actual != expected:
        raise ValueError(f"Source changed or checksum mismatch: {item.path}")
    return {"path": item.path, "sha256": actual, "bytes": target.stat().st_size}


def _make_read_only(output: Path) -> None:
    paths = sorted(output.rglob("*"), key=lambda p: len(p.parts), reverse=True)
    for path in paths:
        path.chmod(0o500 if path.is_dir() else 0o400)
    output.chmod(0o500)


def _remove_partial(output: Path) -> None:
    output.chmod(0o700)
    for path in output.rglob("*"):
        if path.is_dir():
            path.chmod(0o700)
    shutil.rmtree(output)


def create_snapshot(
    inputs: Iterable[SnapshotInput], output: Path, metadata: dict[str, Any],
) -> str:
    """Create a new exclusive bundle and return its manifest SHA-256 anchor.

    The caller must supply an explicit, reviewed non-secret file list and metadata.
    Filename screening is a guardrail, not a general secret-content detector.
    """
    items = tuple(inputs)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Baseline already exists: {output}")
    _validate_inputs(items, output)
    json.dumps(metadata, allow_nan=False)  # Fail before creating output.
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        records = [_copy_item(item, output) for item in sorted(items, key=lambda i: i.path)]
        manifest = {
            "format": FORMAT,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata,
            "files": records,
        }
        manifest_path = output / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n")
        anchor = _sha256(manifest_path)
        verify_snapshot(output, anchor)
        _make_read_only(output)
        return anchor
    except BaseException:
        _remove_partial(output)
        raise


def _validated_records(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict) or manifest.get("format") != FORMAT:
        raise ValueError("Unsupported baseline manifest")
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise ValueError("Invalid baseline file records")
    for record in records:
        if not isinstance(record, dict) or set(record) != {"path", "sha256", "bytes"}:
            raise ValueError("Invalid baseline file record")
        _check_hash(record["sha256"])
        if type(record["bytes"]) is not int or record["bytes"] < 0:
            raise ValueError("Invalid baseline file size")
    _unique_paths(record["path"] for record in records)
    return records


def verify_snapshot(output: Path, expected_sha256: str) -> dict[str, Any]:
    """Check all bytes and paths against an anchor held outside the bundle."""
    _check_hash(expected_sha256)
    manifest_path = output / "manifest.json"
    if output.is_symlink() or manifest_path.is_symlink():
        raise ValueError("Baseline root and manifest cannot be symlinks")
    if not output.is_dir() or {p.name for p in output.iterdir()} != {"manifest.json", "payload"}:
        raise ValueError("Baseline root has missing or unexpected entries")
    if not manifest_path.is_file():
        raise ValueError("Baseline manifest missing")
    manifest_bytes = manifest_path.read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_sha256:
        raise ValueError("Baseline manifest checksum mismatch or missing manifest")
    records = _validated_records(json.loads(manifest_bytes))
    payload = output / "payload"
    if not payload.is_dir() or payload.is_symlink():
        raise ValueError("Baseline payload directory is invalid")
    observed: set[str] = set()
    for path in payload.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError("Baseline contains a symlink or special file")
        if path.is_file():
            observed.add(path.relative_to(payload).as_posix())
    if observed != {record["path"] for record in records}:
        raise ValueError("Baseline payload has missing or unexpected files")
    for record in records:
        target = payload / record["path"]
        if target.stat().st_size != record["bytes"] or _sha256(target) != record["sha256"]:
            raise ValueError(f"Baseline file checksum mismatch: {record['path']}")
    return {"manifest_sha256": expected_sha256, "file_count": len(records),
            "total_bytes": sum(record["bytes"] for record in records), "verified": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--spec", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--snapshot", type=Path, required=True)
    verify.add_argument("--expected-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            spec = json.loads(args.spec.read_text())
            inputs = [SnapshotInput(row["path"], Path(row["source"]), row.get("sha256")) for row in spec["files"]]
            anchor = create_snapshot(inputs, args.output, spec.get("metadata", {}))
            result = {"manifest_sha256": anchor, "snapshot": str(args.output)}
        else:
            result = verify_snapshot(args.snapshot, args.expected_sha256)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Snapshot failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
