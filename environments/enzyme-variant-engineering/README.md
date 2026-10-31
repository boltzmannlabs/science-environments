# Enzyme Variant Optimization

**Status: task and native-specialist implementation; scientific comparison not yet run.**

This environment describes how to improve an existing enzyme, supplies real case
studies and evaluates their outputs. Agent-Scientist does the research, chooses
methods and runs the tools. A native enzyme specialist can review unsuccessful
results and suggest a better next investigation.

There is no new execution engine, plugin, tool catalogue, input validator,
database, scheduler, model client or mandatory scientific tool sequence here.
The original Agent-Scientist source is not modified.
If an older enzyme workflow/research plugin remains installed locally, this
environment does not use its wrappers or require it to be enabled. Existing
profile installations are not silently removed by changing a GitHub folder.

## Layout

```text
enzyme-variant-engineering/
├── README.md                  Overview, layout and how to use this environment
├── ENVIRONMENT_SPEC.md        Reusable scientific process and evidence rules
├── STATUS.md                  Completed work and remaining scientific runs
├── tasks/
│   ├── README.md              Case-study index
│   └── bglb-activity-stability/
│       ├── TASK.md            Actual assignment, prompts and expected outputs
│       └── parent.fasta       Paper-numbered reference sequence
├── specialist/
│   ├── README.md              Native import/review/run instructions
│   └── enzyme-variant-specialist.json
├── tests/
│   ├── README.md
│   └── bglb-activity-stability/
│       ├── ACCEPTANCE.md      Scientific checks, metrics and their limitations
│       ├── evaluate.py        Small local result evaluator; never runs tools
│       ├── test_evaluate.py   Positive and negative evaluator checks
│       └── check_native.py    Optional compatibility check against native SCI
└── results/
    └── bglb-activity-stability/
        ├── reference/         Published source data and interpretation
        ├── agent-alone/       Actual base-agent outputs, once executed
        ├── agent-with-specialist/  Actual assisted outputs, once executed
        └── comparison.md      What can and cannot currently be compared
```

Supporting science and source limitations are in the matching
[research notes](../../research/enzyme-variant-engineering/research-notes.md) and
[references](../../research/enzyme-variant-engineering/references.md).

## Start a case

1. Use an existing, authorized Agent-Scientist installation. Its maintained
   Boltzmann instructions and enzyme input validations remain authoritative.
2. Read [the environment process](ENVIRONMENT_SPEC.md), then the case
   [TASK.md](tasks/bglb-activity-stability/TASK.md).
3. Open a fresh ordinary SCI chat from a working copy of this repository. Paste
   the case's **base-agent prompt**. No profile or environment plugin is required.
4. Save its actual output bundle and native session/job references in that arm's
   results directory. Do not copy credentials, signed URLs or private transcripts
   into GitHub.
5. If useful, import and review the [native specialist](specialist/README.md).
   Use the assisted prompt for a clearly labelled continuation or a separate
   matched run. Record which comparison was actually performed.
6. Evaluate the saved outputs using the case's acceptance instructions.

The first case is BglB hydrolysis of pNPG, based on a published activity/stability
study. The task uses process requirements rather than named molecular tools.
An agent may choose an applicable available method; the method and evidence must
be reported. A documented capability is not a guarantee of backend availability.

## Local checks

Only Python 3.10+ standard-library modules are needed for the evaluator and its
unit tests. From this environment directory:

```bash
python3 -m unittest discover -s tests/bglb-activity-stability -p 'test_*.py' -v
```

These checks do not submit scientific jobs, run a model or use a GPU. Native
specialist compatibility is checked separately using your installed SCI Python;
see [tests/README.md](tests/README.md). No dependency installation is needed here.

## Interpretation and release

Published experimental results, newly calculated predictions and software tests
are separate evidence. Public case-study reproduction is not a leakage-proof
benchmark. Novel sequences without measurements remain unmeasured, regardless of
their model scores. A specialist may improve a workflow but improvement is not
guaranteed or required for a report to be honest.

This replacement removes the previous runner-heavy contribution rather than
shipping its recovery machinery. History remains in Git. The repository's
[license selection](../../LICENSE) is still pending; no new license grant or
public-release readiness is implied.
