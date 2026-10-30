import json
from pathlib import Path

def test_sampl6_manifest_has_pinned_pair_and_fault_cases():
    root = Path(__file__).parents[1]
    data = json.loads((root / "benchmark/sampl6/manifest.json").read_text())
    assert len(data["systems"]) == 2
    assert data["relative_target"]["experimental_delta_delta_g_kcal_mol"] == 0.21
    assert len(data["fault_injection_cases"]) == 12
