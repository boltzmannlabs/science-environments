#!/usr/bin/env python3
"""Read-only retrosynthesis export audit with explicit output and no credentials."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from impurity_env import audit_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="authorized local Boltzmann-style route JSON")
    parser.add_argument("--target-smiles", required=True, help="independently reviewed target structure")
    parser.add_argument("--target-label", required=True, help="label used only in local output")
    parser.add_argument("--output", required=True, type=Path, help="new derived JSON; must not exist")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("refusing to overwrite an existing audit or raw source")
    if args.output.resolve() == args.input.resolve():
        parser.error("output must differ from the input source")
    try:
        result = audit_file(args.input, args.target_smiles)
        result["target_label"] = args.target_label
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Audit failed; no route validated: {exc}\n")
    print("Wrote computational-only audit:", args.output)
    print("Original routes:", result["route_count"], "all decisions: Hold pending evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
