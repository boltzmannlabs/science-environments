"""Task-02 integrity/ownership regressions; no synthetic measurements."""
from pathlib import Path
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

ENV = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENV / "src"))
from formulation_environment.task_02_ranolazine_er_dissolution import run_task02, verify_contract

NAME = "task-02-ranolazine-er-dissolution"
CONFIG = ENV / "config" / NAME


def contract():
    return json.loads((CONFIG / "contract.json").read_text())


class Task02Tests(unittest.TestCase):
    def test_all_task_owned_sections_exist(self):
        for section, relative in contract()["folders"].items():
            self.assertTrue((ENV / relative).is_dir(), section)
            if section != "research":
                self.assertTrue((ENV / relative / "README.md").is_file(), section)

    def test_registry_preserves_task01_and_dispatches_task02(self):
        registry = json.loads((ENV / "config/shared/tasks.json").read_text())["tasks"]
        self.assertIn("Task - 01", registry)
        self.assertEqual(registry["Task - 02"]["folder_slug"], NAME)
        self.assertEqual(registry["Task - 02"]["entrypoint"], "formulation_environment.task_02_ranolazine_er_dissolution:run_task02")

    def test_archive_checks_saved_arithmetic_not_scientific_validity(self):
        result = verify_contract(ENV, contract())
        self.assertEqual(result["status"], "ARCHIVE_CONSISTENCY_VERIFIED")
        self.assertEqual(result["candidate_lab_observations"], 0)
        self.assertEqual(result["product_validation"], "NOT_EVALUATED")
        self.assertGreater(result["metric_checks"], 0)

    def test_corrupted_expected_hash_rejected(self):
        altered = copy.deepcopy(contract())
        altered["input"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_contract(ENV, altered)

    def test_wrong_group_count_rejected(self):
        altered = copy.deepcopy(contract())
        altered["groups"]["pH6.8_transcribed_unverified"] = 99
        with self.assertRaisesRegex(ValueError, "profile count"):
            verify_contract(ENV, altered)

    def test_run_writes_new_verification_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            run_task02(CONFIG, output)
            self.assertTrue((output / "verification.json").is_file())
            with self.assertRaisesRegex(ValueError, "not empty"):
                run_task02(CONFIG, output)

    def test_portable_task_script_and_overwrite_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            argv = [sys.executable, str(ENV / "scripts" / NAME / "verify_archive.py"), "--out", str(output)]
            result = subprocess.run(argv, cwd=directory, env={**os.environ, "PYTHONPATH": ""}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads((output / "run_receipt.json").read_text())
            self.assertEqual(receipt["task_id"], "Task - 02")
            self.assertEqual(receipt["status"], "ARCHIVE_CONSISTENCY_VERIFIED")
            again = subprocess.run(argv, cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)



if __name__ == "__main__":
    unittest.main()
