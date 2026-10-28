# MD agent results

This directory contains versioned execution evidence, not claims that every
specialist is scientifically qualified.

- `core_openmm/`: CUDA water-box reference repeats.
- `real_system_smoke/`: derived PDB repairs and bounded preparation checks.
- `real_system_production/`: bounded CUDA runs on public real-system inputs.
- `benzamidine_parameterization/`: AmberTools GAFF2/AM1-BCC, TIP3P/PME,
  counterion and trypsin–benzamidine evidence.
- `agent_harness.json` and `agent_qualification_report.md`: per-agent adapter
  and independent-evaluator outcomes.

Run from the environment directory:

```bash
python runtime/controller.py --live
python tests/validate_spec.py
python -m pytest -q tests
```

`PASS` is reserved for independently supported evidence. `REVIEW` means the
adapter ran but the required production trajectory, reference comparison,
sampling, recovery, or provenance evidence is incomplete.
