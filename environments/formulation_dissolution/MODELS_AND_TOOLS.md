# Models, algorithms and tools

This inventory distinguishes imported executable code, local algorithms, configuration and proposed capabilities. [References](../../research/formulation_dissolution/references.md) are the canonical source list. Exact installed distributions/versions and direct import inventory are recorded by `scripts/check_release.py` in [validation.json](results/validation.json). All computation here is CPU-only; no GPU or neural-network training occurred.

## 1. Dissolution kinetics — executed

`evaluation/six_model_pipeline.py` calls OpenPKFlow **2.9.0**, `openpkflow.dissolution.models.fit_dissolution_models`. The installed source uses SciPy `curve_fit`, bounded nonlinear least squares with maxfev=10000. Inputs: increasing finite nonnegative times, cumulative release %, formulation/profile label; output: parameters, convergence, warnings, in-sample AICc and predictions. Pipeline time unit is minutes. Nonfinite/failed fits are retained as failures, not perfect scores. Observations above 100% are preserved.

Let Q(t) denote percent nominal dose released. The actual implemented equations have no fitted lag, offset or asymptote:

| Model | Equation / parameters | Assumptions and limits |
| --- | --- | --- |
| Zero-order | Q=k0 t; k0 in percentage points/time | Constant rate over a restricted interval; unbounded extrapolation can exceed 100%. Not a mechanism demonstration. |
| First-order | Q=100(1-exp(-k1 t)); k1 in 1/time | Fixed 100% asymptote and proportional remaining releasable pool; heterogeneous ER matrices may not satisfy it. |
| Higuchi | Q=kH sqrt(t); kH in pp/sqrt(time) | Square-root empirical fit; classic diffusion interpretation assumes appropriate matrix geometry/sink/transport conditions, not established here. Late extrapolation unbounded. |
| Hixson–Crowell | Q=100[1-max(1-k t,0)^3]; k in 1/time | Cube-root shrinking-solid form, geometrical/surface assumptions not verified for ER matrices; implementation saturates at 100%. |
| Korsmeyer–Peppas | Q=k t^n; k in pp/time^n; n dimensionless | Semi-empirical early-release power law. Fit only points <=60%, at least four available. Full-curve metrics are extrapolation. n is not proof of a transport mechanism without geometry/conditions. |
| Weibull | Q=100[1-exp(-(t/beta)^alpha)]; alpha shape, beta time scale | Flexible empirical cumulative form; no independent mechanistic interpretation. Fixed 100% asymptote may mismatch >100% source results. |

AICc from the early-only power-law segment is not compared with whole-curve AICc. Published reconstruction: 59 converged model/profile fits; pH 6.8 and HCl kept separate; one HCl power-law exclusion. Synthetic comparison fits only training means, selects by validation macro RMSE and reports frozen test-batch metrics. These are parameter fits, not a trained composition-to-release model. Weibull-generated fixtures naturally favor Weibull and cannot establish ranolazine reliability.

`evaluation/published_benchmark.py` also implements a separate stdlib first-order reconstruction using a fixed logarithmic rate grid (per minute). It is intentionally labeled same-curve reconstruction, not a predictive holdout. The package-example probe uses pandas/NumPy/OpenPKFlow on OpenPKFlow's bundled example and is not ranolazine data.

`evaluation/exploratory_scenarios.py` imports OpenPKFlow private `_first_order` and `_weibull` equations, explicitly version-pinned. Its times/rates/scales are HOURS, unlike the six-model pipeline. No fit to the research paper or synthetic observations occurs. Private API use is a portability risk; do not upgrade without re-verification.

## 2. Optimization, simulation and sensitivity — executed

