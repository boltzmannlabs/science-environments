# Task: rml_stability

## Description

Generate and optimize **Rhizomucor miehei lipase variants with improved predicted stability and retained functional structure**. Complete parent preparation, baseline evaluation, tool-based sequence generation, property screening, candidate structures and substrate assessment, results-driven sequence optimization, re-evaluation and final comparison.

Agent-Scientist chooses suitable tools from **Boltzmann, ToolUniverse or both**. A language-model-written mutation list, a stability scan alone or a simulation of known mutants does not complete the assignment. Generate new candidates and assess the parent under matched conditions.

## Target

| Field | Task definition |
| --- | --- |
| Enzyme | Mature Rhizomucor miehei lipase, RML. |
| Parent source | Establish the exact 269-residue study parent and a suitable source structure/model independently of its winning mutants; no unverified PDB accession is imposed. |
| Target reaction | Lipase hydrolysis, using 4-nitrophenyl laurate (pNPL) for substrate/structural assessment. |
| Substrate context | Verify pNPL identity, chemical state and reaction-specific water requirements. |
| Operating context | 50°C thermal context; declare and match pH/other modeled conditions. Do not infer an experimental half-life from a generic stability score. |
| Protected features | Verified Ser144, Asp203 and His257, oxyanion-hole, lid, required disulfides and structural ion features. |
| Objective | Improve a frozen computational stability endpoint relative to the parent while retaining required substrate/catalytic/quality safeguards. |
| Shared inputs | Exact mature sequence/structure, residue mapping, pNPL state, protected/editable positions, chemistry sources and final evaluator. |

## Design Constraints

- Preserve the verified mature construct and sequence length. Do not silently substitute a precursor or an existing engineered variant for the parent.
- Select editable positions from parent structure, conservation and stability evidence. Preserve protected catalytic, lid, disulfide and ion features according to the frozen edit mask.
- Execute sequence-design, mutation-search or library-generation tools for initial and revised candidates. Record actual generation settings, seeds, draws and unique full-length outputs.
- Assign unique candidate IDs, lineage and sequence hashes; separate generated draws, native recoveries, duplicate sequences and evaluated variants.
- Evaluate combined mutations directly rather than adding their single-mutant predictions. Retain stability–function trade-offs.
- Require candidate-specific pNPL complexes and quality/catalytic assessments for final designs. A small docking change is not evidence of improved hydrolysis.
- Return up to five supported non-native candidates without padding missing or failed results.

## Computational Tool Capabilities

Execute the following workflow using appropriate tools selected through native SCI from Boltzmann, ToolUniverse or both. Save actual tool inputs and outputs; a planned call does not complete a stage. Required unavailable evidence remains unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Establish mature RML identity, construct/structure correspondence, catalytic/lid features, pNPL chemical state and reaction context. Freeze inputs, edit mask, budgets and final evaluator. | Prepared parent/substrate, residue/atom mapping, sources, protected/editable positions and `RUN_PLAN.json`. |
| 2. Evaluate parent baseline | Calculate the selected stability endpoint and required solubility, structural-quality and pNPL/catalytic safeguards for the parent. | Numeric baseline, method versions/settings, native outputs, units, state and uncertainty. |
| 3. Generate variant sequences | Execute an appropriate constrained design/search tool to produce complete RML variants within the allowed positions and mutation budget. | Sequences, edits, IDs/hashes, algorithm/model, sampling settings, actual draws and native generation outputs. |
| 4. Screen properties | Assess stability, expression-related risks and relevant functional predictions. Choose an initial structural shortlist using declared rules. | Per-candidate observations, matched parent changes, exclusions, uncertainty and documented shortlist. |
| 5. Assess structures and function | Model shortlisted variants and pNPL complexes; verify sequence and substrate identity and assess quality, lid/active-site changes, contacts and geometry. | Candidate-specific structures, confidence, complete-complex quality results, mappings and reaction-relevant measurements. |
| 6. Optimize using results | Identify observed stability losses, exposed hydrophobicity, lid disruption or substrate problems; execute a new design/search batch targeting the weakness. | Evidence-linked revision decision, changed strategy/constraints, expected observation and new tool-generated sequences. |
| 7. Re-evaluate revisions | Repeat affected stability/property and candidate-specific structure/complex assessments, including direct evaluation of combinations. | Revised metrics, actual structures, functional safeguards and comparisons with the parent and initial batch. |
| 8. Select and compare | Apply mandatory evidence requirements, rank eligible variants, seal the selection and obtain a separate common-protocol evaluation. | Final sequences, sealed ranking, quantitative comparison, failures, usage and final report. |

Use the following initial profile unless a reviewed comparison freezes different equal limits. These are environment settings, not the paper's screening protocol.

