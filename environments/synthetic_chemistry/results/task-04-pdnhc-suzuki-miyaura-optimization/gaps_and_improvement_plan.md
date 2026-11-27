# Task 04 — gaps and improvement plan

## Performance gaps and likely reasons

| Gap | Reason | Evidence |
|---|---|---|
| Exact reactant pair absent from top-5 retrosynthesis | Model explored halide/boronic-ester alternatives; no native route scores usable | Routes R1–R5; only R2 partially compatible |
| Three condition-recommendation failures | GLM HTTP 429 on all configured tokens; Discovery RSI backup timeout | Failed call IDs `6b0540e0…`, `6b0543a9…`, `6b058bc6…` |
| Predicted yield weakly condition-specific | Native yield largely reaction-level | 8/10 conditions share 32.338% |
| Yield input-order sensitivity | Service output changed with reactant order; high-yield records lacked catalyst/base | Reversed-order call `6b07dac0…` |
| No Pd-NHC identity from yielding tools | Tools returned generic strings or no catalyst | Internal "palladium catalyst"; Parrot top-6 no catalyst |
| Loading optimization unsupported by yield model | Frozen ReactionT5 excludes equivalents and other condition fields | Identical yields at 0.5 and 5 mol% for same catalyst/base; `pipeline.py:74` |
| No experimental validation | Tool does not run lab hardware; benchmark data withheld | Campaign store has zero reviewed measurements |

## Limitations

- All numerical yields are model fields, not measurements. Score semantics differ across tools and were not converted.
- Literature references are general catalyst-family context; no exact-pair yield or optimum was consulted.
- Parrot weights were executed with compatibility shims in a dedicated environment; Reaxys temperature weights were license-gated and unavailable.
- The local optimizer's design candidates have heuristic scores (0.55 prior, 0.75 domain) with no verified precedents for this pair.
- Training-data contamination of external models cannot be excluded despite no prohibited lookups.
- One persistent campaign was created with six reserved experiments; no measurement, review, Bayesian fit or operating-window study was performed.

## Recommended next steps

1. **Measured HTE campaign:** execute the persisted six-experiment reservation (`SC01_campaign.sqlite`, campaign `a19bfc948594490f9e8f992db4f77af7`) under an approved protocol, then supply real assay yields with unique execution and analytical references through `campaign_cli measure` and `review`. BayBE can fit after at least four reviewed distinct candidates.
2. **Preregistered operating-window study:** reserve ≥3 independent runs per point for the best catalyst/base at 0.5 versus 5 mol% loading through the authenticated HTTP workflow and test ≥90% measured yield retention.
3. **Loading-aware yield model:** train or connect a model that includes mol% loading, base, solvent and temperature as input features; the current frozen ReactionT5 cannot establish retention.
4. **Authentic Pd-NHC descriptors:** add ligand steric/electronic descriptors or computed complex features so catalyst ranking can go beyond equal heuristic scores.
5. **Benchmark validation:** evaluate frozen predictions against withheld benchmark data in the separate non-blind stage only; do not compare against exact experimental records during generation.
6. **Service robustness:** re-run condition recommendation with normalized reactant order once quota allows, and retain the repeated failure record as provenance.
