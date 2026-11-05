# Task: mab_gal3bp_reference_design

## Description

Design paired monoclonal antibody candidates against human Galectin-3-binding protein (Gal-3BP), using the BDBV-43 scaffold evaluated for epitope E1 in the published computational study. Assess whether reference-derived candidates retain an accessible, plausible interface in the glycosylated target context. Compare their evidence with the study's Mut1 result.

## Target

**Target:** Human Gal-3BP (LGALS3BP), UniProt Q08380\
**Reference Antibody:** BDBV-43 scaffold in the study's modeled Gal-3BP/E1 complex\
**Published Design Comparator:** Mut1\
**Binding Region:** Paper-defined E1, mapped to the supplied mature Gal-3BP construct\
**Antibody Format:** Paired heavy/light variable domains\
**Objective:** Reference-derived interface refinement accounting for glycan accessibility

The scaffold is a computational starting point for this target, not an experimentally established Gal-3BP-binding antibody. Obtain the exact study sequences, modeled reference complex and E1 mapping before claiming a matched reproduction.

## Design Constraints

- Preserve the supplied chain pairing and protected framework. Declare CDR editing boundaries and retain the reference-to-candidate mutation record.
- Keep the mature target construct, glycosylation assumptions and oligomeric context explicit. Do not treat predicted antigen coordinates as an experimental PDB structure.
- Compare reference and candidates under matched structural and sampling conditions. Record any unavailable study inputs or changes in assumptions.
- Retain Mut1 as a published comparison control rather than a newly generated design.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Antigen accessibility | Epitope solvent-accessible area, glycan occlusion and context clashes | Report the glycan model and area-difference convention. |
| Interface stability | Interface RMSD and contact persistence across independent samples | Define interface atoms and reference alignment; retain per-sample results. |
| Interaction quality | Matched interaction scores, contact counts, hydrogen bonds and salt bridges | Preserve units and counting definitions; more contacts alone do not establish stronger binding. |
| Sequence quality | Framework edits, humanness and developability liabilities | Compare reference and candidate using the same definitions. |
| Conformational evidence | Populations and free-energy landscapes, where available | Distinguish relative landscape estimates from binding free energy. |

Published comparison data: [Gal-3BP Reference Antibody Design benchmark](../../benchmark/monoclonal_antibody_design/mab_gal3bp_reference_design.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `gal3bp_results/`

- `designed_sequences.fasta`: paired reference-derived candidates with unique identifiers.
- `metrics.json`: matched reference/candidate measurements, glycan assumptions and raw artifact provenance.
- `shortlist.csv`: ranked candidates with supported improvements and unresolved criteria.
- `benchmark_comparison.csv`: published values, new results and explicit distinctions between outcomes and thresholds.
- `report.md`: structural rationale and limitations, with target/complex structures and numerical analysis outputs.

## Important Instructions

- Select methods independently within the user's constraints; no fixed pipeline is prescribed.
- Report `NEEDS_INPUT` if the study's reference complex, paired sequences or epitope mapping cannot be verified.
- Do not substitute a minimum on a conformational free-energy landscape for a binding free-energy measurement.
- Keep computational stability, target binding and functional inhibition as separate conclusions.
