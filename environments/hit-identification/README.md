# Hit identification

Tasks for prioritising small-molecule candidates from supplied libraries. The execution agent receives a task and its scientific inputs and determines a suitable workflow.

| Category | Purpose | D2R task |
| --- | --- | --- |
| `tasks/` | Scientific objective, inputs, constraints and expected outputs | [Task](tasks/task_001_d2r_peripheral_candidate_prioritisation.md) |
| `benchmark/` | Paper source metadata and the step-by-step comparison of paper and agent results | [Comparison](benchmark/task_001_d2r_peripheral_candidate_prioritisation_comparison.md) |
| `results/` | Experiment outputs, benchmark results, execution records and evaluation reports | [Workflow, results and paper comparison](results/task_001_d2r_peripheral_candidate_prioritisation/evaluation_report.md) |

The original task and input bundle are unchanged. Give future execution agents only the selected task and `inputs/`; benchmark reference outcomes and previous results are evaluator material.

The agent's original detailed report, ranked candidates and assessment are preserved under the task's results directory. Independent comparison findings are kept in `results/` and do not overwrite the submission.

Validate with `python scripts/validate_environment.py`, `python scripts/validate_d2r_review.py` and `python -m pytest tests -q`. Offline audit dependencies are listed in `results/task_001_d2r_peripheral_candidate_prioritisation/benchmark_results/requirements-review.txt`. None of these checks submits platform jobs.
