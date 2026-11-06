# Status — research prototype; not a validated synthesis

## Completed

- Retrieved 16 model-generated retrosynthesis routes and produced a sanitized all-route summary.
- Reconstructed explicit transformations despite disagreement with raw `num_steps` values.
- Reviewed top0 step-by-step with forward prediction, atom mapping, impurity prediction and condition recommendation (results summarized without backend handles).
- Compared reaction families with the public references catalogued in `../../research/retro_environment/references.md`.
- Built a route-wise DOCX and executable data consistency tests.
- Added explicit task specifications, a paper/source catalog, machine-readable achieved metrics, a full 16-route CSV and readable reaction-level literature comparison tables. These are regenerated using `scripts/build_comparisons.py` and checked by tests; they do not add new experimental evidence.

## Scientific conclusion

None of the 16 routes has an experimentally verified same-target preparation established by this review. The most useful result is identification of model/condition inconsistencies at the central coupling and protecting step. Numerical model step yields or their illustrative product do not demonstrate superior experimental performance.

## Blockers / remaining validation

- Identify a same-substrate literature or patent route by structure search; current search was text-based and incomplete.
- Confirm availability of actual precursors; not verified.
- Find chemically supported catalyst/base/solvent for the protected aryl-bromide coupling and quantify O/N selectivity.
- Test proposed chemistry and characterize product/intermediates/impurities experimentally; no reactions have been performed.
- Original platform model version, training provenance, sampling parameters and reproducibility seed were not returned.

**No live service capability is promised by this repository snapshot.**
