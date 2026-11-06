"""Synthetic fixtures only: passing checks do not certify chemical feasibility."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from impurity_env.audit import audit_export, audit_file


def synthetic_export(product="CCO", precursor="CC"):
    return {"top0": {"path": {"id": 0, "smile": product, "children": [
        {"id": 1, "smile": product, "reaction_name": "synthetic fixture only", "children": [
            {"id": 2, "smile": precursor, "children": [], "building_block": "True"}],
         "uspto_link": [], "procedure": ["", ""]}]}}}


class AuditFixtureTests(unittest.TestCase):
    def test_synthetic_missing_element_and_evidence(self):
        r = audit_export(synthetic_export(), "CCO", "fixture.json")
        self.assertEqual(r["route_count"], 1)
        route = r["routes"][0]
        self.assertTrue(route["root_matches_supplied_target"])
        self.assertEqual(route["steps"][0]["missing_heavy_element_source_in_listed_inputs"], {"O": 1})
        self.assertIn("MISSING_ELEMENT_SOURCE_IN_LISTED_INPUTS", route["flags"])
        self.assertIn("NO_TRACEABLE_STEP_CITATION", route["flags"])
        self.assertIn("NO_PROCEDURE_TEXT", route["flags"])
        self.assertEqual(route["decision"], "Hold pending evidence")

    def test_mismatch_is_not_validated(self):
        route = audit_export(synthetic_export(), "CC", "fixture.json")["routes"][0]
        self.assertFalse(route["root_matches_supplied_target"])
        self.assertIn("ROOT_SMILES_MISMATCH", route["flags"])

    def test_invalid_structure_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_export(synthetic_export(), "not a SMILES")

    def test_missing_or_malformed_export_fails_closed(self):
        for value in ({}, {"top0": {"path": {"children": "not a list"}}}, {"top0": {}}, {"top0": []}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit_export(value, "CCO")

    def test_readonly_and_source_basename(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "private_example.json"
            before = json.dumps(synthetic_export())
            source.write_text(before, encoding="utf-8")
            result = audit_file(source, "CCO")
            self.assertEqual(source.read_text(encoding="utf-8"), before)
            self.assertEqual(result["source_basename"], source.name)
            self.assertNotIn(directory, json.dumps(result))


if __name__ == "__main__":
    unittest.main()
