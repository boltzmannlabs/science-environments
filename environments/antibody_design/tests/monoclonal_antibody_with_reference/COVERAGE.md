# Reference-guided monoclonal antibody coverage and gaps

## Scope

This scenario suite covers one reusable task: a supplied antigen plus a supplied paired-chain monoclonal reference antibody. Its six objective labels share that reference requirement. The general and tool-specific DENV prompts are two versions of one example, not additional biological tasks. Target-only and bispecific tasks remain under `tasks/` and have separate configuration profiles. Shared checks in `../test_configurations.py` validate their declarations; no scientific design/assessment behavior is tested. This suite's reference-only preflight and bundle validator rejects those other modes.

## What the automated checks prove

| Suite | Coverage | Limit |
| --- | --- | --- |
| `test_reference_guided.py` | Generic public preflight and bundle validation; mandatory reference; rejection of excluded modes/formats; reference files/hashes; protocol evidence groups; chain IDs and numbering; objective-specific requirements; candidate budget; reference records and lineage; sequence-artifact matching; incomplete baseline; manifest/seed/isolation; FASTA/CSV consistency; synthetic-result rejection; CLI missing-input status. | Synthetic file and control-flow checks, not molecular evaluation. |
| `test_denv_reference.py` | Existing DENV-profile regressions for input readiness, protocol cutoff, evidence scope, stale/missing metrics, duplicate pairs, lineage, resource limits, ranking/export consistency, and incomplete/negative results. | Profile-specific contract checks; passing fixtures do not validate supplied biological identities. |
| `test_task_variants.py` | DENV prompt parity, method neutrality, and test-plan consistency. | Documentation checks. |
| `test_mab_testing_criteria.py` | Declared mAb criteria, endpoint separation, metric catalog, and output requirements. | Documentation/catalog assertions, not implemented assays or property calculations. |
| `../test_configurations.py` | All task profiles; local schema references; family/variant routing; budget, identifier, response, and artifact-integrity checks. | Synthetic declarations only; no design or scientific grading. |
| `../validate_spec.py` | Registered scope, schema syntax, examples, file/link presence, dependency order, and execution of the test suites. | Structural checks; the check count changes when document links change. |

Duplicate prompt-parity and test-plan assertions have one owning test module. All scenario tests and shared fixtures are in `monoclonal_antibody_with_reference/`. Monoclonal request/result validation and acceptance documentation are in this same folder. Shared configuration checks and package checks remain directly under `tests/`; generated reports live in `results/`.

The former sequence-liability helper tests were removed because they tested code defined only inside the test file. They did not prove that the environment implements liability screening. No scientific capability was removed from the runtime.

## Drawbacks still blocking scientific readiness

| Gap | Consequence | Evidence needed to close it |
| --- | --- | --- |
| No scientific executor or qualified adapters | The package cannot produce a design run by itself. | An external executor with pinned adapters and an independently reviewed integration run. |
| No complete verified biological example | The supplied examples stop at `NEEDS_INPUT`. | User-supplied target/reference artifacts, identity review, and a compatible qualified protocol. Placeholder hashes are not inputs. |
| Edit constraints are largely declarations | The validator checks reference lineage and reported rule evidence but does not independently calculate allowed-position compliance, mutation counts, or framework preservation from annotations. | A reviewed annotation contract and independent positive/negative conformance evidence. |
| Identity and structure semantics are not verified | Hashes and sequence syntax can pass while construct identity, chain mapping, or coordinates are wrong. | Independent biological and structural checks with reviewed fixtures. |
| Qualification is asserted through metadata and artifacts | `qualified` and `adapter_verified` flags plus accessible files do not establish scientific accuracy, calibration, or provenance authenticity. | Reviewed qualification evidence, justified thresholds, and performance on held-out cases. |
| No direct reference-improvement calculation | Passing absolute protocol rules does not demonstrate improvement over the reference. | A predefined, scientifically justified comparison and uncertainty analysis for the selected objective. |
| Generic coverage is still bounded | Request/result tests do not cover every objective, assay-record combination, failure status, or external execution path. | Additional independent contract and integration cases as each capability is introduced. |
| No experimental outcome evidence | Computational qualification cannot establish binding, developability, function, or safety. | Independently sourced experimental evidence matched to the exact antibody and target. |

`CONTRACT_READY` means the supplied declarations and files passed contract checks. `QUALIFIED` means the recorded results passed the declared rules. Neither status means the antibody or method has been scientifically validated.

## First-release acceptance boundary

Keep reference-guided scientific scenario tests focused on the reference contract; validate additional families through their dedicated config profiles; preserve paired-chain identity and traceable evidence; report missing work honestly. Use the current suites as software acceptance evidence. Keep maturity at **Specification** until scientific inputs, method qualification, and an independently reviewed end-to-end run exist.
