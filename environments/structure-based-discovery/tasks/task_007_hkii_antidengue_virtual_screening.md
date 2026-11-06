# Task: hkii_antidengue_virtual_screening

## Description

Identify and prioritise existing small-molecule compounds from the supplied library against human hexokinase II through reference-guided screening, drug-likeness and ADME/toxicity assessment, molecular docking and molecular-dynamics validation. Retrieve library analogues related to three reference queries, rank retained compounds by binding evidence, select finalists and compare their dynamics with matched reference controls.

## Target

**Name:** Human hexokinase II (HKII)\
**Protein:** Human HKII, a host metabolic enzyme\
**Disease:** Dengue; computational prioritisation for a host-directed therapeutic strategy\
**Objective:** Return an evidence-backed, ranked candidate set for each reference-query group, with reference comparisons and explicit limitations\
**Binding Region:** Chain A N-terminal glucose/glucose-6-phosphate binding region; establish its location in the actual prepared structure\
**Data:** A run-supplied frozen compound library and provenance manifest, with stable identifiers and structures; retain exact membership and do not replace the benchmark library without an explicit run specification\
**PDB:** 2NZT\
**Structure and Context:** Inspect the supplied structure, co-crystallised components, chemical states, missing atoms/residues and preparation changes before binding assessment\
**Reference Inputs:** Alpha-D-glucose (GLC), beta-D-glucose-6-phosphate (BG6) and 2-deoxy-D-glucose; independently validate their structures, identifiers, stereochemistry and chemical states

## Design Constraints

- **Execution scope:** Perform scientific workflow stages through verified capabilities in the Boltzmann small-molecule discovery suite. Choose appropriate methods and tools from the available inventory and document the choices.
- **Input integrity:** Preserve original inputs, assign stable compound identifiers, record chemical states and retain an auditable record of exclusions and transformations. Validate and freeze the reference chemical states before screening. Retrieve missing public input records by verified identifiers where possible; unresolved library membership or reference identity requires NEEDS_INPUT. Do not silently change stereochemistry or molecular identity.
- **Structure preparation:** Preserve the original complex and extract relevant bound reference structures before preparing a docking copy. Remove bound small molecules and waters from that copy, assign chemically appropriate hydrogens/charges and perform energy minimisation. Validate ligand geometry and compatible input representations. Inspect missing atoms/residues and record all structural repairs, minimisation settings and coordinate transformations; unsupported required preparation remains unresolved.
- **Library analogue screening:** Evaluate all three reference-query groups using three-dimensional molecular-shape similarity with atom-feature information, including hydrogen-bonding and aromatic features. Select up to 100 ranked nonreference analogues present in the fixed library per query for property triage, retaining group membership and duplicate records transparently. Preserve candidate molecular identities during conformer preparation and record the score definition and conformer procedure. A two-dimensional similarity result alone does not establish completion of this stage.
- **Binding-site validity:** Establish the assessment region from the actual prepared structure and relevant reference evidence. Use a 26 × 24 × 22 Å search region at the specified binding site and derive its centre in the actual coordinate frame. Verify that the region contains the intended protein/ligand site. Record unsupported controls or any separately declared adaptation; an empty or incorrectly located region is not a valid binding assessment.
- **Drug-likeness:** Assess the initial criteria of molecular weight <500 g/mol, hydrogen-bond donors <5, hydrogen-bond acceptors <10 and logP <5. Retain all reference compounds as controls irrespective of these filters. Record individual violations and exclusions. Any justified exception policy must be declared before reviewing screening/filtering outcomes; do not silently relax the criteria to obtain a desired hit count.
- **ADME/toxicity:** Assess solubility, absorption, distribution, metabolism/excretion and toxicity evidence relevant to the retained candidates. Include endpoint-level acute toxicity, organ toxicity, cytotoxicity, mutagenicity and immunotoxicity coverage where available. State endpoint definitions, units, prediction models, selection rules and unavailable coverage. Declare the required endpoint coverage before selection. Completion requires actual ADME and toxicity evidence supporting the selection rules; an unavailable required endpoint is an execution gap, not a favourable prediction.
- **Reference controls:** Process candidates and references under comparable preparation and assessment settings. Assess reference pose recovery where a suitable crystallographic reference exists, using consistent atom identities and the common receptor coordinate frame. A pose-to-best-mode displacement is not a pose-to-crystal recovery measurement. Keep score, pose and interaction evidence distinct.
- **Candidate prioritisation:** Dock the property-triaged candidates and all three references. Rank candidates using docking scores, poses and interaction evidence; report the top three supported candidates per query group and select one leading candidate per group for dynamics. If a group has insufficient qualifying candidates, report the shortfall without manufacturing favourable results or forcing selection counts.
- **Dynamics validation:** Prepare compatible candidate/reference systems, perform 100 ps equilibration with heavy atoms restrained to their initial positions and 20 ns production for each selected leading candidate and its matched reference. The full three-group comparison comprises three candidate complexes and three reference complexes when qualifying leads exist. Record and justify parameterisation, force field, solvent, thermodynamic conditions, timestep, restraint, equilibration, production, output sampling and analysis settings. Analyse backbone RMSD, residue RMSF, protein–ligand distances and hydrogen-bond behaviour using consistent definitions. Shorter trajectories or preparation attempts do not satisfy the requested production duration.
- **Interpretation:** Computational binding or property predictions support prioritisation; they do not establish inhibition, antiviral efficacy or clinical safety. The workflow is computational only.

