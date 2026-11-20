# Environment Specification

This repository contains saved proteomics analysis outputs and standalone benchmark evaluators. It is not packaged as an installable Python application and does not currently include a dependency lockfile.

## Recommended environment

- **Python:** 3.11 or newer
- **Operating system:** Linux, macOS, or Windows with a standard Python 3 installation
- **Input formats:** CSV and tab-separated text (TSV)
- **Hardware:** No GPU or other specialized hardware is required

The repository does not define a single pinned, tested environment for all tasks.

## Python packages

Install the following packages to run all seven benchmark evaluators and their reference helpers:

```bash
python -m pip install numpy pandas scipy scikit-learn
```

Package roles:

| Package | Used for |
| --- | --- |
| NumPy | Numeric arrays and numerical calculations |
| pandas | Reading and processing protein and peptide tables |
| SciPy | Statistical tests, distributions, and optimization |
| scikit-learn | Imputation helpers and evaluation metrics |

No plotting library is required for evaluation. The evaluators implement multiple-testing correction directly and do not require statsmodels.

## Dependencies by task

| Task | Evaluator and reference-helper dependencies |
| --- | --- |
| 01 | NumPy, pandas, scikit-learn |
| 02 | NumPy, pandas, SciPy, scikit-learn |
| 03 | NumPy, pandas, SciPy, scikit-learn |
| 04 | NumPy, pandas |
| 05 | NumPy, pandas, SciPy |
| 06 | NumPy, pandas, SciPy |
| 07 | NumPy, pandas, SciPy |

Evaluation reads completed outputs from `results/<task>/run_1/` or `run_2/`; it does not require the agent's original analysis code or execution environment.

## Reproducibility

For reproducible evaluation, record the Python and package versions used and retain an environment export or lockfile alongside new evaluation reports. Installing unpinned packages does not guarantee identical results across environments. Software versions mentioned in an agent's analysis report describe that analysis run, not necessarily the environment used for benchmark evaluation.

## Running evaluators

From the repository root, inspect evaluator options with:

```bash
python3 -B benchmark/<task-directory>/evaluation.py --help
```

Tasks 01–04 and 06 require a truth directory; Tasks 05 and 07 derive truth from the input annotations and experiment design. See [benchmark/SCORING.md](benchmark/SCORING.md#running-an-evaluation) for input paths, run selection, and evaluation commands, and [README.md](README.md) for the repository layout.
