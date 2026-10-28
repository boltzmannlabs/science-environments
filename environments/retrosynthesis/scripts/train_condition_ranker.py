"""Train and evaluate the frozen condition-ranker experiment."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from synthesis_route_gym.model_training import train_and_evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output", default=Path("artifacts/model"), type=Path)
    args = parser.parse_args()
    report = train_and_evaluate(args.dataset, args.output)
    print(json.dumps({k: report[k] for k in (
        "model_version", "top_1_regret_improvement_percentage_points",
        "condition_decision_gate_passed", "multi_step_route_improvement_proven", "runtime_seconds")}, indent=2))


if __name__ == "__main__":
    main()
