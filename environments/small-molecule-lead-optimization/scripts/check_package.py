"""Build/install a local wheel offline and exercise it outside the source tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New disposable check directory")
    args = parser.parse_args()
    output = args.output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        parser.error("Use a new output directory; existing outputs are not replaced")
    output.mkdir(parents=True)
    root = Path(__file__).resolve().parents[1]
    source = output / "source"
    source.mkdir()
    for name in ("pyproject.toml", "README.md"):
        shutil.copy2(root / name, source / name)
    shutil.copytree(root / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    wheels = output / "wheels"
    subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-deps",
                    "--no-build-isolation", "--wheel-dir", str(wheels), str(source)], check=True)
    wheel, = wheels.glob("*.whl")
    environment = output / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)], check=True)
    outside = output / "outside-source"
    outside.mkdir()
    probe = r'''
import importlib.metadata
from pathlib import Path
import leadopt_env
from leadopt_env.core import CampaignStore

ep, = importlib.metadata.entry_points().select(group="sci_agent.plugins", name="leadopt_env")
assert callable(ep.load())
skill = Path(leadopt_env.__file__).parent / "skills/lead-optimization/SKILL.md"
assert skill.is_file() and "warn and record" in skill.read_text()
store = CampaignStore("installed-fixture.sqlite")
store.dispatch("create", "installed-fixture", {"task": {"schema_version": 1, "id": "fixture", "version": "1"}})
report = store.dispatch("report", "installed-fixture", {})
assert report["coverage"]["complete"] is False
print("Installed entry point, skill and core campaign dispatch passed; zero model/scientific calls.")
'''
    subprocess.run([str(python), "-I", "-c", probe], cwd=outside, check=True)
    cli = environment / ("Scripts/leadopt-env.exe" if sys.platform == "win32" else "bin/leadopt-env")
    schema = subprocess.run([str(cli), "schema", "task"], cwd=outside, text=True,
                            capture_output=True, check=True)
    assert json.loads(schema.stdout)["properties"]["schema_version"]["const"] == 1
    report = {"package_installation": "passed", "wheel": wheel.name,
              "model_requests": 0, "scientific_submissions": 0,
              "native_host_loader": "tested separately"}
    (output / "package-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
