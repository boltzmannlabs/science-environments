# Task: sars_cov2_mpro_hit_prioritisation

## Objective

Identify and rank promising compounds from the two supplied libraries as candidate inhibitors of the SARS-CoV-2 main protease. Use the available reference compounds as controls. Choose and justify an appropriate workflow, assess the selected candidates against the task criteria, and report the results, limitations and evidence supporting the final ranking.

## Target

**Name:** SARS-CoV-2 main protease (Mpro)\
**Protein:** SARS-CoV-2 3C-like protease (nsp5)\
**Disease:** COVID-19\
**PDB:** 6LU7\
**Structure and Context:** The crystal structure of SARS-CoV-2 Mpro in complex with its co-crystallized inhibitor is supplied as target information. The deposited structure is fully resolved. The co-crystallized inhibitor defines the active site used for structure-based assessment.\
**Reference Inputs:** Remdesivir and ritonavir as reference control compounds; the co-crystallized active-site inhibitor is supplied with its native bound coordinates

## Inputs

- **Target:** `inputs/targets/6LU7_crystal_complex.pdb`, the original source coordinates, and `inputs/targets/target_registry.csv`. The deposited sequence and structure information are supplied alongside it.
- **Compound Libraries:** `inputs/library/approved_drugs.csv` and `inputs/library/approved_drugs.sdf`, containing 281 approved-drug records with database identifiers and molecular structures, and `inputs/library/ritonavir_derivatives.csv` and `inputs/library/ritonavir_derivatives.sdf`, containing 117 ritonavir-derivative records with compound identifiers and molecular structures. The records retain the source stereochemical and naming conventions, including mixed identifier casing.
- **Reference Controls:** `inputs/controls/control_registry.csv` and its accompanying molecular files, including remdesivir and ritonavir. The native bound coordinates of the co-crystallized active-site inhibitor and its atom correspondences are supplied in `inputs/controls/`.

## Constraints

- **Scientific Scope:** Select candidates from the supplied libraries, keeping reference controls distinct from candidate recommendations.
- **Inputs:** Preserve compound identifiers, chemical identities and fixed library membership. Record duplicate identities, ambiguity and justified input interpretations.
- **Scientific Criteria:** Assess each candidate by (i) predicted binding score relative to the reference controls docked in the same run and (ii) engagement of the co-crystal-defined active site, including its catalytic residues and pocket contacts. Define and justify the measures, selection criteria and trade-offs used, and report the reference-control scores alongside the candidate scores.
- **Reference Comparisons:** Explain how the supplied controls inform the assessment and ranking. Keep comparisons scientifically meaningful and report their limitations.
- **Reference Policy:** Evaluator-only outcomes must not guide candidate selection or be copied into run results.
- **Evidence:** Retain the inputs, relevant settings and scientific outputs supporting the conclusions. Distinguish predictions from experimentally established properties and report uncertainty, failures and limitations.

## Expected Output

Provide a ranked shortlist of the **top 20 library candidates** and identify **3 final priority candidates** within that shortlist. Give the evidence supporting each candidate, workflow decisions, failures and limitations. Include a **detailed scientific report** covering the inputs, approach, results, reference comparisons, ranking rationale, supporting evidence and limitations. If fewer candidates are scientifically supportable, report the supported number and explain the shortfall rather than filling the shortlist with unsupported recommendations.

| File | Content |
| --- | --- |
| `ranked_candidates.csv` | Ranked top 20 library compound identifiers, an indication of the 3 final priorities, eligibility information, supporting evidence or result references, ranking rationale and relevant comparisons with the reference controls |
| `assessment.json` | Chosen workflow and its justification, selection criteria, reference use, decisions, input interpretations, coverage counts, missing information, failed or incomplete work, limitations and evidence references |
| `report.md` | A detailed scientific report covering the objective, inputs, approach and relevant settings, results, reference comparisons, top 20 candidates and 3 final priorities, ranking rationale, supporting evidence and artifact locations, workflow decisions, failures, unresolved work and limitations |

Retain the scientific output artifacts supporting the reported results and identify their locations in the report. Account for excluded, unresolved and failed compound assessments.

## Important Instructions

- Return NEEDS_INPUT only when essential inputs are unavailable and the gap cannot be resolved through justified decisions.
- Report incomplete execution as PARTIAL and identify the remaining requirements.
- Keep unavailable measurements unresolved; do not invent results.
- Distinguish a lack of promising candidates from missing inputs or failed execution.
- Base the final conclusions on the completed scientific work.
