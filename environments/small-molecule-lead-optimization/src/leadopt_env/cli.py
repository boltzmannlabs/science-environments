"""Local reproduction and evaluator CLI; normal research uses the native plugin."""
import argparse
import json
from pathlib import Path
import sys

from .contracts import SCHEMAS
from .core import CampaignStore
from .evaluation import evaluate


def read(path):
    return json.loads(Path(path).read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    schema = commands.add_parser("schema")
    schema.add_argument("name", choices=SCHEMAS)
    call = commands.add_parser("call")
    call.add_argument("--db", required=True)
    call.add_argument("--campaign", required=True)
    call.add_argument("operation")
    call.add_argument("--payload", help="JSON payload file")
    final = commands.add_parser("evaluate")
    final.add_argument("--submission", required=True)
    final.add_argument("--reference", required=True)
    final.add_argument("--expected-digest", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            result = {"$schema": "https://json-schema.org/draft/2020-12/schema", **SCHEMAS[args.name]}
        elif args.command == "call":
            result = CampaignStore(args.db).dispatch(args.operation, args.campaign, read(args.payload) if args.payload else {})
        else:
            result = evaluate(read(args.submission), read(args.reference), args.expected_digest)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
