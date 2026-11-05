# Status

**Lifecycle:** In Progress. **Protocol:** v1.2 (freeze `engine-v1.2.0_protocol-v1.2`; gates frozen at v1.0). **Contribution status:** owner/reviewers/issue pending.

## Implemented and evidenced

- Intent routing (5 modes) + 10 active human application profiles; antiviral review-only; plant/pest inactive.
- Requirement-brief contract with confirmed, hashed priorities; staged requirement-aware ranking with mandatory ±25% stability reporting; explorer loop (X1–X5) with proposed constraint re-anchoring.
- Fixed multi-dimensional battery (E1–E6) under 10 frozen, provenance-tagged gates; component validation 11/12 pass + live integration micro-run reproducing a known candidate's values exactly.
- Executed computational benchmarks on public data (see [benchmark/](benchmark/)): clean-cohort predictor AUC 0.7021 (Simone-322); generator clean AUC 0.760 + measured-top-10 at median 97.5th percentile (HIF1A case study); approved-drug site ranks #62/#107 of 598 (TTR); same-side approved-7 comparison; explorer blind post-hoc 0.92/0.92/0.87.

## Not established

No experimental/wet-lab validation of any generated candidate; no delivery or chemistry prediction (none exists publicly); no plant/pest or antiviral execution; ASO models excluded from siRNA scoring.

## Known defects / backlog

1. Input gate rejects clinical-format overhang duplexes (`passenger_not_reverse_complement`, 5/7 approved drugs at intake).
2. 6merDB viability threshold is the weakest-evidence, most aggressive gate (removes 12.4% of measured-effectives on the labeled cohort).
3. Off-target gate scoping **silently depends on a gene-symbol match** (2026-11-05 correction): the HIF1A "saturation" was an artifact — every counted hit was a same-gene isoform match (cross-gene = 0); the mislabeled input symbol disengaged locus-scoping. Under the adapter's own semantics the gate was NOT saturated there. Calibration now means pinning scope explicitly, not just thresholds.
4. E4e RNAhybrid incompatible with the SIREN convention in the installed build (`NOT_RUN(broken-binary)`); the stage has never executed and is quarantined, not silently empty.

## Source workspace

Full curation, freezes, validation-program artifacts and reports: `~/IMRAN/NOV26/siRNA-Design-Task-Specific` (tool registry, heuristics audit, validation program, case study, e2e validation, requirement-ranking and explorer demos).
5. E4a scoping must fail loud: warn on unmatched supplied gene symbols and gene-less transcript headers; pin scope in the thresholds contract. (Found by tool-execution verification 2026-11-05.)
