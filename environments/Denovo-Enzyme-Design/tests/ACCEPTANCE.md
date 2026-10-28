# Acceptance and validation plan

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory. The generated [validation report](specification-validation.json) records actual results for:

- Required package files, local Markdown links and the BioDesignBench-style task sections, with the software-list section replaced by required execution steps.
- JSON Schema well-formedness, monomer/homodimer example requests and separate generation-readiness contracts.
- Synthetic draft profiles: assembly/copy-count consistency, shared sequence groups, unique chain/site IDs, required interface/state evidence, valid cross-references, state/step/site gate coverage and normalized weights.
- Rejection of unsupported assemblies and explicit request/profile assembly mismatches. Synthetic artifact paths/hashes are not scientific evidence.
- Each generation profile must bind to the current resolved request; a stale profile cannot reach generation even if its reviewer returns accept. Case-study biology is never a fallback for another enzyme.
- Request rejection for missing chemistry, invalid count/budget, unsupported controller mode, inconsistent length/count limits, and unpaired/invalid protein concentration and basis.
- Stage order/dependencies: property and fold checks before complex/state/chemistry work.
- Mandatory chemistry, solubility and aggregation groups and no-compensation qualification.
- Bounded reward configuration, positive-weight requirement, held-out policy freezing and chemistry reservation.
- In Progress maturity, implemented fixed-controller scope and absence of a fabricated qualified profile or whole-pipeline validation claim.

These checks validate this specification package only. They do not validate external URLs, the target repository license, molecular parsing, tool installation, model predictions, RL training or enzyme chemistry.

## Stage entry and release requirements

Generation requires a reviewed generation contract and compatible execution capability. Full reaction-profile qualification is not a universal entry gate. Preparation, reference tests and exploratory candidates may advance when their own dependencies pass; complete chemistry, property and assembly evidence is still required for final qualification.

1. For repository release, link the contribution issue and complete the applicable PR/review process. These repository-governance steps are separate from authorized local preparation and scientific execution. The repository structure, rules and pending-license notice were read on 26 October 2026.
2. Connect the controller to the existing execution harness and test actual adapter behavior. Freeze generation inputs and evaluation intent, then prepare later profile fields before their stages use them. A ready generation contract does not assert catalysis or final qualification.
3. Validate actual molecules, stereochemistry, stoichiometry, atom maps and fixed catalytic identity through every format conversion.
4. Enforce profile semantics in the runtime, including the subset checked here on synthetic fixtures: unique IDs; valid state/step references; complete state/step coverage; all nine required rule groups represented by required rules; finite values; compatible units/operators; ordered ranges; positive weights summing to one; and valid reward transforms.
5. Verify immutable artifact hashes, operation coverage, compatible model components and appropriate access for the affected stage. Missing late capability must not invalidate already completed, scientifically justified work.
6. Confirm biological assembly identity, reconstruction operators, chain/atom mapping, identical homodimer sequences and state-specific occupancy against actual files. Qualify the interface/site evaluator and any representative-site equivalence; contract tests do not perform these checks.
7. Check requested conditions against supported domains and resolve relevant buffer/salt, concentration and ligand-occupancy assumptions. Concentration requires its declared basis; omission is unresolved when a required claim depends on it. Link every user hard target to a qualified evidence rule.

## Required functional tests

