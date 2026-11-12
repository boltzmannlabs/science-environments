# siRNA-Bench candidate report

- job: `TTR_anchors_Run-3_2026-11-11`  executed: 2026-11-11T13:21:46Z
- candidates evaluated: **2**
- runtime: 28.8 s

## Evidence-status summary

| status | count |
|---|---|
| NEEDS_EXPERIMENTAL_VALIDATION | 2 |

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
| 1 | patisiran_derived_19nt_core | 75.16 | 0.6401 | 101367 | 24.2 | 72.9 | 0.8121 |
| 2 | vutrisiran_derived_19nt_core | 85.02 | 0.6844 | 123746 | 38.0 | 57.1 | 0.5271 |

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