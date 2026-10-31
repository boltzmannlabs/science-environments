# Published BglB reference — not new agent results

Source: Carlin DA, Hapig-Ward S, Chan BW et al. (2017), *PLOS ONE* 12(5): e0176255,
[article and citation](https://doi.org/10.1371/journal.pone.0176255).
The article is distributed under its stated Creative Commons Attribution terms.
The copied [s1.csv](s1.csv) is the unmodified published supporting table, not
software licensed by this repository or a newly performed experiment.

Download:
https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0176255.s001

SHA-256: `3d94ee8b73d4b67cc7c1f6def54b00a40bdacc6f1eaf1b53bcd01294fe58b619`.
Retrieved and checked on 31 October 2026. The actual CSV contains 128 mutant
records plus the `BglB` row; the article describes 129 mutants. No missing record
has been fabricated to reconcile that discrepancy.

## Reference values and units

The source BglB row reports kcat 880 min^-1, KM 5 mM, catalytic efficiency
174,000 M^-1 min^-1 and functional Tm 39.93 degrees C. Source errors are in the
table's corresponding error columns. Functional Tm is the paper's
activity-after-heat-challenge endpoint, not a universal unfolding Tm.

The table demonstrates why this task evaluates function and stability separately.
For example, W120F has functional Tm 41.68 degrees C but catalytic efficiency
29,334 M^-1 min^-1. An apparently favorable stability result is not enough.
E164A is the highest-stability example discussed in the paper, but violates this
task's protected-site rule and cannot be a valid design just because it is stable.

R240A's reported Tm is 39.90 versus reference 39.93 degrees C. The project's strict
point-estimate rule distinguishes those values; this 0.03-degree difference is
**not evidence of a meaningful loss**, given measurement uncertainty. A future
uncertainty-aware policy must be declared before comparison, not changed after
seeing which arm wins.

## What is not a reference result

No original-method top-five shortlist, new model prediction or Agent-Scientist
output is supplied by this table. Do not label an oracle sorted from all published
measurements as the authors' executed selection algorithm. Model correlations
reported in the paper are not automatically comparable to a new design shortlist.

Both agents may research public literature. This reference is intentionally public
and does not establish blinding or absence of training overlap. New proposed
variants not present in the table need appropriate new measurements.
