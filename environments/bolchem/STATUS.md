# BolChem status

**Lifecycle: Specification.** Updated 5 November 2026.
Owner: Ankith116. Related issue: #46. Human reviewer: not assigned.

## Completed specification work

- Defined a single-target p38α/1A9U de novo task and a DRD2 optimization task.
- Recorded explicit evaluation, output, failure and resource contracts.
- Removed literature identity and reference-method instructions from task prompts.
- Incorporated earlier protocol, execution and independent-critic document reviews.
- Placed the deliverables in the repository's environment/research structure.
- Performed the document checks recorded in
  [specification-validation.md](results/specification-validation.md).

## Remaining execution dependencies

- Assemble and verify the p38α structural/preparation/scoring bundle.
- Assemble verified optimization starting structures and working predictor assets.
- Qualify scorer loading/features/positive-class mapping and exact metric behavior.
- Freeze actual run limits, auxiliary rewards, repeats and evaluation interfaces.
- Run engineering qualification and scientific comparisons as separately scoped work.

The required manifests are contracts, not supplied runnable configuration files.
No scientific jobs, training, molecular generation or docking was performed to
prepare this repository contribution. No runtime or specialist improvement is
claimed by documentation review.

## Contribution tracking

- Local branch: `Bolchem`, as requested; distinct from the existing `BoltChem` branch.
- Base: available `origin/main` snapshot `85ebef7517534010df31f4b8e12e1676e3455e41`.
- A newer remote main was observed, but fetching was denied by automatic approval
  review under the user's earlier fetch/pull restriction. No fetch/pull succeeded.
  A future review branch must start from an authorized current main snapshot.
- Issue #46 is open and provides parent tracking for the wider optimization effort;
  this documentation increment does not complete or close its runtime requirements.
- The branch was first published without the prepared content. On 5 November
  the owner then authorized committing and pushing this specification increment
  using verified account `Ankith116`. Consult branch history for publication state.
  No PR, maintainer approval, merge or issue closure is claimed.
- The owner then requested a working snapshot containing only BolChem material.
  Inherited environment/research files are removed from this branch snapshot by
  an ordinary commit; their history and the main branch are preserved. Prepare
  a fresh branch from main and transfer only BolChem folders for a later PR.

## Dated work record

| Date | Work | Evidence / next step |
| --- | --- | --- |
| 2026-11-05 | Created an isolated branch, organized the reviewed task specifications and completed document checks; the owner subsequently authorized content publication. | Input/scorer bundles, scientific execution and maintainer review remain pending. |
| 2026-11-05 | Organized unchanged tasks into `small-molecule-de-novo-design/tasks/` and `small-molecule-optimization/tasks/`, and prepared the owner-requested BolChem-only working snapshot. | Publication authorized; future PR must transfer only our folders to a fresh branch from main. |
