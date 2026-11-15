# Task - 01 — Clarithromycin 500 mg IR formulation and dissolution investigation

## Overall task

Build an auditable formulation benchmark and informative experimental plan for a 500 mg immediate-release film-coated clarithromycin tablet using exactly eight named excipients. Investigate dissolution, compatibility/stability and manufacture without inventing missing response data.

## Objective

Generate and constraint-check at least ten distinct compositions under a fixed **800 mg finished dry tablet** assumption; propose varied designs for testing; use literature/dissolution tools within their domain; quantify what computational changes improve and what worsens. See [objective and acceptance](OBJECTIVE.md).

## Inputs and provenance

[User-supplied specification](../../benchmark/Task%20-%2001/specification.md), [frozen contract](../../config/task01_contract.json), twelve supplied plus twelve generated recipe inputs, and published R1 numeric mean/SD profiles. All eight excipients are preserved; HPMC/TiO2/PEG4000 are coat solids. This is not the earlier 750 mg screen or ranolazine ER.

## Work performed

1. Source review and dose/composition/core-coat validation.
2. PubChem/Europe PMC/RDKit context and Optuna restricted information design in original v1.
3. Actual PTCalc v1 analysis; source-calculation checks and mechanism eligibility review.
4. v2 deduplication, multiple model baselines, free/capped/fixed plateau comparisons, held-out-timepoint diagnostics and retention of worse results.
5. Complete nine-composition CP/PVP factorial with four additional corners; draft early sampling and pilot plan.
6. Portable offline runner, independent tests and versioned report/data publication.

## Actual outcome

28 valid designs in v2; no efficacy ranking. Weibull capped-plateau forward30 RMSE decreased 39.88% versus our free-Weibull baseline, but its overall LOTO RMSE worsened 4.82%. This is not an improvement over the literature tablet. No new lab samples, candidate release/stability observations or calibrated candidate intervals exist.

## Execute

From the environment root:

```bash
python scripts/run_task.py --task 'Task - 01' --out .runs/task01-new-run
python -m unittest discover -s tests -v
python scripts/validate_environment.py
```

## Linked sections

[Matching benchmark](../../benchmark/Task%20-%2001/README.md) · [Matching results](../../results/Task%20-%2001/README.md) · [Research](../../../../research/clarithromycin-ir-formulation/research-notes.md).
