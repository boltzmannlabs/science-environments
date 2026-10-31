# Denovo Enzyme Design

**Status: In Progress.** A reusable computational environment for soluble, cofactor-free monomer and homodimer enzyme design. The fixed controller and evidence contracts are implemented; reaction-specific methods and complete scientific execution still require validation. RL remains a specified extension.

Give the agent a short scientific request and available reference inputs. The agent resolves the reaction and biological assembly, prepares stage-appropriate inputs, selects real executors, reviews results and performs bounded technical recovery. The user does not have to supply a complete chemistry profile. Missing evidence stays unresolved and cannot become a qualification claim.

## Structure

```text
Denovo-Enzyme-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── config/
├── tasks/
├── tests/
├── scripts/
├── src/
├── benchmark/
└── results/
```

`tasks/` contains [eight published in-silico reproduction tasks](tasks/README.md). Each defines the source computational workflow, inputs, numerical references and comparison procedure; experimental results are supporting context. `tests/`, `benchmark/` and `results/` remain reserved and contain only empty `.gitkeep` files so Git preserves them. Earlier task/test material remains in Git history. The reusable agent instruction lives in `src/TASK.md`; illustrative requests live in `config/`. Do not treat those examples as approved biological or resource defaults.

## Read and run

Read the [specification](ENVIRONMENT_SPEC.md), [agent instruction](src/TASK.md), [tool policy](MODELS_AND_TOOLS.md), [runtime contracts](src/CONTRACTS.md) and [status](STATUS.md). [Research](../../research/Denovo-Enzyme-Design/research-notes.md) and [references](../../research/Denovo-Enzyme-Design/references.md) remain alongside the environment.

Use an already configured harness and its actual platform access. Local controller dependencies are Python, PyYAML and jsonschema. Optional structure preparation also needs NumPy and its separately installed preparation libraries. Copying this package does not configure a harness or scientific services.

```bash
python3 -B scripts/run.py init --run-dir /path/to/new-run --request 'Design a de novo enzyme for the supplied conversion' --input /path/to/reference-manifest.json --agent-config /path/to/agent-config.json
python3 -B /path/to/new-run/environment_snapshot/scripts/run.py doctor --run-dir /path/to/new-run
python3 -B /path/to/new-run/environment_snapshot/scripts/run.py run --run-dir /path/to/new-run
python3 -B /path/to/new-run/environment_snapshot/scripts/run.py status --run-dir /path/to/new-run
```

New runs freeze code, instructions, tool policy and input identity. Resume through that snapshot. Earlier runs must retain their original runtime and accounting; a folder reorganization does not migrate or renew them. Supply the task index, selected reproduction task and prepared manifests through repeated `--input` arguments so their identities are recorded. Keep scientific results in the separate run directory; `tasks/` holds task definitions while the other reserved directories retain only their `.gitkeep` files.

## Validation

```bash
python3 -B scripts/validate_environment.py
```

Use `--report /path/outside/environment/validation.json` to save the check report. The validator checks schemas, request examples, policy invariants, document links and the requested layout. It does not run scientific tools or qualify enzyme activity. The [status](STATUS.md) distinguishes historical checks from current publication validation. Run the preserved regression suite without populating `tests/` using `python3 -B scripts/check_regressions.py`; its test source is pinned to the pre-layout commit and it runs from a temporary directory.

Follow [CONTRIBUTING.md](../../CONTRIBUTING.md). The repository [LICENSE](../../LICENSE) states that license selection is pending. This package follows the repository layout and retains its declared In Progress maturity.
