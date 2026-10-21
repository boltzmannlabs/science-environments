from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from spe_agents.specialist_value import load_dataset  # noqa: E402
from run_conditional_specialist_qualification import gate  # noqa: E402


MANIFEST = ROOT / "benchmark/specialist_qualification_v1/agent07_improvement_v1/dataset_manifest.json"


def test_agent07_improvement_dataset_is_frozen_and_independent() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    assert len(dataset.cases) == 6
    assert set(case["context"]["independent_chemical_case"] for case in dataset.cases.values()) == {
        "methane",
        "ammonia",
        "ethanol",
    }
    assert dataset.manifest["arms"] == [
        "agent-scientist",
        "agent-scientist-plus-specialist",
        "conditional-specialist",
    ]


def test_conditional_gate_is_targeted_to_agent07() -> None:
    assert gate({"environment_id": "07"}) == (True, "basis-set convergence environment")
    assert gate({"environment_id": "17"}) == (False, "no demonstrated Agent 07 behavior in this case")


def test_agent07_improvement_freeze_hashes_are_intact() -> None:
    freeze_path = ROOT / "benchmark/specialist_qualification_v1/agent07_improvement_v1/PROTOCOL_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    assert all(
        hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        for path, expected in freeze["sha256"].items()
    )
