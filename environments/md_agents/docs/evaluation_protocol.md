# Evaluation protocol

Run the fixed packet set with identical inputs, limits, and evaluator rules.
Report adapter execution separately from scientific qualification.

For recovery tasks, preserve the failing input, identify the first failure,
apply at most the permitted correction, and independently verify the rerun.
For sampling and free-energy tasks, require trajectory statistics, replica
agreement, uncertainty, and reference compatibility. A successful exit code
alone is never sufficient for `PASS`.
