# Formulation Optimization Gym — Ranolazine ER investigation and exploratory modeling

Status: working evidence-first software environment and **unvalidated** research-prototype simulation. Case of interest: ranolazine extended-release 500 mg; Glenmark recall D-0092-2024. This document records work actually performed, not a claim of product optimization or regulatory validation. See [environment README](README.md), [research notes](../../research/formulation-optimisation-gym-environments/research-notes.md), and [references](../../research/formulation-optimisation-gym-environments/references.md). The executable implementation is the [working gym](scripts/formulation-optimization-gym/).

## Input problem and scientific decision

Question: Can an agentic formulation-optimization system identify ranolazine formulation/process factors that could cause an extended-release dissolution failure, then propose a more robust 500 mg formulation? Required: trace the reported recall to an authoritative record, distinguish observed facts from hypotheses, inspect product and external research data, implement an auditable investigation environment, explore models/candidate designs when explicitly authorized, and test/report what is and is not established.

Answer so far: the system verified the public recall and product-label identity and supports bounded, source-linked analysis. It has **not** identified the recalled lot's failure mechanism or experimentally validated a better formulation. Its later user-authorized exploratory compositions are different research prototypes under unverified assumptions, not Glenmark batch formulas or approved substitutions.

## Repository layout and relationship to implementation

```text
science-environments/
├── README.md
├── research/
│   ├── README.md
│   └── formulation-optimisation-gym-environments/
│       ├── research-notes.md
│       └── references.md
└── environments/
    └── formulation-optimisation-gym-environments/
        ├── README.md
        ├── ENVIRONMENT_SPEC.md
        ├── ENVIRONMENT_REPORT.md     # this report
        ├── STATUS.md
        ├── ISSUES.md                 # observed run blockers and resolved defects
        ├── scripts/formulation-optimization-gym/ # runnable snapshot
        ├── skills/
        ├── benchmark/
        ├── results/
        ├── config/README.md
        ├── tasks/README.md
        └── tests/README.md
```

A runnable, unchanged-byte snapshot is packaged in `scripts/formulation-optimization-gym/`; the original working gym remains an untouched sibling. Documentation links point to the packaged code, source-linked episode files, tests and output. The original raw public snapshots were copied without altering them. No other environments in the user's example layout were modified or claimed to exist.

## Research workflow actually carried out

