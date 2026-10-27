#!/usr/bin/env python3
"""Exercise actual research/executor code with explicit synthetic responses only."""
import argparse
import importlib.util
import json
from pathlib import Path

from enzyme_research.demo import demo
from enzyme_research.paths import bundled_workflow_source
from enzyme_research.workflow import load_workflow

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=ROOT / ".runtime" / "DiscoveryRSI")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    research = demo(output / "research", args.upstream)
    workflow = bundled_workflow_source()
    load_workflow(workflow)
    spec = importlib.util.spec_from_file_location("enzyme_release_replay", workflow / "examples" / "offline_replay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handoffs = module.run(output / "handoffs")
    result = {"success": research["success"] and handoffs["success"], "synthetic_only": True,
              "research": research, "handoffs": handoffs, "real_model_requests": 0,
              "scientific_platform_jobs": 0, "local_gpu_used": False,
              "scientific_improvement_established": False}
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
