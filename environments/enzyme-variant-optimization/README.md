# Enzyme Variant Optimization

An end-to-end workflow for improving an existing enzyme by generating and evaluating new sequence variants. Agent-Scientist chooses suitable tools from Boltzmann, ToolUniverse or both. The environment defines the scientific work and required evidence; SCI supplies tool discovery, input validation, execution, job tracking and subagent delegation.

The workflow is **prepare → evaluate the parent → generate variants with tools → screen properties → assess structures and catalytic features → optimize → re-evaluate → compare**. A list of mutations proposed by the language model alone does not complete the generation stage.

## Start here

1. Choose a case in [tasks](tasks/README.md), then read the [workflow specification](ENVIRONMENT_SPEC.md).
2. Prepare one shared parent input bundle and freeze the task conditions, design limits and final evaluation method before comparing approaches. SCI can prepare these inputs using its existing tools.
3. Run a fresh SCI conversation with the [agent-alone prompt](scripts/RUN_AGENT_ALONE.txt). For an independent assisted run, use the [specialist prompt](scripts/RUN_WITH_SPECIALIST.txt) with the same public inputs and limits.
4. Keep the two runs separate. An evaluator checks evidence and compares their sealed selections using the [benchmark protocol](benchmark/PROTOCOL.md).

The prompts select the RML case by default. Change the task path and run directory together to select another case. These are complete design assignments, not readiness checks. Scientific execution requires the selected tools and normal platform authorization; reading these files does not submit jobs.

For a scientific run, start SCI with this environment as its working directory:

```bash
cd environments/enzyme-variant-optimization
sci
```

Paste the appropriate run prompt into a fresh conversation. Its `./` input/result paths are narrowly scoped user grants for read-only specialist handoffs; create those directories before the first consultation. Do not replace them with a grant to the whole repository.

## Folder guide

```text
enzyme-variant-optimization/
├── README.md
├── ENVIRONMENT_SPEC.md       # Full scientific workflow and completion rules
├── STATUS.md                 # What is implemented and what remains untested
├── MODELS_AND_TOOLS.md        # Required capabilities and tool-selection guidance
├── config/workflow.json      # Shared stages, budgets and task index
├── tasks/                    # Five agent-facing case studies
├── tests/                    # Evaluation-helper and package tests
├── scripts/                  # Run prompts and a comparison command
├── src/evaluation.py          # Small offline numerical comparison helper
├── benchmark/                # Evaluation protocol and operator reference values
└── results/                  # Evidence policy and validation records
```

Supporting literature is in [research](../../research/enzyme-variant-optimization/research-notes.md). The proposer and critic belong in the [Agent-Scientist repository](https://github.com/boltzmannlabs/agent-scientist), under `examples/specialists/enzyme-variant-optimization/` in the companion local branch. That contribution is not yet published or merged. No specialist definitions or copies of SCI's tool catalogue live here.

## Local checks

The comparison helper and its tests need Python 3.10 or newer and the standard library only:

```bash
python -B -m unittest discover -s environments/enzyme-variant-optimization/tests -v
python -B environments/enzyme-variant-optimization/scripts/evaluate_results.py --help
```

Run these commands from the repository root. No Docker image, model checkpoint or GPU is required for these checks. Scientific tools have their own dependencies and compute requirements. Technical checks do not establish that a variant is better.

See [status](STATUS.md) for current readiness. The repository's [license notice](../../LICENSE) still governs reuse; this environment does not grant additional rights to external software, papers or model weights.
