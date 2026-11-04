# Task: leh_stability

## Description

Generate and optimize **limonene epoxide hydrolase variants with improved predicted stability and preserved catalytic structure**. Execute parent preparation, parent baseline evaluation, tool-based sequence generation, property screening, structural and substrate assessment, results-driven sequence optimization, re-evaluation and final comparison.

Agent-Scientist selects suitable tools from **Boltzmann, ToolUniverse or both**. A list of suggested substitutions or a stability-prediction scan alone does not complete the assignment. Use structural and chemical checks to challenge favorable predictions, then generate and test a revised sequence batch.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Rhodococcus erythropolis limonene epoxide hydrolase, LEH. |
| Parent source | [PDB 1NWW](https://www.rcsb.org/structure/1NWW); establish complete sequence, construct boundaries, chain mapping and biological assembly. |
| Target reaction | Limonene-1,2-epoxide hydrolysis; establish the substrate stereochemistry and reaction state from primary evidence. |
| Substrate context | Preserve required catalytic water and atom correspondence. The bound crystallographic ligand is not automatically the natural substrate. |
| Operating context | Freeze supported pH, temperature, assembly and chemical-state settings for matched parent/candidate evaluation; record unsupported condition dependence. |
| Protected features | Verified Asp132, Arg99 and Asp101 catalytic network, required water-positioning and assembly features. |
| Objective | Improve a frozen computational folding/stability endpoint without violating functional-structure safeguards. |
| Shared inputs | Exact parent/assembly, substrate preparation, residue/atom mapping, allowed edits, chemistry sources and final evaluation protocol. |

## Design Constraints

- Preserve the verified parent construct and length. Declare any tags or existing mutation background consistently for both approaches; do not reuse prior engineered inputs silently.
- Protect the mapped catalytic network, water-positioning features and required assembly. Select editable positions from parent/conservation/design evidence, not published winners.
- Execute appropriate sequence-design, mutation-search or library-generation tools for initial and revised batches. Retain full sequences, actual settings, seeds, draw counts and native outputs.
- Introduce disulfides only with a suitable design method and explicit structural checks, not arbitrary paired cysteine edits. Assess combinations directly rather than summing individual scores.
- Screen surface hydrophobicity, unsatisfied polar interactions, clashes and local flexibility where supported. A favorable folding-energy prediction alone cannot qualify a design.
- Assign unique candidate IDs, hashes and parentage, separating draws, unique variants, native recoveries and structural evaluations.
- Return up to five supported non-native candidates; do not fill a shortlist with failed or unresolved variants.

## Computational Tool Capabilities

Execute each stage using appropriate native SCI tools selected from Boltzmann, ToolUniverse or both. Keep unavailable mandatory evidence unresolved. Inexpensive screens may precede expensive structural calculations, but all stages remain required.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Establish LEH construct/assembly, sequence mapping, protected/editable positions, substrate stereochemistry and catalytic water. Freeze shared inputs, conditions, budgets and final evaluator. | Prepared parent/substrate, residue/atom/assembly mappings, chemistry sources, edit mask and `RUN_PLAN.json`. |
| 2. Evaluate parent baseline | Calculate the selected stability endpoint and required sequence, structure-quality and catalytic/substrate safeguards on the parent. | Numeric baseline, units/sign conventions, actual tool outputs, method/settings and uncertainty. |
| 3. Generate variant sequences | Execute a constrained design or mutation-search tool to explore stabilizing substitutions, with disulfide design only when supported. | Complete variants, edits, IDs/hashes, tool/model settings, seeds, actual draws and native generation records. |
| 4. Screen properties | Assess stability and expression-related risks, including supported checks for exposed hydrophobicity or unfavorable polar interactions. Select an initial structural set. | Candidate observations, parent-relative changes, trade-offs, exclusions and a documented shortlist. |
| 5. Assess structures and function | Predict/model shortlisted variants and relevant substrate complexes; inspect assembly, structural quality, active-site/water features and supported flexibility/geometry measures. | Candidate-specific structures, identity/component mappings, quality results, substrate/catalytic measurements and uncertainties. |
| 6. Optimize using results | Identify observed false-positive stability predictions or functional defects, then execute a revised design/search strategy addressing them. | Observation-linked revision rationale, changed design constraints/strategy, expected effect and new tool-generated sequences. |
| 7. Re-evaluate revisions | Repeat affected stability/property and structural/complex evaluations, including direct checks of combined changes and disulfide geometry where relevant. | Revised observations, actual structures, functional safeguards and matched parent/initial-batch comparisons. |
| 8. Select and compare | Apply mandatory evidence requirements, rank eligible variants, seal the selection and obtain separate common-protocol evaluation. | Final sequences, sealed ranking, numerical comparison, exclusions/failures, resource records and final report. |

Use this initial execution profile unless a reviewed comparison freezes different equal limits. These are task settings rather than a reproduction of the original FRESCO library size.

| Limit | Initial profile |
| --- | --- |
| Initial generation target | Approximately 12 unique non-native variants; record actual draws and unique outputs. |
| Maximum unique sequences including parent | 24 |
| Maximum substitutions per variant | 8 |
| Sequence revision rounds | At least 1 results-driven round; maximum 2. |
| Initial detailed structural assessment | Parent plus at least 5 eligible initial variants; retain any shortfall explicitly. |
| Final structural assessment | Every proposed final candidate. |
| Maximum scientific submission attempts | 60 |
| Maximum final candidates | 5 |

Freeze numeric model-token, scientific-compute, financial and wall-time ceilings before comparison and include specialist calls in the assisted total. Record versions, generation/modeling settings, seed limitations and actual output counts. Missing eligible candidates must not be replaced with fabricated or duplicate outputs.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Parent identity and allowed edits | Full sequences, construct/background, chain mapping, assembly, protected positions, edits and hashes. | Preserve parent length, required assembly and protected/out-of-mask identities within the frozen mutation limits. |
| Generation and revision | Initial/revised generation outputs, unique sequences, algorithm settings, lineage and observed reasons for redesign. | Require actual tool-based generation and a new results-driven sequence round; reranking or repairing a score input alone does not count. |
| Primary stability objective | Frozen folding/stability endpoint, units, sign convention, uncertainty and matched parent/candidate methods. | Rank eligible designs in the declared direction without mixing score scales or treating a predicted energy as measured melting temperature. |
| Orthogonal stability safeguards | Surface hydrophobicity, unsatisfied polar interactions, clashes, supported flexibility measures and disulfide geometry if relevant. | Apply justified frozen safeguards; retain disagreement instead of trusting one favorable predictor. |
| Structural and assembly quality | Candidate-specific sequence identity, coordinates, confidence, local defects, assembly and relevant component mappings. | Require complete mandatory candidate evidence; a parent structure or fold-confidence score alone is insufficient. |
| Catalytic and substrate features | Substrate identity/stereochemistry, catalytic-water/network preservation, atom mappings and reaction-relevant geometry. | Use supported ranges only; otherwise report descriptive values. A different crystallographic ligand cannot silently stand in for the target substrate. |
| Evidence completeness and resources | Native artifacts, revised/final checks, missing/failed stages and available model/scientific usage/cost records. | Keep unresolved evidence explicit; no zero imputation or unsupported candidates added to fill the selection. |

Freeze the primary endpoint, safeguards and tie-breakers before design. Rank eligible designs by that endpoint in its declared direction, then candidate ID as the final tie-breaker. A separate evaluator compares sealed selections using one common method. Keep historical experimental melting temperatures and any noncomparable energy predictions descriptive.

## Expected Output

**Format:** `enzyme_variant_optimization_bundle`

**Directory:** Separate agent-alone and specialist-assisted run folders under `results/local/leh/`.

- `RUN_PLAN.json`: frozen parent/assembly/substrate inputs and hashes, constraints, numeric budgets, methods and common evaluation protocol.
- `candidates.fasta` and `candidate_history.csv`: complete parent/variant sequences, edits, hashes, generation tools, settings/rounds, lineage and raw-output references.
- `observations.csv`: baseline, screening and revised/final measurements with units, method/state settings, uncertainty and evidence paths.
- `structure_evidence/`: candidate structures and substrate complexes, assembly/atom/residue mappings and quality/catalytic reports.
- `decisions.md`: exclusions, shortlisting and revision reasons, including actual proposer/critic receipt references for assisted runs.
- `jobs.json` and `usage.json`: submissions, known IDs, statuses, outputs, failures/unknowns and available runtime/resource/cost records, without credentials.
- `selection.csv`: final `candidate_id,rank,sequence_sha256` rows excluding the parent, with `selection_seal.json` before independent evaluation.
- `REPORT.md`: completion status, numerical parent comparison, final candidates or shortfall, rejected false positives and limitations. A separate evaluator writes `evaluation.json`.

## Important Instructions

- Scientific source: [Computationally designed libraries for rapid enzyme stabilization](https://doi.org/10.1093/protein/gzt061). Its experimental screening informed mutation combinations; this computational task does not reproduce that experimental step or establish measured melting temperatures.
- Do not retrieve published winners, their mutation identities or outcome tables, read `benchmark/REFERENCE_VALUES.md`, or inspect the other approach's results during design. Use permitted primary sources for chemistry; record unintended outcome exposure.
- In agent-alone mode do not delegate. In assisted mode use the reviewed native proposer then critic for bounded initial/result-batch reviews; the parent executes tools and counts all calls in the same budget.
- Use native SCI tool discovery, input validation, submissions and artifact handling with current contracts. No new catalogue, approval layer or custom job runner is required.
- Preserve available results and report what remains unresolved.
- Missing required evidence leaves the workflow unfinished, not numerically failed. Complete with no supported improvement is a valid outcome; computations do not prove improved experimental catalysis or stability.
- The [environment specification](../ENVIRONMENT_SPEC.md), [configuration](../config/workflow.json) and [comparison protocol](../benchmark/PROTOCOL.md) supplement the full workflow stated here.
