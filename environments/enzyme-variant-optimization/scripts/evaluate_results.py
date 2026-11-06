"""Print a comparison of sealed selections and reviewer-supplied measurements."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("protocol", "observations", "selection", "seal"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    try:
        seal = json.loads(args.seal.read_text(encoding="utf-8"))
        selection_bytes = args.selection.read_bytes()
        actual = hashlib.sha256(selection_bytes).hexdigest()
        if not isinstance(seal, dict) or seal.get("selection_sha256") != actual:
            raise ValueError("selection does not match its seal")
        protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
        if not isinstance(protocol, dict):
            raise ValueError("protocol must be a JSON object")
        tables = {}
        for name in ("observations", "selection"):
            handle = (io.StringIO(selection_bytes.decode("utf-8-sig"), newline="") if name == "selection"
                      else args.observations.open(encoding="utf-8-sig", newline=""))
            with handle:
                reader = csv.DictReader(handle)
                expected = ({"candidate_id", "rank", "sequence_sha256"} if name == "selection" else
                            {"candidate_id", "sequence_sha256", "metric", "value", "unit",
                             "protocol_id", "eligibility", "evidence_path"})
                if reader.fieldnames is None or len(reader.fieldnames) != len(expected) or set(reader.fieldnames) != expected:
                    raise ValueError(f"{name}: use the exact documented CSV columns")
                tables[name] = list(reader)
                if any(None in row or any(value is None for value in row.values()) for row in tables[name]):
                    raise ValueError(f"{name}: malformed CSV row width")
        result = evaluate(protocol, tables["observations"], tables["selection"])
        result["selection_sha256"] = actual
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Comparison error: {exc}\n")


if __name__ == "__main__":
    main()
