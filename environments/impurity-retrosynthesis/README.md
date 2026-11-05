# Impurity Retrosynthesis Evidence Environment

Lifecycle: In Progress — executable input/graph audit and literature benchmark; NOT a validated synthetic route, process, or cost estimator.

Three scoped identity records: ibuprofen EP impurity A (CAS 66622-47-7), ibuprofen EP impurity M (CAS 60057-62-7), and a disputed osimertinib impurity label (CAS 1421373-98-9). Planning objective: 100 g isolated per target, ≥95% purity, INR cost. The target name/CAS mapping for the third is unresolved; never submit it by name alone.

## Supported workflow

1. Obtain an authorized, locally stored platform retrosynthesis JSON export and an independently reviewed target SMILES; **do not publish raw profile-scoped exports or credentials**.
2. Install Python >=3.10 and RDKit in an isolated environment. Tested with Python 3.14 and RDKit 2026.9.1. RDKit is optional for the structural check: without it the CLI stops rather than claiming a connectivity check ran.
3. Run `python -m unittest discover -s tests -v` from this directory; run `python scripts/audit_exports.py --help` for CLI options.
4. Example with your authorized local export: `python scripts/audit_exports.py --input /path/to/your_export.json --target-smiles 'your-reviewed-SMILES' --target-label 'A' --output /path/to/a/new/audit.json`. The `--output` file must not exist; raw input is read-only.
5. Review `results/README.md`, `results/screening_summary.json`, and `results/screening_routes.csv`. Verify atom mapping, exact-substrate precedent, suppliers, purity and safety manually before selecting routes.

This is not an automatic gateway to the Boltzmann API, an agent framework, or a reaction simulation. The original platform jobs were executed through Agent-Sci in an authorized profile, outside this publishable package. No direct API endpoint, secret, account identifier, signature, or private raw result is bundled. The results are derived historical summaries with preserved model route keys `top0...`, not reproducible without the authorized input exports. No isolated experimental yields or INR prices were established.

## Navigation

- [Scientific and software specification](ENVIRONMENT_SPEC.md)
- [Status and blockers](STATUS.md)
- [Models and tools](MODELS_AND_TOOLS.md)
- [Execution task](tasks/README.md)
- [Benchmark and comparison](benchmark/README.md)
- [Validation tests](tests/README.md)
- [Historical results and provenance](results/README.md)
- [Separate research notes](../../research/impurity-retrosynthesis/research-notes.md) and [references](../../research/impurity-retrosynthesis/references.md)

Versioning and publication governance follow the repository [CONTRIBUTING.md](../../CONTRIBUTING.md). An in-progress environment does not imply laboratory readiness.
