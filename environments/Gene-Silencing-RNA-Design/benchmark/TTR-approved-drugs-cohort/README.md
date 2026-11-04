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