## Computational Tool Capabilities

Inspect the current suite inventory, input contracts, output artifacts and method limitations before selecting tools. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Audit and prepare inputs | Validate the target, reference structures and library; prepare compatible scientific inputs | Original/prepared input records, identifiers, chemical states, provenance, exclusions and preparation settings |
| 2. Retrieve and screen library analogues | Find and rank existing library compounds by three-dimensional shape/feature similarity to each reference query | Library membership, conformer handling, query-specific rankings, method/settings and stage counts |
| 3. Assess properties and risks | Apply drug-likeness criteria and assess ADME/toxicity before docking selection | Endpoint-level results, units, model identities, declared filters, exclusions and missing coverage |
| 4. Assess binding and controls | Dock retained candidates and references at the validated target region, then select ranked candidates and group leaders | Effective region and preparation settings, docking scores, poses, reference checks, interaction evidence and selection rationale |
| 5. Validate dynamics | Prepare and simulate selected candidate/reference systems with the required equilibration and production durations | Parameterisation records, completed durations, trajectories, RMSD/RMSF, distance and hydrogen-bond summaries |
| 6. Integrate evidence and report | Rank candidates using the recorded evidence and assess workflow completeness | Finalists by query group, reference comparisons, tool-selection rationale, complete artifacts and limitations |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Input integrity and traceability | Validated identities, chemical states, library size, exclusions and retained input artifacts | Every reported candidate and reference must map to a documented input; identity-changing transformations must be explicit |
| Screening coverage | Counts and rankings by query group, three-dimensional shape/feature evidence, conformer handling and filter attrition | Verify candidate membership in the fixed library, reconcile entry counts and unique identities separately, preserve the requested screening method and explain exclusions; do not force a predetermined retained yield |
| Property-based selection | Compound-level properties, endpoint coverage, model identities, units and declared selection rules | Establish endpoint coverage from model definitions rather than names alone; missing predictions remain unresolved and predictions must support the actual selection decisions |
| Binding-region and reference validity | Effective region, coordinate-frame checks, reference poses, available recovery metrics and contemporaneous reference results | Binding claims require a valid region and interpretable controls; score agreement alone does not establish pose recovery |
| Candidate prioritisation | Finalists, reference-relative comparisons and supporting pose/property evidence | Compare compatible methods and protocols; do not treat scores from different models as interchangeable or equate a score with measured affinity |
| Dynamics evidence | Completed equilibration/production duration, analysed systems, atom selections, alignment, units and time-series summaries | Verify 100 ps equilibration and 20 ns production from logs and trajectories per selected candidate/reference system; missing requested systems or incomplete trajectories leave the validation stage incomplete |
| Workflow completeness | Stage outcomes, job records, artifact availability, exclusions and limitations | Classify the run from executed evidence; unavailable required stages prevent a complete-workflow claim |

State undefined or unmeasurable metrics explicitly. Use thresholds justified for the chosen methods and decision, rather than assuming a universal score cutoff.

## Expected Output

**Format:** `small_molecule_vs_bundle`\
**Directory:** `results/task_007/<run_id>/`

