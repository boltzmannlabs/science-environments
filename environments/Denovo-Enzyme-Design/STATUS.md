# Status

**Maturity: In Progress.** Fixed execution, internal review, bounded repair, frozen-run records and evidence validation are implemented. Scientific adapters and target-specific chemistry qualification remain separate requirements. RL is specified but not implemented. No qualified enzyme or experimental activity is established by this package.

## Publication scope

Tracking: [issue #86](https://github.com/boltzmannlabs/science-environments/issues/86). Publish the latest execution-policy and scientific-contract changes together with the standard environment layout. The CLI is `scripts/run.py`, supporting code is in `src/`, schemas/examples are in `config/`, and validation entrypoints are in `scripts/`. The generic agent instruction is `src/TASK.md`.

`tasks/`, `tests/`, `benchmark/` and `results/` contain only empty `.gitkeep` markers. They contain no scientific tasks, test suite, benchmark outputs or run results. Run outputs belong in a separate user-selected run directory.

## Preserved implementation and test history

The reviewed package and its full original regression suite are preserved in [pre-layout commit 7c81252](https://github.com/boltzmannlabs/science-environments/commit/7c81252d67857d1025103a1042d09f58e2671812). Earlier frozen runs must continue with their own runtime and accounting; reorganizing this package does not migrate or renew them. The latest implementation requires new run snapshots.

`scripts/check_regressions.py` reads that pinned commit from local Git history, adapts file-location assumptions and executes the existing tests in a temporary directory against the current package. It requires Python, jsonschema, PyYAML and NumPy. OpenMM-specific coverage is skipped when unavailable. Use a Git checkout containing the pinned commit; a source ZIP or depth-one clone may omit it. The script performs no network fetch or scientific-provider submission.

## Validation

Publication checks on 31 October 2026: **198 specification checks passed; 63 regression tests passed and one optional OpenMM test was skipped**. Controller initialization and frozen-snapshot doctor/status checks passed using a synthetic command backend. No scientific or live-agent jobs were submitted. The tracking issue records the publication evidence. Historical checks are not treated as fresh evidence: the previous package recorded 209 specification checks and 64 unit tests (63 passed, one OpenMM-dependent skip). The initial reorganized filesystem copy passed 197 specification checks and the same location-adapted regression suite. These are software/contract results, not enzyme qualification.

Reproduce current checks from this directory:

```bash
python3 -B scripts/validate_environment.py
python3 -B scripts/check_regressions.py
```

Both scripts accept an optional `--report` path outside the environment; they leave the reserved directories unchanged.

## Acceptance

- Schemas, examples, documentation links and the requested top-level entries resolve.
- The four reserved directories contain no substantive files.
- Initialization freezes executable and instruction dependencies; resume uses the frozen `scripts/run.py`.
- Evidence binding, independent assessment, invalidation, recovery and resource boundaries remain intact.
- Scientific qualification needs applicable controls and all mandatory chemistry, folding, assembly and property evidence. Software checks, confidence, docking and classical MD do not replace that evidence.

## Remaining requirements

Verify the actual harness, platform access, supported combined assembly/motif capabilities and target-specific reaction maps and calculation methods. The last platform audit did not confirm an appropriate aggregation executor or a complete catalytic-reaction executor; capabilities must be rechecked for each run. Missing evidence remains unresolved while independently eligible stages may proceed. Provider access restrictions require harness enforcement. Scientific/domain review remains pending; publication does not claim reviewer approval or successful end-to-end enzyme design.
