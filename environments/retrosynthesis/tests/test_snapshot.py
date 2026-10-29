"""Preservation, tampering, and command-line checks for local baseline bundles."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from synthesis_route_gym.snapshot import SnapshotInput, create_snapshot, verify_snapshot
from synthesis_route_gym import snapshot


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_input(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("the baseline\n")
    return source, SnapshotInput("package/source.txt", source, digest(source))


def test_snapshot_preserves_original_and_refuses_overwrite(tmp_path):
    source, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    anchor = create_snapshot([item], output, {"version": "test"})
    source.write_text("subsequent work")
    report = verify_snapshot(output, anchor)
    assert report["file_count"] == 1
    assert (output / "payload/package/source.txt").read_text() == "the baseline\n"
    assert (output / "payload/package/source.txt").stat().st_mode & 0o222 == 0
    with pytest.raises(FileExistsError):
        create_snapshot([item], output, {})
    assert verify_snapshot(output, anchor) == report


@pytest.mark.parametrize("damage", ["edit", "missing", "extra", "symlink", "manifest"])
def test_corruption_fails_verification(tmp_path, damage):
    source, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    anchor = create_snapshot([item], output, {})
    for path in [output, output / "payload", output / "payload/package"]:
        path.chmod(0o700)
    target = output / "payload/package/source.txt"
    if damage == "edit":
        target.chmod(0o600)
        target.write_text("corruption")
    elif damage == "missing":
        target.unlink()
    elif damage == "extra":
        (output / "payload/extra.txt").write_text("extra")
    elif damage == "symlink":
        target.unlink()
        target.symlink_to(source)
    else:
        manifest = output / "manifest.json"
        manifest.chmod(0o600)
        manifest.write_text("{}")
    with pytest.raises(ValueError):
        verify_snapshot(output, anchor)


@pytest.mark.parametrize("logical", ["../escape", "/absolute", "a/../b", "a\\b", "", "a//b", ".env", "main/auth.json"])
def test_unsafe_paths_rejected(tmp_path, logical):
    source, _ = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    with pytest.raises(ValueError):
        create_snapshot([SnapshotInput(logical, source)], output, {})
    assert not output.exists()


@pytest.mark.parametrize("kind", ["duplicate", "prefix", "symlink", "missing", "changed", "secret"])
def test_bad_inputs_leave_no_partial_bundle(tmp_path, kind):
    source, item = fixture_input(tmp_path)
    inputs = [item]
    if kind == "duplicate":
        inputs.append(item)
    elif kind == "prefix":
        inputs.append(SnapshotInput("package/source.txt/child", source))
    elif kind == "symlink":
        link = tmp_path / "link.txt"
        link.symlink_to(source)
        inputs = [SnapshotInput("link.txt", link)]
    elif kind == "missing":
        source.unlink()
    elif kind == "changed":
        source.write_text("changed since initial inventory")
    else:
        secret = tmp_path / "auth.json"
        secret.write_text("private")
        inputs = [SnapshotInput("renamed.txt", secret)]
    output = tmp_path / "baseline"
    with pytest.raises((ValueError, FileNotFoundError)):
        create_snapshot(inputs, output, {})
    assert not output.exists()


def test_manifest_cannot_escape_even_with_new_anchor(tmp_path):
    _, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    create_snapshot([item], output, {})
    manifest = output / "manifest.json"
    content = json.loads(manifest.read_text())
    content["files"][0]["path"] = "../source.txt"
    manifest.chmod(0o600)
    manifest.write_text(json.dumps(content))
    with pytest.raises(ValueError):
        verify_snapshot(output, digest(manifest))


def test_empty_snapshot_and_invalid_anchor_rejected(tmp_path):
    with pytest.raises(ValueError):
        create_snapshot([], tmp_path / "empty", {})
    _, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    create_snapshot([item], output, {})
    with pytest.raises(ValueError):
        verify_snapshot(output, "not-a-sha256")


def test_unlisted_root_file_rejected(tmp_path):
    _, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    anchor = create_snapshot([item], output, {})
    output.chmod(0o700)
    (output / "unlisted.py").write_text("unverified content")
    with pytest.raises(ValueError, match="root"):
        verify_snapshot(output, anchor)


def test_manifest_replacement_cannot_substitute_unanchored_records(tmp_path, monkeypatch):
    _, item = fixture_input(tmp_path)
    output = tmp_path / "baseline"
    anchor = create_snapshot([item], output, {})
    manifest = output / "manifest.json"
    original_hash = snapshot._sha256

    def replace_after_hash(path):
        result = original_hash(path)
        if path == manifest:
            content = json.loads(manifest.read_text())
            content["metadata"] = {"substituted": True}
            manifest.chmod(0o600)
            manifest.write_text(json.dumps(content))
        return result

    monkeypatch.setattr(snapshot, "_sha256", replace_after_hash)
    # A split hash/read implementation accepts a replacement after the hash.
    # Reading and authenticating one byte buffer avoids that second-read window.
    assert verify_snapshot(output, anchor)["verified"] is True
    assert digest(manifest) == anchor


def test_cli_create_verify_and_failure(tmp_path):
    source, item = fixture_input(tmp_path)
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"metadata": {"version": "test"}, "files": [
        {"path": item.path, "source": str(source), "sha256": item.sha256}
    ]}))
    command = [sys.executable, "-m", "synthesis_route_gym.snapshot"]
    output = tmp_path / "baseline"
    created = subprocess.run(command + ["create", "--spec", str(spec), "--output", str(output)], capture_output=True, text=True)
    assert created.returncode == 0, created.stderr
    anchor = json.loads(created.stdout)["manifest_sha256"]
    verified = subprocess.run(command + ["verify", "--snapshot", str(output), "--expected-sha256", anchor], capture_output=True, text=True)
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["file_count"] == 1
    failed = subprocess.run(command + ["verify", "--snapshot", str(output), "--expected-sha256", "0" * 64], capture_output=True, text=True)
    assert failed.returncode != 0
    assert "mismatch" in failed.stderr
