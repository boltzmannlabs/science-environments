# Workflow Design & Selection

## Candidate workflows
- **Workflow A (SELECTED):** AntiBMPNN (structure-conditioned, all 6 CDRs) -> sequence filter (framework + disulfide) -> Antibody_Prediction (stability/solubility) -> fixed-pose CDR side-chain reconstruction on 1N8Z -> ProDIGy binding metric.
- **Workflow B:** ProteinMPNN (CDR-H3 only) -> Boltz2 -> ... (historical run, in evidence/).
- **Workflow C:** De novo random generation -> Boltz2 -> ... (less targeted).

## Why Workflow A
1. Structure-conditioned: designed CDRs fit the reference 1N8Z backbone (most faithful to the reference binding region).
2. Edits all 6 CDRs (H1/H2/H3, L1/L2/L3) — more degrees of freedom for interaction optimization than CDR-H3 only.
3. Preserves framework + disulfides (verified).
4. Fixed-pose reconstruction enables a matched-conditions binding comparison (closest to the benchmark's fixed-pose REF15 protocol).
5. Boltz2 de novo VH-HER2 prediction is unreliable (ipTM 0.245), so a fixed-pose approach is more defensible for the binding metric.

## Limitations
- REF15 (Rosetta) unavailable — primary benchmark metric not computable.
- ProDIGy is a contact-based predictor (RMSE ~2.6 kcal/mol); a 1 kcal/mol difference is within the noise.
- Side-chain reconstruction uses ideal geometry oriented by the original CB direction — an approximation, not a full rotamer optimization.
- Boltz2 candidate structure downloads failed (300s TTL); reference Boltz2 structures available.
