# Environment specification

## Scientific contract

Task 01 is clarithromycin 500 mg IR under an illustrative 800 mg dry coated tablet basis, not ranolazine ER and not the earlier 750 mg exploratory screen. API dose is fixed, not an optimization variable. Exactly eight excipients and their fixed benchmark bounds are enforced. Core: API, MCC, crospovidone, PVP K30, colloidal silica, magnesium stearate. Coat: hypromellose, titanium dioxide and PEG 4000. API mass assumes 100% as-is potency; real charging requires a defined potency/water convention and rebalancing.

PVP wet granulation is a provisional process stratum, not an executed or validated process. Grades, API form/PSD, suppliers, process windows, reference product, accepted dissolution method, stability conditions and regulatory criteria remain missing or unverified. A removable process solvent is not a ninth retained excipient.

## State and provenance

- Immutable numeric source snapshots and user-supplied specification: `benchmark/clarithromycin-500mg-ir-formulation-dissolution/`.
- Append-only conceptual result versions: `results/clarithromycin-500mg-ir-formulation-dissolution/v1/` and `v2/`; fresh local runs go to `.runs/`.
- Model outputs, literature observations and planned experiments must remain distinguishable.
- Candidate endpoints remain null / NOT_PREDICTED / UNKNOWN; a composition pass never implies a physical-quality pass.

## Task 01 executable behavior

`src/formulation_environment/task01.py::run_task01(input_dir, output_dir)` deduplicates the repeated literature reference, evaluates eleven fixed model/baseline configurations on fifteen published profiles, and exports all fits, errors and diagnostics. In-sample, leave-one-timepoint-out (LOTO) and forward-30 results are distinct. Forward30 is exactly the 30-minute LOTO fold, not independent evidence. Repeated means from the same curve are not independent formulation/batch holdouts.

The function also constructs four valid matched corners, completes a nine-design CP/PVP factorial, calculates design-matrix rank and creates explicitly blank prospective measurement templates. A method draft and readiness gates are not regulatory specifications or experimental results.

## Hard gates

Fixed active dose; exact ingredient set; finite/nonnegative masses; 800 mg total; 100% ±0.1% sum; unchanged ingredient bounds; core/coat conservation; uniqueness under the declared rule (reject when every non-API mass difference is <1 mg). Any failed gate rejects a design, irrespective of score. Constraint functions live in `src/formulation_environment/constraints.py` and are independently tested.

## Honest abstention

No validated target-domain recipe predictor, calibrated candidate interval, efficacy ranking, compatibility score, degradation probability, manufacturing pass or shelf life is available. Published R1 recipes/materials/coat differ. Neither literature curve fitting nor an information determinant establishes product superiority. PTCalc mechanism labels are rejected when the required early-release observations are absent.

## Validation and completion

Software success means reproducible computations and valid contracts, not laboratory success. Tests recalculate exported metrics, verify split disjointness, null endpoints, fixed bounds, unique recipes, blank planned observations and source hashes. A new runner execution must match curated numerical outputs. Human scientific review, independent methods/data and physical confirmation remain pending.