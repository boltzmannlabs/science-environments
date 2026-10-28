# SRG-05 fixed-search implementation and comparison

Status: implemented and validated in the declared development pilot; no accepted-route
improvement demonstrated. Owner: search and benchmark maintainers.
The legacy `planning.run_fixed_workflow` remains unchanged for regression and
comparison. No scientific model or LLM is trained in this step.

## Research and design

[Retro*](https://proceedings.mlr.press/v119/chen20k.html) motivates best-first
AND/OR search, but its learned value function is not implemented or claimed here.
Our new fixed policy uses an explicit deterministic heuristic and the same
LocalRetro expansion backend as the legacy breadth-first policy. It is not an
implementation or reproduction of Retro*.

[AiZynthFinder](https://molecularai.github.io/aizynthfinder/) uses a search policy
and stock collection. Its existing local baseline uses a different expansion
model, so its results remain a separate reference rather than evidence of a
controller-only improvement. [PaRoutes](https://github.com/MolecularAI/PaRoutes)
supplies the curated source tasks; recovering a reference and satisfying stock
constraints are distinct from experimentally establishing feasibility.

## Implementation sequence and acceptance tests

1. Preserve legacy search and prior acceptance receipts. Record the comparison
   selection and budgets before obtaining results.
2. Write failing tests for convergent shared intermediates, deeper routes,
   unresolved branches, actual cycles, repeated reactant obligations, forbidden
   materials and unknown/insufficient amounts.
3. Implement bounded best-first expansion, canonical state/route deduplication,
   safe intermediate reuse and explicit pruning counters. A stored proposal
   counts toward the successful-candidate quota only after passing the same
   deterministic gates as environment submission.
4. Bind cached successful predictions to canonical requests and host-declared
   model/configuration/stock/evidence versions. Do not cache failed calls as
   negative chemistry. Keep external precomputation costs explicit.
5. Expose policy selection in the local CLI. Reserve submission capacity and
   test budget exhaustion, cancellation and a complete CLI flow.
6. Run the frozen development comparison, retain failures and losses, review
   changes and run the complete suite with at least 80% coverage. Select a
   baseline from measured results, with no automatic promotion of the new policy.

## Development comparison declared before results

The pilot selects four development target groups by ascending SHA-256 of
canonical target SMILES and includes both inventory variants: eight tasks,
four independent target groups. Only public task inputs are used. Neither final
labels nor reference routes are expansion seeds. The exact task IDs and input,
code and model asset hashes are written in the run recipe before inference.

Each arm receives 6 expansions, 80 actions, 120 seconds, a top-5 submission cap,
10 predictions per expansion and at most 10,000 search states. These are pilot
budgets, not a revision of the final benchmark protocol. LocalRetro runs on CPU
with one inference thread. Arms alternate execution order across tasks.

Two resource conditions are reported separately:

- **Cold:** each arm starts with an independent empty search cache and invokes
  the same existing LocalRetro adapter. Failed and timed-out calls are retained.
- **Shared precomputed:** the successful union of cold requests is frozen before
  replay. Both arms use the identical table with no model fallback. Logical
  expansion calls still consume the same allowance. Missing table entries are
  explicit unavailable responses. Precomputation calls and time are reported
  separately; faster replay is not an end-to-end inference speedup.

Results must report deterministic accepted submissions, constraint violations,
states, expansions, duplicate work, cache behavior, elapsed time and submission
failures. Predictions remain unreviewed. An eight-task pilot cannot establish
general route feasibility, model superiority or a statistically reliable gain.

The predeclared default-selection rule is conservative: keep the legacy default
unless the new policy has no rejected submissions, reaches at least as many
tasks with accepted routes in both resource conditions, and strictly improves
that count in at least one condition. Report per-target losses even if the
aggregate improves. A tie retains both explicit policies and the legacy default;
timing differences alone in this small pilot do not justify promotion. This
development choice never establishes experimental feasibility or satisfies the
separate mandatory learned-model improvement gate.

## New policy and local interface

The priority is ascending `(number of steps + number of unresolved unique
precursors, unresolved precursors, steps, canonical reaction signature)`.
It is a structural heuristic, not an admissible cost bound, calibrated success
probability or guarantee of an optimal route. Proposal model scores remain
metadata. Full reactant multiplicity stays on the stored reaction steps.

The controller checks directed dependency cycles rather than rejecting every
link to an existing intermediate. It deduplicates equivalent partial reaction
graphs, bounds the visited states and frontier, and counts pruning and cache
events. The local CLI exposes the new policy explicitly:

```sh
.venv/bin/python -m synthesis_route_gym plan \
  --task path/to/task.json --output path/to/result.json \
  --search-policy best_first --expansion-top-k 10 \
  --max-frontier-states 10000 --chemistry-python "$REBOLT_PYTHON"
```

`--search-policy breadth_first` selects the preserved comparator. The default
remains breadth-first following the development decision below. Neither policy implies
independently supported chemistry.

The best-first controller reserves one action for submission. Its wall-time
reserve is an admission guard: an already running backend can still overrun
the remaining episode deadline. Such episodes are recorded as truncated; the
host never invents a submission. Quantity-complete synthesis cannot be inferred
from identity-only expansion predictions. Requested amounts without sufficient
quantitative information therefore prevent deterministic acceptance.

Cache snapshots use `srg-expansion-cache-v1`. They retain only successful,
normalized predicted outputs and bind each query to the capability fingerprint,
canonical molecule and expansion cap. Host-declared identities must honestly
cover model weights, templates and configuration; the cache itself does not
authenticate those external assets. A manually supplied cache requires explicit
`cache_mode='shared_precomputed'` and carries separate precomputation accounting.
That host optimization interface may invoke the configured backend on a cache
miss, charging the episode normally; it is not an additional agent tool. The matched
comparison instead puts a common frozen table behind both arms' expansion
action with no inference fallback, so both pay the same logical expansion allowance.

## Reproduction and validation

Run the actual local pilot into a new output directory (existing runs are never
overwritten):

```sh
.venv/bin/python scripts/run_search_comparison.py \
  --output artifacts/steps/srg-05/development-reproduction
```

The runner uses the SRG-02 public-manifest anchor, existing LocalRetro assets and
the compatible chemistry interpreter recorded in the recipe. It never calls an
LLM or loads private labels. Each episode and its ordered decision are saved
before any possible later evaluation. Source, assets and public inputs are
rechecked after execution; drift invalidates the comparison. Dependency version
inventories are not complete package hashes or a guarantee of bitwise reproduction.

Late model calls are counted when invoked and allowed to settle before the next
arm starts. Cleanup time is separate from episode time; results not observed
within the episode are excluded from the shared table. Failure to settle stops
the comparison and retains the current episode, decision and call records.

Full software validation on the frozen implementation: **767 tests passed,
93.04% branch-inclusive package coverage**, no failures or skips. One existing
Starlette/httpx deprecation warning remains. Tests include a CLI subprocess flow,
actual environment integration and synthetic search/benchmark fixtures; these
test results do not themselves establish model accuracy.

Observed setup limitation: the public loader validates the entire bundle for
each selected task. This pilot performs approximately 1.9 million SMILES
canonicalizations before writing its recipe, including repeated checks of stock,
exclusions and public condition candidates. This common setup cost is outside
both arms' episode timers and is not a search-policy speedup. Batch validation
against one frozen public snapshot is a measured optimization candidate for
SRG-14; the current run retains the existing audited loader unchanged.

## Recorded development result

The [frozen recipe](../artifacts/steps/srg-05/development-v1/plan.json),
[comparison report](../artifacts/steps/srg-05/development-v1/summary.json) and
[selection decision](../artifacts/steps/srg-05/selection.json) preserve the complete
pilot, including its negative finding. All 32 episodes and ordered decisions
were saved and their checksums verified. Source files, model assets and the
public bundle passed the final integrity checks.

| Resource condition | Policy | Tasks with accepted routes | Admitted expansions | States visited | Summed policy elapsed seconds |
|---|---|---:|---:|---:|---:|
| Cold LocalRetro | Legacy breadth-first | 0/8 | 48 | 60 | 432.05 |
| Cold LocalRetro | New best-first | 0/8 | 48 | 152 | 426.87 |
| Shared precomputed | Legacy breadth-first | 0/8 | 48 | 60 | 5.09 |
| Shared precomputed | New best-first | 0/8 | 48 | 152 | 3.96 |

The legacy policy also made eight budget-rejected expansion attempts per mode;
these used actions but did not invoke the backend. The new policy checked the
remaining expansion allowance before dispatch. All such attempts remain in the
episode logs rather than being counted as model inferences.

The 96 cold backend calls all succeeded, taking 848.29 seconds of summed backend
elapsed time. Their union contained 52 successful distinct context-bound query
keys with no conflicts. Shared replay made no additional model calls and had
no missing entries. All episodes submitted empty lists without truncation.
An earlier, separate availability check made one additional LocalRetro call
(17.57 seconds), recorded in [preflight.json](../artifacts/steps/srg-05/preflight.json).
No LLM calls or model training occurred.

**Decision: retain breadth-first as the default.** The predeclared promotion
rule did not pass because accepted-route counts tied at zero in both conditions.
Best-first remains available as an explicit policy and its correctness fixes
are covered by synthetic tests. It examined more states without extra expansion
calls, but that did not yield an accepted route here. Timing differences are
descriptive; they do not establish a reliable speedup. Preparation and environment
construction are outside the policy timer, and precomputation cost is not free.

There are only four independent target groups. Zero submitted routes gives no
empirical inventory-compliance or chemical-feasibility rate; neither is reported
as 100%. No reference matching or source-based chemistry review was performed.
The next scientific-model step must use eligible data and its own decision metric;
this pilot does not satisfy the mandatory model-improvement deliverable.
