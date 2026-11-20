# Benchmark: TREM2 scFv design

**Task:** [TREM2: Reference-Guided scFv Design](../../../tasks/monoclonal_antibody_design/task_009_trem2_scfv_design.md)

## Published computational reference

Source: the [ProteinBase TREM2 reference, golden-gecko-stone](https://proteinbase.com/proteins/golden-gecko-stone), from the saved 10 November 2026 snapshot. This task uses one reference record, so its minimum and maximum are equal.

| Metric | Minimum | Maximum | Scope |
| --- | --- | --- | --- |
| Molecular weight (Da) | 26183.6857 | 26183.6857 | Whole sequence |
| Isoelectric point (pH) | 8.75527401 | 8.75527401 | Whole sequence |
| ESMFold pLDDT (0–100) | 84.24698318 | 84.24698318 | Whole structure |
| ESMFold pLDDT (0–100) | 85.79458785 | 85.79458785 | Source-annotated domains |
| ProteinMPNN original-sequence score | 1.2852 | 1.2852 | ESMFold prediction |
| ProteinMPNN redesigned-sequence score | 0.76449 | 0.76449 | Source redesign calculation |
| ProteinMPNN sequence recovery (raw) | 0.58203 | 0.58203 | Source redesign calculation |
| Boltz2 pTM | 0.9327809811 | 0.9327809811 | Source Boltz2_Binder_SS complex |
| Boltz2 ipTM | 0.9009589553 | 0.9009589553 | Source Boltz2_Binder_SS complex |
| Boltz2 complex pLDDT (raw) | 0.928986609 | 0.928986609 | Source Boltz2_Binder_SS complex |
| Boltz2 complex PDE | 0.3970271945 | 0.3970271945 | Source Boltz2_Binder_SS complex |

pTM and ipTM use a 0–1 scale. The source complex pLDDT value retains its raw 0–1 scale; ESMFold pLDDT is 0–100. ProteinMPNN's original and redesigned scores belong to separate source calculations. Lower negative log likelihood and predicted distance error are preferred; higher confidence scores and recovery are preferred within their stated scope.

## Evaluation criteria

Use the same reference scFv, prepared TREM2 construct and declared CDR masks for candidate evaluation. Check modelled VH/VL sequences against the submitted candidates before including a prediction. Report the matched execution control separately from the catalog value, because identical catalog processing settings are not established.

The four completed design routes and their matched Boltz2 comparisons are in [comparison.md](comparison.md).
