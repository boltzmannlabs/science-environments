# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-bcca74cc9947fde0d317995462ca7f278be1f18f2f5b689cc554dff084f66174-ad5cb62c_unreported_unreported_92629f_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-b1b502cd5d745421c81cf07e7741c823544c27defdddaae27929d353b0f1376a-c01c6ad4_unreported_unreported_92629f_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. The reference sequence was not reconstructed; comparison uses our selected parent.
