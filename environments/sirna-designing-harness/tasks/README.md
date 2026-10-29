# Agent task contracts

These JSON files define scientific tasks for Agent Scientist. They do not automatically submit jobs. The repository-executable technical report consumes recorded outputs from configured scientific tools.

| Task | Scope | Execution boundary |
|---|---|---|
| [technical-validation.json](technical-validation.json) | Supplied pairs, recorded Bench properties/gates, references and earlier-job evidence | Executable portable `technical-report`; no model dispatch |
| [kras-shared-review.json](kras-shared-review.json) | Four-reference human KRAS design objective | Approved existing generators/assessment tools; explicit execution authorization |
| [kras-mutation-blocked.json](kras-mutation-blocked.json) | Comparative intake without an exact mutation | Shared work can proceed; no hypothetical mutant construction |
| [audit.json](audit.json) | Completed artifacts in a new audit directory | No generation/inference/folding/screening repeats unless separately authorized |
| [sensitivity.json](sensitivity.json) | Compatible preserved scores | No imputation, new weights or biological claims from changed ranks |
| [benchmark.json](benchmark.json) | Measured-data and exposure audit | Independent test eligibility must be established before inference |
| [literature-comparison.json](literature-comparison.json) | Original-source versus computational prioritization | Preserve endpoint/context distinctions and actual source evidence |

## Technical validation

The [output contracts](../config/output_contracts.json) define `PASSED_DECLARED_TECHNICAL_GATES` and the properties/flags that accompany it. The command verifies mandatory categories rather than relabelling every native Boolean. Missing required technical evidence blocks; explicit failure wins over missing. Experimental/translational raw gate rows are preserved as a separate scope.

The included recorded task can be exercised locally:

```bash
python3 -B scripts/run.py technical-report \
  --bundle results/case_studies/KRAS_14_technical_validation/bundle.json \
  --out /absolute/path/to/NEW-report-directory
```

A task definition is not a new target's expected numerical answer. Preserve every supplied sequence and source literal. Scientific generation/evaluation remains agent-orchestrated using separately configured tools and reviewed contracts.

## Contribution drafts

[ISSUE_DRAFT.md](ISSUE_DRAFT.md) and [PR_DRAFT.md](PR_DRAFT.md) are local review text. Current read-only GitHub lookup succeeded and found no siRNA-titled issue; no remote issue/PR, assignee, reviewer approval or merge is claimed. Obtain direction to perform those remote contribution actions.
