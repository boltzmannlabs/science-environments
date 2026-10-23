# Contribution Workflow

Contributions follow this traceable sequence:

`Issue → Branch → Deliverable → Validation → Pull Request → Review → Merge → Status update`

Use a focused branch such as `feat/<environment-name>`,
`docs/<topic>`, `fix/<issue>`, or `research/<topic>`. Every contribution must
identify its purpose, deliverables, acceptance criteria, validation evidence,
and limitations. Do not claim implementation or validation that has not been
performed, and do not commit credentials or restricted data.

Environment contributions belong under `environments/<environment-name>/` and
should include `README.md`, `ENVIRONMENT_SPEC.md`, `REFERENCES.md`, task
definitions, applicable tests, and small necessary result summaries. Keep
generated datasets out of the repository.

Before requesting review, run the applicable tests, record the evidence in the
PR, link the issue, and identify unresolved questions. Merge only after the
required review and checks pass. Update the environment maturity status
accurately (`Proposed`, `Specification`, `In Progress`, `Implemented`,
`Validated`, or `Deprecated`).
