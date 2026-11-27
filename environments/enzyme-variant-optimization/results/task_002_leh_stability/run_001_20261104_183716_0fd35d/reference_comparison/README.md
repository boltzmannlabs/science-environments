# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-aaba3d1b64c5fc66d63ecc6167f9d57ca0378f06da99ef281381b15d1cffbfae-ad5cb62c_unreported_unreported_0fd35d_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-5e89963d091da5891d7dd4a55e7914b0351e960be4f4b971b9dfad0a9830db24-c01c6ad4_unreported_unreported_0fd35d_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. The reference sequence was not reconstructed; comparison uses our selected parent.
