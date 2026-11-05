# BolChem small-molecule task specifications

**Status: Specification.** Contribution type: scientific environment specification
and documentation. Owner: **Ankith116**. Related tracking issue:
[#46](https://github.com/boltzmannlabs/science-environments/issues/46).
Scientific and Agent Scientist maintainer review remains to be assigned.

BolChem defines two computational assignments for Agent Scientist:

| Task | Objective | Primary assessment |
| --- | --- | --- |
| [De novo design](tasks/de-novo.md) | Design molecules for p38α using the supplied 1A9U structure for final docking. | Mean derived Smina score across the complete ten-slot panel, with molecular properties and coverage. |
| [Constrained optimization](tasks/optimization.md) | Improve supplied starting molecules for DRD2 while preserving similarity. | Unique molecules satisfying all frozen activity, QED and similarity conditions; an explicit ADMET variant may add conditions. |

Each task permits the agent to choose its generation and search workflow within
common input, scoring and resource constraints. This contribution contains task
contracts, not a new connector, executable runtime, trained model or completed
scientific benchmark.

## What to give the execution agent

Supply **one task Markdown plus its prepared, authorized input/scorer bundle and
execution limits**. The two files under `tasks/` contain no literature names,
citations, links or prescribed reference search algorithm. Keep owner/evaluator
research, comparison outputs and archived candidate solutions outside that context.

The required model, structure preparation, working scoring interfaces, evaluator
and financial/compute limits are not packaged here. Resolve their declared
`NEEDS_INPUT`/`PROTOCOL_REQUIRED` conditions before a live run. Do not treat reading
the Markdown as installing or validating an environment.

## Contribution contents

- [Environment contract](ENVIRONMENT_SPEC.md).
- [Models and tool boundaries](MODELS_AND_TOOLS.md).
- [Status, blockers and dated work record](STATUS.md).
- [Owner-only reference index](REFERENCES.md).
- [Supporting research](../../research/bolchem/research-notes.md).
- [Documentation validation](results/specification-validation.md).

Issue #46 tracks the wider lead-optimization effort. This is a specification-only
increment; it does not close that issue's runtime/native-integration criteria.
The existing small-molecule environment work is not copied or replaced.

No empty runtime/config/test directories or fabricated scientific outputs are
included. Runtime jobs and large artifacts belong outside the versioned
task-definition directory.
