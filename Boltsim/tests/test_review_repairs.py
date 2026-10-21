from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from spe_agents import Atom, LocalBoltzmannSPEAdapter, SPERequest
from spe_agents.adapters import UnsupportedCapabilityError


ROOT = Path(__file__).resolve().parents[1]
QMMM_ROOT = Path("/home/boltzmann15/Esther/Esther/boltzmann_api/qmmm")


def test_qmmm_vendored_spe_parser_exports_only_shipped_writer() -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(QMMM_ROOT / "src")
    code = (
        "from boltzmann_api.spe.parsers import "
        "atoms_to_sdf, atoms_to_sdf_with_bonds, result_to_sdf, write_sdf_file; "
        "from boltzmann_api.qmmm.pipeline.system_builder import SystemBuilder; "
        "print(SystemBuilder.__name__)"
    )
    process = subprocess.run(
        [sys.executable, "-c", code],
        cwd=QMMM_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    assert process.stdout.strip() == "SystemBuilder"


def test_local_adapter_accepts_parenthetical_631g_d_alias(tmp_path: Path) -> None:
    adapter = LocalBoltzmannSPEAdapter(tmp_path)
    assert "6-31G(d)" in adapter.capabilities().supported_basis_sets


def test_local_adapter_rejects_charge_multiplicity_parity_before_execution(
    tmp_path: Path,
) -> None:
    adapter = LocalBoltzmannSPEAdapter(tmp_path)
    request = SPERequest(
        task_id="invalid-water-doublet",
        atoms=(
            Atom("O", 0.0, 0.0, 0.0),
            Atom("H", 0.758602, 0.0, 0.504284),
            Atom("H", -0.758602, 0.0, 0.504284),
        ),
        coordinate_unit="angstrom",
        charge=0,
        multiplicity=2,
        method="B3LYP",
        basis="6-31G(d)",
        requested_properties=("total_energy",),
        settings={},
    )
    with pytest.raises(UnsupportedCapabilityError, match="electron-count mismatch"):
        adapter.submit(request)
    assert list(tmp_path.iterdir()) == []


def test_reproducible_review_fixtures_exist() -> None:
    required = (
        "campaign/fixtures/metadata/agent_12_cu_tetrammine.json",
        "campaign/fixtures/metadata/agent_16_2cht_fragment.json",
        "campaign/fixtures/metadata/agent_18_cyclohexane_conformers.json",
        "campaign/models/mace_anicc/model_manifest.json",
        "campaign/reference_benchmark/v1/acceptance_criteria.json",
    )
    for relative in required:
        assert (ROOT / relative).is_file(), relative
