# Hit identification

Task materials for prioritising small-molecule candidates from a supplied library.
This contribution publishes the selected D2R task benchmark, original agent outputs
and execution prompt from the `Boltchem` branch.

| Folder | Included material |
| --- | --- |
| `benchmark/` | [D2R peripheral candidate prioritisation](benchmark/task_001_d2r_peripheral_candidate_prioritisation.md): published comparison, evaluation criteria and review of the agent results. |
| `results/` | [Original agent report](results/task_001_d2r_peripheral_candidate_prioritisation/report.md), assessment, ranked candidates and supporting tables in the task-specific folder. |
| `tasks/` | [Agent execution prompt](tasks/task_001_d2r_peripheral_candidate_prioritisation_prompt.md). |

Tracking issue: [#123](https://github.com/boltzmannlabs/science-environments/issues/123).

## Source and scope

Source snapshot: [`Boltchem` at `87026acae61e`](https://github.com/boltzmannlabs/science-environments/tree/87026acae61e6304d140476468c68aae73fb1ae6/environments/hit-identification).
The eight result files and the task prompt are copied unchanged. The benchmark's
two links to supporting documents outside this selection point to that pinned
source; its scientific content is unchanged.

The [full task definition](https://github.com/boltzmannlabs/science-environments/blob/87026acae61e6304d140476468c68aae73fb1ae6/environments/hit-identification/tasks/task_001_d2r_peripheral_candidate_prioritisation.md),
[input bundle](https://github.com/boltzmannlabs/science-environments/tree/87026acae61e6304d140476468c68aae73fb1ae6/environments/hit-identification/inputs)
and [full evaluation](https://github.com/boltzmannlabs/science-environments/blob/87026acae61e6304d140476468c68aae73fb1ae6/environments/hit-identification/FINAL_REPORT.md) remain in the source snapshot.
This selected publication does not include the complete executable environment.
The prompt and original report retain historical workspace paths, including
`environments/virtual-screening/`, `task.md` and `results/run_rsi/`; those paths
are not supplied by this subset.

## Reading the results

Read the benchmark alongside the original agent submission. The benchmark records
problems with the agent's brain-access interpretation and score units; preserving
the original report does not endorse those interpretations. No new scientific
execution, reassessment or experimental validation is performed by this transfer.
Give execution agents the selected task and its inputs; keep benchmark outcomes
and earlier results for evaluation.
