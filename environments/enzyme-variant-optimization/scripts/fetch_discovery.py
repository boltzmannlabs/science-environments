#!/usr/bin/env python3
"""Fetch the pinned public source dependency without changing an existing checkout."""
import argparse
import json
from pathlib import Path
import subprocess

from enzyme_research.discovery import UPSTREAM_REVISION, upstream_core

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SOURCE = "https://github.com/Gen-Verse/DiscoveryRSI.git"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=ROOT / ".runtime" / "DiscoveryRSI")
    parser.add_argument("--source", default=PUBLIC_SOURCE, help="Public upstream URL or an existing local Git checkout")
    args = parser.parse_args()
    destination = args.destination.absolute()
    if not destination.exists():
        if args.source != PUBLIC_SOURCE and not Path(args.source).is_dir():
            parser.error("Source must be the official public URL or an existing local Git checkout")
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--no-hardlinks", "--", args.source, str(destination)], check=True)
        subprocess.run(["git", "-C", str(destination), "checkout", "--detach", UPSTREAM_REVISION], check=True)
    upstream_core(destination)
    print(json.dumps({"source": str(destination), "revision": UPSTREAM_REVISION,
                      "existing_checkout_preserved": True, "scientific_jobs_submitted": 0}))


if __name__ == "__main__":
    main()
