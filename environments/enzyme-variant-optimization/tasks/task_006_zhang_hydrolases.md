# Task: task_006_zhang_hydrolases

## Description

Reproduce the **computational stages of Zhang et al.'s two-step thermostability workflow** for Bacillus subtilis cellulase and β-glucanase. Verify the exact enzyme constructs, prepare compatible WT structures, execute complete Pythia scans, verify the supplied stabilized sequence backgrounds, execute complete ESM-2 scans, verify and seal the numerical outputs, and compare clearly reported original predictions.

Report the two enzymes separately within this task. The paper's experimental selection between computational stages is represented by explicitly supplied historical backgrounds. It is not an experiment performed by SCI, and favorable predictions do not establish the paper's measured temperature or activity improvements. This task does not inherit the RML/LEH optimization tasks' docking, MolProbity or results-driven sequence-redesign gates.

## Target

| Field | Task definition |
| --- | --- |
| Enzymes | Bacillus subtilis cellulase and β-glucanase; verify the exact paper construct for each rather than using a related protein by name alone. |
| WT inputs | Exact source-supported WT sequences, full residue numbering and compatible structures. The retained runs used 312-residue cellulase and 215-residue β-glucanase constructs; verify exact bytes and mapping before another run. |
| Structural stage | AlphaFold2 or the documented compatible structure-prediction route for the exact WT constructs, followed by source-pinned Pythia scoring. Preserve any difference from the paper's original coordinate files. |
| Sequence stage: cellulase | Supplied historical M2 background, WT + G177P/L302R. Verify the full sequence and mapping before evaluating additional single substitutions. |
| Sequence stage: β-glucanase | Supplied historical M5 background, WT + N38S/L45E/N65I/A142S/S196K. Verify the full sequence and mapping before evaluating additional single substitutions. |
| Pythia endpoint | Full single-substitution landscape on each WT structure; retain C/P outputs and declare aggregation, negative-score direction and strict < −3.0 rule. |
| ESM-2 endpoint | Full single-substitution masked-marginal landscape on M2 and M5; retain mutant-minus-WT and WT-minus-mutant values, with the declared comparison using negative log-likelihood ratio and strict < −1.5. |
| Functional context | Cellulose and β-glucan hydrolysis. Do not invent a finite monomer substrate to claim reproduction of polymer activity or kinetics. |

## Design Constraints

- Keep cellulase and β-glucanase inputs, structures, score tables, selected libraries and comparisons distinct.
- Preserve exact WT, M2 and M5 sequences, including all supplied background mutations. Label an additional mutation relative to its actual background; do not call an M2/M5 derivative a WT single mutant.
- Use a structure whose residue mapping matches the complete intended WT construct. A related PDB with tags, missing residues or substitutions requires explicit reconciliation; it is not an automatic replacement.
- Freeze structure preparation, Pythia source/checkpoints, ESM-2 checkpoint/tokenizer, masking procedure, score definition, selection rules and effective resources before inference.
- Execute all 19 nonidentity substitutions per eligible residue. Preserve the full landscape and identity controls; selected published rows are an evaluator subset, not permission for a shortened inference run.
- Retain both ESM score orientations. The source's prose/equation and selected negative scores have a sign ambiguity; do not choose a sign or checkpoint after seeing which agrees best with the paper.
- Distinguish source-supported exclusions from unfiltered predictions. If original site exclusions cannot be recovered, complete the supported scan and mark the paper-qualified library unresolved; do not invent a filter.
- Supplied M2/M5 backgrounds are retrospective experimental inputs. Do not claim that the agent discovered those combinations, validated their activity experimentally or performed the paper's greedy experimental selection.
- Keep original candidate rankings and adverse outcomes. Late property predictions or reference retrieval must not silently change the original selection or qualification.

## Computational Tool Capabilities

Use native SCI tool discovery and verified source implementations for the declared computational methods. Choose compatible execution routes independently, retaining their actual contracts, input hashes and returned artifacts. Successful preparation or a pilot score does not complete a scan.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Establish constructs | Extract and verify exact WT, M2 and M5 sequences, backgrounds, lengths and native numbering for both enzymes. | Source citations, FASTAs, full edit lists, sequence hashes and construct correspondence records. |
| 2. Freeze the protocol | Declare structural and sequence-stage inputs, model versions, sign/aggregation conventions, strict cutoffs, exclusions and comparison rules. | `RUN_PLAN.json`, input/source/checkpoint manifests, effective configuration and unresolved historical settings. |
| 3. Prepare WT structures | Predict or obtain compatible structures for each exact WT sequence; validate identity and residue mapping before Pythia inference. | Structure-prediction inputs/jobs, actual coordinate files, sequence-to-coordinate mappings and provenance. Confidence is supporting preparation evidence, not a benchmarked property. |
| 4. Execute Pythia scans | Score every supported WT position with both Pythia components and all 19 nonidentity substitutions for each enzyme. | Complete raw/component scores, declared aggregate, identity controls, coverage and real execution records. |
| 5. Execute ESM-2 scans | Perform the frozen masked-marginal procedure across every position and alternative residue of the full M2 and M5 sequences. | Full score grids, checkpoint/tokenizer metadata, both score signs, mutation/background identity and execution artifacts. |
| 6. Verify and rank | Independently check grid completeness, finite values, WT identities, score arithmetic, strict-cutoff membership and reconstructed variant sequences. | Per-stage verification, ranked tables, selected libraries, excluded/unresolved site records and output hashes. |
| 7. Review and seal | Review stage completion and source-qualified eligibility, preserve unfiltered versus qualified libraries, and freeze original selections. | Sealed selection tables, complete full-background sequences, concerns and final source/protocol limitations. |
| 8. Compare and report | Join original numerical prediction rows by enzyme, background and exact mutation; report same-variant agreement separately from best-published-versus-best-ours comparisons. | Source-linked numerical comparisons, score differences and the actual computational outcome for each enzyme, with failures and cumulative resource records. |

