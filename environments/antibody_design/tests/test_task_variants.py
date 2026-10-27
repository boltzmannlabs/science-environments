"""Task-parity tests for the general and named-method DENV monoclonal-antibody tasks."""
from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENERAL = ROOT / "tasks/denv_antibody_001.md"
TOOL_SPECIFIC = ROOT / "tasks/denv_antibody_001_tools.md"
TEST_PLAN = ROOT / "tests/MONOCLONAL_ANTIBODY_TEST_CASES.md"


def normalized_task(text: str) -> str:
    text = re.sub(r"\*\*Task variant:\*\* `[^`]+`", "**Task variant:** `shared`", text)
    return re.sub(
        r"## Available Computational Methods\n.*?(?=## Required Execution Steps\n)",
        "",
        text,
        flags=re.S,
    )


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"Missing section: {heading}")
    return match.group(1).strip()


class TaskVariantParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.general = GENERAL.read_text()
        cls.specific = TOOL_SPECIFIC.read_text()

    def test_only_allowed_named_method_block_differs(self):
        self.assertEqual(normalized_task(self.general), normalized_task(self.specific))

    def test_both_variants_have_same_task_identity_and_family(self):
        for text in (self.general, self.specific):
            self.assertIn("# Task: denv_antibody_001", text)
            self.assertIn("monoclonal-antibody design and computational assessment", text)
            self.assertIn("DENV-2", text)
            self.assertIn("DV87.1", text)

    def test_general_task_contains_no_named_computational_service(self):
        lowered = self.general.casefold()
        for name in ("stability-binding ddg", "stability-binding-ddg", "prodigy", "ipsae",
                     "stabddg", "boltz", "boltz2"):
            self.assertNotIn(name, lowered)

    def test_named_method_task_uses_current_exact_names(self):
        self.assertIn("Stability-Binding DDG (`stability-binding-ddg`)", self.specific)
        self.assertIn("| PRODIGY |", self.specific)
        self.assertIn("| ipSAE |", self.specific)
        self.assertNotIn("StabDDG", self.specific)
        self.assertNotRegex(self.specific, r"\bBoltz2?\b")

    def test_both_variants_preserve_antigen_reference_and_pairing_contract(self):
        required_phrases = (
            "Exact supplied construct and coordinate file",
            "Complete, correctly paired reference heavy and light chains",
            "sequence-to-structure mapping",
            "Preserve the reference framework, chain pairing, and declared construct format",
            "Antigen–antibody interface evidence",
            ">candidate_id|H",
            ">candidate_id|L",
        )
        for text in (self.general, self.specific):
            for phrase in required_phrases:
                self.assertIn(phrase, text)

    def test_scientific_sections_are_identical(self):
        headings = (
            "Description", "Target", "Design Constraints", "Required Execution Steps",
            "Evaluation Metrics", "Expected Output", "Constraints", "Important Instructions",
        )
        for heading in headings:
            self.assertEqual(section(self.general, heading), section(self.specific, heading), heading)

    def test_test_plan_has_complete_sequential_case_ids(self):
        case_ids = re.findall(r"\| (MAB-\d{3}) \|", TEST_PLAN.read_text())
        self.assertEqual(case_ids, [f"MAB-{number:03d}" for number in range(1, 31)])
        self.assertEqual(len(case_ids), len(set(case_ids)))

    def test_test_plan_covers_both_variants_and_scientific_boundary(self):
        plan = TEST_PLAN.read_text()
        for phrase in (
            "denv_antibody_001.md",
            "denv_antibody_001_tools.md",
            "same antigen, reference antibody",
            "Reference-baseline tests",
            "Antigen–antibody complex and interface tests",
            "Stability and developability tests",
            "Scientific benchmark scenarios",
            "does not mean a designed antibody binds",
        ):
            self.assertIn(phrase, plan)


if __name__ == "__main__":
    unittest.main()
