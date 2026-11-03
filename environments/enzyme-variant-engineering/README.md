# Enzyme Variant Optimization

This environment describes a complete computational workflow for improving an
existing enzyme. It provides the scientific process, a concrete case assignment,
required outputs and comparison rules. Agent-Scientist researches the problem,
chooses suitable tools and performs the work through its existing capabilities.

**Status: In progress.** The current task is Est30 optimization for MHET
hydrolysis. Execution records, scientific output tests and comparative results
will be added after the ongoing runs finish and their artifacts are reviewed.

## Structure

```text
enzyme-variant-engineering/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── .gitignore
└── tasks/
    └── est30-mhet/
        ├── TASK.md
        └── PROMPTS.md
```

Research rationale and sources are in
[research/enzyme-variant-engineering](../../research/enzyme-variant-engineering/research-notes.md).
Tests and results are not represented by empty folders or invented examples.
They will be added with reviewed scientific evidence.

## Workflow

1. Establish the parent sequence, reaction, conditions and allowed changes.
2. Generate complete candidate sequences and evaluate relevant properties.
3. Obtain structures and substrate complexes for shortlisted candidates.
4. Check structural quality, catalytic chemistry and uncertainty.
5. Diagnose weaknesses and execute a justified optimization revision.
6. Re-evaluate the revised candidates and report the final selection.

These are scientific requirements, not a mandatory sequence of named tools.
Agent-Scientist can choose suitable Boltzmann operations, ToolUniverse operations
or both. A listed package or retrieved result is not proof of a new calculation.

## Start the Est30 task

Use an installed, authorized Agent-Scientist with native scientific tool access.
No environment package, plugin, custom profile or dependency installation is
required by this contribution.

Start SCI from this environment directory and open a fresh conversation:

```bash
sci
```

Read [the task](tasks/est30-mhet/TASK.md), then paste the appropriate
[launch prompt](tasks/est30-mhet/PROMPTS.md). Use separate fresh conversations
and separate local output folders for the agent-alone and assisted runs.
Neither may inspect the other run's outputs or withheld reference outcomes.
Existing native service authorization and permissions remain in force.

The assisted run uses named, reviewed subagents supplied separately through
Agent-Scientist. Their definitions, implementation and maintenance belong in the
Agent-Scientist repository, not here. The task names the expected roles; it does
not install them or claim that another user's profile already has them.

## Scope

There is no duplicate tool catalogue, input validator, connector, database,
scheduler, model client or execution engine in this environment. Native SCI
handles those capabilities. This environment also does not provide a new
trained molecular model or an operating-system sandbox.

The previous runner-based package under `enzyme-variant-optimization/` is
replaced, not copied into this environment. Historical commits remain available;
changing the repository does not uninstall plugins or stop existing sessions.

Computational comparisons and experimental measurements remain separate.
Improvement over the parent or published designs must be measured under a
comparable procedure, not assumed from a favorable predictor score.

The repository's [license selection](../../LICENSE) is pending. This contribution
is for review, not a claim of public-release readiness.
