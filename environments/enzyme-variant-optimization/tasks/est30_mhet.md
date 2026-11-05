# Task: est30_mhet

## Description

Generate and optimize **Est30 enzyme variants for MHET hydrolysis** while preserving catalytic function and managing stability. Execute the full sequence of parent preparation, baseline evaluation, tool-based variant generation, property screening, candidate structure and substrate assessment, results-driven sequence optimization, re-evaluation and final comparison.

Agent-Scientist selects suitable tools from **Boltzmann, ToolUniverse or both**. A mutation list written by the language model, a prediction-only exercise or a simulation of known mutants does not complete this task. Evaluate the parent alongside independently generated variants.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Thermophilic carboxylesterase Est30. |
| Parent source | [PDB 1TQH](https://www.rcsb.org/structure/1TQH); recover the full parent sequence and map observed/modelled residues to it. |
| Target reaction | MHET hydrolysis to terephthalate and ethylene glycol; include water where required by the selected reaction model. |
| Substrate context | Establish MHET protonation and atom correspondence from primary chemistry evidence. Do not treat the crystallographic ligand as the MHET reactant. |
| Operating context | pH 7.5 and 50°C. Record which calculations actually represent these conditions. |
| Protected features | Verified Ser94, Asp193 and His223, required oxyanion-hole features and parent functional architecture. |
| Objective | Improve a frozen reaction-relevant computational endpoint relative to the parent while retaining required structural and stability safeguards. |
| Shared inputs | Exact parent sequence/structure, residue mapping, substrate state, chemistry sources, allowed edits and final evaluation protocol. |

## Design Constraints

- Use substitutions in the verified parent construct and preserve its length. Select editable positions using parent structure, conservation or design-tool evidence, not published winners.
- Preserve the mapped catalytic triad and required oxyanion-hole features. Retain relevant chains and chemical components; document modeled missing residues.
- Execute a suitable constrained sequence-design, mutation-search or library-generation tool for both initial and revised sequences. Record model/algorithm identity, settings, seeds, actual draws and unique outputs.
- Assign stable candidate IDs, parentage and sequence hashes. Separate proposed variants, generated draws, unique non-native sequences and structurally assessed candidates.
- Evaluate candidate-specific MHET complexes. Parent coordinates, fold confidence and a favorable kinetic prediction do not replace chemical-state, quality or catalytic assessments.
- Assess combined mutations directly. Do not assume that favorable single-mutation effects add together.
- Return up to five supported non-native candidates. Do not fill the selection with failed or unresolved designs.

## Computational Tool Capabilities

Execute these stages in order, allowing inexpensive screening before expensive modeling. Choose the actual tools from current native SCI capabilities and contracts; the capability is mandatory, not a particular vendor or model name. Preserve unavailable required evidence as unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Establish Est30 construct identity, sequence/structure correspondence, protected positions, MHET chemical state and reaction chemistry. Freeze inputs, conditions, budgets and final evaluator before design. | Prepared parent and substrate files, residue/atom mappings, primary sources, edit mask and `RUN_PLAN.json`. |
| 2. Evaluate parent baseline | Calculate the selected reaction/property endpoint and required stability, structure-quality and substrate/catalytic safeguards for the parent. | Numerical parent observations with units, native outputs, method settings and chemical-state limitations. |
| 3. Generate variant sequences | Execute an appropriate sequence-design or mutation-search tool within the edit mask and mutation limit. Produce complete variants rather than advisory substitutions alone. | Full sequences, edits, candidate IDs/hashes, generation tool, seeds/settings, draws, deduplicated outputs and provenance. |
| 4. Screen properties | Evaluate reaction-relevant predictions and stability/solubility risks. Select a structural shortlist using the frozen rules and retain trade-offs and uncertainty. | Per-candidate scores, parent comparisons, exclusions and a documented initial shortlist. |
| 5. Assess structures and function | Predict/model the shortlisted sequences and their MHET complexes; check sequence identity, structural quality, ligand state, contacts and catalytic geometry. | Candidate-specific structures, confidence, complete-complex quality reports, substrate/atom mappings and geometry measurements. |
| 6. Optimize using results | Diagnose actual weaknesses such as poor substrate orientation or stability loss, then execute a revised sequence-generation/search step addressing them. | Observation-linked decision, changed design region/strategy or constraints, expected effect and new tool-generated sequences. |
| 7. Re-evaluate revisions | Repeat affected property and structural/complex checks on revised variants. Assess all proposed final candidates under comparable conditions. | Revised observations, actual structures, quality/geometry findings and direct comparisons with the parent and initial batch. |
| 8. Select and compare | Apply mandatory evidence requirements, rank eligible designs, seal the final selection and pass it to a separate evaluator. | Final sequences, ranked sealed selection, common-protocol comparison, failures, resource use and final report. |

Use the following initial execution profile unless a reviewed comparison freezes different equal limits for both approaches. These are task settings, not values taken from the motivating study.

| Limit | Initial profile |
| --- | --- |
| Initial generation target | Approximately 12 unique non-native variants; record actual draws and unique counts. |
| Maximum unique sequences including parent | 24 |
| Maximum substitutions per variant | 8 |
| Sequence revision rounds | At least 1 results-driven round; maximum 2. |
| Initial detailed structural assessment | Parent plus at least 5 eligible initial variants; retain any shortfall explicitly. |
| Final structural assessment | Every proposed final candidate. |
| Maximum scientific submission attempts | 60 |
| Maximum final candidates | 5 |

Freeze numeric model-token, compute, financial and wall-time ceilings before comparison; include specialist usage in the assisted total. Record model versions, sampling settings, seeds or seed limitations, and actual outputs. Insufficient eligible designs must not be padded with duplicates or invented successes.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Parent identity and allowed edits | Complete sequences, construct/residue mapping, protected-position identities, mutation counts and hashes. | Require unchanged parent length, no protected/out-of-mask edits and compliance with the frozen limits. |
| Generation and optimization | Actual initial/revised tool outputs, unique variants, parentage and observation-linked revision decisions. | Require executed tool-based generation and at least one new sequence round informed by results; reranking or repairing a scoring input alone is insufficient. |
| Reaction-related objective | Frozen primary endpoint, native units, uncertainty and matched parent/candidate settings. | Rank eligible designs in the declared direction; a kinetic prediction, binding score and experimental activity are not interchangeable. |
| Stability and expression risks | Declared stability/solubility assessments and parent-relative changes. | Apply only frozen justified safeguards and retain activity–stability trade-offs. |
| Structural quality and identity | Candidate-specific sequence correspondence, missing coordinates, confidence, clashes and relevant backbone/side-chain/ligand findings. | Require complete mandatory evidence and a correctly identified candidate complex; confidence alone is not catalytic evidence. |
| MHET positioning and catalytic features | Ligand identity/state, atom mapping, contacts, reaction-relevant distances/angles and sampling information. | Apply evidence-backed state-specific ranges only. Without justified ranges, report descriptive measurements; static geometry is not trajectory occupancy. |
| Evidence completeness and resources | Native job/artifact references, settings, revised/final evaluations, pending/failed stages and available usage/cost. | Preserve missing results explicitly; do not convert unknown observations to zero or fill an incomplete selection. |

Freeze the primary endpoint, eligibility rules and tie-breakers before design. Rank eligible variants by that endpoint in its declared direction, using candidate ID as the final deterministic tie-breaker. Retain secondary metrics separately. A separate evaluator compares sealed selections under one common protocol; historical comparisons require compatible methods, units and chemical states.

## Expected Output

**Format:** `enzyme_variant_optimization_bundle`

**Directory:** Separate run folders under `results/local/est30/` for agent-alone and specialist-assisted executions.

- `RUN_PLAN.json`: frozen parent/chemical inputs and hashes, constraints, numeric budgets, tool settings and common final-evaluation protocol.
- `candidates.fasta` and `candidate_history.csv`: complete parent/variant sequences, identities, edits, lineage, generation tools, rounds and raw-output references.
- `observations.csv`: parent and candidate measurements, units, settings, uncertainty and actual evidence paths.
- `structure_evidence/`: candidate structures, MHET complexes, residue/atom mappings and structure-quality/catalytic reports.
- `decisions.md`: screening, shortlisting and revision rationale; assisted runs include actual proposer/critic receipt references.
- `jobs.json` and `usage.json`: real submissions, IDs, statuses, outputs, failures/unknowns and available runtime/resource/cost accounting, without credentials.
- `selection.csv`: ordered `candidate_id,rank,sequence_sha256` rows excluding the parent; `selection_seal.json` records the selection hash before independent evaluation.
- `REPORT.md`: completed and unresolved stages, numerical parent comparison, final selection or honest shortfall, trade-offs and limitations. The separate evaluator writes `evaluation.json`.

## Important Instructions

- Apply the shared [execution-error and output-recovery requirements](../ENVIRONMENT_SPEC.md#execution-errors-and-recovery).

- Scientific source: [Computational design of highly efficient thermostable MHET hydrolases and dual enzyme system for PET recycling](https://doi.org/10.1038/s42003-023-05523-5). This task adapts the problem, not a promise to reproduce its exact methods or values.
- Do not retrieve published winning sequences, mutations or outcome tables, read `benchmark/REFERENCE_VALUES.md`, or inspect the other approach's results during design. Research reaction chemistry using permitted primary sources; record unintended exposure.
- Old local Est30 runs used different generation requirements and are not results for this task version. Est30 is not an unseen rediscovery test.
- In agent-alone mode do not delegate. In assisted mode use the reviewed native proposer then critic for bounded initial/result-batch advice; the parent executes scientific tools and counts all calls within the shared budget.
- Use SCI's existing discovery, input validation, submissions and artifact handling. Follow each selected tool's actual input contract. No additional registry, approval layer or custom job runner is required.
- Preserve available results and report what remains unresolved.
- Report only actual observations. Missing required evidence leaves the workflow unfinished. A complete workflow can find no supported improvement; predictions do not demonstrate experimental improvement.
- The [environment specification](../ENVIRONMENT_SPEC.md), [configuration](../config/workflow.json) and [comparison protocol](../benchmark/PROTOCOL.md) provide shared details; all required execution stages are stated above.
