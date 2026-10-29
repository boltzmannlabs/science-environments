"""Independent adversarial review: synthetic records, no scientific services."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from leadopt_env.core import CampaignStore, digest


SIGNATURE = dict(endpoint="artificial_score", unit="arbitrary", method="fixture",
                 method_version="1", context="synthetic_only", kind="synthetic")


def candidate(cid):
    return dict(id=cid, representation="synthetic:" + cid, form_id="form:" + cid,
                source="software fixture; not a molecule")


def observation(oid, cid, value, **changes):
    result = dict(id=oid, candidate_id=cid, form_id="form:" + cid,
                  **SIGNATURE, value=value, qualifier="=", status="completed", source="fixture")
    result.update(changes)
    return result


def task():
    return dict(schema_version=1, id="critic_fixture", version="1", question="test records",
                context="synthetic_only", sources=["fixture"],
                starting_candidates=[candidate("lead"), candidate("candidate")],
                initial_observations=[observation("base", "lead", 1), observation("new", "candidate", 2)],
                objectives=[dict(id="objective", **SIGNATURE, baseline_id="lead", direction="maximize",
                                 support="later_assessment", support_evidence="fixture contract")],
                constraints=[], allowed_jobs=["fixture_job"], candidate_scope={"mode": "analogues"},
                budgets={"submissions": 3},
                evaluation=dict(kind="synthetic", protocol="fixture", source_version="1"))


class CriticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "campaigns.sqlite"
        self.store = CampaignStore(self.db)

    def create(self, record=None, cid="campaign"):
        return self.store.dispatch("create", cid, {"task": task() if record is None else record})

    def report(self):
        return self.store.dispatch("report", "campaign")

    def comparison(self, report):
        return next(r for r in report["comparisons"] if r["candidate_id"] == "candidate")

    def test_missing_capability_support_cannot_produce_pass(self):
        record = task()
        del record["objectives"][0]["support"]
        report = self.create(record)
        self.assertEqual(self.comparison(report)["status"], "unresolved")

    def test_incompatible_or_missing_signature_never_passes(self):
        cases = ({"unit": "other"}, {"method_version": "2"}, {"kind": "experimental"},
                 {"context": "other"}, {"form_id": "other"}, {"qualifier": "<"},
                 {"status": "failed"}, {"value": None})
        for index, change in enumerate(cases):
            with self.subTest(change=change):
                record = task()
                record["initial_observations"][1].update(change)
                report = self.create(record, "case_" + str(index))
                self.assertEqual(self.comparison(report)["status"], "unresolved")

    def test_ambiguous_repeated_evidence_is_not_cherry_picked(self):
        record = task()
        record["initial_observations"].append(observation("new_again", "candidate", -3))
        self.assertEqual(self.comparison(self.create(record))["status"], "unresolved")

    def test_nonfinite_arithmetic_never_produces_scientific_pass(self):
        record = task()
        record["initial_observations"][0]["value"] = -1e308
        record["initial_observations"][1]["value"] = 1e308
        report = self.create(record)
        self.assertEqual(self.comparison(report)["status"], "unresolved")
        json.dumps(report, allow_nan=False)

    def test_unchecked_disallowed_action_is_recorded_and_warned(self):
        record = task()
        record["candidate_scope"] = {"mode": "fixed_library", "allowed_ids": ["lead"]}
        self.create(record)
        action = dict(id="action", attempt_id="attempt", job="forbidden_job", candidate_ids=["candidate"],
                      status="accepted", source="fixture", rationale="agent elects to continue")
        result = self.store.dispatch("action", "campaign", action)
        self.assertTrue(result["recorded"])
        codes = {w["code"] for w in self.report()["warnings"]}
        self.assertTrue({"action_without_check", "job_not_allowed", "candidate_not_allowed"} <= codes)

    def test_warning_does_not_prevent_recording_continuation(self):
        self.create()
        check = dict(id="check", job="forbidden_job", candidate_ids=["candidate"],
                     resource_requests={"submissions": 100})
        advice = self.store.dispatch("check", "campaign", check)
        self.assertTrue(advice["can_continue"])
        self.assertIn("budget_exceeded", {w["code"] for w in advice["warnings"]})
        action = dict(id="action", attempt_id="attempt", job="forbidden_job", candidate_ids=["candidate"],
                      status="unknown", source="fixture", check_id="check")
        self.assertTrue(self.store.dispatch("action", "campaign", action)["recorded"])
        restarted = CampaignStore(self.db).dispatch("report", "campaign")
        self.assertEqual(restarted["unresolved_usage_commitments"][0]["resource_requests"], {"submissions": 100})

    def test_repeated_check_is_original_advice_not_recomputed(self):
        self.create()
        check = dict(id="check", job="fixture_job", candidate_ids=["candidate"], resource_requests={})
        original = self.store.dispatch("check", "campaign", check)
        self.store.dispatch("usage", "campaign", dict(id="overrun", unit="submissions", amount=5,
                            category="observed", scope="campaign", source="fixture"))
        self.assertEqual(self.store.dispatch("check", "campaign", deepcopy(check)), original)

    def test_identical_concurrent_writes_are_idempotent_and_restart_safe(self):
        self.create()
        usage = dict(id="one", unit="submissions", amount=1, category="observed", scope="campaign", source="fixture")
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: CampaignStore(self.db).dispatch("usage", "campaign", usage), range(8)))
        self.assertEqual(sum(r["recorded"] for r in results), 1)
        restarted = CampaignStore(self.db).dispatch("report", "campaign")
        self.assertEqual(len(restarted["usage"]), 1)
        self.assertEqual(restarted["resource_summary"]["submissions"]["observed|campaign"]["amount"], 1)

    def test_conflicting_event_id_does_not_overwrite_evidence(self):
        self.create()
        with self.assertRaises(ValueError):
            self.store.dispatch("observation", "campaign", observation("new", "candidate", 999))
        self.assertEqual(self.comparison(self.report())["candidate_value"], 2)

    def test_freeze_survives_new_evidence_and_external_mutation(self):
        self.create()
        request = dict(id="frozen", candidate_ids=["candidate"], rationale="fixture", stopping_reason="test")
        original = self.store.dispatch("freeze", "campaign", request)
        expected = deepcopy(original)
        original["snapshot"]["task"]["version"] = "mutated outside store"
        self.store.dispatch("observation", "campaign", observation("later", "candidate", 999))
        recovered = CampaignStore(self.db).dispatch("freeze", "campaign", request)
        self.assertEqual(recovered, expected)
        self.assertEqual(recovered["digest"], digest(recovered["snapshot"]))

    def test_session_cannot_be_silently_reassigned_or_detached_elsewhere(self):
        self.create()
        self.create(cid="other")
        self.store.dispatch("attach", "campaign", {"session_id": "session"})
        for operation in ("attach", "detach"):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                self.store.dispatch(operation, "other", {"session_id": "session"})
        self.assertEqual(self.report()["sessions"], ["session"])
        self.store.dispatch("detach", "campaign", {"session_id": "session"})
        self.store.dispatch("attach", "other", {"session_id": "session"})

    def test_host_session_mutation_of_other_campaign_is_not_silent(self):
        from leadopt_env.plugin import register
        self.create()
        self.create(cid="other")
        self.store.dispatch("attach", "campaign", {"session_id": "session"})
        database_path = str(self.db)

        class Context:
            def get_config(self, name, default=None):
                return database_path if name == "db_path" else default

            def register_tool(self, **kwargs):
                self.handler = kwargs["handler"]

            def register_skill(self, *args, **kwargs):
                pass

            def register_system_prompt_section(self, *args, **kwargs):
                pass

        context = Context()
        register(context)
        response = json.loads(context.handler(dict(operation="candidate", campaign_id="other",
                                                  payload=candidate("new")), session_id="session"))
        codes = {w["code"] for w in response.get("warnings", [])}
        self.assertTrue(response.get("error") or "session_campaign_mismatch" in codes,
                        "A bound session should not silently write a different active campaign")

    def test_unknown_usage_never_becomes_zero(self):
        self.create()
        self.store.dispatch("usage", "campaign", dict(id="unknown", unit="submissions", amount=None,
                            category="unknown", scope="campaign", source="fixture"))
        report = self.report()
        self.assertIsNone(report["resource_summary"]["submissions"]["unknown|campaign"]["amount"])
        self.assertIn("usage_incomplete", {w["code"] for w in report["warnings"]})


if __name__ == "__main__":
    unittest.main()
