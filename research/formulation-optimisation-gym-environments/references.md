# References — formulation optimization gym

Sources listed here have different evidentiary scope; availability is not endorsement of a recalled-lot formulation or numeric QC specification. Source status and access outcomes are in [research notes](research-notes.md) and [tool matrix](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/docs/source_and_tool_matrix.md).

## Primary public records

1. U.S. FDA openFDA, [drug Enforcement Reports documentation](https://open.fda.gov/apis/drug/enforcement/); exact [Glenmark recall D-0092-2024](https://api.fda.gov/drug/enforcement.json?search=recall_number%3A%22D-0092-2024%22) (500 mg, lot 17230388); exact [Ajanta recall D-0010-2027](https://api.fda.gov/drug/enforcement.json?search=recall_number%3A%22D-0010-2027%22) (separate 1000 mg case). FDA reported reasons, not raw numeric dissolution measurements.
2. FDA [Glenmark label by SPL set ID](https://api.fda.gov/drug/label.json?search=openfda.spl_set_id%3A%220cf58732-c242-49b0-8e3f-248778b4458d%22); DailyMed documented [SPL v2 web services](https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm) and [Glenmark SPL XML](https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/0cf58732-c242-49b0-8e3f-248778b4458d.xml). Later current label, not a verified historical batch record.
3. FDA [Dissolution Methods Database](https://www.fda.gov/drugs/drug-approvals-and-databases/dissolution-methods-database). Landing page accessible; linked search blocked by anti-abuse response; no product-specific entry/SOP obtained. A recommended generic bioequivalence method would not automatically be the manufacturer's controlled recalled-lot test.

## External ranolazine research (not recalled lots)

4. Arigela et al., “Formulation and Evaluation of Ranolazine Extended Release Tablets” (2018), [DOI:10.5281/zenodo.1311884](https://doi.org/10.5281/zenodo.1311884). Matrix study; PDF numeric extraction had misaligned/blank Table 6 and possible nonmonotonic values, so no unverified time-course table was imported.
5. Saritha and Sanjana, “Formulation Development and Invitro Evaluation of Ranolazine Extended Release Tablets” (2018), [DOI:10.5281/zenodo.1170150](https://doi.org/10.5281/zenodo.1170150). Table 1 published research recipe amounts, Table 3 hardness, abstract F8 24 h endpoint. Profiles graphed; not a curated held-out training/evaluation set. Repository reported CC-BY-4.0 for both papers; license details are recorded in [literature catalog](../../environments/formulation-optimisation-gym-environments/scripts/formulation-optimization-gym/data/processed/public_literature_catalog.json).

## Literature benchmark disposition

The one usable numeric external comparison is Saritha and Sanjana's author-reported F8 value of 99.5% at 24 h (abstract; not replicate-level data). The assumption-only model's F8 medians are about 89.38–89.47% (absolute discrepancies about 10.0 percentage points), and both lie above the model's assumption-scenario 95th percentiles. Treat this strictly as a mismatch/sanity check, not validation or support for changing model parameters using a single endpoint. Arigela et al.'s Table 6 is excluded from numeric comparison because the extracted table has missing/misaligned entries and questionable monotonicity; source verification and details are recorded in the [benchmark report](../../environments/formulation-optimisation-gym-environments/benchmark/LITERATURE_BENCHMARK.md). Product holdout performance remains unevaluated.

## Open-source methods and capabilities

6. [OpenPKFlow PyPI package](https://pypi.org/project/openpkflow/) (installed/tested at v2.9.0): empirical first-order/Weibull functions used for assumption-only research-prototype scenario simulation and model-fitting smoke test on its bundled NON-ranolazine example. The pinned version's private equation functions require version review on upgrade.
7. [Open Systems Pharmacology documentation](https://docs.open-systems-pharmacology.org/): particle/PBPK modeling investigated but not run here. [SciPy](https://docs.scipy.org/doc/scipy/) and [NumPy](https://numpy.org/doc/) installed only in the isolated model environment. [BoTorch](https://botorch.org/) and [Optuna](https://optuna.org/) were considered but not run/trained for this case.