| File | Content |
| --- | --- |
| `input_manifest.json` | Target/reference identities, library provenance, input hashes, preparation records and chemical-state choices |
| `workflow_plan.json` | Selected capabilities, verified input/output contracts, effective settings, selection rules and required/optional stages |
| `screening_results.csv` | Candidate identities, query membership, screening ranks/results and reconciled stage counts |
| `property_results.csv` | Properties/predictions, units, model identities, filtering decisions and missing endpoints |
| `binding_results.csv` | Candidate/reference results, effective protocol identifiers and links to pose/interaction artifacts |
| `candidate_results.csv` | Ranked finalists by query group, reference comparisons, selection rationale and limitations |
| `dynamics_results.csv` | Requested systems, candidate/reference roles, completion status, actual equilibration/production durations, analysis definitions/units, RMSD/RMSF/distance/hydrogen-bond summaries and links to retained trajectories and analysis files |
| `artifact_manifest.csv` | Original platform output filenames, corresponding job/stage, locations and integrity information |
| `workflow_assessment.json` | Completion status, query-group coverage, stage outcomes, dynamics status and unresolved requirements |
| `report.md` | Scientific reasoning, tool-selection rationale, results, controls, exclusions and interpretation |

Retain all available native structure, pose and other platform outputs alongside these tables. Retain dynamics preparation files, settings, trajectories and analysis artifacts for every simulated system; report unavailable exports explicitly. For a required but unexecuted system, record its status/reason and leave its numerical measurements missing rather than inventing a completed result.

**Completion Rule:** All 3 query groups must have an auditable screening, filtering, docking and candidate-selection outcome, with justified reference comparisons and reconciled artifacts. Complete dynamics validation for every selected candidate and matched reference before claiming a complete candidate-validation workflow. If no candidate qualifies in a group, report that scientific outcome explicitly rather than inventing a candidate or claiming its simulation ran. An unsupported or unexecuted required capability leaves the run PARTIAL or NEEDS_INPUT.

Return the assessment in this form, with actual values replacing the descriptions:

```text
<EVAL_ANSWER>
{"completion_status":"<COMPLETE|PARTIAL|NEEDS_INPUT>","query_groups_evaluated":["<evaluated group identifiers>"],"dynamics_status":"<COMPLETE|PARTIAL|UNAVAILABLE|NO_QUALIFYING_CANDIDATE>","unresolved_requirements":["<specific missing requirements, or an empty list>"]}
</EVAL_ANSWER>
```

Use distinct identifiers from `GLC`, `BG6` and `2DG` for `query_groups_evaluated`; these identify the declared query groups, not automatically validated database component codes. The answer fields must agree with `workflow_assessment.json`, the stage evidence and the report. COMPLETE requires all three groups and no unresolved required stages. NO_QUALIFYING_CANDIDATE is valid only after completed screening and property assessment establish that no candidate qualifies; it cannot represent a failed tool or unavailable prediction.

## Constraints

- **Execution Budget:** Follow the resource limits and deadline supplied by the execution context; record actual working time, job duration and unfinished work.
- **Reference Policy:** Use the supplied scientific inputs, public input records and platform documentation. Evaluator-only reference outcomes must not guide candidate selection or be copied into run results.
- **Input Policy:** Use the fixed run inputs for benchmark comparisons. If the library or required reference definition is absent and cannot be retrieved unambiguously, return NEEDS_INPUT; a separately chosen exploratory library is a different experiment.
- **Reproducibility:** Preserve job identifiers, effective settings, input/output provenance and secret-free execution records. Make every reported count and comparison reproducible.
- **Scope:** Use scientific capabilities available through the Boltzmann suite; report any unavailable required capability rather than supplying it through an undeclared external scientific service.

## Important Instructions

- Independently select relevant suite capabilities and execute the workflow in the stated order. No particular implementation is prescribed.
- Validate actual input/output compatibility and method suitability before submitting work.
- Mark missing prerequisites as NEEDS_INPUT and required execution gaps as PARTIAL; neither represents a completed workflow.
- Distinguish scientific rejection of a candidate from preparation failure, unavailable predictions or missing data.
- Preserve chemical identity and coordinate-frame consistency throughout the workflow.
- Keep unavailable measurements unresolved, and base the final assessment on executed evidence.
