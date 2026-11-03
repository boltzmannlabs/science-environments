"""Monoclonal-antibody testing-criteria tests.

These tests encode the general monoclonal-antibody testing program that applies when a
reference antibody and a target antigen are supplied: identity/lineage, physicochemical
characterization, framework preservation, structural confidence, the non-interchangeable
binding-endpoint hierarchy (predicted energy vs Kd vs kinetics vs ELISA EC50 vs
neutralization vs ADE), specificity, the developability panel including standard sequence
liabilities, immunogenicity, and qualification semantics.

The named computational services (Stability-Binding DDG, PRODIGY, ipSAE) are treated as
secondary implementation detail: the tests assert that the general criteria hold for both
task variants and that naming a service never relaxes a criterion.

These assertions check documentation and catalog declarations. They do not implement
sequence-liability screening or establish scientific validity.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
TEST_SUITE = ROOT / "tests/monoclonal_antibody_with_reference"
GENERAL = ROOT / "tasks/monoclonal_reference/denv_antibody_001.md"
TOOL_SPECIFIC = ROOT / "tasks/monoclonal_reference/denv_antibody_001_tools.md"
TEST_PLAN = TEST_SUITE / "MONOCLONAL_ANTIBODY_TEST_CASES.md"
METRIC_CATALOG = ROOT / "config/shared/metric-catalog.json"


def _norm(text: str) -> str:
    """Collapse whitespace and case so prose checks survive markdown soft-wrapping."""
    return re.sub(r"\s+", " ", text).strip().lower()


# General monoclonal-antibody testing criteria, mapped to the phrases each task variant must
# state. A criterion present in one variant must be present in the other (variant parity).
MAB_CRITERIA_PHRASES = (
    # Target and reference identity (reference antibody + target antigen scenario)
    "Dengue virus serotype 2, DENV-2",
    "Domain III, EDIII",
    "DV87.1",
    "Complete, correctly paired reference heavy and light chains",
    "sequence-to-structure mapping",
    "The supplied, verified EDIII annotation; do not guess residue numbering",
    # Lineage and pairing
    "Preserve the reference framework, chain pairing, and declared construct format",
    "unique candidate IDs",
    "Reject malformed or duplicate pairs",
    # Structure
    "predicted fold/complex confidence, local uncertainty, and coordinate integrity",
    "Keep local structural confidence separate from interface confidence",
    # Binding: endpoint hierarchy must be distinguished, never converted
    "predicted binding energy, measured Kd, ELISA binding EC50, and neutralization potency",
    "do not establish measured affinity",
    "Antigen–antibody interface evidence must not be replaced by heavy/light-chain interface evidence",
    # Developability as separate groups
    "stability, aggregation, solubility, expression-related liabilities, polyreactivity, and immunogenicity indicators separately",
    # Dynamics (conditional)
    "numerical structural deviations, residue fluctuations, and interface persistence",
    # Qualification semantics
    "pass every mandatory rule in the frozen evaluation protocol",
    "`PASS`, `FAIL`, and `UNRESOLVED`",
    "`NO_QUALIFYING_DESIGNS` from `INCOMPLETE`",
    "never fill the shortlist with unresolved or failed candidates",
    # Output contract
    "`designed_sequences.fasta`",
    "`metrics.json`",
    "`shortlist.csv`",
    "`report.md`",
    ">candidate_id|H",
    ">candidate_id|L",
    # Preflight semantics
    "`NEEDS_INPUT` or `PROTOCOL_REQUIRED`",
    # Frozen cutoff and evaluation integrity
    "2024-09-01",
    "keep historical candidate rankings and experimental outcomes hidden",
)

# General mAb testing criteria the test plan itself must document (method-neutral language).
PLAN_CRITERIA_PHRASES = (
    "reference antibody and a target antigen are given",
    "Identity and lineage",
    "Physicochemical characterization",
    "Framework preservation and permitted edits",
    "Structural confidence (fold and interface, kept separate)",
    "the non-interchangeable endpoint hierarchy",
    "Equilibrium affinity (Kd)",
    "Binding kinetics (kon/koff)",
    "Binding EC50 (ELISA)",
    "Neutralization potency (e.g., PRNT/FRNT IC50)",
    "ADE risk (antibody-dependent enhancement)",
    "Specificity, cross-reactivity, and polyreactivity",
    "Developability panel",
    "Asn deamidation (NG, N-S/T)",
    "Asp isomerization (DG, D-S/T)",
    "Met/Trp oxidation",
    "N-glycosylation sequon (N-X-S/T)",
    "unpaired cysteines",
    "Immunogenicity and safety indicators",
    "Dynamics (conditional)",
    "Qualification, ranking, and output integrity",
    "ICH Q6B",
    "WHO",
    "reference leakage",
    "does not mean a designed antibody binds",
    "antibody-dependent enhancement",
    "neutralizes dengue virus",
)


class TaskCriteriaTests(unittest.TestCase):
    """Both task variants must state the general monoclonal-antibody testing criteria."""

    @classmethod
    def setUpClass(cls):
        cls.general = GENERAL.read_text()
        cls.specific = TOOL_SPECIFIC.read_text()

    def test_both_variants_state_every_general_mab_testing_criterion(self):
        for text in (self.general, self.specific):
            for phrase in MAB_CRITERIA_PHRASES:
                self.assertIn(phrase, text, f"Missing criterion: {phrase}")


    def test_capability_sections_do_not_replace_scientific_criteria(self):
        for text in (self.general, self.specific):
            self.assertIn("## Computational Tool Capabilities", text)
            self.assertIn("## Evaluation Metrics", text)
            self.assertIn("Record unavailable capabilities", text)

    def test_both_variants_keep_predicted_and_measured_endpoints_apart(self):
        for text in (self.general, self.specific):
            self.assertIn(
                "Distinguish predicted binding energy, measured Kd, ELISA binding EC50, and neutralization potency",
                text)
            self.assertIn("Computational predictions do not establish biological validity", text)

    def test_both_variants_require_all_mandatory_rules_to_pass(self):
        for text in (self.general, self.specific):
            self.assertIn("qualification requires every mandatory rule to pass", text)
            self.assertIn(
                "Missing or failed mandatory evidence cannot be compensated by an unrelated favorable score",
                text)


class TestPlanCriteriaTests(unittest.TestCase):
    """The test plan must document the full general mAb testing program."""

    @classmethod
    def setUpClass(cls):
        cls.plan = TEST_PLAN.read_text()
        cls.plan_norm = _norm(cls.plan)

    def test_plan_covers_the_reference_antibody_plus_target_antigen_scenario(self):
        for phrase in PLAN_CRITERIA_PHRASES:
            self.assertIn(_norm(phrase), self.plan_norm, f"Missing plan criterion: {phrase}")

    def test_plan_binding_endpoint_hierarchy_is_complete_and_ordered(self):
        # The hierarchy rows must appear in the scientific order: predicted energy,
        # predicted interface confidence, Kd, kinetics, ELISA EC50, neutralization, ADE.
        anchors = (
            "Predicted interaction energetics",
            "Predicted interface confidence",
            "Equilibrium affinity (Kd)",
            "Binding kinetics (kon/koff)",
            "Binding EC50 (ELISA)",
            "Neutralization potency (e.g., PRNT/FRNT IC50)",
            "ADE risk (antibody-dependent enhancement)",
        )
        position = -1
        for anchor in anchors:
            next_position = self.plan_norm.find(_norm(anchor))
            self.assertNotEqual(next_position, -1, f"Missing endpoint row: {anchor}")
            self.assertGreater(next_position, position, f"Endpoint order broken at: {anchor}")
            position = next_position

    def test_plan_developability_panel_has_all_seven_groups(self):
        for group in ("Stability", "Chemical liabilities", "Aggregation", "Solubility",
                      "Expression", "Polyreactivity", "Immunogenicity"):
            match = re.search(rf"^\| {re.escape(group)} \|", self.plan, re.M)
            self.assertIsNotNone(match, f"Missing developability group row: {group}")

    def test_plan_keeps_tools_secondary_to_criteria(self):
        # Naming a service must never relax a testing criterion: the plan states this
        # invariant, and the criteria sections themselves are method-neutral.
        self.assertIn("naming a service never relaxes a testing criterion", self.plan_norm)
        self.assertIn("no criterion may be skipped because another criterion looks favorable",
                      self.plan_norm)

    def test_plan_case_matrix_is_complete_sequential_and_unique(self):
        case_ids = re.findall(r"\| (MAB-\d{3}) \|", self.plan)
        self.assertEqual(len(case_ids), len(set(case_ids)), "Duplicate case IDs")
        self.assertEqual(case_ids, [f"MAB-{number:03d}" for number in range(1, len(case_ids) + 1)],
                         "Case IDs must be sequential from MAB-001")
        self.assertGreaterEqual(len(case_ids), 37, "Case matrix must cover the full criteria set")

    def test_plan_covers_both_task_variants(self):
        self.assertIn("denv_antibody_001.md", self.plan)
        self.assertIn("denv_antibody_001_tools.md", self.plan)
        self.assertIn("same antigen, reference antibody", self.plan)
        self.assertIn("capability block is the only permitted", self.plan)

    def test_plan_states_the_scientific_claim_boundary(self):
        for phrase in ("It does not mean a designed antibody binds DENV-2 EDIII",
                       "neutralizes dengue virus",
                       "avoids antibody-dependent enhancement",
                       "require appropriate experimental evidence"):
            self.assertIn(_norm(phrase), self.plan_norm, f"Missing boundary phrase: {phrase}")


class MetricCatalogCriteriaTests(unittest.TestCase):
    """The metric catalog must cover the general mAb testing criteria vocabulary."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(METRIC_CATALOG.read_text())
        cls.metrics = {item["metric_id"]: item for item in cls.catalog["metrics"]}

    def test_catalog_covers_structure_interface_and_binding_criteria(self):
        for metric_id in ("plddt", "iptm", "ipsae", "interface_buried_area",
                          "interface_contact_count", "prodigy_binding_energy"):
            self.assertIn(metric_id, self.metrics, f"Missing metric: {metric_id}")
        self.assertEqual(self.metrics["iptm"]["scope"], "antigen_antibody")
        self.assertEqual(self.metrics["plddt"]["scope"], "antibody")

    def test_catalog_covers_developability_criteria(self):
        for metric_id in ("stabddg_delta_delta_g", "aggregation_risk_score",
                          "solubility_prediction", "expression_prediction",
                          "polyreactivity_prediction", "immunogenicity_prediction",
                          "cdr_surface_hydrophobicity", "cdr_positive_charge",
                          "cdr_negative_charge", "paired_surface_charge_asymmetry",
                          "h_cdr3_length"):
            self.assertIn(metric_id, self.metrics, f"Missing developability metric: {metric_id}")

    def test_catalog_covers_measured_binding_endpoints(self):
        for metric_id in ("measured_kd", "measured_kon", "measured_koff",
                          "measured_elisa_ec50", "measured_neutralization_ic50"):
            self.assertIn(metric_id, self.metrics, f"Missing measured endpoint metric: {metric_id}")

    def test_catalog_keeps_endpoints_non_interchangeable(self):
        endpoint_ids = {item["endpoint"] for item in self.catalog["noninterchangeable_endpoints"]}
        self.assertEqual(endpoint_ids, {
            "equilibrium_dissociation_constant", "ELISA_binding_EC50",
            "viral_neutralization_potency", "antibody_dependent_enhancement_risk"})
        by_endpoint = {item["endpoint"]: item for item in self.catalog["noninterchangeable_endpoints"]}
        self.assertIn("predicted_binding_energy",
                      by_endpoint["equilibrium_dissociation_constant"]["cannot_be_inferred_from"])
        self.assertIn("target_binding_prediction",
                      by_endpoint["viral_neutralization_potency"]["cannot_be_inferred_from"])
        self.assertIn("EDIII_binding_prediction",
                      by_endpoint["antibody_dependent_enhancement_risk"]["cannot_be_inferred_from"])

    def test_catalog_covers_dynamics_criteria(self):
        for metric_id in ("trajectory_rmsd", "trajectory_rmsf", "interface_contact_persistence"):
            self.assertIn(metric_id, self.metrics, f"Missing dynamics metric: {metric_id}")
            self.assertEqual(self.metrics[metric_id]["scope"], "antigen_antibody")


