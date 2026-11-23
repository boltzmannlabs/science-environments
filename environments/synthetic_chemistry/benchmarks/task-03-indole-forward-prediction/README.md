# Task 03 — indole forward-prediction benchmark

[Task and input structures](../../tasks/task-03-indole-forward-prediction/README.md) · [Results](../../results/task-03-indole-forward-prediction/README.md)

## Primary reference and supplied product key

Zhang, Lang, Luo, Han, Zeng and Li, “Precision indole skeletal editing for single-carbon replacement,” *Science* **392**, 512–518 (2026), [DOI: 10.1126/science.aec3587](https://doi.org/10.1126/science.aec3587). The user supplied the article's supporting information; the literature audit identifies substrates and products in printed SI pp. 14–18 and 55–58. The SI PDF is not redistributed here. The [task outline](https://github.com/boltzmannlabs/science-environments/blob/Rebolt/environments/Tasks/task2_forward_prediction_indole_skeletal_editing.md) is an outline, not an independently verified ground-truth table.

The user-provided [reference product SMILES](literature_products_reference.md) were held back from the predictor and used only for post hoc evaluation. SI chemical names and assignments support 1a–1g and 1j–1l mapping to 2a–2g and 2j–2l, including their named substituents; this was not independent digitization of every structure drawing. Main-article full text was inaccessible to the original audit.

## Evaluation methodology

Compare each returned candidate only against its own reference by RDKit canonical isomeric SMILES; enumerate original one-based model ranks. Fingerprint resemblance uses Morgan radius 2, 2048-bit fingerprints and Tanimoto similarity; it is not model confidence or an experimental outcome. Manually transcribed candidates remain provisional until reconciled with original machine-readable outputs. Literature experimental products are reference observations, whereas candidate SMILES and similarity are computational. See the [assessment](../../results/task-03-indole-forward-prediction/comparison_report.md).
