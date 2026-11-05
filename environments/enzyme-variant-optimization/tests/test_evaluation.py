"""Synthetic behavior tests; no measured enzyme data or remote execution."""
import csv
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("enzyme_evaluation", ROOT / "src/evaluation.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sequence_hash(label):
    return hashlib.sha256(label.encode()).hexdigest()


def protocol(**changes):
    return {"parent_id": "parent", "metric": "synthetic_metric", "unit": "test_units",
            "protocol_id": "synthetic-protocol", "direction": "maximize", "max_selected": 5,
            "min_improvement": 0.0, "ratio_allowed": False, **changes}


def observation(candidate, measured_value, **changes):
    return {"candidate_id": candidate, "sequence_sha256": sequence_hash(candidate),
            "metric": "synthetic_metric", "value": measured_value, "unit": "test_units",
            "protocol_id": "synthetic-protocol", "eligibility": "true",
            "evidence_path": f"synthetic/{candidate}.txt", **changes}


def selection(*candidates):
    return [{"candidate_id": candidate, "rank": rank, "sequence_sha256": sequence_hash(candidate)}
            for rank, candidate in enumerate(candidates, 1)]


class EvaluationTests(unittest.TestCase):
    def test_cli_parses_the_same_selection_snapshot_it_hashes(self):
        cli_spec = importlib.util.spec_from_file_location("enzyme_evaluation_cli", ROOT / "scripts/evaluate_results.py")
        cli = importlib.util.module_from_spec(cli_spec)
        cli_spec.loader.exec_module(cli)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "protocol.json").write_text(json.dumps(protocol()), encoding="utf-8")
            for filename, rows in (("observations.csv", [observation("parent", 10), observation("a", 12), observation("b", 8)]),
                                   ("selection.csv", selection("a"))):
                with (root / filename).open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
            selection_path = root / "selection.csv"
            digest = hashlib.sha256(selection_path.read_bytes()).hexdigest()
            (root / "seal.json").write_text(json.dumps({"selection_sha256": digest}), encoding="utf-8")
            original_read = Path.read_bytes

            def replace_after_read(path):
                snapshot = original_read(path)
                if path == selection_path:
                    with path.open("w", newline="", encoding="utf-8") as handle:
                        writer = csv.DictWriter(handle, fieldnames=list(selection("b")[0]))
                        writer.writeheader()
                        writer.writerows(selection("b"))
                return snapshot

            command = ["evaluate_results.py"]
            for key, filename in (("protocol", "protocol.json"), ("observations", "observations.csv"),
                                  ("selection", "selection.csv"), ("seal", "seal.json")):
                command += [f"--{key}", str(root / filename)]
            output = io.StringIO()
            with patch.object(sys, "argv", command), patch.object(Path, "read_bytes", replace_after_read), redirect_stdout(output):
                cli.main()
            result = json.loads(output.getvalue())
            self.assertEqual(result["selection_sha256"], digest)
            self.assertEqual(result["rows"][0]["candidate_id"], "a")

    def test_metric_direction_and_ratio_are_explicit(self):
        data = [observation("parent", 10), observation("a", 12), observation("b", 8)]
        for direction, expected in (("maximize", [2, -2]), ("minimize", [-2, 2])):
            with self.subTest(direction=direction):
                result = MODULE.evaluate(protocol(direction=direction), data, selection("a", "b"))
                self.assertEqual(result["status"], "scored")
                self.assertEqual([r["signed_improvement"] for r in result["rows"]], expected)
                self.assertEqual(result["numerically_improved_count"], 1)
                self.assertEqual(result["mean_signed_improvement"], 0)
                self.assertTrue(all(r["parent_ratio"] is None for r in result["rows"]))
        result = MODULE.evaluate(protocol(ratio_allowed=True), data, selection("a"))
        self.assertEqual(result["rows"][0]["parent_ratio"], 1.2)

    def test_missing_or_unknown_evidence_is_not_zero_or_an_aggregate_score(self):
        for changes in ({"value": ""}, {"eligibility": "unknown"}):
            with self.subTest(changes=changes):
                data = [observation("parent", 10), observation("a", 12, **changes)]
                result = MODULE.evaluate(protocol(), data, selection("a"))
                self.assertEqual(result["status"], "incomplete")
                self.assertIsNone(result["mean_signed_improvement"])
                self.assertIsNone(result["rows"][0]["signed_improvement"])
        result = MODULE.evaluate(protocol(), [observation("a", 12)], selection("a"))
        self.assertIsNone(result["parent_value"])
        result = MODULE.evaluate(protocol(), [observation("parent", 10)], selection("a"))
        self.assertEqual(result["rows"][0]["status"], "unresolved")

    def test_failed_gate_and_empty_selection_are_distinct(self):
        data = [observation("parent", 10), observation("a", 100, eligibility="false")]
        result = MODULE.evaluate(protocol(), data, selection("a"))
        self.assertEqual(result["status"], "invalid_selection")
        self.assertIsNone(result["mean_signed_improvement"])
        self.assertEqual(MODULE.evaluate(protocol(), [], [])["status"], "no_selection")

    def test_incompatible_or_duplicate_measurements_are_rejected(self):
        for changes in ({"unit": "other"}, {"metric": "other"}, {"protocol_id": "other"},
                        {"eligibility": "passed"}, {"evidence_path": ""}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                MODULE.evaluate(protocol(), [observation("parent", 10), observation("a", 12, **changes)], selection("a"))
        with self.assertRaisesRegex(ValueError, "duplicate observation"):
            MODULE.evaluate(protocol(), [observation("parent", 10)] * 2, selection("a"))

    def test_invalid_selections_cannot_be_scored(self):
        data = [observation("parent", 10), observation("a", 12)]
        cases = [selection("parent"), selection("a", "a"),
                 [{**selection("a")[0], "rank": 2}],
                 [{**selection("a")[0], "sequence_sha256": sequence_hash("other")}],
                 [{**selection("a")[0], "sequence_sha256": sequence_hash("parent")}],
                 selection("a") + [{"candidate_id": "alias", "rank": 2, "sequence_sha256": sequence_hash("a")}]]
        for chosen in cases:
            with self.subTest(selection=chosen), self.assertRaises(ValueError):
                MODULE.evaluate(protocol(), data, chosen)
        with self.assertRaisesRegex(ValueError, "max_selected"):
            MODULE.evaluate(protocol(max_selected=1), data, selection("a", "b"))

    def test_nonfinite_and_invalid_protocol_values_are_rejected(self):
        for value in ("nan", "inf", "-inf", True, "not-a-number"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.evaluate(protocol(), [observation("parent", 10), observation("a", value)], selection("a"))
        for changes in ({"direction": "automatic"}, {"min_improvement": -1},
                        {"max_selected": True}, {"max_selected": 0}, {"ratio_allowed": "false"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                MODULE.evaluate(protocol(**changes), [], [])

    def test_small_gain_and_zero_parent_do_not_create_unsupported_ratios(self):
        result = MODULE.evaluate(protocol(min_improvement=2),
                                 [observation("parent", 10), observation("a", 12)], selection("a"))
        self.assertFalse(result["rows"][0]["numerically_improved"])
        for parent in (0, -10):
            result = MODULE.evaluate(protocol(ratio_allowed=True),
                                     [observation("parent", parent), observation("a", 12)], selection("a"))
            self.assertIsNone(result["rows"][0]["parent_ratio"])

    def test_cli_uses_real_files_and_detects_changed_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "protocol.json").write_text(json.dumps(protocol()), encoding="utf-8")
            for filename, rows in (("observations.csv", [observation("parent", 10), observation("a", 12)]),
                                   ("selection.csv", selection("a"))):
                with (root / filename).open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
            digest = hashlib.sha256((root / "selection.csv").read_bytes()).hexdigest()
            (root / "seal.json").write_text(json.dumps({"selection_sha256": digest}), encoding="utf-8")
            command = [sys.executable, "-B", str(ROOT / "scripts/evaluate_results.py")]
            for key, filename in (("protocol", "protocol.json"), ("observations", "observations.csv"),
                                  ("selection", "selection.csv"), ("seal", "seal.json")):
                command += [f"--{key}", str(root / filename)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "scored")
            (root / "selection.csv").write_text("changed\n", encoding="utf-8")
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("seal", result.stderr)


if __name__ == "__main__":
    unittest.main()
