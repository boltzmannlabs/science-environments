"""Read-only artifact evaluator; optional supplied measured/predicted profile pair."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation.exploratory_verifier import verify_scenario
from evaluation.profile_comparison import compare
from evaluation.six_model_verifier import verify


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path)
    p.add_argument("--six-model", type=Path)
    p.add_argument(
        "--comparison",
        type=Path,
        help="JSON containing predicted and observed profiles",
    )
    args = p.parse_args()
    result = {}
    if args.run:
        record = json.loads((args.run / "report.json").read_text())
        hashes = {
            name: hashlib.sha256((args.run / name).read_bytes()).hexdigest() == sha
            for name, sha in record["artifact_sha256"].items()
        }
        result["artifact_hashes"] = hashes
        result["status"] = record["status"]
        if record["status"] == "completed_scenario_only":
            findings = verify_scenario(
                json.loads((args.run / "scenario.json").read_text()),
                record["scenario_configuration"],
            )
            result["scenario_findings"] = findings
    if args.six_model:
        result["six_model_findings"] = verify(
            json.loads((args.six_model / "six_model_results.json").read_text()),
            json.loads((args.six_model / "synthetic_batch_fixture.json").read_text()),
        )
    if args.comparison:
        pair = json.loads(args.comparison.read_text())
        result["supplied_profile_comparison"] = compare(
            pair["predicted"], pair.get("observed")
        )
    if not result:
        p.error("provide --run, --six-model or --comparison")
    print(json.dumps(result, indent=2, allow_nan=False))
    if (
        any(v is False for v in result.get("artifact_hashes", {}).values())
        or result.get("scenario_findings")
        or result.get("six_model_findings")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
