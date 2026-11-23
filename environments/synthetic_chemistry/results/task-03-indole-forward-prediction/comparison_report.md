# Task 03 — literature product and prediction comparison

[Task](../../tasks/task-03-indole-forward-prediction/README.md) · [Literature reference and methodology](../../benchmarks/task-03-indole-forward-prediction/README.md) · [Candidate files](README.md)

## Source verification and evidence boundaries

Names and assignments in the supplied supporting information support the mapping from input 1a–1g and 1j–1l to reported products 2a–2g and 2j–2l. This is a name/assignment check, not independent digitization of every figure. Candidate-list results below use manually transcribed outputs and are conditional on their faithful transcription. Similarity is Morgan radius-2, 2048-bit Tanimoto, not a model probability or yield.

| Input → literature product | Transcribed candidates | Exact match | Nearest original rank | Similarity |
|---|---:|---|---:|---:|
| 1a → 2a | 29 | No | 2 | 0.5333 |
| 1b → 2b | 28 | No | 10 | 0.5000 |
| 1c → 2c | 31 | No | 15 | 0.4062 |
| 1d → 2d | 30 | No | 3 | 0.4898 |
| 1e → 2e | 29 | No | 3 | 0.5106 |
| 1f → 2f | 30 | No | 4 | 0.4898 |
| 1g → 2g | 30 | No | 4 | 0.4898 |
| 1j → 2j | 30 | No | 9 | 0.4706 |
| 1k → 2k | 30 | No | 15 | 0.4444 |
| 1l → 2l | 30 | No | 8 | 0.4706 |

## Interpretation

The initially selected products did not match the ten corresponding references. Among the transcribed candidates, no exact match was found across 297 entries. Nine nearest candidates preserve the indole/secondary-amine side chain but omit the literature product's C2 aryl group; the 1c nearest candidate retains an amide and has a C2 formyl rather than the required direct aryl linkage. The earlier assistant-selected 1d structure was an extrapolation, not a returned model candidate. Some candidate transformations require reagent sources absent from the submitted input; this is a missing-evidence flag, not proof of impossibility.

This is a substrate-only prediction assessment, not a reproduction of the reported experimental process: solvent and other experimental context were not encoded in the model submissions. It cannot establish why the model missed the products or whether omitted context caused the errors. The ten related cases do not measure general performance on unrelated chemistry. No alternative candidate has been experimentally verified or shown superior.

## Next validation

Reconcile all transcribed candidate identities, ranks and counts with original structured outputs without resubmitting the blind jobs; retain original ranks and agent selection separately. Digitize and independently verify paper structures if exact source-graph confirmation is required. Report molecule-only versus any separately authorized condition-aware assessment as different experiments.
