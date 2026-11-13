# siRNA-Bench candidate report

- job: `MYC_Run-3_2026-11-11`  executed: 2026-11-11T12:54:36Z
- candidates evaluated: **24**
- runtime: 190.8 s

## Evidence-status summary

| status | count |
|---|---|
| NEEDS_EXPERIMENTAL_VALIDATION | 17 |
| REJECTED_INPUT | 7 |

## Model availability

```json
{
  "structure": "RNAfold 2.7.2",
  "efficacy": {
    "RN.Ai-Predict": "AVAILABLE_PRETRAINED",
    "RNAiSpline": "AVAILABLE_PRETRAINED",
    "siRNADiscovery": "CODE_ONLY"
  },
  "offtarget": "bowtie2 GENCODE v50 + siSPOTR POTS(Apache-2.0) + 6merDB(MIT)",
  "seed_toxicity": "6merDB (NW_CellToxicityDB v1.5)",
  "nupack": "LICENSE_RESTRICTED (not installed)",
  "rnastructure": "NOT_INSTALLED (optional; academic license)",
  "pkpd": "NCA of supplied data only; PBPK NOT_EVALUATED"
}
```

## Top prioritized candidates

| rank | candidate | RN.Ai-Predict % | RNAiSpline P | seed matches | POTS pct | seed viability (human avg) | score |
|---|---|---|---|---|---|---|---|
| 1 | NM_002467.6_site_3568 | 88.37 | 0.6852 | 74134 | 20.2 | 80.5 | 1.4053 |
| 2 | NM_002467.6_site_2467 | 92.55 | 0.6879 | 70273 | 45.7 | 90.0 | 1.3758 |
| 3 | NM_002467.6_site_1185 | 86.54 | 0.6834 | 105502 | 13.5 | 84.9 | 1.2694 |
| 4 | NM_002467.6_site_2448 | 81.2 | 0.679 | 77774 | 55.6 | 89.4 | 1.2329 |
| 5 | NM_002467.6_site_2746 | 91.61 | 0.6868 | 101384 | 9.2 | 78.4 | 1.2327 |
| 6 | NM_002467.6_site_1555 | 87.88 | 0.6868 | 136209 | 4.6 | 69.1 | 1.1335 |
| 7 | NM_002467.6_site_1184 | 79.73 | 0.6703 | 110620 | 22.7 | 83.6 | 1.0939 |
| 8 | NM_002467.6_site_2439 | 76.56 | 0.6575 | 130498 | 27.4 | 78.7 | 1.0649 |
| 9 | NM_002467.6_site_1729 | 88.62 | 0.686 | 50382 | 73.3 | 89.8 | 1.0587 |
| 10 | NM_002467.6_site_1178 | 74.88 | 0.6695 | 30291 | 80.4 | 81.0 | 0.9599 |
| 11 | NM_002467.6_site_1725 | 86.65 | 0.6864 | 134598 | 3.3 | 65.2 | 0.9307 |
| 12 | NM_002467.6_site_1182 | 76.49 | 0.6242 | 21983 | 88.0 | 83.4 | 0.9007 |
| 13 | NM_002467.6_site_2870 | 83.9 | 0.682 | 120037 | 21.1 | 81.5 | 0.8967 |
| 14 | NM_002467.6_site_1186 | 78.19 | 0.6704 | 152530 | 14.5 | 83.7 | 0.8451 |
| 15 | NM_002467.6_site_1188 | 75.25 | 0.6596 | 152293 | 4.1 | 76.0 | 0.7499 |

## Interpretation rules

- `RN.Ai-Predict` scores are predicted % inhibition (0-100); `RNAiSpline` scores are
  P(effective-class); **these endpoints are never averaged or merged**.
- Off-target rows are *predicted sequence matches* (bowtie2/POTS), not experimentally
  established repression; seed-toxicity values are cancer-cell-line viability phenotypes
  from one scaffold chemistry (6merDB) — neither predicts clinical toxicity.
- No validated ML toxicity predictor exists for siRNA in this platform;
  ASO-trained models (OligoAI, ASO Atlas 2.0) are deliberately NOT transferred.
- PK rows are non-compartmental analyses of *supplied* concentration-time data;
  organ exposure is never predicted from sequence.

## Limitations & missing experiments

- NUPACK: LICENSE_RESTRICTED (not installed) — duplex energies from ViennaRNA only.
- siRNADiscovery: CODE_ONLY (no published checkpoint).
- No RNA-seq / protein / splice measurements supplied for this job.
- All filter thresholds are user-operational defaults unless overridden:
```json
{
  "max_full_length_offtarget_hits": 10,
  "max_seed_occurrence_fold": 2.0,
  "max_pots_percentile": 90.0,
  "min_seed_viability_avg_human": 50.0,
  "min_rnai_predict_score": 50.0,
  "min_rnaispline_score": 0.5,
  "min_duplex_delta_g": -45.0,
  "max_duplex_delta_g": -25.0,
  "gc_min": 0.3,
  "gc_max": 0.7
}
```

## Reproduction

```bash
sirna-platform run --config configs/example.yaml   # same inputs -> same outputs
```
Candidate-level provenance: `provenance.json`, `09_filter_decisions.csv`,
`final_ranked_candidates.json`.

*Computational prioritization for research; not experimentally validated
therapeutic candidates.*