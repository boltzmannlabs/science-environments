# Models and tools

## Task - 02 ownership and execution

Task-02 uses a standard-library archive verifier in `formulation_environment.task_02_ranolazine_er_dissolution`, not the clarithromycin fitting engine. Original ranolazine models/results remain separate and unchanged. See the [task folder map](../task-02-ranolazine-er-dissolution/README.md).

| Component | Actual role | Boundary |
|---|---|---|
| NumPy 2.2.4 / pandas 3.0.3 / SciPy 1.15.3 | Portable offline fitting, exports, factorial algebra and checks | Not physical formulation validation |
| Eleven v2 configurations | Mean/interpolation baselines; free/capped/fixed first-order and Weibull; free/capped/origin-constrained logistic | Held-out timepoint diagnostics within one source study |
| PTCalc.Core 1.1.0 + MathNet 5.0.0 | Actually executed in archived v1 follow-up; 256 catalog fits + 32 variants | Curated outputs supplied; upstream runtime/source is not vendored or required for the portable v2 runner |
| PubChem PUG REST / Europe PMC | Source chemistry and primary-study abstracts retrieved in original investigation | No exact-recipe ground truth |
| RDKit 2026.03.1 | Archived molecular descriptors | No solubility/compatibility prediction from descriptors alone |
| Optuna 4.9.0 | Archived 100-trial restricted information-design search, exactly enumerated | Not pharmaceutical performance optimization |
| scikit-learn 1.9.0 | Archived composition geometry | No fitted endpoint surrogate or applicability domain |
| Agent Scientist | Coordinated source retrieval, calculations, audits and reporting | No specialist agents or laboratory backend executed |

## Equation and metric definitions

First-order: `A(1-exp(-kt))`; Weibull: `A(1-exp(-(t/tau)^beta))`; time-logistic: `A sigmoid(k(t-g))`. Free A is numerically bounded 1..150; capped A 1..100; fixed A=100. Three deterministic optimization starts are retained. No target efficacy model is trained.

v2 reports mean RMSE `sqrt(SS/n)` and MAE in percentage points; MAPE is relative percent. PTCalc's residual RMSE uses `n-p`, and its AIC/AICc conventions differ from variance-counting formulations. Do not compare raw metrics across definitions. Library convergence flags do not demonstrate true mechanisms.

PTCalc 1.1.0 falls back to all points for KP when fewer than two meet F<=60%; all sixteen published KP mechanism interpretations were rejected. Weibull displayed Td is derived, not another fitted parameter. Full/truncated f2 arithmetic is not a regulatory similarity determination.

## Provenance and unavailable tools

PTCalc archive DOI: https://doi.org/10.5281/zenodo.22957458 . Upstream SDK, tool source and full third-party article HTML are intentionally not redistributed. v1 outputs record the actual scope; v2 execution uses SciPy and does not silently rerun PTCalc. BoTorch/GPyTorch, degradation models, calibrated process simulations and live lab services were not used.
