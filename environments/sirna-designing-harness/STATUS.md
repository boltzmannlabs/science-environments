# siRNA Designing Harness — status

## Achieved technical milestone

**Technical component: Implemented and tested.** The environment now provides executable sequence/evidence checks and technical property reporting, alongside the Agent Scientist scientific workflow contracts.

**Recorded KRAS14 result: 14 of14 candidates passed the declared technical gates.** The portable replay retains each pair, predicted/calculated properties, source-job identity, earlier-job comparison and review flags. See [technical report](results/technical_validation_KRAS14/technical_report.md).

**Repository lifecycle: In Progress.** New-host scientific backend deployment and maintainer integration/review are separate remaining work; they do not negate the completed technical component.

## Delivered scope

- Required environment/research layout, specifications, configuration, task contracts and linked sources.
- Executable `technical-report` and `verify-technical-case` commands, standard library only.
- Seven mandatory technical categories with explicit failure/missing precedence.
- Bounded real KRAS14 recorded evidence, four exact reference views and a distinct earlier-job comparison.
- Success-first candidate property reporting with raw native gates and flags preserved.
- Original workflow skill/helpers and unchanged85-file historical KRAS snapshot.
- Versioned prior receipts and superseded report layout under `results/history/20261029T100703Z/`.

## Actual validation

Current final implementation passed **100 software tests on Python3.14.7 and100 on Python3.13.7**:

| Suite | Passed per interpreter |
|---|---:|
| Existing environment/contract tests |22|
| Dedicated technical-report positive/negative tests |46|
| Original portable helper tests |32|

Both runs also passed project/link/JSON checks, original skill integrity, historical snapshot integrity, new recorded-case integrity and a real CLI report replay returning14 technical passes. The blank deployment template returned its intended explicit missing-configuration blocker. The default run additionally reverified10 original small historical summary/receipt files without writing to them.

Tests cover pairing/output identity, exact reference/coverage mapping, explicit model statuses and numeric bounds, native failed/missing fields, supplemental sequence identity, distinct-job reproducibility, checksums, unsafe paths/symlinks, duplicate data keys/IDs, no-overwrite output, candidate risk preservation and grouped rather than per-candidate repeated scope notes.

Actual evidence: `results/validation_receipt.json`, `results/validation_receipt.python313.json` and named command logs. Each receipt binds the tested implementation/config/task bytes and recorded-case snapshot. The final project manifest/receipt are `results/output_manifest.json` and `results/verification_receipt.json`; verify with `python3 -B tests/seal_contribution.py --verify-only` after sealing.

The earlier54-test project and intermediate97-test update receipts are retained as historical revisions, not current validation claims. Packaging and tests perform zero new scientific generation/inference/folding/screening jobs.

## Reporting scope

Technical validation covers the declared computational checks; biological efficacy, safety and delivery are separate evaluation stages. The current report preserves nine Ridge extrapolation flags, four low passenger-seed source annotations, near-match opportunities, native metadata gaps and the POTS convention limitation. The historical experimental-data audit and mutation arm retain their original scoped outcomes; no historical qualification record is rewritten to obtain the technical pass.

## Contribution governance and licensing

- Current branch: `feat/sirna-technical-validation-environment`.
- Authenticated read-only GitHub issue lookup succeeded; no siRNA-titled issue matched.
- No remote issue/PR, owner/reviewer assignment, commit, push, approval or merge was requested/performed. Local task/PR drafts document the outstanding workflow steps.
- Repository-wide license selection remains pending; the bundled original helper MIT notice is separate.
- No third-party predictor implementation, weights, embeddings, transcriptome indices, raw papers, restricted experimental datasets or credentials are added. Small derived reference views are explicitly included for offline evidence replay.

## Next integration work

1. Create/link a tracking issue with maintainer direction and assign reviewers.
2. Review/merge the focused local contribution through the repository workflow.
3. Configure and validate scientific integrations on each destination host as needed.
4. Define application-specific follow-up evaluation without weakening mandatory technical gates or hiding candidate flags.
