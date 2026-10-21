from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


class AccuracyTrackError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_accuracy_track(path: Path | str, project_root: Path | str) -> dict[str, Any]:
    manifest_path = Path(path).resolve()
    root = Path(project_root).resolve()
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if raw.get("included_in_primary_reliability_gate") is not False:
        raise AccuracyTrackError("independent accuracy track must remain outside reliability gates")
    for section, path_key, hash_key in (
        ("structure", "path", "sha256"),
        ("independent_reference", "input_path", "input_sha256"),
        ("independent_reference", "output_path", "output_sha256"),
        ("source_report", "path", "sha256"),
    ):
        record = raw.get(section)
        if not isinstance(record, dict):
            raise AccuracyTrackError(f"missing {section} record")
        artifact = (root / str(record[path_key])).resolve()
        if not artifact.is_file():
            raise AccuracyTrackError(f"accuracy artifact is missing: {artifact}")
        actual = _sha256(artifact)
        if actual != record[hash_key]:
            raise AccuracyTrackError(
                f"accuracy artifact hash mismatch for {artifact}: {actual}"
            )
    reference = float(raw["independent_reference"]["energy_hartree"])
    boltzmann = float(raw["boltzmann_result"]["energy_hartree"])
    recorded = float(raw["comparison"]["absolute_difference_hartree"])
    if not math.isclose(abs(reference - boltzmann), recorded, rel_tol=0, abs_tol=1e-14):
        raise AccuracyTrackError("recorded independent energy difference is inconsistent")
    threshold = float(raw["comparison"]["predeclared_max_difference_hartree"])
    expected_pass = recorded <= threshold
    if bool(raw["comparison"]["energy_agreement_pass"]) is not expected_pass:
        raise AccuracyTrackError("energy pass flag conflicts with the frozen threshold")
    expected_status = "pass" if expected_pass else "review"
    if raw.get("status") != expected_status:
        raise AccuracyTrackError("accuracy status conflicts with the measured comparison")
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the separate SPE accuracy track")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    record = validate_accuracy_track(args.manifest, args.project_root)
    print(json.dumps({"track_id": record["track_id"], "status": record["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
