# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-5d44adefca89b900c43fda6dba71a7e7937b3096c361dbde84a7df4515900cf1-ad5cb62c_unreported_unreported_7cf059_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-ebbdf633cc76ae873e4c1c4499a14ee05e5b7718f3b94854b5ab1fc9edbad9e1-c01c6ad4_unreported_unreported_7cf059_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Open-source folding stability assessment

[EvoEF1 predictions](sha256-3833b7b30b4a4bffc1a086d503413923f48c6488e1177daaca1244366db0de4e-600acec4_unreported_unreported_7cf059_unreported_unreported.csv) compare the complete reported reference variants and our candidates under the same paired-WT calculation. Negative folding ΔΔG predicts stabilization. [Native paired energies](evoef/sha256-2a33917fda72f3cbbda936064c5c509b024b23452a97101454fd501a0bd1a9c8-d359b279_unreported_unreported_7cf059_unreported_unreported.csv) and [method settings](evoef/method.json) retain the numerical basis. Published FoldX predictions remain separately labeled; both sequence groups are recalculated here with EvoEF1.

## Packing-geometric entropy

[PACKMAN results](packman/sha256-26e3d00bd71f40ab9e9ad08233335d641c03af5f255ccd0c70aa7e3dc9bde54f-5fc14272_unreported_unreported_7cf059_unreported_unreported.csv) compare the parent, K319W, E336S and our candidate after identical fixed-backbone FASPR preparation. Values are J K⁻¹ mol⁻¹; changes use our evaluated parent. This is a static packing estimate. The paper’s Table S4 used MD-prepared structures, so its original values remain a separate reference. [Method and recovery](packman/method.json).
