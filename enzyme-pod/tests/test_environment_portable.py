"""Stdlib-only clean-install tests; no runtime installation, auth or network."""
import json
from pathlib import Path
import tempfile
import unittest

from enzyme_benchmark.contracts import TaskContract, validate_candidates as core_candidates
from enzyme_environment.demo import demo
from enzyme_environment.policy import Audit,Policy,strict_json,verify_audit
from enzyme_environment.runtime import regular_file
from enzyme_environment.data_views import candidate_index
from enzyme_environment.data_views import compact_scores


class PortableEnvironmentTests(unittest.TestCase):
    def test_shared_benchmark_contract_not_a_duplicate(self):
        from enzyme_environment.inputs import validate_candidates
        self.assertIs(validate_candidates,core_candidates)
        self.assertEqual(TaskContract.__module__,"enzyme_benchmark.contracts")

    def test_duplicate_json_is_not_accepted(self):
        with self.assertRaises(ValueError):strict_json('{"key":1,"key":2}')

    def test_files_must_be_bounded_regular_not_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"input"
            path.write_text("ok")
            self.assertEqual(regular_file(path),b"ok")
            with self.assertRaises(ValueError):regular_file(path,limit=1)
            alias=Path(folder)/"alias"
            alias.symlink_to(path)
            with self.assertRaises(ValueError):regular_file(alias)

    def test_compact_view_retains_identity_and_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            audit=Audit(Path(folder)/"audit")
            try:
                rows=[{"candidate_id":"X","mutation":"A1C","sequences":"CA"}]
                policy=Policy({"candidates":rows},Path(folder)/"result",audit,compact_candidates=True)
                view=policy.tool("benchmark_read",{"dataset":"candidates"})
                self.assertEqual(view["rows"],[{"candidate_id":"X","mutation":"A1C"}])
                self.assertEqual(policy.datasets["candidates"],rows)
                self.assertEqual(len(verify_audit(audit.path)),1)
            finally:audit.close()

    def test_scripted_demo_and_no_output_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"demo"
            report=demo(path)
            self.assertTrue(report["success"])
            self.assertTrue(report["synthetic_only"])
            self.assertFalse(report["native_agent_executed"])
            self.assertEqual(report["model_requests"],0)
            self.assertEqual(report["unique_candidates_scored"],20)
            self.assertEqual(report,json.loads((path/"report.json").read_text()))
            with self.assertRaises(FileExistsError):demo(path)

    def test_index_matrix_retains_all_identity_and_mutation_information(self):
        rows=[{"candidate_id":"X","mutation":"A1C","sequences":"CA"},{"candidate_id":"Y","mutation":"A2D","sequences":"AD"}]
        index=candidate_index(rows)
        self.assertEqual(index["columns"],["candidate_id","mutation"])
        self.assertEqual(index["rows"],[["X","A1C"],["Y","A2D"]])

    def test_score_matrix_is_lossless_without_rounding_or_ledger_loss(self):
        original={"model_id":"synthetic","score_type":"prediction_not_experimental_measurement",
            "rows":[{"candidate_id":"X","predicted_score":0.12345678901234567},{"candidate_id":"Y","predicted_score":-0.0}],
            "accounting":{"unique_candidates_scored":2,"candidate_score_requests":2,"cache_hits":0}}
        view=compact_scores(original)
        restored=[dict(zip(view["row_columns"],row)) for row in view["rows"]]
        self.assertEqual(restored,original["rows"])
        self.assertEqual(view["accounting"],original["accounting"])
        self.assertEqual(view["model_id"],original["model_id"])
        self.assertEqual(view["score_type"],original["score_type"])
        self.assertEqual(len(original["rows"]),2)


if __name__=="__main__":unittest.main()