| Scenario | Required behavior |
| --- | --- |
| No qualified full reaction profile, ready generation contract | Exploratory generation is eligible; final qualification remains unavailable until complete evidence passes. |
| Missing generation prerequisite | Prepare or repair it; no generation based on an invented motif, unresolved reaction or incompatible assembly. |
| Missing seed, counts or unspecified research settings | Resolve from policy and documented evidence; record assumptions rather than requesting routine approval |
| Human scientific reviewer not named | Agent reviews actual qualification evidence; a missing human name alone does not block preparation or otherwise justified execution |
| Valid reference/adapter test before full profile qualification | Execute within its own input/resource constraints; label outputs development evidence and exclude them from candidate success counts |
| Generated sequence with real but unresolved backbone geometry | Reviewer may accept only `accept_sequence_only` with a hashed defect report; run sequence_screen on the immutable FASTA, not on a fabricated repaired candidate. |
| Sequence-only generation reaches fold | Permit sequence-input prediction before generated-coordinate repair. Require separate assessment models with exact sequence/chain mapping, raw prediction provenance and independently reviewed geometry/control evidence before downstream structural promotion. Preserve the original defect. |
| Startup components pass separately but combined execution fails | Check actual input parsing, mappings, checkpoint, device/runtime, logging and instrumentation jointly where possible. Version and test corrections; retain failures and cumulative accounting. |
| Abbreviated sampling produces distorted coordinates | Retain as integration evidence; test a supported quality-assessment schedule before drawing conclusions about generator suitability. Initial diffusion noise is not a final-model failure. |
| Fixed ligand-contact atoms remain near ligand but far from their backbone | Check all relevant motif covalent bonds, peptide links and masks together; selected preserved distances do not establish complete geometry. Version a task-specific motif choice and retest; do not impose whole-residue fixing on every enzyme. |
| Assembly flag parses but combined motif/occupancy output is unsuitable | Verify effective runtime operator, copy indexing and enforcement path; test simpler controls before dependent campaigns. Keep capability unresolved on failure; two chains or identical placeholder sequences are insufficient. |
| Execution tool denies approval or its approval request times out | Preserve exact failure/command/receipt in execution_approval_block; no automatic repair, alternate command or limit renewal. |
| Configured execution gate returns actual smart-mode approval | Record it and continue within existing policy; no additional manual prompt unless explicitly requested, no blanket approval or settings changes. |
| Poll response names another job/provider or omits original job identities | Reject the receipt, retain original handles and accounted usage; no duplicate submission or downstream acceptance. Apply the same rule after restart. |
| Previously exported candidates lose qualification or evidence changes | Archive the superseded bundle with an explicit marker; remove its structure/chemistry copies from current results while preserving raw artifacts. |
| Positive reference control fails | Record METHOD_CONTROL_FAILED, investigate mapping and method applicability, and preserve the candidate as unassessed for affected claims. Do not infer candidate rejection or improvement. |
| Structural promotion is blocked but sequence-property methods are applicable | Continue actual sequence-based assessments within policy, retaining applicability and uncertainty. Composition descriptors do not substitute for solubility or aggregation predictions. |
| Pairwise alignment disagrees with designed catalytic numbering | Reconcile generator atom/motif provenance and structure before accepting or rejecting correspondence; do not replace the map from sequence alignment alone. |
| Control uses richer input information than candidate | Require an evidence-backed applicability assessment for the candidate regime; no fabricated alignments or automatic transfer of control success. |
| Method controls are missing, stale or bound to different settings | Allow exploratory control calculations; reject structural promotion until agent-generated method-validation evidence and independent review pass. |
| Candidate integrity incomplete versus failed | Distinguish STRUCTURAL_INTEGRITY_UNRESOLVED from STRUCTURAL_INTEGRITY_FAILED; never use a generic file-identity error for both. |
| Later stage or final export uses another coordinate version | Reject missing/stale assessment-model bindings; final export and assembly map must identify the reviewed assessment structure, retaining the generated scaffold as provenance. |
| Controller terminates with a stage marked running | Mark local work incomplete; preserve uncertain remote handles under awaiting_reconciliation without implying cancellation. |
| Constrained preparation of candidate and matched reference | Use the same pinned method/conditions; record cis-link provenance, all observed backbone links and modeled residues, mapped catalytic identities, source/product hashes and restraint scope. A minimized model is not an independent fold or catalytic PASS. |
| Review finds execution or preparation failure | Controller performs bounded retry/repair and resumes, preserving the failure and invalidating affected downstream evidence. |
| Review finds failed or unresolved scientific evidence | Reject verified disqualifying failure; missing prerequisite blocks dependent work. Neither opinion nor continued independent assessment turns UNRESOLVED into PASS. |
| No task-specific compute budget | Apply configured local fallback ceilings and existing entitlements; no new paid-service authorization is inferred |
| Requested job exceeds effective limits or has unknown required paid access | Complete independent work; report the precise resource/access blocker, without silently extending limits |
| Earlier preparation report asks for routine approvals | Preserve the historical report; continue under the current autonomy policy |
| Reviewer requests a routine setting or gives no structured reason | Redirect to bounded internal repair; record the question and correction, then continue when resolved. |
| Reviewer confirms essential ambiguity or access outside policy | Require a structured reason, affected item and source/finding resolution attempts; retain the accepted question in the report. |
| Routine question persists through the repair allowance | Return the actual blocker or partial result; do not escalate a routine decision to the user or loop indefinitely. |
| Historical session allowance expired | New controller state cannot silently renew that allowance; keep its deadline and usage evidence. |
| Setup and campaign accounting | Report separate counters within the same authorized total, unless an explicit policy allocates separate limits. |
| Resume after interruption | Verify immutable inputs and current artifact hashes, reconcile recorded jobs and continue eligible work without duplicating submission or charging. |
| Same setup failure recurs | Attempt bounded evidence-based recovery; never repeat indefinitely or shrink the scientific task to make a smoke test pass. |
| Missing essential user information | `NEEDS_INPUT` with the required clarification |
| Required capability unavailable | Agent-selected mode may use a verified compatible alternative; exact-tool condition preserves the constraint. Continue independent work, then report the affected stage. |
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
| Exploratory results exist but mandatory evaluation is incomplete | PARTIAL with explicit missing evidence, possibly zero qualified designs; never mark the run scientifically successful. |

Run controller/bridge behavior tests separately with `/usr/bin/python3 -m unittest discover -s tests -p 'test_*.py'`. These must exercise real small subprocesses, persistence, retries, repair decisions, invalidation, timeouts and incomplete outcomes, using synthetic evidence labeled as software fixtures. Use real qualified fixtures for scientific assertions; software fixtures cannot qualify an enzyme or calibrate a gate.

## Required assembly runtime tests

These tests are acceptance requirements, not completed molecular validation:

| Scenario | Required behavior |
| --- | --- |
| Assembly unspecified | Resolve from biological evidence; never silently choose monomer |
| One-chain asymmetric unit with biological dimer | Reconstruct the recorded biological assembly and preserve transformation provenance |
| Conflicting assembly evidence or unsupported assembly | `BLOCKED` with the missing scientific prerequisite; do not launch generation |
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

The specification-package report does not establish these scientific results. Controller/bridge checks establish only the behaviors actually exercised. Environment maturity remains **In Progress** until complete scientific adapters and a named reaction scope have passed appropriate end-to-end validation.
