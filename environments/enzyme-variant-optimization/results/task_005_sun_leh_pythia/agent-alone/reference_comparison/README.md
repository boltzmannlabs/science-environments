# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](predictions.csv): full precision and parent-relative Tm changes.
- [Predictor records](predictor_outputs.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Additional stability comparison

[DDGun SEQ](open_source_metrics.csv) predicts unfolding ΔΔG relative to native LEH: P57A −0.6, D101V +1.5 and T85V +1.6 kcal/mol. Positive predicts stabilization. P57A/D101V were newly calculated; the exact T85V result was reused. The Pythia reference-versus-candidate comparison is retained in the same compact table.
