"""Create account-free, internally consistent parser/task fixtures."""
import argparse
import json
from pathlib import Path
from enzyme_research.demo import fixture_task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    task = fixture_task(output)
    target = output / "task.json"
    target.write_text(json.dumps(task, indent=2) + "\n")
    print(json.dumps({"task_path": str(target), "synthetic_only": True, "scientific_jobs_submitted": 0}))


if __name__ == "__main__":
    main()
