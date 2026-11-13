# Task: task_005_sun_leh_pythia

## Description

Reproduce the **computational mutation-scoring stage of Sun et al.'s limonene epoxide hydrolase (LEH) case study**. Prepare a verified structure/sequence mapping, execute a complete Pythia substitution scan, retain both published model components, build the declared candidate library, verify the numerical outputs, seal the results and compare eligible published predictions separately.

This is a computational reproduction task. It does not require de novo enzyme generation, docking, MolProbity, a sequence-redesign round or experimental screening. A few chosen mutations, a pilot calculation or a proposed tool call do not replace the complete scan. SCI chooses a compatible implementation and execution route while preserving the paper method and the frozen input definitions.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Rhodococcus erythropolis limonene epoxide hydrolase; establish the exact native parent construct. |
| Starting reference | [PDB 1NWW](https://www.rcsb.org/structure/1NWW). Verify sequence, numbering, chain identity, unresolved residues and assembly rather than assuming coordinate indices equal native positions. |
| Primary structural context | One explicitly frozen monomer context, shared by the compared approaches. Record chain identity and the complete coordinate-file hash. |
| Secondary structural context | A separately labeled dimer-context sensitivity analysis when using the supplied assembly; report chain-specific predictions separately. A chain-context score is not a directly evaluated simultaneous homodimer mutation. |
| Scientific method | Source-pinned Pythia models C and P, with original feature preparation and checkpoint identities verified before inference. |
| Computational objective | Exhaustive single-substitution scores at all supported coordinate positions; rank and select under a declared negative-score convention. |
| Selection rule | Strict score < −2 and the best substitution per eligible position, after freezing which score aggregation the threshold applies to. The threshold is not a predicted temperature or the paper's best candidate score. |
| Functional context | LEH catalyzes limonene-epoxide hydrolysis. Record catalytic-site substitutions and other functional concerns separately; favorable Pythia scores alone do not qualify an enzyme. |

## Design Constraints

- Preserve the verified full parent sequence and native residue numbering. Never silently truncate the sequence to match the coordinate array.
- Record missing coordinates as unscored. Do not reconstruct missing residues or score them from invented geometry to make the coverage appear complete.
- Freeze source revision, dependencies, checkpoint hashes, structural contexts, model settings, aggregation, selection rules and resource policies before inference.
- Run the complete supported nonidentity substitution grid: 19 alternative amino acids per eligible residue. Retain the identity controls separately where the implementation emits them.
- Preserve model C and P outputs, their explicitly defined sum and mean, and the log-ratio direction. Do not select a favorable sign or aggregation after examining comparison results.
- A mean-score sensitivity library is a distinct analysis, not a silent replacement for the primary summed-score run. If the historical paper mapping remains ambiguous, disclose it.
- Preserve every raw hit, including catalytic-site concerns and failed qualification flags. Apply only a separately frozen, evidence-backed filter; do not retrospectively hide an unfavorable selection.
- Keep agent-alone and specialist-assisted workspaces separate. This publication's retained historical results are agent-alone and have no assigned configuration version.

## Computational Tool Capabilities

Execute the full task-specific stages through native SCI, using the pinned upstream implementation or a verified compatible scientific tool. Save actual inputs and outputs; a plan, successful import or short diagnostic is not full inference.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Establish the parent | Verify the LEH construct, full sequence, 1NWW chain/assembly correspondence and unresolved positions. | Parent FASTA, original coordinates, native-to-model residue map, source citations and sequence/structure hashes. |
| 2. Freeze the method | Inspect the Pythia source and published model definitions; select primary/secondary contexts and declare score sign, aggregation, strict cutoff and tie-breakers. | `RUN_PLAN.json`, input/checkpoint/source manifests, effective configuration and an explicit record of historical-method uncertainties. |
| 3. Prepare execution | Establish an isolated compatible environment and validate feature preparation, checkpoint loading and residue mapping before the full run. | Dependency versions, preparation logs, input checks and resource settings. A diagnostic does not count as a completed scan. |
| 4. Execute full inference | Score every supported position with both models and all 19 nonidentity alternatives in each declared context. | Native outputs, full component scores and raw logits/probabilities when returned, real process/job records and observed coverage. |
| 5. Verify numerical output | Check expected grid size, residue identities, finite scores, identity controls, complete residue mapping and score reconstruction where raw outputs permit it. | `verification.json`, exact row counts, missing/unscored-position ledger and output hashes. |
| 6. Rank and build libraries | Produce the full ranking, best-per-position table and strict-cutoff library under the frozen convention; label sensitivity analyses separately. | Full ranked CSVs, selected mutation tables, complete mutant sequences and qualification/catalytic-site annotations. |
| 7. Review and seal | Review task coverage, method differences and selection provenance; freeze the original ranking and candidate identities before evaluator comparison. | `selection.csv`, sequence hashes, `selection_seal.json`, exclusions/concerns and a completion record. |
| 8. Compare and report | Compare only clearly reported numerical predictions on compatible identities/definitions; retain missing candidate values and unresolved settings explicitly. | Separate same-variant comparison, source-linked report, failures and usage records. Computational completion and exact historical reproduction are reported separately. |

Execution settings belong in the selected [configuration version](../config/task_005_sun_leh_pythia/README.md). Record the actual SCI model/provider, scientific model versions, resource policies and authorized amendments with the run. The LLM and Pythia are different models and must be named separately.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Input identity | Full sequence, source coordinates, chains, assembly, residue map and hashes. | Require a verified mapping; preserve unresolved positions and construct differences. |
| Inference coverage | Eligible residues, 19 nonidentity alternatives per residue, contexts and expected/returned row counts. | Complete the declared coordinate-supported grid; report sequence positions without coordinates as unscored rather than zero. |
| Score correctness | C/P components, log-ratio orientation, sum/mean definitions, finite values and identity controls. | Preserve native outputs and verify arithmetic; do not rename a unitless score as kcal/mol or °C. |
| Selection correctness | Strict < −2 membership, best-per-position selection, deterministic ties and full-sequence reconstruction. | Apply the frozen rule exactly; do not use ≤ or mix primary and sensitivity scales. |
| Functional interpretation | Catalytic-site changes and other declared qualification concerns. | Keep raw score ranking visible while distinguishing a favorable score from a functionally supported enzyme. |
| Paper-score agreement | Exact same mutation, input context and score definition; clearly numerical published reference if available. | Report differences only when meaningful. If a candidate score is not identified in the inspected source, leave it unavailable; a cutoff is not a candidate prediction. |
| Completion and resources | Native inference artifacts, verification/seal, errors, real IDs and available model/scientific usage. | Report complete computational execution separately from unresolved historical settings and biological performance. |

## Expected Output

**Format:** `enzyme_computational_reproduction_bundle`

**Directory:** `results/local/task_005_sun_leh_pythia/<config-version>/<approach>/<run-id>/`, or a declared isolated workspace. Historical exports remain under `results/task_005_sun_leh_pythia/agent-alone/` without retroactively assigning v1/v2.

- `RUN_PLAN.json` and `INPUT_MANIFEST.json`: full parent/context identities, source/checkpoint hashes, score definitions, selection rules and actual effective settings.
- `all_scores.csv` and a ranked view: exact mutation/context mapping, C/P values, declared aggregations and all supported nonidentity scores.
- `best_per_position.csv`, cutoff-specific libraries and `candidates.fasta`: exact selections and reconstructed full-length sequences; label each aggregation/context.
- `verification.json` and a missing-position record: coverage, numerical checks, identity controls and preservation hashes.
- `selection.csv` and `selection_seal.json`: frozen original selection and its content hash before retrospective comparison.
- `jobs.json`, `errors.md` and `usage.json`: actual execution attempts, known IDs, diagnostic/correction history, permissions and cumulative accounting without credentials.
- `REPORT.md` in the execution workspace: actual stages completed, selected library, functional concerns, method ambiguities and unresolved paper comparisons. The repository's public comparison report is [comparison.pdf](../benchmark/task_005_sun_leh_pythia/comparisions/benchmark_report.pdf).

## Important Instructions

- Apply the shared [execution-error and output-recovery requirements](../ENVIRONMENT_SPEC.md#execution-errors-and-recovery) and [task-scoped reproduction rules](../ENVIRONMENT_SPEC.md#task-scoped-computational-reproductions).
- Primary source: [Sun et al., Structure-based self-supervised learning enables ultrafast protein stability prediction upon mutation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11763918/). The earlier frozen task has source hash `21036fa53b42e731100d5ec20b5d836d17ea133efcc639acf4f12eb4f4798b71`; this expanded document clarifies its scope and does not rewrite historical execution.
- Model methods and public parent identity are permitted inputs. Keep benchmark winner identities, outcome tables and other-arm results outside the primary selection process; comparisons after selection must be labeled retrospective.
- Agent-alone does not delegate. Assisted runs use reviewed native proposer/critic roles within the same declared accounting and independently execute their own scientific work.
- Exclude MLDE. Use current scientific-tool contracts or a verified source-pinned implementation; do not duplicate pending or acceptance-unknown submissions.
- No experimental screening was performed by this computational task. Do not claim measured thermostability, activity improvement or exact paper reproduction from a favorable ranking.
