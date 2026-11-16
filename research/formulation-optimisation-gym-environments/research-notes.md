# Research notes — ranolazine ER dissolution investigation

## Problem, case and limits

Reported ranolazine extended-release dissolution failure prompted an evidence-first investigation. The target case is Glenmark ranolazine 500 mg, FDA recall `D-0092-2024`, lot `17230388`, NDC `68462-319-60`. The distinct Ajanta 1000 mg recall `D-0010-2027` is tracked separately. FDA's reported recall reason does not include time-point dissolution measurements or establish a cause. Public current labels give qualitative ingredients and dosage-form identity; the currently served Glenmark label became effective after the recall, so historical batch formulation cannot be recovered from it. [Primary-source links](references.md#primary-public-records).

## Source evidence and research curation

- FDA openFDA enforcement and label records were saved as immutable local snapshots in the [gym raw-source directory](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/data/raw/), matched by exact recall ID, SPL set ID and package NDC. Current label cross-check used documented DailyMed SPL v2 XML. The provenance-linked Glenmark [episode](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/data/processed/D-0092-2024.dailymed.episode.json) contains no measured dissolution result.
- FDA dissolution database's landing page was accessible but its interactive search returned an anti-abuse response. Neither the recalled manufacturer's controlled QC SOP nor product-specific acceptance limits were verified. PubChem documentation and PubMed search were not reliably accessible in this session; no result is asserted from them.
- Two external ranolazine extended-release studies were found via Zenodo and recorded in [literature catalog](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/data/processed/public_literature_catalog.json). One article's extracted Table 6 had ambiguous alignment/possible nonmonotonic values; it was not used as measured model input. Another article reports F1–F8 500 mg research recipes with total nominal 695 mg and hardness values; its time-course curves were graphed and not curated into time-point measurements. The paper reports F8 99.5% at 24 h in its abstract; that value is a literature claim about another study, not a Glenmark lot result.

## Hypotheses, not findings

Release-polymer amount/grade, API particle size/solid state, matrix porosity and compression, granulation/coating variability, moisture/storage exposure and dissolution assay method differences could all matter to release. No recalled-lot comparative records established direction or magnitude of any effect. Public research Compritol/Carbopol recipes differ from the currently served Glenmark ingredient listing; they cannot be treated as recalled-batch prototypes.

## Exploratory modeling decision

After explicit user authorization to explore unverified inputs, use external research recipes only as a hypothetical study-specific mass-balanced composition window; keep all kinetic parameters, effect signs, dose potency, release goals and hardness-grid choices marked `assumed`. Execute actual first-order/Weibull open-source release functions, but **do not fit** generated curves as if observed data. Propagate both possible signs for uncertain ingredient effects and expose conditional scenario quantiles, scalar scores and Pareto candidates as unvalidated outputs. A single paper F8 endpoint does not supply a profile/holdout. See [full environment report](../../environments/formulation-optimisation-gym-environments/ENVIRONMENT_REPORT.md), [scenario config](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/configs/exploratory_ranolazine_500.json), [outputs](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/data/processed/ranolazine_research_scenario_results.json), and [source references](references.md).

## Evidence to acquire for scientifically valid optimization

Authorized original lot-level batch formula/material grades/potency/PSD/solid state; versioned product-specific dissolution SOP with acceptance limits; individual-unit failing and passing profiles plus run metadata; compression/porosity/coating/stability and process deviations. Freeze controlled constraints and independent measured holdout splits before estimating effect signs or optimizing. Expert human approval is required before physical experiments or formulation changes.
