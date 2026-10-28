"""Adversarial evaluator tests using only invented scalar observations."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from leadopt_env.core import CampaignStore, digest
from leadopt_env.evaluation import evaluate


def fixture(kind="synthetic", evidence_kind="synthetic", same_scorer=False):
    candidates = [dict(id=cid, representation="synthetic:" + cid, form_id=cid, source="invented")
                  for cid in ("lead", "candidate")]
    signature = dict(endpoint="fixture", unit="arbitrary", method="fixture-search",
                     method_version="1", context="software-only", kind=evidence_kind)
    objective = dict(id="objective", **signature, baseline_id="lead", direction="maximize",
                     support="later_assessment", support_evidence="invented fixture")
    final = dict(objective, method="fixture-search" if same_scorer else "fixture-final")
    task = dict(schema_version=1, id="evaluator-critic", version="1", question="software test",
                context="software-only", sources=["fixture"], starting_candidates=candidates,
                objectives=[objective], constraints=[], candidate_scope=dict(mode="analogues"),
                allowed_jobs=["fixture_job"], budgets={"submissions": 3},
                evaluation=dict(kind=kind, source_version="v1", protocol="invented test",
                                objectives=[final], constraints=[]))
    observations = [dict(id=cid + "-final", candidate_id=cid, form_id=cid,
                         **{k: final[k] for k in signature}, value=value, qualifier="=",
                         status="completed", source="invented fixture")
                    for cid, value in (("lead", 1), ("candidate", 2))]
    reference = dict(schema_version=1, task_digest=digest(task), source_version="v1",
                     provenance="Invented fixture; no chemical evidence", candidates=candidates,
                     observations=observations)
    return task, reference


class EvaluationCriticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CampaignStore(Path(self.temp.name) / "records.sqlite")

    def prepare(self, observed=1, unknown=False, pending=False, **fixture_args):
        task, reference = fixture(**fixture_args)
        self.store.dispatch("create", "campaign", {"task": task})
        if observed is not None:
            self.store.dispatch("usage", "campaign", dict(id="usage", unit="submissions", amount=observed,
                                category="observed", scope="campaign", source="fixture"))
        if unknown:
            self.store.dispatch("usage", "campaign", dict(id="unknown", unit="submissions", amount=None,
                                category="unknown", scope="campaign", source="fixture"))
        if pending:
            self.store.dispatch("action", "campaign", dict(id="pending", attempt_id="attempt",
                                job="fixture_job", candidate_ids=["candidate"], status="unknown", source="fixture"))
        request = dict(id="freeze", candidate_ids=["candidate"], rationale="fixture", stopping_reason="test")
        frozen = self.store.dispatch("freeze", "campaign", request)
        return frozen, reference

    def test_absent_budget_evidence_prevents_eligibility_pass(self):
        frozen, reference = self.prepare(observed=None)
        result = evaluate(frozen, reference, frozen["digest"])
        self.assertEqual(result["results"][0]["eligibility"], "unresolved")

    def test_unknown_budget_consumption_prevents_eligibility_pass(self):
        frozen, reference = self.prepare(unknown=True)
        result = evaluate(frozen, reference, frozen["digest"])
        self.assertEqual(result["results"][0]["eligibility"], "unresolved")

    def test_pending_work_prevents_complete_resource_eligibility(self):
        frozen, reference = self.prepare(pending=True)
        result = evaluate(frozen, reference, frozen["digest"])
        self.assertEqual(result["results"][0]["eligibility"], "unresolved")

    def test_exact_budget_limit_is_not_an_overrun(self):
        frozen, reference = self.prepare(observed=3)
        result = evaluate(frozen, reference, frozen["digest"])
        self.assertNotEqual(result["results"][0]["eligibility"], "fail")

    def test_heldout_claim_rejects_synthetic_evidence(self):
        frozen, reference = self.prepare(kind="heldout_measurement", evidence_kind="synthetic")
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen["digest"])

    def test_different_predictor_claim_rejects_same_scorer(self):
        frozen, reference = self.prepare(kind="different_predictor", evidence_kind="predicted", same_scorer=True)
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen["digest"])

    def test_recomputed_digest_cannot_defeat_retained_receipt(self):
        frozen, reference = self.prepare()
        receipt = frozen["digest"]
        tampered = deepcopy(frozen)
        tampered["snapshot"]["submission"]["candidate_ids"] = ["lead"]
        tampered["digest"] = digest(tampered["snapshot"])
        with self.assertRaises(ValueError):
            evaluate(tampered, reference, receipt)

    def test_different_predictor_cannot_be_exposed_as_search_observation(self):
        frozen, reference = self.prepare(kind="different_predictor", evidence_kind="predicted")
        self.store.dispatch("observation", "campaign", dict(reference["observations"][1], id="search-exposure"))
        new = self.store.dispatch("freeze", "campaign", {**frozen["request"], "id":"after-exposure"})
        with self.assertRaises(ValueError):
            evaluate(new, reference, new["digest"])

    def test_different_predictor_cannot_already_be_a_search_constraint(self):
        task, reference = fixture(kind="different_predictor", evidence_kind="predicted")
        final = task["evaluation"]["objectives"][0]
        task["constraints"] = [{k: final[k] for k in ("id", "endpoint", "unit", "method", "method_version", "context", "kind")}]
        task["constraints"][0]["minimum"] = 0
        reference["task_digest"] = digest(task)
        self.store.dispatch("create", "campaign", {"task": task})
        frozen = self.store.dispatch("freeze", "campaign", dict(id="final",candidate_ids=["candidate"],rationale="fixture",stopping_reason="test"))
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen["digest"])

    def test_postfreeze_records_cannot_change_frozen_score_or_usage(self):
        frozen, reference = self.prepare()
        original = evaluate(frozen, reference, frozen["digest"])
        self.store.dispatch("usage", "campaign", dict(id="later", unit="submissions", amount=99,
                            category="observed", scope="campaign", source="fixture"))
        observation = dict(reference["observations"][1], id="agent-later", value=-999)
        self.store.dispatch("observation", "campaign", observation)
        recovered = self.store.dispatch("freeze", "campaign", frozen["request"])
        self.assertEqual(evaluate(recovered, reference, frozen["digest"]), original)
        self.assertFalse(original["isolation_verified"])

    def test_reference_identity_substitution_is_rejected(self):
        frozen, reference = self.prepare()
        reference["candidates"][1]["representation"] = "synthetic:different"
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen["digest"])

    def test_inverted_final_objective_range_is_rejected_at_intake(self):
        task, _ = fixture()
        task["evaluation"]["objectives"][0].update(direction="range", target_min=3, target_max=1)
        with self.assertRaises(ValueError):
            self.store.dispatch("create", "campaign", {"task": task})


if __name__ == "__main__":
    unittest.main()
