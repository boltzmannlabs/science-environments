"""Install pinned LocalRetro assets from an existing local REBOLT copy.

This script neither downloads nor publishes third-party model artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

CHECKPOINT = "req_data/LocalRetro_boltz_USPTO_MIT.pth"
PINNED = {
    CHECKPOINT: "0147fa71b0d1801f0c9843ce54c8a25f631f8a62cdd900583c49710211fd442c",
    "req_data/USPTO_MIT/atom_templates.csv": "8bf08eab1b8e2a8d7acc7e0cfedfe7e2f30358e110f5d9a9ac87992c671039b8",
    "req_data/USPTO_MIT/bond_templates.csv": "e760a57365636a89f83ed9ad29ffbe15aa311dd2f6784eef14a7148ca8fd5125",
    "req_data/USPTO_MIT/template_infos.csv": "f2d6178f94ff8a097b2031f5d01edb74452ad2a69876778bc7cfe1c2cf5983ae",
}
CHECKPOINT_SHA256 = PINNED[CHECKPOINT]
REQUIRED_FILES = (*PINNED,
    "rebolt_update_opt/localretro/LocalRetro/default_config.json",
    "rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py",
    "rebolt_update_opt/localretro/LocalRetro/LICENSE")
RUNTIME_KEYS = frozenset(("SRG_PACKAGE_ROOT", "SRG_CHEMISTRY_PYTHON", "REBOLT_ROOT",
                          "REBOLT_PYTHON", "SRG_BACKEND_TIMEOUT_SECONDS"))


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def _safe_file(root: Path, name: str) -> Path:
    path = root / name
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError(f"LocalRetro source contains symlink: {name}")
    if not path.is_file():
        raise ValueError(f"LocalRetro source asset missing: {name}")
    return path


def _inventory(source_root: Path, expected_checkpoint: str | None = None,
               pinned: dict | None = None) -> tuple[dict, dict]:
    root = Path(source_root).expanduser()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("LocalRetro source cannot be a symlink")
    sources_dir = root / "rebolt_update_opt/localretro/LocalRetro"
    names = sorted(set(REQUIRED_FILES) | {p.relative_to(root).as_posix() for p in sources_dir.rglob("*.py")})
    sources = {name: _safe_file(root, name) for name in names}
    pinned = dict(PINNED if pinned is None else pinned)
    pinned[CHECKPOINT] = expected_checkpoint or pinned[CHECKPOINT]
    hashes = {name: _digest(path) for name, path in sources.items()}
    for name, expected in pinned.items():
        if hashes.get(name) != expected:
            raise ValueError(f"LocalRetro checkpoint digest or pinned template digest mismatch: {name}")
    report = {"schema_version": "srg-localretro-managed-v1",
              "checkpoint_sha256": hashes[CHECKPOINT], "files": hashes,
              "source": "operator-provided local REBOLT assets"}
    return sources, report


def install_assets(source_root: Path, destination: Path,
                   *, expected_checkpoint: str | None = None,
                   pinned: dict | None = None) -> dict:
    """Verify executable model inputs and atomically copy an allowlisted bundle."""
    dest = Path(destination).expanduser()
    if any(p.is_symlink() for p in (dest, *dest.parents)):
        raise ValueError("LocalRetro destination cannot be a symlink")
    sources, report = _inventory(source_root, expected_checkpoint, pinned)
    hashes = report["files"]
    if dest.exists():
        manifest = dest / "asset-manifest.json"
        if manifest.is_file() and json.loads(manifest.read_text()) == report and all(
                (dest / name).is_file() and _digest(dest / name) == digest
                for name, digest in hashes.items()):
            return report
        raise ValueError("Managed LocalRetro destination differs; move it before reinstalling")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".localretro-", dir=dest.parent))
    try:
        for name, source in sources.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target, follow_symlinks=False)
            if _digest(target) != hashes[name]:
                raise ValueError(f"LocalRetro source changed during copy: {name}")
        (stage / "asset-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
        if dest.exists():
            raise ValueError("Managed LocalRetro destination appeared during install")
        stage.rename(dest)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return report


def validate_model_python(value: Path) -> Path:
    python = Path(value).expanduser().resolve()
    if not python.is_file() or not os.access(python, os.X_OK):
        raise ValueError("A compatible LocalRetro runtime executable is required")
    probe = subprocess.run([str(python), "-c", "import torch,dgl,dgllife,rdkit,pandas,sklearn"],
                           capture_output=True, text=True, timeout=120, check=False)
    if probe.returncode:
        raise ValueError("A compatible LocalRetro runtime with torch, DGL, DGLLife, RDKit, pandas and sklearn is required")
    return python


def discover_source(explicit: Path | None = None) -> Path:
    if explicit is not None:
        path = Path(explicit).expanduser()
        if not (path / CHECKPOINT).is_file():
            raise ValueError("Invalid explicit LocalRetro source: required checkpoint missing")
        return path.resolve()
    candidates = [explicit, os.environ.get("REBOLT_ROOT")]
    candidates.extend(Path.home().glob("server3_data/*/*/REBOLT-FEATURES"))
    for candidate in candidates:
        if candidate and (Path(candidate).expanduser() / CHECKPOINT).is_file():
            return Path(candidate).expanduser().resolve()
    raise ValueError("LocalRetro assets unavailable; supply --existing-rebolt-root")


def discover_model_python(source: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        try:
            return validate_model_python(explicit)
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Invalid explicit LocalRetro runtime") from exc
    candidates = (explicit, os.environ.get("REBOLT_PYTHON"),
                  source.parent.parent / "anaconda3/envs/mol_gpu/bin/python", sys.executable)
    for candidate in candidates:
        if candidate:
            try:
                return validate_model_python(Path(candidate))
            except (ValueError, OSError, subprocess.TimeoutExpired):
                continue
    raise ValueError("No compatible model runtime found; supply --existing-rebolt-python")


def ensure_chemistry_python(package: Path, sci_home: Path, explicit: Path | None = None) -> Path:
    existing = explicit or os.environ.get("SRG_CHEMISTRY_PYTHON") or package / ".venv/bin/python"
    if Path(existing).is_file():
        python = Path(existing).expanduser().resolve()
        probe = subprocess.run([str(python), "-c", "import rdkit,pydantic,numpy,sklearn"],
                               capture_output=True, text=True, timeout=120, check=False)
        if probe.returncode:
            raise ValueError("Existing chemistry runtime lacks required dependencies")
        return python
    if explicit is not None or os.environ.get("SRG_CHEMISTRY_PYTHON"):
        raise ValueError("Configured chemistry runtime executable is missing")
    runtime = sci_home / "runtimes/retrosynthesis"
    if runtime.exists():
        python = runtime / "bin/python"
        if python.is_file():
            probe = subprocess.run([str(python), "-c", "import rdkit,pydantic,numpy,sklearn"],
                                   capture_output=True, text=True, timeout=120, check=False)
            if probe.returncode == 0:
                return python
        raise ValueError("Existing chemistry runtime incomplete; move it before reinstalling")
    runtime.parent.mkdir(parents=True, exist_ok=True)
    try:
        venv.EnvBuilder(with_pip=True).create(runtime)
        python = runtime / "bin/python"
        subprocess.run([str(python), "-m", "pip", "install", "--no-input",
                        str(package) + "[search]"], check=True, timeout=1800)
        probe = subprocess.run([str(python), "-c", "import rdkit,pydantic,numpy,sklearn"],
                               capture_output=True, text=True, timeout=120, check=False)
        if probe.returncode:
            raise ValueError("Installed chemistry runtime lacks required dependencies")
        return python
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        shutil.rmtree(runtime, ignore_errors=True)
        raise ValueError("Could not install the chemistry runtime") from None


def write_runtime_config(sci_home: Path, settings: dict) -> Path:
    if set(settings) != RUNTIME_KEYS or any(not isinstance(v, str) or not v for v in settings.values()):
        raise ValueError("Invalid retrosynthesis runtime settings")
    plugin = Path(sci_home) / "plugins/retrosynthesis"
    plugin.mkdir(parents=True, exist_ok=True)
    path = plugin / "runtime.json"
    fd, temp = tempfile.mkstemp(prefix=".runtime-", dir=plugin)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(settings, stream, indent=2)
            stream.write("\n")
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return path


def _enable_plugin(sci_executable: str, sci_home: Path) -> None:
    subprocess.run([sci_executable, "plugins", "enable", "retrosynthesis",
                    "--no-allow-tool-override"], check=True, timeout=1800,
                   env={**os.environ, "SCI_HOME": str(sci_home)})


def _legacy_enabled_without_yaml(data: str) -> bool:
    """Recognize simple profile plugin lists without confusing disabled entries."""
    in_plugins = in_enabled = False
    for raw in data.splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        value = line.strip()
        if indent == 0:
            in_plugins, in_enabled = value == "plugins:", False
        elif in_plugins and indent == 2:
            in_enabled = value.startswith("enabled:")
            if in_enabled and "synthesis-route-gym" in value.split(":", 1)[1]:
                return True
        elif in_plugins and in_enabled and indent > 2 and value.startswith("-"):
            if value[1:].strip().strip("\"'") == "synthesis-route-gym":
                return True
    return False


def check_legacy_plugin(sci_home: Path) -> None:
    config = Path(sci_home) / "config.yaml"
    if not config.is_file():
        return
    data = config.read_text()
    try:
        import yaml
        parsed = yaml.safe_load(data) or {}
        plugins = parsed.get("plugins", {}) if isinstance(parsed, dict) else {}
        enabled = plugins.get("enabled", []) if isinstance(plugins, dict) else []
        legacy_enabled = isinstance(enabled, list) and "synthesis-route-gym" in enabled
    except ImportError:
        legacy_enabled = _legacy_enabled_without_yaml(data)
    if legacy_enabled:
        raise ValueError("First run `sci plugins disable synthesis-route-gym` to avoid duplicate srg_action registration")


def install(*, package_root: Path, source_root: Path, model_python: Path,
            chemistry_python: Path, sci_home: Path, sci_executable: str) -> dict:
    package, home = Path(package_root).resolve(), Path(sci_home).expanduser().resolve()
    model = validate_model_python(model_python)
    chemistry = Path(chemistry_python).expanduser().resolve()
    if not chemistry.is_file() or not os.access(chemistry, os.X_OK):
        raise ValueError("Chemistry Python executable missing")
    plugin_source, skill_source = package / "integrations/agent_scientist", package / "skills/retrosynthesis"
    if not (plugin_source / "plugin.yaml").is_file() or not (skill_source / "SKILL.md").is_file():
        raise ValueError("Retrosynthesis plugin or skill missing")
    plugin, skill = home / "plugins/retrosynthesis", home / "skills/retrosynthesis"
    model_root = home / "models/retrosynthesis/localretro"
    check_legacy_plugin(home)
    if plugin.exists() or skill.exists():
        raise ValueError("Retrosynthesis is already installed in this profile")
    model_preexisting = model_root.exists()
    report = install_assets(source_root, model_root)
    try:
        plugin.parent.mkdir(parents=True, exist_ok=True)
        skill.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(plugin_source, plugin)
        shutil.copytree(skill_source, skill)
        write_runtime_config(home, {"SRG_PACKAGE_ROOT": str(package),
            "SRG_CHEMISTRY_PYTHON": str(chemistry), "REBOLT_ROOT": str(model_root),
            "REBOLT_PYTHON": str(model), "SRG_BACKEND_TIMEOUT_SECONDS": "300"})
        _enable_plugin(sci_executable, home)
    except BaseException:
        shutil.rmtree(plugin, ignore_errors=True)
        shutil.rmtree(skill, ignore_errors=True)
        if not model_preexisting:
            shutil.rmtree(model_root, ignore_errors=True)
        raise
    return {"installed": True, "profile": str(home), "checkpoint_sha256": report["checkpoint_sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install",))
    parser.add_argument("--sci-home", type=Path, default=Path(os.environ.get("SCI_HOME", Path.home() / ".sci")))
    parser.add_argument("--existing-rebolt-root", type=Path)
    parser.add_argument("--existing-rebolt-python", type=Path)
    parser.add_argument("--chemistry-python", type=Path)
    parser.add_argument("--sci-executable", default=shutil.which("sci") or "sci")
    args = parser.parse_args(argv)
    package = Path(__file__).resolve().parents[1]
    source = discover_source(args.existing_rebolt_root)
    check_legacy_plugin(args.sci_home)
    _inventory(source)
    model = discover_model_python(source, args.existing_rebolt_python)
    managed_runtime = args.sci_home / "runtimes/retrosynthesis"
    runtime_preexisting = managed_runtime.exists()
    chemistry = ensure_chemistry_python(package, args.sci_home, args.chemistry_python)
    try:
        report = install(package_root=package, source_root=source, model_python=model,
                         chemistry_python=chemistry, sci_home=args.sci_home,
                         sci_executable=args.sci_executable)
    except BaseException:
        if not runtime_preexisting:
            shutil.rmtree(managed_runtime, ignore_errors=True)
        raise
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
