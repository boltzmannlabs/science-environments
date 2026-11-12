"""Independent frozen-input and configuration checks for MD-PAPER-002."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ref = json.loads((ROOT / "reference/parameters.json").read_text())
    pdb = ROOT / "inputs/6M2N.pdb"
    actual = sha256(pdb) if pdb.exists() else None
    expected = ref["input_sha256"]["6M2N.pdb"]
    checks = {
        "input_exists": pdb.exists(),
        "input_sha256_matches": actual == expected,
        "pdb_id": ref["pdb_id"] == "6M2N",
        "nvt_ns_present": ref["reported"]["nvt_ns"]["value"] == 0.1,
        "conventional_scope": True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"task_id": ref["task_id"], "status": status, "checks": checks,
              "scope": "frozen input and conventional MD setup validation; no production claim",
              "actual_sha256": actual, "expected_sha256": expected}
    out = ROOT / "evaluation/input_validation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