- **Grid enumeration:** prescribed Compritol/Carbopol/hardness axes, balanced Avicel, deterministic constraint rejection; 117 feasible points in the default configuration. This is exhaustive grid search, not Bayesian optimization or ML training.
- **Monte Carlo:** stdlib `random.Random(2931)`, 128 independent uniform parameter draws for each of first-order/Weibull, 256 scenarios/candidate. Ingredients and hardness alter an explicitly invented log-rate term. Draws are shared across candidates/comparators. p05/p50/p95 are interpolated quantiles of assumptions, not calibrated uncertainty or observed lab variability.
- **Weighted score:** 0.75 assumed joint-goal fraction +0.15 clipped release margin +0.10 lower-polymer-mass preference. Goals and preferences are not approved QC criteria or real cost/manufacturability predictions.
- **Pareto filtering:** non-dominance on scenario-goal fraction, 24h p05, polymer mass and 2h p95. No evolutionary search is implemented.
- **Sensitivity:** one-at-a-time assumed coefficient effects; mirrored positive/negative slopes and same-draw zero-effect negative control. When rate effects vanish, profile-based differences vanish; residual rankings reflect the mass preference/tie-breaking, not learned evidence.
- **Bounded integration wrapper:** `simulation.py` validates supported dose/config/grid, preflights candidate/scenario budgets, delegates to the existing simulator and records every candidate. It abstains rather than reporting a partial-grid winner if the full grid exceeds budget. Comparator/detail/sensitivity calls are extra equation evaluations, not new independent candidate proposals. No process walltime guarantee.
- **Acquisition ranker v1:** `models/acquisition_policy.py`, weighted sum of supplied objectives for caller-marked feasible, cost-labelled candidates under remaining cost; deterministic sorting. Implemented/tested illustrative policy, not scientifically validated or learned.
- **Experimental design specialist:** records factors/responses/controls/replicates/rationale for a supplied hypothesis and returns an approval-required proposal. No factorial/optimal DoE generation or physical execution occurred.

## 3. Mixture prediction and compatibility/stability

**nearest-mixture-v1** (`models/mixture_predictor.py`): implemented deterministic Euclidean nearest neighbor over an explicit roster of mass fractions summing to one. Fit requires source-linked measured target rows in a matching unit; output is predicted scalar, distance, source and unestablished uncertainty. No ranolazine measured-data training occurred. It is not a time-conditioned whole-profile surrogate; groups/method eligibility require external curation. Tests use synthetic contract rows, not a measured scientific benchmark.

**Compatibility/stability triage** (`agents/compatibility_stability.py`): source/material/evidence filtering only. Inputs are material IDs and supplied findings; output is matching findings or insufficient_data. No RDKit descriptors/fingerprints, functional-group rules, similarity retrieval, chemical interaction predictor, degradation kinetics, Arrhenius, humidity model or validated stability prediction is implemented or executed. No compatibility training occurred. Missing findings remain missing.

**Composition/constraint validator** (`tools/mixture_validator.py`): finite nonnegative mg or % w/w, mass/sum balance, material identity, dose/potency and caller bounds/process windows. Arithmetic validation does not establish manufacturability, chemical compatibility or equivalence.

## 4. Validation algorithms — executed software checks

- Whole-formulation LOFO mean baseline for six related pH 6.8 summaries and a separate three-profile HCl baseline; zero time excluded. Not independent-source or commercial-lot validation. Reference formulation remains context, not a duplicate training row.
- Synthetic Weibull generator: seed 31415, four arbitrary rate labels, 24 batches, lognormal scale effect and point noise; fixed whole-batch split 12/4/8. Fits use training means only. Test MAE/RMSE/bias/residuals exclude the shared zero anchor.
- Illustrative interval: maximum absolute residual per validation batch and interpolated 90th percentile over only four validation batches; empirical test coverage/width reported, calibration not established.
- OpenPKFlow f2 in synthetic benchmarks is arithmetic only; out-of-range predictions are ineligible. `evaluation/profile_comparison.py` adds stdlib f1/f2 for supplied context-matched profiles under explicit mathematical guards. Neither supplies unit-count/CV or approved ER regulatory acceptance evidence.
- `evaluation/six_model_verifier.py`, `exploratory_verifier.py`, `verifier.py`: independent arithmetic/label/split/mass/negative-claim checks. They are software audits, not experimental confirmation.
- Group-hash split and descriptive error helper for an authorized future measured dataset: implemented; no eligible ranolazine dataset supplied. No A/B/C/D matched base-agent comparison or time-aware measured prospective validation has occurred.

## 5. Software and infrastructure

