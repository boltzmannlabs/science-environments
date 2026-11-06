# Task: d2r_peripheral_candidate_prioritisation

## Objective

Identify and rank promising compounds from the supplied library for human dopamine D2 receptor (D2R). Use the available reference compounds as controls. Choose and justify an appropriate workflow, assess the selected candidates against the task criteria, and report the results, limitations and evidence supporting the final ranking.

## Target

**Name:** Human dopamine D2 receptor (D2R)\
**Protein:** Human dopamine D2 receptor (DRD2)\
**Disease:** Neuroprotection research; a proposed peripheral D2R–prolactin strategy\
**PDB:** 6CM4\
**Structure and Context:** The crystal structure of human D2R in complex with risperidone is supplied as target information. The deposited structure contains unresolved atoms and regions, documented in the accompanying structure information. Additional receptor structures 6A93, 3RZE and 7B6W are available as supporting context.\
**Reference Inputs:** Risperidone (8NU) as the primary reference and domperidone as an additional peripheral-reference compound; accompanying receptor structures include their native bound reference molecules

## Inputs

- **Target:** `inputs/targets/6CM4_crystal_complex.pdb`, the original source coordinates, and `inputs/targets/target_registry.csv`. The human DRD2 reference sequence is supplied in `inputs/targets/DRD2_P14416.fasta`; the deposited construct sequence and structure information are supplied alongside it.
- **Compound Library:** `inputs/library/compounds_400.csv` and `inputs/library/compounds_400.sdf`, containing 400 source records with compound identifiers and molecular structures. The SDF contains two-dimensional coordinates; the supplied records retain the source stereochemical specifications.
- **Reference Controls:** `inputs/controls/control_registry.csv` and its accompanying molecular files, including risperidone, its native bound reference coordinates and domperidone. Native atom correspondences are supplied in `inputs/controls/native_atom_mapping.csv`.

## Constraints

- **Scientific Scope:** Select candidates from the supplied library, keeping reference controls distinct from candidate recommendations.
- **Inputs:** Preserve compound identifiers, chemical identities and fixed library membership. Record duplicate identities, ambiguity and justified input interpretations.
- **Scientific Criteria:** Support recommendations with evidence relevant to D2R, restricted brain access and intestinal absorption. Define and justify the measures, selection criteria and trade-offs used to assess these goals.
- **Reference Comparisons:** Explain how the supplied controls inform the assessment and ranking. Keep comparisons scientifically meaningful and report their limitations.
- **Reference Policy:** Evaluator-only outcomes must not guide candidate selection or be copied into run results.
- **Evidence:** Retain the inputs, relevant settings and scientific outputs supporting the conclusions. Distinguish predictions from experimentally established properties and report uncertainty, failures and limitations.

## Expected Output

Provide a ranked shortlist of the **top 8 library candidates** and identify **2 final priority candidates** within that shortlist. Give the evidence supporting each candidate, workflow decisions, failures and limitations. Include a **detailed scientific report** covering the inputs, approach, results, reference comparisons, ranking rationale, supporting evidence and limitations. If fewer candidates are scientifically supportable, report the supported number and explain the shortfall rather than filling the shortlist with unsupported recommendations.

| File | Content |
| --- | --- |
| `ranked_candidates.csv` | Ranked top 8 library compound identifiers, an indication of the 2 final priorities, eligibility information, supporting evidence or result references, ranking rationale and relevant comparisons with the reference controls |
| `assessment.json` | Chosen workflow and its justification, selection criteria, reference use, decisions, input interpretations, coverage counts, missing information, failed or incomplete work, limitations and evidence references |
| `report.md` | A detailed scientific report covering the objective, inputs, approach and relevant settings, results, reference comparisons, top 8 candidates and 2 final priorities, ranking rationale, supporting evidence and artifact locations, workflow decisions, failures, unresolved work and limitations |

Retain the scientific output artifacts supporting the reported results and identify their locations in the report. Account for excluded, unresolved and failed compound assessments.

## Important Instructions

- Return NEEDS_INPUT only when essential inputs are unavailable and the gap cannot be resolved through justified decisions.
- Report incomplete execution as PARTIAL and identify the remaining requirements.
- Keep unavailable measurements unresolved; do not invent results.
- Distinguish a lack of promising candidates from missing inputs or failed execution.
- Base the final conclusions on the completed scientific work.