1. **Discovery and verification.** Queried the documented [FDA Enforcement Reports API](https://open.fda.gov/apis/drug/enforcement/) by exact recall number. Stored separate FDA responses for Glenmark D-0092-2024 and Ajanta D-0010-2027; cross-matched each FDA label to its package NDC and SPL set ID. Used DailyMed's documented SPL v2 XML service to independently cross-check current set ID, version, and NDC. Importers recorded original response URLs, SHA-256 hashes, source-linked claims and evidence labels. Current label versions were not treated as historical batch records.
2. **Evidence triage.** Retained the Ajanta 1000 mg event as a distinct case; only Glenmark 500 mg is targeted here. Enumerated absent controlled method/specifications, measured unit/timepoint profiles, original batch formula, API PSD, material properties, manufacturing settings and history. A recall reason is not a dissolution curve. The public FDA dissolution-method search returned an anti-abuse page; no method or manufacturer QC limits were fabricated.
3. **Research discovery.** Discovered two ranolazine ER research studies via Zenodo: [10.5281/zenodo.1311884](https://doi.org/10.5281/zenodo.1311884) and [10.5281/zenodo.1170150](https://doi.org/10.5281/zenodo.1170150). Cataloged DOI, reported CC-BY-4.0 license, PDF SHA-256 and extraction-quality warnings. The first article's dissolution table has misaligned/blank extraction and a possibly nonmonotonic profile; the second primarily graphs profiles. Neither article supplies recalled-lot results or an appropriate measured model holdout.
4. **Gym implementation.** Built persistent episode state, validated actions, observation labels, budgets, approved-tool registry/adapters, deterministic mixture validation, six bounded specialist contracts, independent evidence auditor/verifier, conventional baseline and holdout harness. Added importers, schemas, configuration, CLI, docs and tests. Historical cases remain source-linked and abstain when critical measurements/criteria are missing.
5. **Case orchestration.** Ran six requested investigation roles on the Glenmark episode with raw-source-hash checks and an independent verifier. The output is [D-0092-2024.investigation.json](scripts/formulation-optimization-gym/data/processed/D-0092-2024.investigation.json): `insufficient_data_for_optimization`; no recalled-product candidate or prediction was inserted into the episode.
6. **Model smoke test.** Installed OpenPKFlow 2.9.0 in a separate scratch virtual environment; checked its model contract and ran five empirical-model fits on its own bundled example profiles only. In-sample AICc favored Weibull for the package's `reference` example and Hixson–Crowell for its `test` example. These are **software demo** outputs, not ranolazine model-fit results. See [demo JSON](scripts/formulation-optimization-gym/data/processed/openpkflow_package_demo.json).
7. **Authorized exploratory simulation.** After explicit user permission to use unverified inputs, extracted the clearer 500 mg *research-prototype* ingredient table and hardness values from [10.5281/zenodo.1170150](https://doi.org/10.5281/zenodo.1170150). Checked source PDF hash and recipe mass balance. Kept all paper values `literature_reported`; set hypothetical dose potency, release kinetics, ingredient-effect directions, exploratory windows and toy goals as `assumed`. Used OpenPKFlow's version-pinned first-order and Weibull functions, Monte Carlo scenario sampling and an exhaustive mass-balanced grid; performed sign-reversal sensitivity analysis, multi-objective Pareto screening and a declared arbitrary scalar ranking. No simulated data were relabeled as measurements or used to fit a pseudo-observed dataset. See [full simulation report](scripts/formulation-optimization-gym/EXPLORATORY_SIMULATIONS.md).
8. **Independent checks and limits.** Ran an independent mechanical scenario verifier, unit tests in base and model-enabled Python, and the no-holdout benchmark. Did not run Open Systems Pharmacology particle dissolution, Bayesian optimization, a physical experiment, or a live Boltzmann dissolution connector: missing case-specific inputs, validated objectives, runtime/permissions or authorized access prevented those steps. Software consistency does not establish drug-product accuracy.

## Sources: what was verified versus assumed

| Item | Status | Scope |
| --- | --- | --- |
| FDA recall D-0092-2024: Glenmark 500 mg, NDC `68462-319-60`, lot `17230388`, report date 2023-11-15, reported dissolution OOS | FDA-reported fact | [Exact enforcement query](https://api.fda.gov/drug/enforcement.json?search=recall_number%3A%22D-0092-2024%22); not a numeric profile or cause |
| Current Glenmark SPL set `0cf58732-c242-49b0-8e3f-248778b4458d`, effective 2026-01-23; 500 mg film-coated oblong tablet marked G/319; qualitative excipient list | FDA/DailyMed-reported current label | [SPL XML](https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/0cf58732-c242-49b0-8e3f-248778b4458d.xml); label postdates recall and gives no historical fractions |
| Ajanta D-0010-2027, 1000 mg, different lot and manufacturer | Separate FDA-reported case | [Exact enforcement query](https://api.fda.gov/drug/enforcement.json?search=recall_number%3A%22D-0010-2027%22); never pooled with Glenmark |
| F1–F8 research recipes, nominal 500 mg API/695 mg tablet and reported hardness; F8 abstract's 99.5% at 24 h | Literature-reported for **other research tablets** | [Saritha and Sanjana](https://doi.org/10.5281/zenodo.1170150); not batch composition, manufacturer QC profile or validated holdout |
| Kinetic constants, recipe-to-release effects, uniform scenario ranges, 100% nominal potency, hardness grid, and illustrative 2 h/24 h goals | **Assumed** | [Scenario configuration](scripts/formulation-optimization-gym/configs/exploratory_ranolazine_500.json); goals are **not** FDA/manufacturer specifications |
| Curves, scenario percentile spread, conditional pass fractions, Pareto membership, arbitrary scores | **Simulated/derived** | [Scenario results](scripts/formulation-optimization-gym/data/processed/ranolazine_research_scenario_results.json); no calibrated uncertainty or experimental confirmation |

Glenmark's current label does not list Compritol or Carbopol 934 from the exploratory paper. Thus even a mass-balanced scenario is not established as a Glenmark-feasible or approved formulation.

## Tools and models used — precise execution status

| Tool/model | What actually happened | What cannot be inferred |
| --- | --- | --- |
| SCI terminal/file tools; `sci tools list`, `sci mcp list` | Inspected local capabilities, stored artifacts, ran importers, scripts and tests | Registry access is not an authorized scientific measurement API; autonomous delegation was unavailable |
| HTTPS `curl` to documented FDA openFDA and DailyMed APIs; Zenodo public records | Retrieved public recall/labels and research metadata/PDFs; verified identifiers and snapshots | Public material does not reveal controlled QC SOP, process conditions or failing-lot numbers |
| Python standard library (`json`, `hashlib`, `unittest`, `random`), local validators | Executed ingestion, provenance, deterministic mixture checks, episode audit and seed-fixed scenario generation | Mechanical feasibility is not regulatory/manufacturing feasibility |
| OpenPKFlow **2.9.0**, SciPy/NumPy/pandas in isolated model environment | Ran package-example model fits and `f1/f2` demo; ran first-order/Weibull functions for explicitly assumed research-prototype scenarios | No fitted ranolazine product model, calibrated interval or independent product-model validation |
| Exhaustive grid, fixed-seed Monte Carlo, Pareto filter, arbitrary weighted score; one-at-a-time sensitivity | Evaluated 117 grid points × 256 assumed scenarios, compared literature recipe scenarios, detected sign sensitivity | This is **not** trained Bayesian optimization or a statistically justified probability of passing controlled criteria |
| Open Systems Pharmacology / PK-Sim particle dissolution | Documentation consulted; **not run** (no compatible runtime or qualified PSD/solubility and product inputs) | No particle-scale or PBPK prediction |
| BoTorch, Optuna, RDKit, scikit-learn, PubChem PUG REST, PubMed, Hugging Face datasets | Availability or access checked, but **not used** for case-specific numerical prediction/training | Installation/public catalog listings do not create measured lot data |
| Boltzmann connector | Bundled but locked pending authorized setup; **no API invocation** | No Boltzmann dissolution simulation or measurement |

[Source/tool matrix](scripts/formulation-optimization-gym/docs/source_and_tool_matrix.md) provides more detailed dispositions, including the inaccessible FDA interactive dissolution search.

## Specialist roles and real implementation

Requested investigation-role names were backed by local bounded specialist calls in [`agents/investigation_coordinator.py`](scripts/formulation-optimization-gym/agents/investigation_coordinator.py); **six independent AI processes were not spawned**. The underlying gym also has six typed local contracts under [`agents/`](scripts/formulation-optimization-gym/agents/): `formulation_design`, `compatibility_stability`, `property_prediction`, `experimental_design`, `constraint_critic`, and `evidence_auditor`.

| Requested role | Work performed |
| --- | --- |
| Recall Research Agent | Checked FDA recall identity, manufacturer, strength, lot; separated Ajanta |
| Evidence Retrieval Agent | Matched three Glenmark public raw snapshots to episode SHA-256 source links, marked missing controlled data |
| Formulation Analysis Agent | Applied bounded design/compatibility contracts; abstained for recalled batch; separately mass-balanced published prototype compositions |
| Dissolution Modeling Agent | Abstained for Glenmark due missing method/profiles; executed OpenPKFlow software demo and separately labeled assumed prototype simulations |
| Experimental Design and Bayesian Optimization Agent | Documented missing objective/bounds/measurements and required approval; ran a transparent hypothetical grid/Pareto exercise, **not** BO or a physical DoE |
| Independent Validation Agent | Episode evidence auditor and verifier; separate `evaluation/exploratory_verifier.py` checked scenario arithmetic, units/mass, rankings and quantile ordering, not empirical accuracy |

## Outputs actually achieved

- Source-linked FDA/DailyMed episodes for two **separate** recalls. Glenmark case has valid public-source hash checks, accepted public provenance and no independent verifier findings, but remains `insufficient_data_for_optimization`.
- Distinct OpenPKFlow **package-demo** output and an exploratory **other-product** simulation output, neither entered as recalled-lot measurement. The model source PDF hash was checked for the exploration.
- Under the specified assumptions, the prototype grid returned 117 mass-balanced search points and 32 nondominated multi-objective points. Top distinct illustrative recipes (Compritol/Carbopol 934/Avicel PH101, mg; all also include 500 mg API and fixed other ingredients): `84/42/39` score `0.7280`, `84/35/46` score `0.7235`, `91/35/39` score `0.7185`, at assumed hardness `8.5 kg/cm²`. These are *scenario-conditional rankings*, **not** a robust formulation for the recalled product.
- First scenario's simulated release medians at 2/8/24 h: `19.6/56.9/91.0%`; 5th–95th scenario spreads: `15.5–26.9 / 49.1–63.7 / 85.7–94.7%`. These are **not** calibrated confidence intervals. Full profiles for all candidates are in the results JSON.
- One author-reported F8 research endpoint was used as an unfitted sanity check: the paper claims `99.5%` at 24 h, while toy first-order/Weibull scenario medians were `89.38/89.47%`. Their ≈10-percentage-point discrepancy warns against claiming predictive fit.
- Final execution check: **29 software tests passed** with the optional model environment; base Python reported **29 tests run: 28 passed, one optional model test skipped**. Independent scenario audit returned `mechanically_consistent_NOT_experimentally_validated` with zero reported issues. Scientific A/B/C/D holdout benchmark reported `not_evaluated` for all arms (no suitable independent measured dataset). No laboratory experiment or authorized product modification was run.

## Missing evidence, uncertainty and approval gates

For recalled-lot root cause and genuine optimization: obtain an authorized, versioned product-specific dissolution SOP, approved criteria and stage/timepoint limits; individual-unit failing and passing lot profiles and run metadata; actual batch formulation, material grades/potency, API PSD and solid state; tablet dimensions, hardness/porosity and coating; granulation/compression/storage/deviation records. Then predefine approved candidate/process bounds, stability/manufacturability criteria, balanced baselines and independent lot-level holdout groups. Require human approval for experiments or product changes. Do not reinterpret literature recipe intervals as safety limits or rank probability as empirically calibrated performance.

## Issues faced during execution

See the [prioritized issues register](ISSUES.md) for evidence, impact, workaround, status and next action for each issue. Principal **open** blockers were missing controlled lot records and release data (G1–G2), inaccessible FDA interactive dissolution search (A1), unavailable authenticated scientific connector/delegation (A2), unrun OSP with missing qualified inputs (A3), ambiguous/unavailable literature timepoint profiles (D1), uncalibrated and direction-sensitive scenario assumptions (M1–M2), and no measured benchmark/BO training set (M3). **Resolved execution defects** were the multi-claim DailyMed product selector (I1), the pandas `set` column indexer in the OpenPKFlow demo (I2), and broken relative documentation links (I3). The isolated scratch-only model runtime and private version-pinned model functions remain a portability risk (R1). Resolved software issues do **not** resolve scientific blockers.

## Reproduction and source of truth

Run from the [working gym](scripts/formulation-optimization-gym/) root. The case investigation, simulation, mechanical audit and test commands are in its [README](scripts/formulation-optimization-gym/README.md) and [exploratory report](scripts/formulation-optimization-gym/EXPLORATORY_SIMULATIONS.md). This documentation reports those verified files; it neither duplicates regulated source documents nor manufactures inputs. Related links: [environment specification](ENVIRONMENT_SPEC.md), [status](STATUS.md), [research notes](../../research/formulation-optimisation-gym-environments/research-notes.md), [references](../../research/formulation-optimisation-gym-environments/references.md).
