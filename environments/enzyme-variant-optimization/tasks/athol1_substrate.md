# Task: athol1_substrate

## Description

Generate and optimize **AtHOL1 variants for improved computational support of a non-native substrate, ethyl iodide**. Complete parent preparation, baseline evaluation, tool-based sequence generation, property screening, candidate structures and reaction-complex assessment, results-driven sequence optimization, re-evaluation and final comparison.

Agent-Scientist selects suitable tools from **Boltzmann, ToolUniverse or both**. Do not reduce the task to docking known mutants, a single electric-field calculation or language-model-proposed substitutions. Generate new sequences and evaluate the parent and variants under matched conditions.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Arabidopsis thaliana Harmless to Ozone Layer 1 methyltransferase, AtHOL1. |
| Parent source | [PDB 3LCC](https://www.rcsb.org/structure/3LCC); establish the complete parent sequence, construct, assembly and residue correspondence. |
| Target transformation | Ethyl iodide conversion with S-adenosyl-L-homocysteine to the corresponding ethylated sulfonium product. |
| Reaction context | Include both reacting partners and their verified chemical states/atom mappings. Distinguish ethyl iodide from the parent enzyme's methyl-iodide substrate. |
| Operating context | Freeze supported reaction-state, pH/temperature and modeling assumptions consistently for parent and candidates; record condition dependence that a method does not model. |
| Protected features | Indispensable reaction/cosubstrate-binding and functional-structure features established from primary mechanism evidence. |
| Objective | Improve a declared reaction-relevant computational endpoint while retaining stability and required catalytic/chemical safeguards. |
| Shared inputs | Exact parent/assembly, both reacting partners, atom/residue mappings, protected/editable positions, chemistry sources and common final evaluator. |

## Design Constraints

- Preserve the verified parent construct/length and protected functional features. Derive the editable region from parent and mechanism evidence, not published winners.
- Execute suitable constrained sequence-design, mutation-search or library-generation tools for initial and revised variants. Retain full sequences, actual settings, seeds, draws and raw outputs.
- Keep chemical state, cosubstrate identity, stereochemistry and atom mapping consistent across candidate comparisons. A reactant complex and a transition-state model are different inputs.
- Evaluate folding/thermal risks as well as substrate accommodation. A larger pocket or a favorable docking score alone does not establish faster conversion.
- Assess combined mutations directly, with stable candidate IDs, sequence hashes and lineage. Separate generated draws, unique variants, native recoveries and evaluated structures.
- Use reaction-energy/electric-field methods only when their chemical model, definitions, parameters, software and resource needs are supported; do not relabel docking as a reaction barrier.
- Return up to five supported non-native candidates without padding missing or failed evaluations.

## Computational Tool Capabilities

Execute each stage with appropriate current native SCI tools selected from Boltzmann, ToolUniverse or both. Tool choice is flexible; actual generation, evaluation and revision are required. Preserve unavailable mandatory evidence explicitly.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Establish AtHOL1 construct/assembly, both reacting partners, protected/editable features and a defensible reaction-state model. Freeze inputs, budgets, conditions and final evaluator. | Parent/reactant files, residue/atom mappings, primary chemistry sources, edit mask and `RUN_PLAN.json`. |
| 2. Evaluate parent baseline | Calculate the chosen reaction-relevant endpoint plus required stability, quality and reaction-arrangement safeguards on the parent. | Numeric baseline, method/chemical-state settings, units, uncertainty, actual artifacts and applicability limits. |
| 3. Generate variant sequences | Execute an appropriate constrained design or mutation-search tool targeting supported editable positions. | Complete sequences, edits, IDs/hashes, generation tool/model, settings/seeds, draws and native outputs. |
| 4. Screen properties | Assess the objective and folding/stability/expression risks; select candidates for detailed reaction-complex assessment using declared rules. | Per-candidate observations, parent-relative changes, exclusions, uncertainty and a documented initial shortlist. |
| 5. Assess structures and function | Model shortlisted variants with the reacting partners; verify sequences, chemical states and quality; assess accommodation, reactive alignment and supported mechanistic measurements. | Candidate-specific structures, component/atom mappings, quality reports, reaction geometry and supported interaction/energetic evidence. |
| 6. Optimize using results | Diagnose observed steric, alignment or stability weaknesses and execute a revised sequence-design/search strategy addressing them. | Observation-linked decision, changed strategy/region/constraints, distinguishing expected effect and new tool-generated sequences. |
| 7. Re-evaluate revisions | Repeat affected objective, stability and candidate-specific reaction-complex checks on revised variants, including direct evaluation of combinations. | Revised observations, actual structures, reaction-state safeguards and matched parent/initial-batch comparisons. |
| 8. Select and compare | Apply mandatory evidence rules, rank eligible variants, seal the selection and obtain a separate common-protocol evaluation. | Final sequences, sealed ranking, numerical comparison, failed/unresolved stages, usage and final report. |

Use the following initial profile unless a reviewed comparison freezes different equal limits. This is a bounded variant-design task, not a reproduction of SubTuner's original library size or compute allocation.

| Limit | Initial profile |
| --- | --- |
| Initial generation target | Approximately 12 unique non-native variants; record actual draws and unique counts. |
| Maximum unique sequences including parent | 24 |
| Maximum substitutions per variant | 8 |
| Sequence revision rounds | At least 1 results-driven round; maximum 2. |
| Initial detailed structural assessment | Parent plus at least 5 eligible initial variants; record any shortfall explicitly. |
| Final structural assessment | Every proposed final candidate. |
| Maximum scientific submission attempts | 60 |
| Maximum final candidates | 5 |

Freeze numeric model-token, compute, financial and wall-time ceilings before comparing approaches, including specialist calls in the assisted total. Record actual tool/model versions, reaction/preparation parameters, sampling settings, seeds or limitations and output counts.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Parent identity and allowed edits | Complete sequences, construct/assembly, protected-position mapping, edits, length and hashes. | Require unchanged length and protected/out-of-mask identities within the frozen mutation budget. |
| Generation and revision | Initial/revised native generation outputs, actual unique variants, lineage and observation-linked decisions. | Require tools and at least one new results-driven sequence batch; advisory mutations, reranking or a scoring-input correction alone are insufficient. |
| Primary reaction-related endpoint | Frozen metric, units/sign convention, uncertainty, method/settings and consistent reactant or transition-state definition. | Rank eligible designs in the declared direction; use the same evaluator on parent and candidates. Do not equate docking, electric fields and reaction energies. |
| Stability and expression risks | Supported folding/stability/solubility observations and parent-relative changes. | Apply justified frozen safeguards and retain substrate-expansion/stability trade-offs. |
| Structure quality and chemical identity | Candidate-specific sequence correspondence, structural defects, component identity/state and atom mappings. | Require complete mandatory candidate evidence with both reacting partners; confidence or a parent pose alone is insufficient. |
| Reaction arrangement and mechanistic evidence | Substrate accommodation, reactive-atom geometry, supported interaction/electrostatic measurements and relevant sampling. | Apply state-specific evidence-backed ranges only or descriptive reporting. Pocket size alone is not catalytic evidence. |
| Evidence completeness and resources | Native artifacts, revised/final checks, parameter/source records, failed/unknown stages and available model/scientific usage/cost. | Preserve missing evidence explicitly; do not fabricate results or substitute a zero score for unresolved work. |

Freeze the primary endpoint, eligibility requirements and tie-breakers before design. Rank eligible designs in the declared direction and use candidate ID as the final tie-breaker. A separate evaluator uses one common protocol. Reproducing the published electrostatic endpoint requires compatible chemical models and electronic-structure methods; a narrower frozen proxy comparison cannot be called a SubTuner reproduction.

## Expected Output

**Format:** `enzyme_variant_optimization_bundle`

**Directory:** Separate agent-alone and specialist-assisted run folders under `results/local/athol1/`.

- `RUN_PLAN.json`: frozen parent/reactant/state inputs and hashes, constraints, numeric budgets, methods and common evaluation protocol.
- `candidates.fasta` and `candidate_history.csv`: full parent/variant sequences, edits, hashes, lineage, generation tool/round/settings and native-output references.
- `observations.csv`: baseline, screening and revised/final measurements with units, chemical-state/settings, uncertainty and evidence paths.
- `structure_evidence/`: candidate reaction complexes, residue/atom/component mappings and quality/catalytic/mechanistic reports.
- `decisions.md`: shortlist/revision rationale and actual proposer/critic receipt references in assisted runs.
- `jobs.json` and `usage.json`: submissions, real IDs, statuses, outputs, failed/unknown work and available runtime/resource/cost accounting, without credentials.
- `selection.csv`: final `candidate_id,rank,sequence_sha256` rows excluding the parent; `selection_seal.json` records the selection hash before independent evaluation.
- `REPORT.md`: completed/unresolved stages, numerical parent comparison, final candidates or honest shortfall, method compatibility and limitations. A separate evaluator writes `evaluation.json`.

## Important Instructions

- Scientific source: [SubTuner leverages physics-based modeling to complement AI in enzyme engineering toward non-native substrates](https://doi.org/10.1016/j.checat.2025.101334). This case requires extra chemical preparation; missing advanced resources remain explicit rather than replaced by a different endpoint after seeing results.
- Do not retrieve published winners, mutation identities or outcome tables, read `benchmark/REFERENCE_VALUES.md`, or inspect other-arm results during design. Use permitted primary chemistry sources and record unintended exposure.
- In agent-alone mode do not delegate. In assisted mode use the reviewed native proposer then critic for bounded initial/result-batch advice; the parent executes tools and counts advisory usage within the same budget.
- Use SCI's existing discovery, current input contracts, validation, submissions and artifact handling. Do not add another catalogue, approval layer or job runner.
- Preserve available results and report what remains unresolved.
- Missing required evidence leaves the workflow unfinished. A complete workflow can report no supported improvement. Computed interaction/reactivity scores are not experimental conversion or kinetic measurements.
- The [environment specification](../ENVIRONMENT_SPEC.md), [configuration](../config/workflow.json) and [comparison protocol](../benchmark/PROTOCOL.md) supplement the complete workflow above.