class OutputContractCriteriaTests(unittest.TestCase):
    """Output bundle criteria: FASTA/CSV/metrics/report must be stated in both variants."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {name: path.read_text() for name, path in
                     (("general", GENERAL), ("tool_specific", TOOL_SPECIFIC))}

    def test_output_files_and_headers_are_declared(self):
        for text in self.texts.values():
            for phrase in ("**Format:** `antibody_design_bundle`",
                           "designed_sequences.fasta", "metrics.json", "shortlist.csv",
                           "report.md", ">candidate_id|H", ">candidate_id|L",
                           "`rank,candidate_id,sequence_sha256`", "SHA-256"):
                self.assertIn(phrase, text, f"Missing output contract element: {phrase}")

    def test_reference_is_excluded_from_shortlist_outputs(self):
        for text in self.texts.values():
            self.assertIn("the reference cannot appear as a designed candidate", text)
            self.assertIn("Reference results belong in `metrics.json`", text)

    def test_status_semantics_are_declared(self):
        for text in self.texts.values():
            for phrase in ("`NO_QUALIFYING_DESIGNS`", "`INCOMPLETE`", "`NEEDS_INPUT`",
                           "`PROTOCOL_REQUIRED`"):
                self.assertIn(phrase, text, f"Missing status: {phrase}")

    def test_empty_shortlist_semantics_are_declared(self):
        for text in self.texts.values():
            self.assertIn("A completed negative result has an empty FASTA and a header-only shortlist", text)


if __name__ == "__main__":
    unittest.main()
