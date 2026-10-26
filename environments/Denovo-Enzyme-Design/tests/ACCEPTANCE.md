# Acceptance and validation plan

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory. The generated [validation report](specification-validation.json) records actual results for:

- Required package files, local Markdown links and the BioDesignBench-style task sections, with the software-list section replaced by required execution steps.
- JSON Schema well-formedness and example-request validity.
- Request rejection for missing chemistry, invalid count/budget, unsupported controller mode and inconsistent length/count limits.
- Stage order/dependencies: property and fold checks before complex/state/chemistry work.
- Mandatory chemistry, solubility and aggregation groups and no-compensation qualification.
- Bounded reward configuration, positive-weight requirement, held-out policy freezing and chemistry reservation.
- Absence of an implemented/validated status claim or a supplied fabricated qualified profile.

These checks validate this specification package only. They do not validate external URLs, the target repository license, molecular parsing, tool installation, model predictions, RL training or enzyme chemistry.

## Required before implementation can execute a profile

1. Link the contribution issue and complete the required PR/review process. The repository structure, rules and pending-license notice were read on 26 October 2026; this is separate from automated specification validation.
2. Implement the task resolver, adapters, candidate store, scheduler and evaluator; qualify a complete reaction profile with real evidence.
3. Validate actual molecules, stereochemistry, stoichiometry, atom maps and fixed catalytic identity through every format conversion.
4. Enforce profile semantics beyond JSON Schema: unique IDs; valid state/step references; complete state/step coverage; all eight required rule groups represented by required rules; finite values; compatible units/operators; ordered ranges; positive weights summing to one; and valid reward transforms.
5. Verify immutable artifact hashes, complete operation coverage, compatibility of all model components and appropriate data/model/service access.
6. Check requested conditions against supported domains and require explicit resolution of buffer/salt assumptions. Link every user hard target to a qualified evidence rule.

## Required functional tests

| Scenario | Required behavior |
| --- | --- |
| No qualified reaction profile | `PROTOCOL_REQUIRED`; no model-generation job |
| Missing essential user information | `NEEDS_INPUT` with the required clarification |
| Required tool/model unavailable | `BLOCKED`; preserve provenance and explanation |
| Broken fixed catalytic group | Rejection despite high fold/pose confidence |
| Solubility or aggregation failure | Candidate cannot qualify |
| Unsupported predictor domain | Unresolved/profile-required evidence, never automatic PASS |
| Missing state/step or unconverged path | Chemistry remains UNRESOLVED |
| Electronic barrier mislabeled as free energy | Report rejected or corrected using explicit provenance |
| Sequence/structure edit | New candidate identity; affected caches and rewards invalidated |
| Repeated evidence or duplicate job | No duplicate reward or duplicate charging |
| Budget exhaustion / cancellation | Stop dispatch; retain evidence; no gate relaxation |
| RL tries to edit scientific criteria | Invalid action, masked/rejected before dispatch |
| Incomplete or failed candidate | Never included in qualified FASTA |
| Fewer than K qualified candidates | PARTIAL or NO_QUALIFYING_DESIGNS with exact counts |

Use real qualified fixtures for scientific assertions. Synthetic test fixtures may test software control flow but must be labeled and must not be presented as enzyme validation.

## Required scientific and benchmark evidence

Demonstrate the complete pipeline for a supported reaction profile, with qualified chemistry controls and each required property adapter. Verify parameter/state transfer, QM/MM boundaries, transition-state connectivity, uncertainty and applicability. Record method, model, hardware, seed and resource identifiers.

Compare fixed execution, rule-based refinement and frozen RL on predeclared held-out tasks under equal compute. Keep training and evaluation evidence separate and report RL training cost. Measure qualified yield, diversity, failure/unresolved fractions, compute and agreement with measured activity only where appropriate data exist.

No items in these implementation/scientific sections have been executed merely by generating the specification-package report. Environment maturity remains **Specification**.
