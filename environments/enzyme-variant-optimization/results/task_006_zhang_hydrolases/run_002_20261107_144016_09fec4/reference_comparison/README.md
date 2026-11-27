# Reference property comparison

Tm, raw pHPred and NetSolP predictions use the same endpoint methods for our selected candidates and reconstructable reference variants. These calculations followed original selection.

- [Prediction table](sha256-cb96b82f6750c405245ef8aa661c4aa4a8a4250b341909dec8cc535e63cd27c2-ad5cb62c_unreported_unreported_09fec4_unreported_unreported.csv): full precision and parent-relative Tm changes.
- [Predictor records](sha256-42c712f9443a679987cfcd2a2b7374ffe05f1fcca476484bb0acda2960b3713d-c01c6ad4_unreported_unreported_09fec4_unreported_unreported.csv): method, model, units and provenance for each endpoint.
- [Shared assessment jobs](jobs.json).

Tm uses TemBERTureTm ensemble mean in °C; NetSolP is the native S-mode ensemble score (0–1); pHPred is retained on its returned raw scale. Neither a NetSolP percentage nor experimental activity is inferred. Reference sequences and their declared backgrounds are retained in reference_sequences.fasta.

## Open-source folding stability assessment

[EvoEF1 predictions](sha256-075a68ec096aa016802f45d6ebd99e106828940d310537742334d2c0eaac05b5-600acec4_unreported_unreported_09fec4_unreported_unreported.csv) compare the complete reported reference variants and our candidates under the same paired-WT calculation. Negative folding ΔΔG predicts stabilization. [Native paired energies](evoef/sha256-f873a5ce4ab692114613c0f1a71ea0ec070f066eb5808f93e513617e4a8ff38c-d359b279_unreported_unreported_09fec4_unreported_unreported.csv) and [method settings](evoef/method.json) retain the numerical basis. These folding-energy estimates complement the paper-method Pythia and ESM score comparisons.
