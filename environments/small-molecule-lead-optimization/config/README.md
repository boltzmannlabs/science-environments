# Configuration and record contracts

**Version 0.1: implemented.** The standalone plugin requires Python 3.10+ and the existing Agent-Scientist plugin interface. Its campaign core uses the Python standard library. Installation and tested host revision are documented in [installation](../scripts/README.md) and [validation evidence](../results/validation.md).

## Runtime and scientific configuration

The only plugin setting is `plugins.entries.leadopt_env.settings.db_path`: an absolute path to a local SQLite database outside the installed package. Choose campaign storage separately from task inputs. Service credentials and profile/access setup remain owned by Agent-Scientist.

Scientific choices belong in the task: starting leads, context, objectives, constraints, permitted jobs, budgets and evaluation. Missing scientific information produces warnings and unresolved assessments. Malformed JSON, conflicting immutable IDs and incorrect record associations produce data-integrity errors; these do not impose scientific execution blocks.

## Versioned contracts

The runtime source of truth is [contracts.py](../src/leadopt_env/contracts.py). JSON Schema exports in this directory are checked against it by the test suite. The agent can call `leadopt_campaign(operation="describe")` without configuring storage, or a maintainer can use `leadopt-env schema task`.

| Record | Contract |
| --- | --- |
| Task snapshot | [task.schema.json](task.schema.json) |
| Candidate/form identity and lineage | [candidate.schema.json](candidate.schema.json) |
| Endpoint observation | [observation.schema.json](observation.schema.json) |
| Planned-action advice | [check.schema.json](check.schema.json) |
| Execution event and attempt identity | [action.schema.json](action.schema.json) |
| Resource increment | [usage.schema.json](usage.schema.json) |
| Investigation decision | [decision.schema.json](decision.schema.json) |
| Final submission | [freeze.schema.json](freeze.schema.json) |

Records use immutable IDs. Identical retries return the existing record; changed content under an existing ID is rejected. The task is immutable after creation. Explicitly create a new campaign/version for revised task rules. Repeating a check ID returns the historical advice; use a new ID for a fresh check.

Candidate representations are opaque strings retained verbatim, with explicit form IDs. No canonicalization, salt equivalence, stereochemistry resolution or graph constraints are implemented. Observation comparisons require matching endpoint, unit, evidence kind, method, method version and context, plus association to the recorded form. Missing signatures, censored values and multiple matching observations remain unresolved. The environment does not choose replicate aggregation or accept the most favorable observation automatically.

## Resource accounting

Each usage record is an **increment**, with unit, scope, source and category: `requested`, `observed`, `estimated` or `unknown`. Unknown requires `amount: null`; other categories require a finite nonnegative number. Reusing an event ID prevents double counting that event. Supplying the same cumulative counter as multiple increments is incorrect.

Task `budgets` map unit names to allowances. Version 0.1 compares them only with `observed` increments whose scope is exactly `campaign`. Other scopes/categories are reported separately. No remote internal scoring count is inferred from a job or molecule count. No numerical budget is supplied as a general default.

Reaching an allowance warns; exceeding it is a recorded violation. Unknown/missing budget evidence or pending attempts prevents a final resource-eligibility pass. Requested resources attached to pending/unknown attempts remain unresolved commitments, separate from observed consumption. The environment does not reserve resources or enforce dispatch limits.

Recording is explicit and agent supplied. Reports always disclose incomplete observation coverage and unauthenticated provenance. Equal declared budgets do not establish equal total work.

## Scientific tools and final evaluation

Use the current installed Boltzmann catalogue and complete generated module for scientific request/file formats. The [tool mapping](tool-mapping.md) records inspected capabilities; it is not a duplicate request schema or live worker certification.

Final objective/constraint signatures and source version belong in the task's `evaluation` object before the run. The offline evaluator reads a frozen submission, a separately retained digest receipt and evaluator-owned reference records. Reference identities and task/source versions must match. Evaluator references are never exposed through the plugin tool.

Checksums do not isolate hidden answers. For an independent benchmark, the host/operator must keep reference files and evaluator access outside the tested agent's readable environment. The public synthetic example demonstrates software behavior only. The [comparison protocol](../tests/COMPARISON_PROTOCOL.md) describes the scientific requirements still pending.
