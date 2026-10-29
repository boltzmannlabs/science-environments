"""Evaluate frozen condition model through actual one-step route contracts."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from synthesis_route_gym.heldout_route_benchmark import run_heldout_route_benchmark


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--model-dir", default=Path("artifacts/model"), type=Path)
    parser.add_argument("--output", default=Path("artifacts/model/route_decisions"), type=Path)
    args = parser.parse_args()
    report = run_heldout_route_benchmark(args.dataset, args.model_dir, args.output)
    print(json.dumps({k: report[k] for k in (
        "target_task_count", "heldout_product_family_count", "candidate_count", "top_1_gain_percentage_points",
        "quantity_compliance_proven", "multi_step_route_improvement_proven", "review", "runtime_seconds")}, indent=2))


if __name__ == "__main__":
    main()
