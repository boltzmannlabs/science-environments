# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-50f12ebcd0e78d7aa8ab6a9cc86ace24f5547bd878c224e4c368e563a59b2942-ad5cb62c_unreported_unreported_0bd28c_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-41c324a7a175821950e9a2126d9f587508c4c35c90f5192c62e76b8d4ac15b8c-c01c6ad4_unreported_unreported_0bd28c_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Open-source folding stability assessment

[EvoEF1 predictions](sha256-9edb2f6da4a7f722cef6c48f39e4e97e6aea81e4ec4285a2f2b7cb02f255ea32-600acec4_unreported_unreported_0bd28c_unreported_unreported.csv) compare the complete reported reference variants and our candidates under the same paired-WT calculation. Negative folding ΔΔG predicts stabilization. [Native paired energies](evoef/sha256-8ae801cffc76b5ede8eab2b12d4160bbfbbbe5ae208c310ea61186d86c0ab05c-d359b279_unreported_unreported_0bd28c_unreported_unreported.csv) and [method settings](evoef/method.json) retain the numerical basis. This intrinsic folding estimate is separate from the reaction-site electrostatic assessment.
