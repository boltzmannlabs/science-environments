# siRNA-Bench candidate report

- job: `PCSK9_Run-3_2026-11-11`  executed: 2026-11-11T13:04:01Z
- candidates evaluated: **24**
- runtime: 185.8 s

## Evidence-status summary

| status | count |
|---|---|
| NEEDS_EXPERIMENTAL_VALIDATION | 21 |
| REJECTED_INPUT | 3 |

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
| 1 | NM_174936.4_site_2610 | 83.74 | 0.6615 | 96032 | 23.4 | 91.2 | 1.2113 |
| 2 | NM_174936.4_site_3467 | 87.75 | 0.684 | 149966 | 3.0 | 75.2 | 1.0971 |
| 3 | NM_174936.4_site_3352 | 88.91 | 0.6807 | 26553 | 80.2 | 98.3 | 1.0841 |
| 4 | NM_174936.4_site_1091 | 83.98 | 0.6799 | 35106 | 83.5 | 97.5 | 1.0257 |
| 5 | NM_174936.4_site_2694 | 75.68 | 0.5898 | 101834 | 18.2 | 87.8 | 0.9629 |
| 6 | NM_174936.4_site_2881 | 88.81 | 0.6861 | 115631 | 38.4 | 79.9 | 0.9315 |
| 7 | NM_174936.4_site_1090 | 85.28 | 0.6812 | 24256 | 86.5 | 86.6 | 0.9223 |
| 8 | NM_174936.4_site_2884 | 80.91 | 0.6427 | 38986 | 63.8 | 78.9 | 0.9194 |
| 9 | NM_174936.4_site_2612 | 80.78 | 0.6753 | 104022 | 36.7 | 71.0 | 0.8987 |
| 10 | NM_174936.4_site_2681 | 85.62 | 0.6687 | 129747 | 3.1 | 70.5 | 0.8887 |
| 11 | NM_174936.4_site_1546 | 86.11 | 0.682 | 115523 | 41.8 | 77.8 | 0.8684 |
| 12 | NM_174936.4_site_2794 | 67.67 | 0.595 | 25238 | 83.9 | 91.5 | 0.8341 |
| 13 | NM_174936.4_site_3147 | 84.78 | 0.6843 | 148033 | 36.6 | 85.8 | 0.8249 |
| 14 | NM_174936.4_site_2618 | 76.46 | 0.619 | 28521 | 87.0 | 81.1 | 0.8059 |
| 15 | NM_174936.4_site_3355 | 81.71 | 0.6554 | 13477 | 70.9 | 53.5 | 0.7954 |

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