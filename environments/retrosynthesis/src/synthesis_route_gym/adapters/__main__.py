"""Smoke CLI: python -m synthesis_route_gym.adapters localretro TARGET --python PATH."""

from __future__ import annotations

import argparse
import json

from . import AiZynthFinderAdapter, LocalRetroAdapter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend", choices=["localretro", "aizynthfinder"])
    parser.add_argument("target")
    parser.add_argument("--python", dest="python_executable")
    parser.add_argument("--repo-root")
    parser.add_argument("--config")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    args = parser.parse_args()
    if args.backend == "localretro":
        adapter = LocalRetroAdapter(args.repo_root, args.python_executable,
                                    timeout_seconds=args.timeout_seconds)
    else:
        if not args.config:
            parser.error("--config is required for AiZynthFinder")
        options = {"python_executable": args.python_executable} if args.python_executable else {}
        adapter = AiZynthFinderAdapter(args.config, timeout_seconds=args.timeout_seconds, **options)
    result = adapter.expand(args.target, top_k=args.top_k)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
