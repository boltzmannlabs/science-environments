from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents import EvaluationDecision, IndependentEvaluator, SPERegistry  # noqa: E402


class IndependentEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.environment = SPERegistry(ROOT / "environments").get("01")
        cls.evaluator = IndependentEvaluator()

    def test_all_explicitly_passing_evidence_passes(self) -> None:
        evidence = {criterion: True for criterion in self.environment.acceptance_criteria}
        report = self.evaluator.evaluate(self.environment, evidence, execution_completed=True)
        self.assertEqual(report.decision, EvaluationDecision.PASS)
        self.assertFalse(report.failed)
        self.assertFalse(report.missing)

    def test_one_failed_criterion_fails(self) -> None:
        evidence = {criterion: True for criterion in self.environment.acceptance_criteria}
        evidence[self.environment.acceptance_criteria[0]] = False
        report = self.evaluator.evaluate(self.environment, evidence, execution_completed=True)
        self.assertEqual(report.decision, EvaluationDecision.FAIL)

    def test_missing_evidence_requires_review(self) -> None:
        report = self.evaluator.evaluate(self.environment, {}, execution_completed=True)
        self.assertEqual(report.decision, EvaluationDecision.NEEDS_REVIEW)
        self.assertEqual(report.missing, self.environment.acceptance_criteria)

    def test_no_execution_or_evidence_is_not_evaluated(self) -> None:
        report = self.evaluator.evaluate(self.environment, {}, execution_completed=False)
        self.assertEqual(report.decision, EvaluationDecision.NOT_EVALUATED)


if __name__ == "__main__":
    unittest.main()
