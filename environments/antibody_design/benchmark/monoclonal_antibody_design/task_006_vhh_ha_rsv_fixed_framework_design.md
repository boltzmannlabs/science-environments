
**Task ID:** `task_006_vhh_ha_rsv_fixed_framework_design`

**Task:** [HA-Targeted Fixed-Framework VHH Design with RSV Comparison](../../tasks/monoclonal_antibody_design/task_006_vhh_ha_rsv_fixed_framework_design.md)

## Published Results

**Source:** [Atomically accurate de novo design of antibodies with RFdiffusion, Nature 649, 183–193 (2026)](https://doi.org/10.1038/s41586-025-09721-5), Extended Data Figure 3b,c; Supplementary Information, Figure 1d, Methods §§6.2, 6.3, 6.5 and 6.7, and Methods Tables 5–6, printed pages 64–68.

The published reference uses RFdiffusion for backbone generation, ProteinMPNN for CDR sequence design, and fine-tuned RoseTTAFold2 for structure-based filtering. Framework sequence is held fixed during sequence design. The HA design epitope is **5VLI B521, B545 and B552**.

| Published metric | Reported value or outcome | Scope and score definition |
| --- | --- | --- |
| Spatial aggregation propensity, SAP | Filtered designed VHHs have a slightly higher SAP distribution than native VHHs. | Extended Data Figure 3c and Methods §6.5. Lower SAP is favorable within the same definition and solvent-exposure treatment. |
| Interface interaction energy, Rosetta ddG | Filtered designed interfaces have slightly less favorable ddG than native VHH interfaces. | Extended Data Figure 3c and Methods §6.5. Interfaces were relaxed with Rosetta FastRelax before scoring. Retain native Rosetta units, score function and partner selections. |
| Humanness, OASis Identity | Designed VHHs are more human-like than random-CDR controls and less human-like than therapeutic-CDR controls. | Supplementary Figure 1d and Methods §6.7. Relaxed peptide prevalence is **≥10% of subjects**; the analysis uses **100 designs from each of four campaigns** and **400 therapeutic-CDR controls** in the same humanized framework. |
| Predicted cross-target specificity | Intended-target entries are stronger than most cross-target entries in the normalized pAE-positive fraction matrix. | Extended Data Figure 3b and Methods §6.3. A positive prediction uses **RF2 pAE <10 Å**; decoy positive fractions are normalized to the intended-target positive fraction. |



| Published structure-filtering protocol | Acceptance conditions | Provenance |
| --- | --- | --- |
| Fine-tuned RF2 | Design-consistency Cα RMSD **<2 Å** and interaction pAE **<10 Å**, jointly | Methods §6.5 and Methods Table 6 |
| AlphaFold3 | Whole-complex Cα RMSD **<5 Å** and ipTM **>0.5**, jointly | Methods Table 6 |

| HA/H1-stem published analysis | Reported success rate |
| --- | ---: |
| RF2, hotspot proportion 1 | **11.5%** |
| RF2, hotspot proportion 0.1 | **7.5%** |
| RF2, hotspot proportion 0 | **3.5%** |
| AF3 | **5.0%** |

Provenance: Methods Table 6. The computational analysis used **200 backbones**, selecting the best of **eight MPNN sequences per backbone** under the respective filtering method. These rates describe the published HA campaign, not a single-VHH acceptance threshold. The SAP/ddG reference population was filtered using both RF2 conditions before interface scoring and includes **1,296 nonredundant native VHH complexes** as a reference set.

## Workflow Results

The following values belong to the current HA-targeted VHH workflow and are kept separate from the published observations.

For aggregation-related surface assessment, this workflow uses **Shrake–Rupley solvent exposure with exposure-filtered Kyte–Doolittle hydrophobicity**. For humanness assessment, it uses **whole-VHH human-immunoglobulin 9-mer reference matching**. These are the selected workflow implementations for the properties assessed by SAP and OASis in the paper, with their own score definitions and native scales.

| Task property | Workflow value | Definition and comparison scope |
| --- | ---: | --- |
| Surface aggregation-related descriptor | **-1.242** | Selected surface-assessment method: mean Kyte–Doolittle hydrophobicity over **55/121** VHH residues with relative exposure >0.3, calculated using Shrake–Rupley exposure. The negative mean describes a hydrophilic average on the KD scale. |
| Whole-sequence hydrophobicity | **-0.217** | Sequence-only KD mean, separate from the surface score. |
| Whole-VHH repertoire matching | **0.5487** | Selected humanness-assessment method: the fraction of unique whole-VHH 9-mers present in the human-immunoglobulin reference collection, **62/113**. |
| HA interface-affinity estimate | **-12.2 kcal/mol** | PRODIGY, with the same partner-selection and service protocol as the RSV comparison. |
| RSV-crop interface-affinity estimate | **-10.8 kcal/mol** | PRODIGY on the RSV comparison construct. |
| HA-versus-RSV preference difference | **+1.4 kcal/mol** | ΔG(RSV crop) − ΔG(HA); positive values favor HA within this matched pair. This is an energy contrast, not a normalized pAE-positive fraction. |

| Supporting structure metric | Workflow value | Interpretation |
| --- | ---: | --- |
| Interaction PAE | **6.895 Å** | Boltz-2 symmetric mean over both full cross-chain PAE blocks; below the published numerical reference of 10 Å, with predictor and averaging definition retained. |
| ipTM | **0.8147** | Boltz-2 interface-confidence score; above the numerical AF3 reference of 0.5, considered separately from the AF3 RMSD requirement. |
| VHH internal-geometry RMSD | **1.929 Å** | VHH-self-aligned over 121 Cα atoms using Biopython SVDSuperimposer, checked against a known rigid transformation. Supports internal VHH structural consistency; it is not an antigen-frame docking test. |
| Antigen-relative VHH RMSD | **20.854 Å** | After alignment on the 170 antigen Cα atoms, the designed docking pose is not reproduced by this assessment. |
| Antigen internal-geometry RMSD | **8.816 Å** | Antigen-self-aligned; antigen deformation also affects interpretation of the target-frame VHH RMSD. |

| Design-validity check | Workflow result |
| --- | --- |
| Scaffold | **3EAK chain A**, compared with the paper's humanized NbBCII10 framework |
| HA hotspots | **B521, B545, B552**; assessment mapping **21, 45, 52** |
| Candidate CDR lengths | **7 / 6 / 13 residues** |
| Protected framework sequence | **95/95 mapped residues preserved** |
| Generation-time framework RMSD | **0.1614 Å**, below the declared **0.5 Å** tolerance |
| Generation-time hotspot coverage | **3/3** |

Provenance and construct scope: the canonical PPIFlow backbone and the sequence-based assessment structures are separate. Generation-time framework preservation and hotspot coverage describe the canonical backbone. The same VHH sequence is retained across the assessment structures. The confidence/RMSD HA construct has P at segment position 9, whereas the HA energy/surface construct has F there. The comparison panel contains **2/2 scored constructs**: a **170-residue HA segment** and an **RSV segment covering residues 250–380**. The RSV crop does not include the complete interprotomer site containing residues 305 and 456.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Aggregation propensity | Use the selected exposure-filtered surface KD implementation for workflow assessment, recording exposure treatment, structure and sequence scope. Direct numerical SAP benchmarking requires the SAP definition. | Interpret the workflow value on the KD hydrophobicity scale and the published reference on the SAP scale; retain the separate scales without assigning a cross-method pass cutoff. |
| Humanness | Use the selected whole-VHH 9-mer reference-matching implementation for workflow assessment. Direct numerical OASis benchmarking requires matching peptide windows, repertoire and the ≥10%-of-subjects prevalence criterion. | Report **0.5487** as the reference-match fraction on the workflow's 0–1 scale; retain OASis subject prevalence as the published method's separate definition. |
| Interface interaction energy | Score reference and candidates under identical preparation, partner selections and energy definitions; retain units and sign convention. | More favorable scores are interpreted within the matched protocol. PRODIGY kcal/mol and Rosetta ddG are not numerically interchangeable; an explicit complex-minus-separated energy calculation is distinct from a contact-based affinity estimate. |
| HA-versus-RSV comparison | Evaluate the same HA-targeted VHH against HA and the declared RSV crop under matched conditions. Retain both antigen-specific values. | Positive ΔG(RSV) − ΔG(HA) favors HA in this pair. General specificity and normalized positive fractions require their own defined panel and classification method. |
| Structure confidence and consistency | Match predictor, sequence construct, atom selection, alignment and PAE averaging. Assess each published joint filter as a complete rule. | RF2: RMSD <2 Å **and** pAE <10 Å. AF3: whole-complex RMSD <5 Å **and** ipTM >0.5. Separate favorable scores do not establish a complete joint-filter pass. |
| Allowed changes and structure | Verify task-defined CDR edits, loop lengths, framework identities, geometry and intended epitope mapping. | A favorable property score cannot compensate for a violated design constraint; the task's 0.5 Å generation-time framework tolerance is separate from design-prediction RMSD. |
| Published endpoint comparison | Match the exact published observation, construct, score definition and provenance before numerical grading. | Published population summaries remain separate from individual workflow results; unavailable candidate-level values remain unavailable. |
