# Impurity Retrosynthesis Evidence Environment

Reusable computational screening of retrosynthesis exports against target identity, reaction evidence and process-development requirements. This is an evidence audit, not experimental synthesis validation.

## Quickstart

Use Python >=3.10 and RDKit in an isolated environment. From this environment directory:

```sh
python -m unittest discover -s tests -v
python scripts/verify_publication.py
python scripts/audit_exports.py --help
```

Audit an authorized local export with `scripts/audit_exports.py --input export.json --target-smiles 'reviewed-SMILES' --target-label 'target' --output new-audit.json`. Output must not exist; source files are read-only. No credentials or live backend are required for local auditing. RDKit is required for structural checks.

## Documentation

- [Specification](ENVIRONMENT_SPEC.md): general input/output and evidence gates.
- [Models/tools](MODELS_AND_TOOLS.md): actual capabilities and limits.
- [Status](STATUS.md): software readiness and scientific limitations.
- [Tasks](tasks/README.md), [tests](tests/README.md), [benchmark](benchmark/README.md).
- [Results](results/README.md): case-study status and artifact coverage.
- [Research](../../research/impurity-retrosynthesis/research-notes.md) and [references](../../research/impurity-retrosynthesis/references.md).

Case-study status is kept in results rather than defining the reusable environment by a fixed roster of targets. Racemic ibuprofen is a completed run/literature comparison according to the project owner; it is not the unresolved osimertinib proposal. See the results register for evidence provenance and numerical-data availability.
