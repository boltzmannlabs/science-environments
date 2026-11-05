# Task: bla_high_temperature

## Description

Generate and optimize **Bacillus licheniformis α-amylase variants for improved predicted stability with retained starch-processing structure**. Complete parent preparation, baseline evaluation, tool-based generation, property screening, candidate structures and substrate assessment, results-driven sequence optimization, re-evaluation and final comparison.

Agent-Scientist selects suitable methods from **Boltzmann, ToolUniverse or both**. This is an enzyme variant-design assignment, not only a flexibility simulation, stability scan or list of suggested mutations. Assess the parent and newly generated variants under matched conditions.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Bacillus licheniformis α-amylase, BLA. |
| Parent source | [PDB 1BLI](https://www.rcsb.org/structure/1BLI), reconciled with study accession WP_061576039.1; resolve construct/numbering differences before design. |
| Target reaction | Starch hydrolysis. |
| Substrate context | Select and freeze a chemically justified carbohydrate proxy for structural assessment. It represents a defined fragment, not the whole starch polymer. |
| Operating context | High-temperature application; declare one supported pH/temperature/metal state for each calculation and match it across parent and candidates. Do not merge different reported assay or simulation conditions. |
| Protected features | Verified Asp231, Glu261 and Asp328 catalytic system, essential ion coordination, required disulfides and functional architecture. |
| Objective | Improve a frozen computational stability endpoint while retaining substrate/catalytic/structural safeguards. |
| Shared inputs | Exact parent construct/structure, sequence mapping, carbohydrate proxy, relevant ions, protected/editable positions and final evaluation protocol. |

## Design Constraints

- Preserve the verified parent sequence length and construct. Resolve numbering before selecting an edit mask and protect mapped catalytic and required structural features.
- Select editable regions using parent structure, conservation, flexibility or design-tool evidence, not historical winning substitutions.
- Execute sequence-design, mutation-search or library-generation tools for initial and revised batches; retain complete sequences, actual settings, seeds, draws and raw outputs.
- Retain required ions, chemical components and relevant chain/assembly context; do not remove them merely to obtain favorable protein-only scores.
- Evaluate stability–function trade-offs. Reduced flexibility is not automatically beneficial and fold confidence does not establish high-temperature catalytic activity.
- Assess combinations directly, track candidate IDs/parentage/hashes and distinguish generated draws from unique non-native variants.
- Return up to five supported final candidates. Missing required evidence is not permission to pad the shortlist or infer unmeasured performance.

## Computational Tool Capabilities

Execute the following stages using current native SCI tools selected from Boltzmann, ToolUniverse or both. A capability requirement does not force the historical paper's software. Save actual outputs; leave unavailable required observations unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Establish the BLA construct, sequence/structure mapping, catalytic/metal features, carbohydrate proxy and modeled conditions. Freeze inputs, edit mask, budgets and final evaluation. | Prepared parent/proxy/ion inputs, mappings, chemistry sources, design constraints and `RUN_PLAN.json`. |
| 2. Evaluate parent baseline | Calculate the chosen stability endpoint and required structure-quality, expression-related and catalytic/substrate safeguards on the parent. | Numerical baseline, units, uncertainty, native outputs, method/settings and modeled-condition limitations. |
| 3. Generate variant sequences | Execute an appropriate constrained design or mutation-search method to generate complete variants in the selected regions. | Candidate sequences/edits, IDs/hashes, generation tool/model, actual draws, settings/seeds and native output provenance. |
| 4. Screen properties | Assess stability and expression-related risks plus available functional predictions; choose a justified initial structural shortlist. | Per-candidate observations, parent-relative changes, trade-offs, exclusions and documented shortlist. |
| 5. Assess structures and function | Model candidate structures and the declared carbohydrate-proxy complexes; verify sequence, structural quality, catalytic geometry and required ion environment. | Candidate-specific structures, confidence, component/residue/atom mappings, quality reports and functional measurements. |
| 6. Optimize using results | Diagnose actual weaknesses such as destabilization, excessive rigidity or disturbed substrate/metal interactions; execute a revised sequence-design/search step. | Evidence-linked decision, changed strategy/region/constraints, expected observation and new tool-generated sequences. |
| 7. Re-evaluate revisions | Repeat affected property and structural/complex checks on revised variants, directly assessing combinations and all proposed final candidates. | Revised metrics, actual structures, catalytic/metal safeguards and matched parent/initial-batch comparisons. |
| 8. Select and compare | Apply mandatory requirements, rank eligible designs, seal the selection and obtain a separate common-protocol evaluation. | Final sequences, sealed ranking, numerical comparison, unresolved/failed stages, usage and final report. |

Use this initial profile unless a reviewed comparison freezes different equal limits. These are environment settings, not a claim to reproduce the study's original screening size or simulation schedule.

| Limit | Initial profile |
| --- | --- |
| Initial generation target | Approximately 12 unique non-native variants; report actual generation and deduplication counts. |
| Maximum unique sequences including parent | 24 |
| Maximum substitutions per variant | 8 |
| Sequence revision rounds | At least 1 results-driven round; maximum 2. |
| Initial detailed structural assessment | Parent plus at least 5 eligible initial variants; report any shortfall explicitly. |
| Final structural assessment | Every proposed final candidate. |
| Maximum scientific submission attempts | 60 |
| Maximum final candidates | 5 |

Freeze numeric model-token, compute, financial and wall-time ceilings before comparison; include specialist usage in the assisted total. Record versions, generation/structure settings, seed limitations and actual outputs. Advanced dynamics may support assessment when justified but does not replace generation and optimization.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Parent identity and allowed edits | Full sequences, construct/position mapping, protected identities, edits, length and hashes. | Require no protected/out-of-mask substitutions, retained construct/length and compliance with frozen limits. |
| Generation and revision | Initial/revised generation artifacts, unique variants, lineage and observation-linked redesign. | Require actual tools and a new results-driven sequence round; reranking or a scoring-input correction alone does not count. |
| Primary stability endpoint | Frozen computational stability metric, units/sign convention, uncertainty and matched conditions. | Rank eligible variants in the declared direction. A stability estimate is not measured high-temperature activity, half-life or melting temperature. |
| Stability–function trade-offs | Supported flexibility, expression-related and functional measurements relative to the parent. | Apply only justified frozen safeguards; preserve conflicting results instead of assuming less motion is always better. |
| Structural quality and metal environment | Candidate sequence correspondence, coordinates, confidence, clashes, quality reports and protected ion coordination. | Require mandatory candidate-specific evidence and retained functional components; do not substitute protein-only confidence for full assessment. |
| Substrate/catalytic features | Proxy identity/state, atom correspondence, interactions and reaction-relevant geometry. | Use supported ranges only or descriptive measurements. Do not treat a proxy result as an assay on bulk starch. |
| Evidence completeness and resources | Raw outputs, revised/final checks, method/condition records, failures/unknowns and available runtime/cost/resource accounting. | Missing mandatory evidence remains unresolved; never substitute zeros or fabricated structures/scores. |

Freeze the primary endpoint, eligibility criteria and tie-breakers before design. Rank eligible designs by the primary endpoint in the declared direction and use candidate ID as the last tie-breaker. Retain secondary metrics separately. Historical energy units and per-variant values must be reconciled before numerical comparison; a published selection cutoff is not a winning score.

## Expected Output

**Format:** `enzyme_variant_optimization_bundle`

**Directory:** Separate agent-alone and specialist-assisted run folders under `results/local/bla/`.

- `RUN_PLAN.json`: frozen construct/proxy/ion inputs and hashes, conditions, constraints, budgets, methods and common evaluation protocol.
- `candidates.fasta` and `candidate_history.csv`: complete parent/variant sequences, edits, IDs/hashes, lineage, generation tool/round and raw-output references.
- `observations.csv`: baseline, screening and revised/final measurements with units, conditions, uncertainty and native evidence paths.
- `structure_evidence/`: candidate structures, carbohydrate-proxy complexes, residue/atom/ion mappings and quality/catalytic reports.
- `decisions.md`: shortlist/revision decisions and actual proposer/critic receipt references in assisted runs.
- `jobs.json` and `usage.json`: real submissions/IDs, statuses, outputs, failures/unknowns and available runtime/resources/cost, with credentials removed.
- `selection.csv`: final `candidate_id,rank,sequence_sha256` rows excluding the parent, plus `selection_seal.json` before independent evaluation.
- `REPORT.md`: completed/unresolved stages, numerical parent comparison, final candidates or honest shortfall, trade-offs and limitations. A separate evaluator writes `evaluation.json`.

## Important Instructions

- Apply the shared [execution-error and output-recovery requirements](../ENVIRONMENT_SPEC.md#execution-errors-and-recovery).

- Scientific source: [Computational design of α-amylase from Bacillus licheniformis to increase its activity and stability at high temperatures](https://doi.org/10.1016/j.csbj.2024.02.005). Do not combine inconsistent condition statements or silently repair reported numerical units. Historical comparison requires checking the supplement and exact inputs.
- Do not retrieve published winners, mutation identities or outcome tables, read `benchmark/REFERENCE_VALUES.md`, or inspect other-arm results during design. Research reaction chemistry using permitted primary sources and record unintended exposure.
- In agent-alone mode do not delegate. In assisted mode use the reviewed native proposer then critic for bounded initial/result-batch reviews; the parent executes tools and includes all calls in the shared budget.
- Use SCI's native discovery, input validation, current contracts, submissions and artifacts. No new catalogue, approval layer or custom job runner is required.
- Preserve available results and report what remains unresolved.
- Missing required evidence leaves the workflow unfinished. A complete run can return no supported improvement; computational scores are not experimental high-temperature performance.
- The [environment specification](../ENVIRONMENT_SPEC.md), [configuration](../config/workflow.json) and [comparison protocol](../benchmark/PROTOCOL.md) supplement the complete workflow stated above.
