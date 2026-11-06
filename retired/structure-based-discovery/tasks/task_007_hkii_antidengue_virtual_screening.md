# Task: hkii_antidengue_virtual_screening

## Description

Identify and prioritise existing small-molecule compounds from the supplied library against human hexokinase II through reference-guided screening, drug-likeness and ADME/toxicity assessment, molecular docking and molecular-dynamics analysis. Retrieve analogues related to three reference queries, rank retained compounds, select finalists and compare their binding and dynamics with matched reference controls.

## Target

**Name:** Human hexokinase II (HKII)\
**Protein:** Human HKII, a host metabolic enzyme\
**Disease:** Dengue; computational prioritisation for a host-directed therapeutic strategy\
**Objective:** Produce ranked candidates for each reference-query group, supported by property, docking and dynamics results\
**Binding Region:** Chain A N-terminal glucose/glucose-6-phosphate binding region\
**Data:** A supplied frozen compound library and provenance manifest, with stable compound identifiers and structures\
**PDB:** 2NZT\
**Structure and Context:** The target crystal structure and its bound reference components; prepared protein and ligand inputs for docking and dynamics\
**Reference Inputs:** Alpha-D-glucose (GLC), beta-D-glucose-6-phosphate (BG6) and 2-deoxy-D-glucose, with their supplied chemical-state definitions

## Design Constraints

- **Scope:** A computational workflow using the Boltzmann small-molecule discovery suite and the supplied scientific inputs.
- **Structure preparation:** Prepare the receptor and ligands for the requested analyses. Retain the bound reference structures separately, remove bound small molecules and waters from the docking receptor, assign hydrogens/charges and perform energy minimisation. Record the preparation conditions and any changes to the structures.
- **Library screening:** Screen all three reference-query groups using three-dimensional molecular-shape similarity with atom-feature information, including hydrogen-bonding and aromatic features. Select up to 100 ranked nonreference library analogues per query for property assessment. Retain query membership and the screening results.
- **Drug-likeness:** Assess molecular weight <500 g/mol, hydrogen-bond donors <5, hydrogen-bond acceptors <10 and logP <5. Report the properties, filtering decisions and any stated exceptions. Retain the three reference compounds as controls.
- **ADME/toxicity:** Assess solubility, absorption, distribution, metabolism/excretion and toxicity for the screened candidates. Report available acute toxicity, organ toxicity, cytotoxicity, mutagenicity and immunotoxicity results, together with endpoint definitions, units, selection criteria and missing coverage.
- **Docking:** Dock property-triaged candidates and references into the specified binding region using a 26 × 24 × 22 Å search region. Redock the bound GLC and BG6 references. Record the docking settings, poses, scores and interactions.
- **Candidate selection:** Report the top three supported candidates per query group using docking and interaction evidence, then select one leading candidate per group for dynamics. Report a shortfall when fewer candidates qualify.
- **Molecular dynamics:** Perform 100 ps equilibration with heavy atoms restrained to their initial positions, followed by 20 ns production for each selected leading candidate and its matched reference. When all three groups yield qualifying leads, this comprises three candidate complexes and three reference complexes. Record the simulation conditions.
- **Dynamics analysis:** Analyse backbone RMSD, residue RMSF, protein–ligand distances and hydrogen-bond behaviour, and compare each candidate with its corresponding reference. Report the analysis definitions and units.
- **Interpretation:** Report computational findings and their limitations without asserting experimental inhibition, antiviral efficacy or clinical safety.

## Computational Tool Capabilities

