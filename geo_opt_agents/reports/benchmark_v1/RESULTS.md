# GeoOpt-Bench v1.0 frozen pilot

Backend: **PySCF+GPU4PySCF 1.7.0 + SciPy BFGS**.

- Specialist qualification records: **18**
- Qualification status: **16 pass, 2 review, 0 fail**
- Live GPU specialist-linked results: **3**
- Input packets: **18/18 valid**
- Automated tests: **6 passed**
- Hashes recorded: **148**

## Cost and reproducibility

The local run used no language-model API calls or token budget. Engine wall times are preserved in the per-case JSON reports. Every frozen input, task packet, qualification result, and engine result is hashed with SHA-256 in `summary.json`.

## Scope limits

This is a frozen pilot, not a claim that all 18 specialists have independent live optimization implementations. The three-arm comparison, repeat panel, Hessian/frequency backend, protein-ligand reference case, and broader task expansion remain explicitly not evaluated.
