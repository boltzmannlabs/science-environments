# siRNA-Bench candidate report

- job: `TNF_Run-3_2026-11-11`  executed: 2026-11-11T13:11:20Z
- candidates evaluated: **24**
- runtime: 185.1 s

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
| 1 | NM_000594.4_site_1650 | 80.95 | 0.6743 | 114479 | 9.7 | 94.8 | 1.4469 |
| 2 | NM_000594.4_site_443 | 82.24 | 0.6698 | 53647 | 48.5 | 96.6 | 1.2973 |
| 3 | NM_000594.4_site_1444 | 80.85 | 0.6691 | 34834 | 22.6 | 78.4 | 1.288 |
| 4 | NM_000594.4_site_1005 | 88.28 | 0.6863 | 83252 | 37.0 | 97.9 | 1.2155 |
| 5 | NM_000594.4_site_1084 | 84.95 | 0.6851 | 135505 | 17.6 | 80.1 | 1.1567 |
| 6 | NM_000594.4_site_1646 | 80.81 | 0.6739 | 127352 | 6.5 | 79.5 | 1.1145 |
| 7 | NM_000594.4_site_1645 | 79.11 | 0.6615 | 133280 | 8.9 | 80.8 | 1.0083 |
| 8 | NM_000594.4_site_1211 | 86.48 | 0.68 | 157449 | 9.4 | 77.4 | 0.9455 |
| 9 | NM_000594.4_site_45 | 80.61 | 0.6847 | 136143 | 42.0 | 77.5 | 0.846 |
| 10 | NM_000594.4_site_1649 | 74.8 | 0.6244 | 106925 | 34.4 | 69.7 | 0.8373 |
| 11 | NM_000594.4_site_1010 | 80.22 | 0.6697 | 143291 | 36.5 | 78.0 | 0.7758 |
| 12 | NM_000594.4_site_1442 | 82.56 | 0.6793 | 41554 | 76.5 | 78.8 | 0.7417 |
| 13 | NM_000594.4_site_185 | 73.54 | 0.6155 | 45553 | 79.0 | 76.6 | 0.7206 |
| 14 | NM_000594.4_site_1443 | 79.14 | 0.6772 | 42877 | 75.8 | 75.4 | 0.7128 |
| 15 | NM_000594.4_site_853 | 68.27 | 0.5819 | 80716 | 30.0 | 69.2 | 0.7105 |

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