Execution settings belong in the selected [configuration version](../config/task_006_zhang_hydrolases/README.md). Record the SCI LLM separately from AlphaFold2, Pythia and ESM-2. Historical exports have no retroactively assigned configuration version.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Construct/background identity | Full WT/M2/M5 sequences, all background edits, lengths, hashes and numbering. | Require exact identity; never join an M2/M5 mutation to a WT score by label alone. |
| Structure compatibility | Actual model bytes, sequence-to-coordinate correspondence, missing positions and preparation settings. | Require a verified compatible input; distinguish new same-construct models from the unavailable original paper coordinates. |
| Pythia coverage and values | Expected/returned 19-substitution grid, C/P values, declared aggregation and finite scores. | Complete the supported grid for each WT; retain missing positions and scale ambiguities explicitly. |
| ESM-2 coverage and values | Full M2/M5 masking coverage, all substitutions, both log-ratio directions and identity controls. | Use the frozen checkpoint/masking method; score leaders must use the declared paper-oriented direction. |
| Selection and eligibility | Strict < −3.0 / < −1.5 membership, original exclusions and background-relative full sequences. | Separate raw threshold hits from source-qualified selections. Unknown exclusions cannot become invented accepted sites. |
| Same-variant paper agreement | Matched original prediction rows from S1/S3/S5/S7, numerical differences, MAE and publication-rounding agreement. | Compare the same score and exact background; state original setting uncertainties. These metrics measure score reproduction, not experimental accuracy. |
| Candidate comparison | Best available raw-score candidate, supplied background lineage, sign and qualification concerns. | Keep different-mutation comparisons separate from same-variant reproduction; do not present opposite-sign diagnostic hits as favorable leaders. |
| Completeness and resources | Actual stage artifacts, verification/seal, failures/unknowns, permissions and model/scientific usage. | Report both enzymes and all declared computational stages; preserve an unresolved exact-reproduction boundary despite completed inference. |

## Expected Output

**Format:** `enzyme_computational_reproduction_bundle`

**Directory:** `results/local/task_006_zhang_hydrolases/<config-version>/<approach>/<run-id>/`, or a declared isolated workspace. Retained historical exports are under `results/task_006_zhang_hydrolases/agent-alone/` without assigning them to a newly written configuration.

- `RUN_PLAN.json` and `INPUT_MANIFEST.json`: exact constructs/backgrounds, model and source versions, score definitions, selection/exclusion rules, resource policies and authorized amendments.
- `inputs/` and `structures/`: full WT/M2/M5 sequences, prepared WT coordinate files, chain/residue mapping and actual structure-prediction provenance.
- Separate `Pythia_<enzyme>_WT.csv` and `ESM2_<enzyme>_<background>.csv`: complete grids with native score precision, mutation identities, component/sign information and coverage.
- Ranked and cutoff-specific libraries, `candidates.fasta` and a lineage table: exact full-background variants with filtering and functional/eligibility concerns.
- `verification.json`, `selection.csv` and `selection_seal.json`: independent numerical checks and original frozen selections.
- `jobs.json`, `errors.md` and `usage.json`: all actual attempts, real IDs/statuses, correction history, permission events and cumulative accounting; no credentials or duplicate unknown submissions.
- Source-linked same-variant and best-versus-best comparison tables, kept as distinct analyses. The repository retains prediction columns only in its concise comparison CSV.
- `REPORT.md` in the execution workspace: stage completion for each enzyme, method ambiguities, numerical findings and remaining evidence gaps. The public report with embedded figures is [comparison.docx](../benchmark/task_006_zhang_hydrolases/comparisions/benchmark_report.docx).

## Important Instructions

- Apply the shared [execution-error and output-recovery requirements](../ENVIRONMENT_SPEC.md#execution-errors-and-recovery) and [task-scoped reproduction rules](../ENVIRONMENT_SPEC.md#task-scoped-computational-reproductions).
- Primary source: [Zhang et al., Two-step computational redesign of Bacillus subtilis cellulase and β-glucanase for enhanced thermostability and activity](https://doi.org/10.1016/j.ijbiomac.2024.138274). The earlier frozen task has hash `969e9ca4a60cf2a322258bc8ec7d2cb68b2abebdae9f244e3be5c54cebe2081b`; this expanded specification clarifies the same computational scope.
- Prediction reference columns are in [the original supplement](https://ars.els-cdn.com/content/image/1-s2.0-S0141813024090858-mmc1.docx), Tables S1/S3/S5/S7. Keep their numerical outcome rows outside original selection inputs; a later evaluator may use them retrospectively after sealing. Experimental Tm and activity columns are not prediction targets.
- Agent-alone does not delegate. Assisted runs use reviewed native proposer/critic roles, independently execute their scientific work and preserve the same comparison constraints and cumulative accounting.
- Exclude MLDE. Use current contracts or source-pinned code; diagnose recoverable input failures and verify corrected outputs without weakening scientific identity or duplicating pending jobs.
- Do not create an additional docking/chemical-quality/redesign obligation just because another task uses it. Complete the declared reproduction stages and honestly distinguish computational completion, exact historical reproduction and experimental improvement.
