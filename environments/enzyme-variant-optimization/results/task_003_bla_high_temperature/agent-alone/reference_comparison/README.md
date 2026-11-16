# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](predictions.csv): full precision and parent-relative Tm changes.
- [Predictor records](predictor_outputs.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Open-source folding stability assessment

[EvoEF1 predictions](open_source_metrics.csv) compare the complete reported reference variants and our candidates under the same paired-WT calculation. Negative folding ΔΔG predicts stabilization. [Native paired energies](evoef/paired_energies.csv) and [method settings](evoef/method.json) retain the numerical basis. Published FoldX predictions remain separately labeled; both sequence groups are recalculated here with EvoEF1.

## Packing-geometric entropy

[PACKMAN results](packman/predictions.csv) compare the parent, K319W, E336S and our candidate after identical fixed-backbone FASPR preparation. Values are J K⁻¹ mol⁻¹; changes use our evaluated parent. This is a static packing estimate. The paper’s Table S4 used MD-prepared structures, so its original values remain a separate reference. [Method and recovery](packman/method.json).
