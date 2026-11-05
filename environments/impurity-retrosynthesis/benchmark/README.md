# Benchmark: literature versus generated routes

Protocol version 1 (documentary screening; NOT a predictive accuracy benchmark).

- Retain source route IDs, target separately and original model fields without interpreting `path_cost` as INR or `reaction_yield` as observed yield.
- Compare target connectivity and actual bond/precursor/product of each step, not route labels alone, to primary exact-substrate reports, analogous transformations and unsupported model-only steps.
- Score no route with an incorrect target structure, unreviewed safety stop, or unresolved chemistry. No weighted aggregate score was computed in the historical run.
- A direct *product* patent may lack precedent for every *step in a different model path*. Assign citations at step granularity with substrate similarity and source excerpt.
- Establish new prospective metrics only after non-leaked target-reference datasets exist: exact-product recovery, top-k *fully feasible* route recovery, per-step exact/analogue citation precision, cost/isolated-yield error on held-out real batches, analyst time and blind chemistry-review agreement. Do not substitute model rank or counts of paths for these metrics.

Historic benchmark: A patent CN108794319B reports Suzuki + ester hydrolysis route; WO2003043625A1 names (R,S) target via organotin coupling + hydrogenation + ester cleavage. Generated A top5 shares a Suzuki bond family with a different protected substrate; A top3 resembles a coupling/hydrogenation/hydrolysis *topology* but not the original Stille substrate. The exact model route is not validated. M top4 shares a cyanohydrin feedstock class with Aramini et al., but their deoxygenated product class does not validate retention of target alpha-OH. No osimertinib tool output exists; WO2013014448A1 Example 59 is a named-product literature comparator only. The two unverified bibliographic fragments must not be promoted to exact precedents. Full reference provenance is in `../../../research/impurity-retrosynthesis/references.md`.

Historical result aggregates and per-route flags are in `../results/`. These are not a randomized matched performance comparison; **no claim of outperforming literature in yield, purity, cost or scale is supported**. The observed advantage was breadth of displayed alternatives and a reproducible input audit.
