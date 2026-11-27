# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-88a4de0767188fe09361d8781f0fb782ff888d22304e0c6d7476c424af728eff-ad5cb62c_unreported_unreported_f4aa65_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-f0e73ea0c34cf6f406c02755dd6c3282fda0305b4003b999691609b9cfac0e6b-c01c6ad4_unreported_unreported_f4aa65_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Additional stability comparison

[DDGun SEQ](sha256-1bca6a6f5e9185d22c6909b0dfc0ed323c2d0cb65105a19a1ff69c4febe21185-600acec4_unreported_unreported_f4aa65_unreported_unreported.csv) predicts unfolding ΔΔG relative to native LEH: P57A −0.6, D101V +1.5 and T85V +1.6 kcal/mol. Positive predicts stabilization. P57A/D101V were newly calculated; the exact T85V result was reused. The Pythia reference-versus-candidate comparison is retained in the same compact table.
