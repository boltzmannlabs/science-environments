# Acceptance and validation plan

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory (stdlib only). It records actual results to [validation.json](validation.json) for:

- Required package files, config/task example duplication, and local Markdown links.
- JSON Schema well-formedness for the requirement-brief and candidate contracts; both example briefs validate against the brief schema.
- `environment.yaml` invariants: frozen-threshold file exists and carries 10 provenance-tagged gates; endpoint blending forbidden; endpoint-blending=forbidden; evidence ceiling correct; review-only/inactive applications present; backlog items listed; known E4e defect recorded.
- Benchmark artifacts parse and their headline numbers match the ENVIRONMENT_SPEC §7 table (Simone 0.7021; HIF1A 0.760/0.7803; TTR ranks #62/#107); PROVENANCE.sha256 rows match the shipped files.
- Runtime scripts import and behave on synthetic fixtures (`test_runtime.py`): immune scanner canonical behaviors (UGUGU motif, clean 19-mer, ≥21-nt class flag, invalid-character rejection); requirement ranking (vetoes, cohort-percentile ordering, perturbation stability fields, seed-distinct panel).

These checks validate this specification package only. They do not validate external backends, model predictions, database access or biological efficacy.

## Scientific validation status

- Component-level backend validation (11/12 pass; live integration micro-run reproducing a known candidate's values exactly; E4e RNAhybrid defect documented) was executed in the source workspace on 2026-11-04 and is summarized in [STATUS](../STATUS.md).
- Computational benchmarks on public data are included in [benchmark/](../benchmark/) with no-tuning attestation; they are not biological validation.
- For repository release: link the contribution issue and complete the applicable PR/review process; owner/reviewers currently pending.
