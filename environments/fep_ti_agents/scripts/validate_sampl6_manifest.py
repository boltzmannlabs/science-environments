#!/usr/bin/env python3
"""Validate the bounded SAMPL6 benchmark manifest without downloading data."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
manifest = json.loads((ROOT / "benchmark/sampl6/manifest.json").read_text())
assert len(manifest["systems"]) == 2
assert {s["id"] for s in manifest["systems"]} == {"SAMPL6-OA-G3", "SAMPL6-OA-G6"}
assert manifest["relative_target"]["experimental_delta_delta_g_kcal_mol"] == 0.21
assert len(manifest["fault_injection_cases"]) == 12
assert all(s["complex_structure_url"].startswith("https://raw.githubusercontent.com/") for s in manifest["systems"])
print("PASS: SAMPL6 OA-G3/OA-G6 manifest, reference values, and 12 fault cases")
