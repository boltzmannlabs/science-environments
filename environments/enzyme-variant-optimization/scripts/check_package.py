#!/usr/bin/env python3
"""Build and exercise a fresh installed wheel without accounts, GPUs or services."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=ROOT / ".runtime" / "DiscoveryRSI")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
           "PIP_CONFIG_FILE": "/dev/null", "PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1", "CUDA_VISIBLE_DEVICES": "",
           "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2"}

    def command(values):
        result = subprocess.run(values, cwd=output, env=env, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError("Package verification failed: " + result.stderr[-2500:])
        return result.stdout

    command([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-deps", "--no-build-isolation",
             "--wheel-dir", str(output / "wheels"), str(ROOT)])
    wheels = list((output / "wheels").glob("boltzmann_enzyme_research-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("Expected exactly one wheel")
    wheel = wheels[0]
    required = {"enzyme_research/plugin.yaml", "enzyme_research/skills/enzyme-research/SKILL.md",
                "enzyme_research/_support/enzyme_workflow/contracts/tool_registry.json",
                "enzyme_research/_support/enzyme_workflow/examples/offline_replay.py"}
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if not required <= names:
            raise RuntimeError("Installed resources are missing")
        forbidden = {"runs", "runtime", ".runs", ".runtime", "evaluator_private", ".sci", ".git"}
        if any(set(Path(name).parts) & forbidden for name in names):
            raise RuntimeError("Wheel contains execution or private material")
        if any(name.startswith("enzyme_workflow/") for name in names):
            raise RuntimeError("Support snapshot must not install a second top-level workflow plugin")
        for notice in ("THIRD_PARTY_NOTICES.md", "SOURCE_PROVENANCE.json"):
            if not any(name.endswith("/share/enzyme-variant-optimization/" + notice) for name in names):
                raise RuntimeError("Source provenance/notice is missing from wheel")
    command([sys.executable, "-m", "venv", str(output / "venv")])
    python = str(output / "venv" / "bin" / "python")
    command([python, "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)])
    installation = json.loads(command([python, "-I", "-B", "-c",
        "import importlib.metadata as m,json; d=m.distribution('boltzmann-enzyme-research'); "
        "print(json.dumps({'version': d.version, 'entry_points': {p.name:p.value for p in d.entry_points}}))"]))
    command([str(output / "venv" / "bin" / "enzyme-research"), "--help"])
    research = json.loads(command([python, "-I", "-B", "-m", "enzyme_research.cli", "demo",
                                   "--upstream", str(args.upstream.absolute()), "--output", str(output / "research")]))
    replay_code = (
        "import importlib.util,json; from enzyme_research.paths import bundled_workflow_source; "
        "from enzyme_research.workflow import load_workflow; p=bundled_workflow_source(); load_workflow(p); "
        "s=importlib.util.spec_from_file_location('installed_replay',p/'examples'/'offline_replay.py'); "
        "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        "import sys; print(json.dumps(m.run(sys.argv[1])))"
    )
    handoffs = json.loads(command([python, "-I", "-B", "-c", replay_code, str(output / "handoffs")]))
    if not (research["success"] and research["actual_upstream_code_executed"] and handoffs["success"]):
        raise RuntimeError("Installed demonstrations did not succeed")
    report = {"success": True, "python": sys.version.split()[0], "installed": installation,
              "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
              "resources_present": sorted(required), "source_notices_packaged": True, "installed_research_demo_passed": True,
              "installed_executor_replay_passed": True, "restart_recovered": research["restart_recovered"],
              "upstream_revision": research["upstream_revision"], "synthetic_only": True,
              "network_installs_during_check": 0, "real_model_requests": 0,
              "scientific_platform_jobs": 0, "local_gpu_used": False,
              "scientific_comparison_complete": False}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