| Limit | Initial profile |
| --- | --- |
| Initial generation target | Approximately 12 unique non-native variants; retain actual generation counts. |
| Maximum unique sequences including parent | 24 |
| Maximum substitutions per variant | 8 |
| Sequence revision rounds | At least 1 results-driven round; maximum 2. |
| Initial detailed structural assessment | Parent plus at least 5 eligible initial variants; record any shortfall rather than padding. |
| Final structural assessment | Every proposed final candidate. |
| Maximum scientific submission attempts | 60 |
| Maximum final candidates | 5 |

Freeze numeric model-token, compute, financial and wall-time ceilings before comparing approaches. Include specialist calls in the assisted total. Record actual method/model versions, generation settings, seeds or limitations and output counts.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Parent identity and allowed edits | Mature construct, full sequences, residue mapping, protected features, edits and hashes. | Preserve length, protected/out-of-mask identities and the frozen mutation budget. |
| Generation and revision | Initial/revised native generation records, unique sequences, lineage and observation-linked decisions. | Require actual generation tools and a new sequence round informed by results; reranking or a scoring-input correction alone is insufficient. |
| Primary stability objective | Declared mutation/stability endpoint, native units, sign convention and matched parent/candidate settings. | Rank eligible candidates in the frozen direction. Do not mix predictors with opposite sign conventions or call a stability score an experimental half-life. |
| Expression-related risks | Solubility and other declared sequence/developability measurements. | Apply frozen justified safeguards and retain uncertainty and trade-offs. |
| Structural quality and functional features | Candidate-specific sequence mapping, confidence, clashes, backbone/side-chain/ligand findings, lid and required structural components. | Require complete mandatory evidence; parent coordinates or confidence alone do not qualify a candidate. |
| Substrate and catalytic assessment | pNPL identity/state, atom mapping, contacts and reaction-specific geometry. | Use supported acceptance ranges only; otherwise retain descriptive measurements. Docking is not a catalytic-rate measurement. |
| Completeness and resource use | Native artifacts, revised/final assessments, job statuses, failures and available cost/runtime/resource records. | Preserve unknowns and required-evidence gaps; no fabricated outputs or zero substitution for missing values. |

Freeze the common final stability endpoint, functional safeguards and tie-breakers before design. Rank eligible variants by the primary endpoint in its declared direction, with candidate ID as the last deterministic tie-breaker. Keep docking and experimental half-life as separate endpoints; historical comparisons need compatible methods, units and chemical states.

## Expected Output

**Format:** `enzyme_variant_optimization_bundle`

**Directory:** `results/local/rml/agent-alone/` or `results/local/rml/agent-with-specialist/`, according to the selected approach.

- `RUN_PLAN.json`: exact parent/substrate inputs and hashes, constraints, numeric budgets, method settings and frozen evaluation protocol.
- `candidates.fasta` and `candidate_history.csv`: full parent/variant sequences, edits, hashes, generation tool/round, lineage and output provenance.
- `observations.csv`: baseline, screening and revised/final measurements with units, settings, uncertainty and native evidence references.
- `structure_evidence/`: candidate-specific structures and pNPL complexes, mappings, quality findings and catalytic measurements.
- `decisions.md`: shortlisting/revision rationale and actual proposer/critic receipt references in assisted runs.
- `jobs.json` and `usage.json`: submissions, real IDs, statuses, outputs, failures/unknowns and available resource/runtime/cost accounting; no credentials.
- `selection.csv`: final `candidate_id,rank,sequence_sha256` rows excluding the parent, plus `selection_seal.json` before independent evaluation.
- `REPORT.md`: workflow completion, parent-relative results, final candidates or honest shortfall, trade-offs and limitations. A separate evaluator produces `evaluation.json`.

## Important Instructions

- Scientific source: [Computer-Aided Design to Improve the Thermal Stability of Rhizomucor miehei Lipase](https://doi.org/10.3390/foods13244023). Establish source construct/model identity without retrieving winner mutations; the task does not reproduce experimental oil conversion or half-life assays.
- Do not access published winning sequences/mutations, outcome tables, `benchmark/REFERENCE_VALUES.md` or the other approach's results during design. Use permitted primary sources for parent identity and chemistry, and log unintended outcome exposure.
- Agent-alone runs do not delegate. Assisted runs use the reviewed native proposer then critic for initial/result-batch advice; the parent executes tools and includes advisory calls in the same budget.
- Use existing SCI discovery, current input contracts and normal execution/artifact handling. No separate registry, approval layer or custom job runner is required.
- Preserve available results and report what remains unresolved.
- Missing essential evidence leaves the workflow unfinished. A complete run can report no supported improvement. Computational stability, docking and geometry are not experimental performance.
- The [environment specification](../ENVIRONMENT_SPEC.md), [configuration](../config/workflow.json) and [comparison protocol](../benchmark/PROTOCOL.md) supplement the full task workflow stated above.
