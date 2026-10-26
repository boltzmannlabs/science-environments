# Acceptance and validation plan

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory. The generated [validation report](specification-validation.json) records actual results for:

- Required package files, local Markdown links and the BioDesignBench-style task sections, with the software-list section replaced by required execution steps.
- JSON Schema well-formedness and monomer/homodimer example-request validity.
- Synthetic draft profiles: assembly/copy-count consistency, shared sequence groups, unique chain/site IDs, required interface/state evidence, valid cross-references, state/step/site gate coverage and normalized weights.
- Rejection of unsupported assemblies and explicit request/profile assembly mismatches. Synthetic artifact paths/hashes are not scientific evidence.
- Request rejection for missing chemistry, invalid count/budget, unsupported controller mode, inconsistent length/count limits, and unpaired/invalid protein concentration and basis.
- Stage order/dependencies: property and fold checks before complex/state/chemistry work.
- Mandatory chemistry, solubility and aggregation groups and no-compensation qualification.
- Bounded reward configuration, positive-weight requirement, held-out policy freezing and chemistry reservation.
- Absence of an implemented/validated status claim or a supplied fabricated qualified profile.

These checks validate this specification package only. They do not validate external URLs, the target repository license, molecular parsing, tool installation, model predictions, RL training or enzyme chemistry.

## Required before implementation can execute a profile

1. Link the contribution issue and complete the required PR/review process. The repository structure, rules and pending-license notice were read on 26 October 2026; this is separate from automated specification validation.
2. Implement the task resolver, adapters, candidate store, scheduler and evaluator; qualify a complete reaction profile with real evidence.
3. Validate actual molecules, stereochemistry, stoichiometry, atom maps and fixed catalytic identity through every format conversion.
4. Enforce profile semantics in the runtime, including the subset checked here on synthetic fixtures: unique IDs; valid state/step references; complete state/step coverage; all nine required rule groups represented by required rules; finite values; compatible units/operators; ordered ranges; positive weights summing to one; and valid reward transforms.
5. Verify immutable artifact hashes, complete operation coverage, compatibility of all model components and appropriate data/model/service access.
6. Confirm biological assembly identity, reconstruction operators, chain/atom mapping, identical homodimer sequences and state-specific occupancy against actual files. Qualify the interface/site evaluator and any representative-site equivalence; contract tests do not perform these checks.
7. Check requested conditions against supported domains and resolve relevant buffer/salt, concentration and ligand-occupancy assumptions. Concentration requires its declared basis; omission is unresolved when a required claim depends on it. Link every user hard target to a qualified evidence rule.

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
| Free-energy claim without sampling/convergence and reference-state evidence | UNRESOLVED; stationary-point validation alone cannot establish a free-energy barrier |
| Retained reference scaffold with a new sequence | Label scaffold redesign; do not count it as a newly generated scaffold |
| Low sequence identity or agreement between correlated predictions | Report provenance, alignment coverage and structural similarity; do not infer novelty or activity from these alone |
| Sequence/structure edit | New candidate identity; affected caches and rewards invalidated |
| Repeated evidence or duplicate job | No duplicate reward or duplicate charging |
| Budget exhaustion / cancellation | Stop dispatch; retain evidence; no gate relaxation |
| RL tries to edit scientific criteria | Invalid action, masked/rejected before dispatch |
| Incomplete or failed candidate | Never included in qualified FASTA |
| Fewer than K qualified candidates | PARTIAL or NO_QUALIFYING_DESIGNS with exact counts |

Use real qualified fixtures for scientific assertions. Synthetic test fixtures may test software control flow but must be labeled and must not be presented as enzyme validation.

## Required assembly runtime tests

These tests are acceptance requirements, not completed molecular validation:

| Scenario | Required behavior |
| --- | --- |
| Assembly unspecified | Resolve from biological evidence; never silently choose monomer |
| One-chain asymmetric unit with biological dimer | Reconstruct the recorded biological assembly and preserve transformation provenance |
| Conflicting assembly evidence or unsupported assembly | `PROTOCOL_REQUIRED`; do not launch generation |
| Missing required multichain capability | `BLOCKED` with the capability and affected stage |
| Missing partner or unequal homodimer sequences | Reject actual candidate artifacts; no silent copy/sequence repair without a new candidate |
| Chain-label permutation | Preserve physical equivalence through recorded mapping; do not confuse sites or count duplicate designs |
| One interface-spanning site | Evaluate its contributions from both chains; do not invent two independent sites |
| Justified asymmetric occupancy/state | Preserve the profile-defined state; do not force equal ligand occupancy or coordinates |
| Empty/resting partner site | Apply its state-specific rules; do not require simultaneous productive geometry at every site |
| Fixed catalytic identity across reaction states | Preserve residue identity while allowing declared motion, protonation and bond changes |
| Required concentration-dependent claim without resolved concentration/basis | Request essential input or return missing scientific evidence; do not silently assume a stable dimer |
| Per-dimer activity compared with per-subunit activity | Require justified conversion and matched conditions; otherwise report not comparable |
| High local confidence but invalid interface | Cannot pass assembly qualification |
| Failure at one required site, high overall mean | Reject or refine; averaging cannot create PASS |
| Symmetry- or geometry-restrained result | Label imposed constraints; do not present construction constraints as independent confirmation |
| Buried interface exposed only after dissociation | Report assembled and dissociated contexts separately under qualified property rules |
| Interface/state edit with unchanged sequence | Invalidate all affected assembly, complex, chemistry and applicable property evidence |
| Shared-sequence edit | Update both copies; verify ties; invalidate affected downstream evidence |
| Reused equivalent-site evidence | Require frozen equivalence evidence, site mapping and no duplicate reward |
| Complete homodimer output | One unique FASTA entry per candidate, two chains in its assembly and explicit site/copy mapping |
| Unsupported or contradictory evidence at a gate | Preserve UNRESOLVED; record review reason and bounded permitted action |

## Required scientific and benchmark evidence

Demonstrate the monomer and homodimer routes separately for their declared supported profiles, with qualified chemistry controls and each required property adapter. Verify parameter/state transfer, QM/MM boundaries, route-appropriate path or free-energy validation, uncertainty and applicability. Record method, model, hardware, seed and resource identifiers. Biological activity comparisons require declared concentration/normalization bases and matched conditions; no inferred whole-cycle rate follows automatically from a chemical-step barrier.

Compare fixed execution, rule-based refinement and frozen RL on predeclared held-out tasks under equal compute. Keep training and evaluation evidence separate and report RL training cost. Measure qualified yield, diversity, failure/unresolved fractions, compute and agreement with measured activity only where appropriate data exist.

Record per-chain/interface/site evidence and actual assembly-level costs. Reference reproduction, newly generated assemblies, predicted oligomerization and experimentally measured assembly/function are different endpoints. Do not claim the whole homodimer scope is validated from a single successful example.

No items in these implementation/scientific sections have been executed merely by generating the specification-package report. Environment maturity remains **Specification**.
