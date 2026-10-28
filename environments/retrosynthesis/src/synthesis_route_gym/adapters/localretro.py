"""Bounded LocalRetro inference using the existing REBOLT code and checkpoints."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from .common import normalise_result, response, run_worker, validate_request


@dataclass(frozen=True)
class LocalRetroAdapter:
    repo_root: Path | str | None = None
    python_executable: Path | str | None = None
    source_subdir: str = "rebolt_update_opt"
    timeout_seconds: float = 120.0

    def expand(self, target_smiles: str, top_k: int = 10) -> dict:
        try:
            target = validate_request(target_smiles, top_k)
        except ValueError as error:
            return response("error", str(error))
        root = Path(self.repo_root or os.environ.get("REBOLT_ROOT") or Path(__file__).parents[4]).resolve()
        source = root / self.source_subdir / "localretro"
        required = [
            root / "req_data/LocalRetro_boltz_USPTO_MIT.pth",
            root / "req_data/USPTO_MIT/atom_templates.csv",
            root / "req_data/USPTO_MIT/bond_templates.csv",
            root / "req_data/USPTO_MIT/template_infos.csv",
            source / "LocalRetro/default_config.json",
            source / "LocalRetro/Retrosynthesis.py",
        ]
        if any(not p.is_file() for p in required):
            return response("unavailable", "LocalRetro code, checkpoint, or template files are missing.")
        python = self.python_executable or os.environ.get("REBOLT_PYTHON") or sys.executable
        result = run_worker(python, {
            "backend": "localretro", "repo_root": str(root), "source_dir": str(source),
            "target_smiles": target, "top_k": top_k,
        }, self.timeout_seconds)
        return normalise_result(result, "LocalRetro", top_k)
