"""Task-parity tests for the general and capability-detailed DENV monoclonal-antibody tasks."""
from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
GENERAL = ROOT / "tasks/denv_antibody_001.md"
TOOL_SPECIFIC = ROOT / "tasks/denv_antibody_001_tools.md"


def normalized_task(text: str) -> str:
    text = re.sub(r"\*\*Task variant:\*\* `[^`]+`", "**Task variant:** `shared`", text)
    return re.sub(
        r"## Computational Tool Capabilities\n.*?(?=## Evaluation Metrics\n)",
        "",
        text,
        flags=re.S,
    )


class TaskVariantParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.general = GENERAL.read_text()
        cls.specific = TOOL_SPECIFIC.read_text()

    def test_only_allowed_capability_block_differs(self):
        self.assertEqual(normalized_task(self.general), normalized_task(self.specific))

    def test_both_variants_have_same_task_identity_and_family(self):
        for text in (self.general, self.specific):
            self.assertIn("# Task: denv_antibody_001", text)
            self.assertIn("monoclonal-antibody design and computational assessment", text)
            self.assertIn("DENV-2", text)
            self.assertIn("DV87.1", text)

    def test_both_tasks_avoid_named_computational_services(self):
        for text in (self.general, self.specific):
            for name in ("stability-binding ddg", "stability-binding-ddg", "prodigy", "ipsae",
                         "stabddg", "boltz", "alphafold", "rfdiffusion", "proteinmpnn"):
                self.assertNotIn(name, text.casefold())

    def test_tools_variant_specifies_method_evidence_without_software_names(self):
        for phrase in ("interface confidence inputs", "energy units and conditions",
                       "verified energy-change sign convention", "native outputs"):
            self.assertIn(phrase, self.specific)
        for text in (self.general, self.specific):
            for stage in ("1. Validate inputs and baseline", "2. Generate or register candidates",
                          "3. Assess antibody structure", "4. Assess target complexes",
                          "5. Evaluate binding and specificity", "6. Assess developability",
                          "7. Refine when justified", "8. Select and report"):
                self.assertIn(stage, text)

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


if __name__ == "__main__":
    unittest.main()
