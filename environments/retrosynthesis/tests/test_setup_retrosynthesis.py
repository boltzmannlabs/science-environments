"""Installer contracts for local, pinned LocalRetro provisioning."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts/setup_retrosynthesis.py"
spec = importlib.util.spec_from_file_location("setup_retrosynthesis", SCRIPT)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def _source(tmp_path, checkpoint=b"fixture"):
    root = tmp_path / "rebolt"
    for name in setup.REQUIRED_FILES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(checkpoint if name == setup.CHECKPOINT else b"source")
    return root


def test_install_assets_rejects_wrong_checkpoint_before_creating_destination(tmp_path):
    source = _source(tmp_path)
    with pytest.raises(ValueError, match="checkpoint digest"):
        setup.install_assets(source, tmp_path / "profile" / "models", expected_checkpoint="0" * 64)
    assert not (tmp_path / "profile" / "models").exists()


def test_install_assets_copies_required_files_and_records_digest(tmp_path):
    source = _source(tmp_path)
    digest = hashlib.sha256(b"fixture").hexdigest()
    dest = tmp_path / "profile" / "models"
    pinned = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in setup.PINNED}
    report = setup.install_assets(source, dest, expected_checkpoint=digest, pinned=pinned)
    assert report["checkpoint_sha256"] == digest
    assert all((dest / name).read_bytes() == (source / name).read_bytes() for name in setup.REQUIRED_FILES)
    assert json.loads((dest / "asset-manifest.json").read_text())["checkpoint_sha256"] == digest


def test_install_assets_rejects_symlink_source(tmp_path):
    source = _source(tmp_path)
    path = source / setup.CHECKPOINT
    path.unlink()
    path.symlink_to(tmp_path / "elsewhere")
    with pytest.raises(ValueError, match="symlink"):
        setup.install_assets(source, tmp_path / "models", expected_checkpoint="0" * 64)


def test_runtime_config_is_private_and_atomic(tmp_path):
    home = tmp_path / "sci"
    p = setup.write_runtime_config(home, {
        "SRG_PACKAGE_ROOT": str(tmp_path / "package"),
        "SRG_CHEMISTRY_PYTHON": str(tmp_path / "chemistry-python"),
        "REBOLT_ROOT": str(tmp_path / "model"),
        "REBOLT_PYTHON": str(tmp_path / "model-python"),
        "SRG_BACKEND_TIMEOUT_SECONDS": "300",
    })
    assert p == home / "plugins/retrosynthesis/runtime.json"
    assert p.stat().st_mode & 0o777 == 0o600
    assert json.loads(p.read_text())["SRG_BACKEND_TIMEOUT_SECONDS"] == "300"


def test_python_dependency_probe_reports_missing_modules(tmp_path, monkeypatch):
    executable = tmp_path / "python"
    executable.write_text("x")
    executable.chmod(0o700)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kw: SimpleNamespace(returncode=1, stderr="No module named dgl"))
    with pytest.raises(ValueError, match="compatible LocalRetro runtime"):
        setup.validate_model_python(executable)


def test_setup_failure_does_not_enable_plugin_or_leave_partial_install(tmp_path, monkeypatch):
    source = _source(tmp_path)
    sci_home = tmp_path / "sci"
    digest = hashlib.sha256(b"fixture").hexdigest()
    monkeypatch.setattr(setup, "validate_model_python", lambda p: Path(p))
    monkeypatch.setattr(setup, "PINNED", {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                      for name in setup.PINNED})
    monkeypatch.setattr(setup, "_enable_plugin", lambda *args: (_ for _ in ()).throw(RuntimeError("enable failed")))
    package = Path(__file__).parents[1]
    model_python = tmp_path / "python"
    model_python.write_text("x")
    model_python.chmod(0o700)
    with pytest.raises(RuntimeError, match="enable failed"):
        setup.install(package_root=package, source_root=source, model_python=model_python,
                      chemistry_python=model_python, sci_home=sci_home, sci_executable="sci")
    assert not (sci_home / "plugins/retrosynthesis").exists()
    assert not (sci_home / "models/retrosynthesis/localretro").exists()


def test_failed_enable_preserves_preexisting_verified_model(tmp_path, monkeypatch):
    source = _source(tmp_path)
    home = tmp_path / "sci"
    monkeypatch.setattr(setup, "PINNED", {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                      for name in setup.PINNED})
    managed = home / "models/retrosynthesis/localretro"
    setup.install_assets(source, managed)
    monkeypatch.setattr(setup, "validate_model_python", lambda p: Path(p))
    monkeypatch.setattr(setup, "_enable_plugin", lambda *args: (_ for _ in ()).throw(RuntimeError("enable failed")))
    python = tmp_path / "python"
    python.write_text("x")
    python.chmod(0o700)
    with pytest.raises(RuntimeError, match="enable failed"):
        setup.install(package_root=Path(__file__).parents[1], source_root=source,
                      model_python=python, chemistry_python=python, sci_home=home,
                      sci_executable="sci")
    assert (managed / setup.CHECKPOINT).is_file()


def test_existing_chemistry_python_requires_chemistry_dependencies(tmp_path, monkeypatch):
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text("x")
    python.chmod(0o700)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kw: SimpleNamespace(returncode=1, stderr="missing rdkit"))
    with pytest.raises(ValueError, match="chemistry runtime"):
        setup.ensure_chemistry_python(tmp_path, tmp_path / "sci", python)


def test_main_rejects_bad_model_before_provisioning_chemistry(tmp_path, monkeypatch):
    source = _source(tmp_path)
    home = tmp_path / "sci"
    monkeypatch.setattr(setup, "ensure_chemistry_python", lambda *args: (_ for _ in ()).throw(AssertionError("runtime was created")))
    monkeypatch.setattr(setup, "discover_model_python", lambda *args: tmp_path / "model-python")
    with pytest.raises(ValueError, match="checkpoint digest"):
        setup.main(["install", "--sci-home", str(home), "--existing-rebolt-root", str(source)])
    assert not (home / "runtimes/retrosynthesis").exists()


def test_complete_existing_managed_runtime_is_reusable(tmp_path, monkeypatch):
    python = tmp_path / "sci/runtimes/retrosynthesis/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text("x")
    python.chmod(0o700)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kw: SimpleNamespace(returncode=0, stderr=""))
    assert setup.ensure_chemistry_python(tmp_path, tmp_path / "sci") == python


def test_explicit_invalid_source_does_not_fall_back(tmp_path, monkeypatch):
    source = _source(tmp_path)
    monkeypatch.setenv("REBOLT_ROOT", str(source))
    with pytest.raises(ValueError, match="explicit LocalRetro source"):
        setup.discover_source(tmp_path / "missing")


def test_explicit_invalid_model_python_does_not_fall_back(tmp_path, monkeypatch):
    source = _source(tmp_path)
    monkeypatch.setenv("REBOLT_PYTHON", sys.executable)
    with pytest.raises(ValueError, match="explicit LocalRetro runtime"):
        setup.discover_model_python(source, tmp_path / "missing-python")


def test_enabled_legacy_plugin_blocks_duplicate_registration(tmp_path):
    home = tmp_path / "sci"
    home.mkdir()
    (home / "config.yaml").write_text("plugins:\n  enabled: [synthesis-route-gym]\n")
    with pytest.raises(ValueError, match="disable synthesis-route-gym"):
        setup.check_legacy_plugin(home)


def test_install_enables_private_profile_with_managed_asset_paths(tmp_path, monkeypatch):
    source = _source(tmp_path)
    home = tmp_path / "sci"
    python = tmp_path / "python"
    python.write_text("x")
    python.chmod(0o700)
    monkeypatch.setattr(setup, "PINNED", {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                      for name in setup.PINNED})
    monkeypatch.setattr(setup, "validate_model_python", lambda p: Path(p))
    enabled = []
    monkeypatch.setattr(setup, "_enable_plugin", lambda executable, profile: enabled.append((executable, profile)))
    report = setup.install(package_root=Path(__file__).parents[1], source_root=source,
                           model_python=python, chemistry_python=python,
                           sci_home=home, sci_executable="sci")
    settings = json.loads((home / "plugins/retrosynthesis/runtime.json").read_text())
    assert report["installed"] and enabled == [("sci", home)]
    assert settings["REBOLT_ROOT"] == str(home / "models/retrosynthesis/localretro")
    assert (home / "skills/retrosynthesis/SKILL.md").is_file()


def test_chemistry_runtime_created_when_no_compatible_existing_python(tmp_path, monkeypatch):
    root = tmp_path / "package"
    root.mkdir()
    home = tmp_path / "sci"
    monkeypatch.delenv("SRG_CHEMISTRY_PYTHON", raising=False)
    def create(_self, location):
        python = Path(location) / "bin/python"
        python.parent.mkdir(parents=True)
        python.write_text("x")
    monkeypatch.setattr(setup.venv.EnvBuilder, "create", create)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kw: SimpleNamespace(returncode=0, stderr=""))
    assert setup.ensure_chemistry_python(root, home) == home / "runtimes/retrosynthesis/bin/python"


def test_chemistry_install_failure_cleans_new_runtime(tmp_path, monkeypatch):
    root = tmp_path / "package"
    root.mkdir()
    home = tmp_path / "sci"
    monkeypatch.delenv("SRG_CHEMISTRY_PYTHON", raising=False)
    def create(_self, location):
        Path(location).mkdir(parents=True)
    monkeypatch.setattr(setup.venv.EnvBuilder, "create", create)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kw: (_ for _ in ()).throw(setup.subprocess.CalledProcessError(1, "pip")))
    with pytest.raises(ValueError, match="Could not install"):
        setup.ensure_chemistry_python(root, home)
    assert not (home / "runtimes/retrosynthesis").exists()


def test_disabled_legacy_plugin_does_not_block_setup(tmp_path):
    home = tmp_path / "sci"
    home.mkdir()
    data = "plugins:\n  enabled: [other]\n  disabled: [synthesis-route-gym]\n"
    (home / "config.yaml").write_text(data)
    setup.check_legacy_plugin(home)
    assert not setup._legacy_enabled_without_yaml(data)


def test_main_removes_new_chemistry_runtime_when_enable_fails(tmp_path, monkeypatch):
    source = _source(tmp_path)
    home = tmp_path / "sci"
    monkeypatch.setattr(setup, "PINNED", {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                      for name in setup.PINNED})
    monkeypatch.setattr(setup, "discover_model_python", lambda *args: tmp_path / "model-python")
    def ensure(_package, profile, _explicit):
        runtime = profile / "runtimes/retrosynthesis"
        runtime.mkdir(parents=True)
        return runtime / "bin/python"
    monkeypatch.setattr(setup, "ensure_chemistry_python", ensure)
    monkeypatch.setattr(setup, "install", lambda **kw: (_ for _ in ()).throw(RuntimeError("enable failed")))
    with pytest.raises(RuntimeError, match="enable failed"):
        setup.main(["install", "--sci-home", str(home), "--existing-rebolt-root", str(source)])
    assert not (home / "runtimes/retrosynthesis").exists()


def test_existing_verified_assets_are_reused_but_tampering_is_rejected(tmp_path):
    source = _source(tmp_path)
    pinned = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in setup.PINNED}
    target = tmp_path / "managed"
    first = setup.install_assets(source, target, pinned=pinned)
    assert setup.install_assets(source, target, pinned=pinned) == first
    (target / "req_data/USPTO_MIT/template_infos.csv").write_text("changed")
    with pytest.raises(ValueError, match="destination differs"):
        setup.install_assets(source, target, pinned=pinned)


def test_source_discovery_honors_configured_root(tmp_path, monkeypatch):
    source = _source(tmp_path)
    monkeypatch.setenv("REBOLT_ROOT", str(source))
    assert setup.discover_source() == source


def test_runtime_discovery_uses_first_compatible_candidate(tmp_path, monkeypatch):
    source = _source(tmp_path)
    compatible = tmp_path / "model-python"
    monkeypatch.setenv("REBOLT_PYTHON", str(compatible))
    monkeypatch.setattr(setup, "validate_model_python", lambda path: Path(path))
    assert setup.discover_model_python(source) == compatible


def test_fallback_parser_reads_only_enabled_block():
    assert setup._legacy_enabled_without_yaml(
        "plugins:\n  disabled: [other]\n  enabled:\n    - synthesis-route-gym\n")
    assert not setup._legacy_enabled_without_yaml(
        "plugins:\n  enabled: [other]\n  disabled:\n    - synthesis-route-gym\n")
