# siRNA-Bench candidate report

- job: `TTR_Run-3_2026-11-11`  executed: 2026-11-11T12:42:09Z
- candidates evaluated: **24**
- runtime: 222.8 s

## Evidence-status summary

| status | count |
|---|---|
| NEEDS_EXPERIMENTAL_VALIDATION | 20 |
| REJECTED_INPUT | 4 |

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
| 1 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_278 | 84.87 | 0.6781 | 79480 | 17.0 | 88.2 | 1.3787 |
| 2 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_557 | 88.33 | 0.6837 | 82303 | 19.8 | 82.9 | 1.2619 |
| 3 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_266 | 80.97 | 0.6557 | 98809 | 25.8 | 92.3 | 1.2265 |
| 4 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_121 | 77.19 | 0.6567 | 52040 | 32.8 | 75.1 | 1.2143 |
| 5 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_262 | 83.12 | 0.6614 | 152808 | 7.9 | 89.9 | 1.0858 |
| 6 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_277 | 80.07 | 0.6709 | 105723 | 21.1 | 83.7 | 1.0812 |
| 7 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_296 | 86.18 | 0.6866 | 116477 | 40.9 | 88.3 | 1.0624 |
| 8 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_122 | 77.24 | 0.6512 | 101625 | 26.3 | 83.2 | 1.0618 |
| 9 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_265 | 73.87 | 0.6326 | 109148 | 20.5 | 81.1 | 0.9966 |
| 10 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_552 | 84.41 | 0.6783 | 79853 | 50.4 | 81.6 | 0.9797 |
| 11 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_263 | 84.28 | 0.673 | 153180 | 2.7 | 72.5 | 0.9739 |
| 12 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_503 | 85.92 | 0.6834 | 82717 | 28.1 | 76.9 | 0.971 |
| 13 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_272 | 87.62 | 0.6879 | 88828 | 49.1 | 67.3 | 0.9597 |
| 14 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_271 | 85.2 | 0.6516 | 171476 | 12.9 | 82.5 | 0.9408 |
| 15 | ENST00000237014.8|ENSG00000118271.14|OTTHUMG00000131984.4|OTTHUMT00000254948.1|TTR-201|TTR|616|protein_coding|_site_118 | 79.35 | 0.6596 | 110720 | 36.1 | 77.3 | 0.8326 |

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