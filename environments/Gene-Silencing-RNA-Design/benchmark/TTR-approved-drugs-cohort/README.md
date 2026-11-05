# TTR / approved-drugs cohort — same-side battery + site-rank audit

Published designs: all 7 approved siRNA drugs (patisiran, givosiran, lumasiran, inclisiran,
vutrisiran, nedosiran, fitusiran) with sequences verified via FDA GINAS + EMA EPAR (decoded
modification maps) in the source workspace. Our arm: OligoFormer top-20 TTR windows
(ENST00000237014.8). Identical harness, GENCODE v50 reference, frozen thresholds.

- Approved-site rank audit (`drug_site_rank_audit.json`): vutrisiran site **#62/598**
  (89.6th pct), patisiran **#107/598** (82.1st pct) in the generator's ranking.
- Same-side summary (`same_side_summary.json`): RN.Ai median 84.5 (drugs) vs 84.3 (ours);
  0 full-length off-target hits both cohorts; approved duplexes more stable (−35.2 vs −29.6);
  gates flag 6/20 of ours (decision-matrix audit; corrected from an initial 2/20 spot count).
- Honest observations: fitusiran/vutrisiran carry viability-depleting seeds per 6merDB
  (scaffold caveat); 5/7 drugs reject at the intake gate on clinical-format overhangs
  (backlog #1); givosiran duplex NOT_RUN (isoform context).

## Benchmark metrics

### Site-rank audit (generator vs approved drugs)

| Drug | Window | OligoFormer score | Rank | Percentile |
|---|---|---|---|---|
| patisiran | ENST00000237014.8_site_518 | 0.851 | **#107**/598 | 82.1th |
| vutrisiran | ENST00000237014.8_site_509 | 0.8978 | **#62**/598 | 89.6th |

### Same-side battery (identical harness)

| Dimension | Approved-7 (median, range) | Our TTR top-20 (median, range) |
|---|---|---|
| eff_RN.Ai-Predict | 84.53 (70.86–91.54; n=7) | 84.345 (73.87–88.33; n=20) |
| eff_RNAiSpline | 0.64 (0.599–0.684; n=7) | 0.674 (0.633–0.688; n=20) |
| guide_target_duplex_delta_g_kcal_mol | -35.2 (-38.0–-28.4; n=6) | -29.6 (-33.9–-25.0; n=20) |
| full_length_offtarget_hits | 0.0 (0.0–0.0; n=7) | 0.0 (0.0–0.0; n=20) |
| seed_occurrence_fold_over_expected | 1.374 (1.075–1.865; n=7) | 1.261 (0.5–2.569; n=20) |
| pots_seed_percentile | 24.152 (1.404–37.964; n=7) | 22.501 (2.698–80.023; n=20) |
| seed_tox_viability_avg_human | 79.3 (51.7–85.1; n=7) | 76.2 (37.5–89.9; n=20) |

Gate decisions: drugs 7/7 pass all computational gates (5/7 reject at intake on overhang format — backlog #1); our pool 14/20 all-gates-clean, 6/20 flagged (4 seed-fold, 1 GC, 1 viability).
