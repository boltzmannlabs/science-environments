# Reusable task-folder standard

Use one identifier `task-NN-descriptive-topic` under `tasks/`, `benchmark/` and `results/`. The repository's established directory is singular `benchmark/`; do not create a parallel `benchmarks/` tree. Each README must link to its matching task, benchmark and results sections using repository-relative links.

## tasks/<id>/README.md

Required sections: Overall objective; Problem statement and scope; exact target/input and source provenance; Execution approach; Expected outcomes and acceptance criteria; Actual outcomes with links. State whether physical experiments, model jobs, simulations or documentary reviews actually ran. Keep distinct chemical targets distinct.

## benchmark/<id>/

README.md: evaluation boundary, comparator eligibility and metric interpretation.

papers.md (optional papers.json): primary citations/URLs, exact substrate/product match vs analogy, reported experimental results, units, source example/table, verification/access caveats. Unverified fragments are not reference measurements.

achieved_metrics.json: observed model/software metrics separately from literature-reported and project-measured values. Missing numerical data is null with provenance; never replace it with an assumed zero. Prespecify a fair improvement criterion and starting-material/purity/scale boundaries before claiming superiority.

## results/<id>/

README.md: output inventory, actual achievements, observations, limitations and comparison summary.

task_record.json: schema version, shared task ID, reference/metric/artifact links, evidence and validation scope. Data filenames can vary by test case; preserve original route identifiers and avoid unnecessary duplicate formats.

Keep sanitized JSON/CSV or reports, achievements_and_comparison.md and gaps_and_improvement_plan.md as relevant. Add new authorized experimental records with explicit measured provenance and dated protocol; do not relabel predictions as experiments or overwrite historical records. Account-scoped raw exports, credentials, signed URLs and personal paths are not public task outputs.

## Validation

Run all existing environment tests, validate links and JSON/CSV consistency, compare route counts/IDs and source scope, check no private paths/secrets, and run git diff --check before commit. Store a validation receipt where appropriate. Preserve prior tasks and unrelated environments. Task 02's tests demonstrate this standard; Task 01's existing artifact names and tests remain intact.
