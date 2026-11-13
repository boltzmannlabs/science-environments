# siRNA-Bench candidate report

- job: `HK2_Run-3_2026-11-11`  executed: 2026-11-11T12:48:34Z
- candidates evaluated: **24**
- runtime: 187.2 s

## Evidence-status summary

| status | count |
|---|---|
| NEEDS_EXPERIMENTAL_VALIDATION | 15 |
| REJECTED_INPUT | 9 |

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
| 1 | NM_000189.5_site_1920 | 83.62 | 0.6803 | 109490 | 6.5 | 80.7 | 1.5198 |
| 2 | NM_000189.5_site_4403 | 84.88 | 0.6877 | 93142 | 4.4 | 93.9 | 1.4961 |
| 3 | NM_000189.5_site_4760 | 90.73 | 0.6897 | 74287 | 9.0 | 80.2 | 1.4544 |
| 4 | NM_000189.5_site_4888 | 86.23 | 0.6819 | 64353 | 33.5 | 81.4 | 1.2014 |
| 5 | NM_000189.5_site_1919 | 77.7 | 0.6655 | 74922 | 40.0 | 68.4 | 1.1818 |
| 6 | NM_000189.5_site_868 | 90.66 | 0.6906 | 175640 | 14.8 | 85.0 | 1.0168 |
| 7 | NM_000189.5_site_4807 | 84.51 | 0.6796 | 150673 | 7.8 | 78.2 | 0.9417 |
| 8 | NM_000189.5_site_4921 | 84.58 | 0.6823 | 113464 | 29.6 | 66.7 | 0.9355 |
| 9 | NM_000189.5_site_4928 | 86.05 | 0.6855 | 46177 | 85.9 | 79.8 | 0.928 |
| 10 | NM_000189.5_site_728 | 84.02 | 0.6809 | 104590 | 12.3 | 64.1 | 0.8819 |
| 11 | NM_000189.5_site_4927 | 81.61 | 0.6842 | 38700 | 81.8 | 69.7 | 0.85 |
| 12 | NM_000189.5_site_1458 | 76.94 | 0.6764 | 154899 | 12.4 | 79.6 | 0.8334 |
| 13 | NM_000189.5_site_4486 | 87.52 | 0.686 | 134633 | 35.3 | 79.0 | 0.8301 |
| 14 | NM_000189.5_site_1263 | 69.18 | 0.5723 | 39198 | 52.0 | 61.3 | 0.6341 |
| 15 | NM_000189.5_site_5165 | 79.59 | 0.6408 | 99582 | 60.7 | 74.7 | 0.5203 |

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