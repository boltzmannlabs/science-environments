# Benchmark: HER2 Biparatopic Antibody Design

**Task:** [HER2 biparatopic antibody design](../../tasks/bispecific_design/bispecific_antibody_design.md)

## Benchmark Type

Literature-based structural and functional comparison against zanidatamab. Assesses two HER2-binding components within a defined biparatopic molecule, covering both individual arms and the assembled product.

## Metrics and Reference Values

| Metric or reference property | Published value | Benchmark context |
| --- | --- | --- |
| Structural reference | PDB 8FFJ | Zanidatamab–HER2 structural evidence. |
| Cryo-EM reconstruction resolution | 7.6 Å | Experimental map resolution; not a prediction-error threshold. |
| Binding-domain assignments | ECD2-binding Fab and ECD4-binding scFv | Reference architecture and specificity assignments. |
| Receptor engagement | In trans across separate HER2 molecules | Published reference arrangement for structural comparison. |
| Maximum cell-binding capacity | 1.3–1.6-fold relative to monospecific comparators | Experimental flow-cytometry comparison with trastuzumab and pertuzumab. |
| Candidate-level ipTM, pLDDT, PAE, DockQ and REF15 | Not established by the cited reference | No published numerical acceptance thresholds for these design scores. |

## Benchmark Interpretation

Assess both HER2 specificities and the complete assembly. Compare domain assignments, mapped interfaces, chain pairing, steric compatibility and the declared receptor arrangement with the reference evidence. Report resolved and missing structural regions when using PDB 8FFJ.

Apply the task's declared arm-level and product-level acceptance criteria. A passing arm cannot compensate for a failed mandatory criterion in the other arm or assembled molecule. Keep new computational measurements separate from published experimental results; predicted confidence or energy cannot reproduce the reported cell-binding endpoint.

**References:** [Zanidatamab structural and functional study, Nature Communications (2023), Figures 1–2](https://doi.org/10.1038/s41467-023-37029-3); [PDB 8FFJ](https://www.rcsb.org/structure/8FFJ).
