# Acceptance and Validation Plan

The detailed scientific and contract test matrix for the supplied DENV-2 EDIII antigen and DV87.1 reference antibody is in [MONOCLONAL_ANTIBODY_TEST_CASES.md](MONOCLONAL_ANTIBODY_TEST_CASES.md). It applies identically to `denv_antibody_001.md` and `denv_antibody_001_tools.md`; the presence of the named-method section cannot change biological inputs, evidence requirements, thresholds, budget, ranking, or expected outputs.

## Package checks

Run `python3 tests/validate_spec.py` from the environment directory. The generated report records file presence, schema validity, task-variant equivalence, output/document links, YAML dependency order, and the result of the behavioral test suite.

The validator and tests check the following contract behaviors:

- Missing target construct, reference chains, or sequence artifacts blocks preflight.
- A protocol must be qualified, use immutable revisions, include current evidence artifacts, and cover every mandatory rule group.
- When the request cutoff is set, a method released afterward is rejected.
- Target-binding rules and metrics require antigen–antibody scope.
- Missing metric values remain `null` and `UNRESOLVED`; a claimed `PASS` with no value or artifact is rejected.
- Metric evidence must match the candidate sequence hash and exact rule units, scale, scope, and method.
- Candidate pairs are unique, directly traceable to the reference, and keep chain pairing intact.
- A ranked shortlist includes eligible candidates only and cannot include DV87.1.
- The paired FASTA, ordered CSV, requested count, status, artifacts, and resource use must agree.
- Synthetic fixtures are rejected by ordinary result validation unless an explicit test-only flag is set.
- The tool-free task contains no named method; the tool-specific task names only the approved services; all antigen, reference-antibody, scientific, budget, evaluation, and output requirements are otherwise identical.
- Both task variants pass the same complete-input preflight and fail on the same missing antigen or reference-antibody inputs.
- The tool-specific protocol maps Stability-Binding DDG, PRODIGY, and ipSAE to their declared evidence roles and rejects legacy StabDDG/Boltz2 naming.
- The monoclonal-antibody test plan documents the general mAb testing criteria applied when a reference antibody and target antigen are given — identity/lineage, physicochemical characterization, framework preservation, fold-versus-interface structure, the non-interchangeable binding endpoint hierarchy (predicted energy, Kd, kon/koff, ELISA EC50, neutralization, ADE), specificity, the developability panel including sequence liabilities, and immunogenicity — and `tests/test_mab_testing_criteria.py` verifies those criteria against both task variants.

Passing these checks establishes consistency of the specification and integrity of declared files. It does not reproduce molecular predictions, verify a target's biological identity, establish binding, or validate a therapeutic claim.

## Required before scientific execution

1. Supply the exact DENV-2 strain, sequence, target construct, structural coordinates, antigen chain, binding-region mapping, and residue-numbering relationship.
2. Supply DV87.1 heavy/light sequences, declared molecular format, chain identities, antibody numbering scheme, and framework/CDR annotations.
3. Resolve the candidate sequence/sample crosswalk before comparing any historical experimental value.
4. Implement and verify an adapter for each claimed capability, with a pinned version/model, input/output contract, availability evidence, and cutoff eligibility.
5. Resolve unspecified docking, developability, and dynamics implementations; verify applicability, metric scale, calibration, and artifacts.
6. Freeze scientifically justified thresholds, ranking, budget, and missing-evidence rules before unblinding historical results.
7. Validate predicted candidates against withheld, nonredundant antibody–antigen cases and report performance by task difficulty; use an independent frozen evaluator.
8. Obtain antibody-science and software review before changing maturity beyond Specification.

## Required end-to-end scenarios

| Scenario | Expected behavior |
| --- | --- |
| Incomplete antigen or reference | `NEEDS_INPUT`; do not claim a run |
| Unqualified or cutoff-ineligible method lock | `PROTOCOL_REQUIRED` |
| Target/chain or sequence/structure mapping conflict | Stop dependent stages and preserve the specific failure |
| VH/VL pairing changes or duplicate candidate | Reject candidate and retain the audit record |
| Only monomer structure confidence is available | Leave target-interface rule `UNRESOLVED` |
| Interface metric covers VH–VL only | Reject it as evidence for antigen binding |
| Candidate sequence changes after scoring | Require fresh sequence-bound evidence |
| Binding score passes, required developability rule fails | Candidate does not qualify |
| Missing or uncalibrated metric | `UNRESOLVED`; do not substitute zero or a passing value |
| Budget expires during a required stage | `INCOMPLETE` unless eligible candidates already form a shorter `PARTIAL` shortlist |
| Completed evaluation returns zero candidates | `NO_QUALIFYING_DESIGNS` only when every assessed candidate has a verified required failure |
| EC50 has no verified sample/sequence mapping | Keep it unassigned; do not use it for candidate ranking |
| Predicted binding is presented as measured Kd, EC50, neutralization, or ADE safety | Reject the claim; endpoints are non-interchangeable and DENV functional endpoints need assay evidence |
| Prediction is presented as neutralization or clinical performance | Reject the claim; those endpoints were not measured |

## Scientific test boundary

Unit tests use visibly synthetic strings and files to exercise software control flow only. Never cite them as antibody sequences, structures, or model outputs. A scientifically valid fixture requires independently verified biological inputs and reviewed expected results.