The workflow requires the following capabilities and scientific outputs.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Prepare the target, reference compounds and library for screening, docking and dynamics | Prepared structures, compound identities, library membership and preparation conditions |
| 2. Retrieve and screen library analogues | Rank library compounds by three-dimensional shape/feature similarity to each reference query | Query-specific screening results, ranks and selected analogues |
| 3. Assess properties | Apply drug-likeness criteria and assess ADME/toxicity before docking selection | Compound-level properties, predictions, filtering decisions and retained candidates |
| 4. Dock and rank | Dock retained candidates and references, redock bound references and select ranked candidates | Scores, poses, interactions, reference results and selected group leaders |
| 5. Run molecular dynamics | Prepare and simulate the selected candidate/reference systems | Preparation files, simulation settings, trajectories and completed durations |
| 6. Analyse and report | Compare binding and dynamics results and report prioritised candidates | RMSD/RMSF, distance and hydrogen-bond results, candidate rankings and interpretation |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Input and preparation records | Compound identities, library membership, reference definitions and preparation conditions | Associate reported results with the supplied inputs and documented preparation |
| Screening results | Similarity results, ranks and selected compound counts for each query group | Report all three groups and distinguish query entries from unique compounds |
| Property-based selection | Drug-likeness values, ADME/toxicity predictions, units and filtering decisions | Explain candidate retention using the stated criteria and available predictions |
| Reference docking | Redocked GLC/BG6 poses and reference docking results | Report the reference conformations and binding results alongside candidate results |
| Candidate ranking | Candidate scores, poses, interactions and corresponding reference comparisons | Support the reported top candidates and selected group leaders with binding evidence |
| Dynamics results | Equilibration/production duration, backbone RMSD, residue RMSF, distances and hydrogen-bond behaviour | Report 100 ps equilibration and 20 ns production for selected candidate/reference systems, with comparisons and consistent definitions/units |
| Workflow completion | Completed stages, scientific outputs and remaining requirements | Distinguish completed execution from incomplete or unavailable stages |

Report undefined or unavailable measurements explicitly. The scientific results and completion assessment must be supported by the retained outputs.

## Expected Output

**Format:** `small_molecule_vs_bundle`\
**Directory:** `results/task_007/<run_id>/`

| File | Content |
| --- | --- |
| `input_manifest.json` | Target/reference definitions, library provenance, input records and preparation conditions |
| `workflow_plan.json` | Workflow stages, chosen methods, scientific parameters and selection criteria |
| `screening_results.csv` | Library compound identities, query membership, similarity results and ranks |
| `property_results.csv` | Properties/predictions, units, filtering decisions and missing endpoints |
| `binding_results.csv` | Candidate/reference docking results, interactions and associated pose files |
| `candidate_results.csv` | Ranked candidates by query group, selected leaders and reference comparisons |
| `dynamics_results.csv` | Simulated systems, conditions, completed durations, RMSD/RMSF, distance and hydrogen-bond results |
| `artifact_manifest.csv` | Scientific output files, corresponding jobs/stages and artifact locations |
| `workflow_assessment.json` | Completed stages, query-group outcomes, dynamics status and remaining requirements |
| `report.md` | Methods, results, interpretation and limitations |

Retain the prepared structures, docking poses, simulation preparation files, trajectories and analysis outputs with the result bundle.

**Completion Rule:** Report workflow outcomes for all 3 reference-query groups. Complete the applicable screening, filtering, docking, candidate-selection and candidate/reference dynamics stages before claiming complete execution. Report missing candidates, inputs, capabilities or results explicitly.

Return the assessment in this format:

```text
<EVAL_ANSWER>
{"completion_status":"<COMPLETE|PARTIAL|NEEDS_INPUT>","query_groups_evaluated":["<evaluated group identifiers>"],"dynamics_status":"<COMPLETE|PARTIAL|UNAVAILABLE|NO_QUALIFYING_CANDIDATE>","unresolved_requirements":["<specific remaining requirements, or an empty list>"]}
</EVAL_ANSWER>
```

Use `GLC`, `BG6` and `2DG` as query-group identifiers. The answer fields must match the reported scientific outputs and `workflow_assessment.json`.

## Constraints

- **Execution Budget:** Follow the resource limits and deadline supplied with the run.
- **Reference Policy:** Use the supplied scientific inputs and public input records. Evaluator-only outcomes must not guide candidate selection or be copied into run results.
- **Inputs:** Use the fixed library and reference definitions supplied for the benchmark run.
- **Records:** Retain scientific settings, job records, inputs, outputs and stated limitations.

## Important Instructions

- Return NEEDS_INPUT when required inputs are unavailable.
- Report incomplete execution as PARTIAL and identify the remaining requirements.
- Keep unavailable measurements unresolved; do not invent results.
- Distinguish a lack of qualifying candidates from missing inputs or failed execution.
- Base the final conclusions on the completed scientific work.