| Tool/library | Actual role, I/O and status | Training / restrictions |
| --- | --- | --- |
| Python 3.14.7 tested; >=3.10 declared | stdlib dataclasses, JSON/CSV/XML, pathlib, hashlib, random, statistics, argparse, unittest, urllib, concurrent futures; local state, APIs and reports | No training; Python/PSF licensing. Other Python versions not exercised here. |
| OpenPKFlow 2.9.0 | Imported equations, fitted models, example data and f2; optional simulation dependency | MIT from installed metadata; no bundled vendor code/checkpoints. |
| NumPy 2.5.4 | Direct curve arrays/math and package-example error computation; OpenPKFlow dependency | BSD family; no training. |
| SciPy 1.18.1 | OpenPKFlow's nonlinear least-squares backend, transitive import | BSD family; curve parameter fitting only. No ODE/PDE solver used. |
| pandas 3.1.0 | Direct CSV/grouping in package-example probe, OpenPKFlow dependency | BSD family; not a data source or trained predictor. |
| Matplotlib 3.11.2 | Direct headless synthetic overlay/residual PNGs | Matplotlib license; CPU only. |
| Pydantic, Jinja2, Typer | Dependencies installed through OpenPKFlow, not direct environment imports | Installed metadata/versions in receipt. Not separate environment models or claimed trained tools. |
| pytest, unittest | Automated synthetic/contract/integration tests | pytest MIT; stdlib unittest. Passing tests does not establish accuracy. |
| setuptools/build/pip, Ruff | Package build/install and fatal-error lint tooling | Versions/actual commands in receipt. No repo-wide type-check contract exists. |
| Git / GitHub CLI | Feature branch, issue, commit/push and PR workflow | No runtime scientific dependency. Authorization handled outside repository. |
| Local specialist contracts | Six bounded dataclass functions and coordinator; typed requests -> conservative findings/status | Not autonomous model agents; no LLM/model weights needed. |
| Historical coding subagents | Prior read-only modeling/validation/provenance reviews indexed in provenance | Review text is not measurements or a deployed multi-agent framework; no new scientific agent run claimed here. |
| Approved callable registry | Injected name/version/capability/validators/callable with timeout/retry and predicted-output gate | Starts empty. Timeout cannot prove cancellation; no live scientific service or lab qualification. |
| Lab controller | Fixture submission/poll/ingest and dry-run contract | Fixture cannot create measured evidence; local approval attestation is not signed GMP authentication. |

Executed I/O formats: JSON, JSON-syntax YAML, CSV, XML, HTML, PNG, TOML and Markdown. No YAML parser, relational database, neural trainer or external reporting service is required by the default workflows. Licenses are package metadata summaries, not a blanket grant for public-source content; see [notices](THIRD_PARTY_NOTICES.md).

## 6. Data sources and proposals

- FDA/openFDA enforcement and label JSON; DailyMed SPL XML: historical identity checks, not quantitative dissolution or batch formula. Local public snapshots preserve original hashes; integration needs no live FDA fetch.
- US6525057B2 patent HTML/Table 4: prior primary-text sequence check; HCl summary curves, no unit variance. 201741007784 pH 6.8 table: supplied transcription, independent primary numerical check unavailable (source 403 historically). Neither supports recalled-lot QC scoring.
- Zenodo 1170150/1311884: research-publication metadata; 1170150 recipe/hardness and author endpoint context, not curated measured training profiles. Original PDFs are not bundled. Catalog records licence/quality flags. References distinguish metadata checks from table verification.
- **Proposed/not run:** PTCalc, mechanistic particle/mass-transfer dissolution, OSP/PK-Sim, ODE/PDE transport; need verified solubility/solid state/PSD/matrix/method inputs and a documented runtime contract. PTCalc status tool_unavailable.
- **Proposed/not run:** Bayesian optimization/GP/BoTorch/Optuna, evolutionary optimization, learned multiobjective surrogate, automated DoE. Need defensible measured data/objectives/bounds and comparison protocol.
- **Not imported or executed:** RDKit, scikit-learn, XGBoost, LightGBM, CatBoost, PyTorch, TensorFlow. Mentions/proposals do not make them dependencies. No PubChem/Hugging Face training dataset or live controlled LIMS access was used.
