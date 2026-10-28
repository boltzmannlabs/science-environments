import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_four_cuda_core_repeats_are_complete_and_finite():
    results = []
    for repeat in range(1, 5):
        path = ROOT / "results" / "core_openmm" / f"repeat_{repeat}.json"
        result = json.loads(path.read_text())
        results.append(result)
        assert result["status"] == "PASS"
        assert result["engine"] == "OpenMM"
        assert result["engine_version"] == "8.2"
        assert result["platform_name"] == "CUDA"
        assert result["atom_count"] == 1482
        assert result["trajectory_frames"] == 10
        assert result["trajectory_sha256"]
        assert result["log_sha256"]
        assert result["minimized_potential_kj_mol"] == result["minimized_potential_kj_mol"]
        assert result["final_potential_kj_mol"] == result["final_potential_kj_mol"]
    assert len({r["request_sha256"] for r in results}) == 1
    assert len({r["structure_sha256"] for r in results}) == 1

def test_core_packet_declares_runtime_and_acceptance():
    packet = json.loads((ROOT / "inputs/MD-CORE-001-water-box/task.json").read_text())
    assert packet["runtime"]["engine"] == "OpenMM"
    assert packet["runtime"]["production_steps"] == 1000
    assert packet["runtime"]["repeat_ids"] == [1, 2, 3, 4]
    assert packet["acceptance"]["atom_count"] == 1482
