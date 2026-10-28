"""Reproduce a local benchmark cohort from explicitly hashed curator inputs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from .benchmark_curation import load_seen_doyle, prepare_tasks
from .condition_data import load_condition_records, SOURCE_ID
from .dataset_bundle import build_bundle, verify_bundle
from .route_data import load_stock


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inputs(config):
    if set(config) != {"schema_version", "seed", "quotas", "inputs", "provenance"} or config["schema_version"] != "1.0":
        raise ValueError("Unsupported curation configuration")
    entries = config["inputs"]
    if not {"routes", "stock", "fresh_conditions", "seen_doyle"} <= set(entries):
        raise ValueError("Missing declared curation inputs")
    paths = {}
    for key, value in entries.items():
        if set(value) != {"path", "sha256"} or re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is None:
            raise ValueError("Invalid input hash declaration")
        path = Path(value["path"])
        if path.is_symlink() or not path.is_file() or file_hash(path) != value["sha256"]:
            raise ValueError(f"Input hash mismatch or invalid source: {key}")
        paths[key] = path
    return paths


def _assignments(prepared):
    condition_by_id = {row["record_id"]: row for row in prepared["assignments"]}
    condition_tasks = [{"task_id": task["task_id"], **condition_by_id[task["task_id"]]}
                       for task in prepared["tasks"] if task["track"] == "measured_conditions"]
    return [*prepared["task_groups"], *condition_tasks,
            {"record_id": "curation-graph", "full_record_assignments": prepared["assignments"],
             "group_links": prepared["group_links"]}]


def curate_from_config(config_path, public_dir, private_dir, report_dir):
    """Trusted-host operation; no label contents are returned or printed."""
    public_dir, private_dir, report_dir = map(Path, (public_dir, private_dir, report_dir))
    destinations = tuple(path.resolve() for path in (public_dir, private_dir, report_dir))
    if any(a == b or a in b.parents or b in a.parents for i, a in enumerate(destinations) for b in destinations[i+1:]):
        raise ValueError("Curation output directories must be disjoint")
    if any(path.exists() or path.is_symlink() for path in (public_dir, private_dir, report_dir)):
        raise ValueError("Curation output already exists; choose a new version")
    config = json.loads(Path(config_path).read_text())
    paths = _inputs(config)
    routes = json.loads(paths["routes"].read_text())
    stock = load_stock(paths["stock"])
    fresh = load_condition_records(paths["fresh_conditions"], SOURCE_ID)
    seen = load_seen_doyle(paths["seen_doyle"])
    overlap = json.loads(paths["training_overlap"].read_text()) if "training_overlap" in paths else {}
    excluded = set(overlap.get("reference_records_with_publication_number_match", [])) | set(
        overlap.get("reference_records_with_exact_reaction_match", []))
    prepared = prepare_tasks(routes, stock, fresh, seen, quotas=config["quotas"], seed=config["seed"],
                             training_overlap_record_ids=excluded)
    receipt = build_bundle(public_dir, private_dir, tasks=prepared["tasks"], labels=prepared["labels"],
                           provenance=config["provenance"], inventory=stock, assignments=_assignments(prepared))
    verified = verify_bundle(public_dir, private_dir,
                             expected_manifest_sha256=receipt["public_manifest_sha256"],
                             expected_private_manifest_sha256=receipt["private_manifest_sha256"])
    report_dir.mkdir(mode=0o700)
    report = {**prepared["report"], "config_sha256": file_hash(config_path),
              "public_manifest_sha256": receipt["public_manifest_sha256"], "verification": verified}
    # Keep the private answer-manifest anchor in an operator-only receipt.
    for name, data in (("curation.json", report), ("bundle_receipt.json", receipt)):
        path = report_dir / name
        with path.open("x") as stream:
            json.dump(data, stream, sort_keys=True, indent=2)
            stream.write("\n")
        path.chmod(0o600)
    return {"status": "curated", "task_count": receipt["task_count"],
            "route_targets": report["route_targets"], "final_run_authorized": False,
            "public_manifest_sha256": receipt["public_manifest_sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = curate_from_config(args.config, args.public_output, args.private_output, args.report_output)
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"Curation failed ({type(error).__name__}); no scientific result asserted.", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
