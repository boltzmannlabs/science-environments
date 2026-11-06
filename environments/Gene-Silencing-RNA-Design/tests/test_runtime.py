"""Runtime behavior tests (synthetic fixtures only — never scientific evidence)."""
import importlib.util, inspect, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(os.path.dirname(HERE), "runtime")

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(RUNTIME, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

immune = load("immune_scan")
ranking = load("rank_by_requirements")
explore_mod = load("explore_design")

class TestImmuneScan(unittest.TestCase):
    def test_ugugu_motif_detected(self):
        self.assertTrue(immune.scan("GCAUGUGUGUACGCUAAUCG")["any_tlr7_motif"])

    def test_clean_19mer_no_flags(self):
        r = immune.scan("ACAAAAGCAAAACAGGUCUA")["guide"]
        self.assertFalse(r["UGUGU_tlr7"] or r["U_rich_5prime"] or r["len_ge21_tlr3_class"])

    def test_tlr3_length_class(self):
        self.assertTrue(immune.scan("ACAAAAGCAAAACAGGUCUAGAA")["guide"]["len_ge21_tlr3_class"])

    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):
            immune.scan("ACGB")

    def test_both_strands(self):
        r = immune.scan("ACAAAAGCAAAACAGGUCUA", passenger="GCAUGUGUGUACGCUAAUCG")
        self.assertTrue(r["any_tlr7_motif"], "passenger strand UGUGU must set the flag")

    def test_dna_auto_convert(self):
        r = immune.scan("ACAAAAGCAAAACAGGTCUA")
        self.assertFalse(r["guide"]["UGUGU_tlr7"], "T should be silently converted to U")

class TestRequirementRanking(unittest.TestCase):
    ROWS = [
        {"candidate_id": "a", "guide": "ACAAAAGCAAAACAGGUCUA", "eff_RN.Ai-Predict": 90.0,
         "pots_seed_percentile": 10.0, "seed_tox_viability_avg_human": 80.0,
         "guide_target_duplex_delta_g_kcal_mol": -30.0},
        {"candidate_id": "b", "guide": "UCCUCAGGUGGCUUGUCAG", "eff_RN.Ai-Predict": 60.0,
         "pots_seed_percentile": 50.0, "seed_tox_viability_avg_human": 70.0,
         "guide_target_duplex_delta_g_kcal_mol": -28.0},
        {"candidate_id": "c_ugugu", "guide": "GCAUGUGUGUACGCUAAUCG", "eff_RN.Ai-Predict": 95.0,
         "pots_seed_percentile": 5.0, "seed_tox_viability_avg_human": 85.0,
         "guide_target_duplex_delta_g_kcal_mol": -35.0},
        {"candidate_id": "d_low_rnai", "guide": "GGAAUUUGUAGAAGGGAUA", "eff_RN.Ai-Predict": 40.0,
         "pots_seed_percentile": 80.0, "seed_tox_viability_avg_human": 65.0,
         "guide_target_duplex_delta_g_kcal_mol": -26.0},
    ]
    BRIEF = {"priorities": {"hard_vetoes": ["immune_ugugu"], "weights": {
        "efficacy": .5, "specificity": .2, "immune": .1, "seed_tox": .1, "stability": .1},
        "min_standards": {"rnai": 50}},
        "constraints": {"panel_size": 2, "seed_distinct": True}}
    FLAGS = None  # computed in setUpClass

    @classmethod
    def setUpClass(cls):
        cls.FLAGS = [immune.scan(r["guide"]) for r in cls.ROWS]

    def test_veto_removes_ugugu(self):
        rep = ranking.run(self.ROWS, self.BRIEF, self.FLAGS, "t")
        ids = {c["candidate_id"] for c in rep["panel"]}
        self.assertNotIn("c_ugugu", ids)
        self.assertEqual(rep["n_after_vetoes"], 2)  # a + b survive (d vetoed by rnai<50)

    def test_stability_report_present_and_disclosure(self):
        rep = ranking.run(self.ROWS, self.BRIEF, self.FLAGS, "t")
        self.assertTrue(any(k.startswith("stability_top") for k in rep))
        self.assertIn("not an efficacy estimate", rep["disclosure"])

    def test_panel_respects_size(self):
        rep = ranking.run(self.ROWS, self.BRIEF, self.FLAGS, "t")
        self.assertLessEqual(len(rep["panel"]), 2)

class TestExploreDesign(unittest.TestCase):
    def test_importable(self):
        self.assertTrue(hasattr(explore_mod, "explore"))

    def test_signature_has_target_gene(self):
        sig = inspect.signature(explore_mod.explore)
        self.assertIn("target_gene", sig.parameters,
                      "v1.2.1 scope-explicit E4a requires target_gene parameter")

    def test_signature_required_params(self):
        sig = inspect.signature(explore_mod.explore)
        self.assertIn("pool_path", sig.parameters)
        self.assertIn("transcript_fa", sig.parameters)
        self.assertIn("panel_size", sig.parameters)

if __name__ == "__main__":
    unittest.main()
