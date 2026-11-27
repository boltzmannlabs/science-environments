# Scripts

Run commands from the environment directory. These scripts use native SCI for execution; they do not implement a separate scientific runner.

| Script | Purpose | Dependencies |
|---|---|---|
| `launch_task.py` | Prepare a new task and print its native goal command; starts only with explicit `--start`. | Python standard library; reviewed SCI needed to start. |
| `start_goal.py` | Start the prepared `/goal` in an interactive terminal with the selected SCI runtime/profile. | Reviewed SCI runtime and enabled capabilities; assisted runs require the three 1.2.0 packages and coordinator. |
| `evaluate_results.py` | Compare sealed selections and reviewer-supplied numerical observations. | Python standard library. |
| `build_reports.py` | Rebuild six historical comparison reports and linked figures from saved data. | Matplotlib. |
| `validate_run_records.py` | Check schemas, safe declaring-directory references, usage scopes, benchmark approach and artifact provenance/hashes. | PyYAML and jsonschema. |
| `check_record_validation.py` | Regression checks for invalid paths, provenance, usage and benchmark attribution. | PyYAML and jsonschema. |
| `verify_migrated_artifacts.py` | Recompute original Git-blob and current-file checksums for every exported result/benchmark artifact. | Python standard library and Git with PR history. |

## Prepare a fresh execution

Choose a task and freeze its settings first. Supply the model, provider and reasoning level explicitly; the launcher does not choose them. Historical configurations marked `launch_ready: false` cannot be used to launch.

```bash
python scripts/launch_task.py \
  --task task_002_leh_stability \
  --settings /path/to/frozen_settings.json \
  --approach agent_with_specialist \
  --profile your-dedicated-profile \
  --run-dir /path/to/empty-run-directory \
  --sci-python /path/to/reviewed-sci-python \
  --sci-source /path/to/reviewed-agent-scientist
```

Run the printed command in an interactive terminal, or add `--start` to the preparation command there. The starter applies SCI’s normal bootstrap, uses the actual configured ToolUniverse MCP name, verifies frozen settings and prevents a second fresh start in the same workspace. It queues the native `/goal` command and retains `goals.max_turns=20`. Use `agent_alone` for a run without specialists. SCI owns job execution, delegation, permissions and history.

Assisted runs use reviewed `enzyme-method`, `enzyme-recovery` and `enzyme-evaluator` 1.2.0 packages and the environment’s `enzyme-coordinator` skill. Install them through SCI’s reviewed package workflow before starting. The native selected profile determines credentials and enabled connectors; no secrets belong in this repository.

## Continue an existing execution

```bash
sci -p your-original-profile --resume ORIGINAL_NATIVE_SESSION_ID
```

Use the original profile/workspace and saved native assignment identities. After the retained goal allowance, use native `/goal resume` in that conversation. Reconcile accepted or unknown jobs before any new submission. Preparation scripts do not replay historical runs.

## Offline checks and reports

```bash
python scripts/validate_run_records.py
python scripts/check_record_validation.py
python scripts/verify_migrated_artifacts.py
python scripts/build_reports.py
python scripts/evaluate_results.py --help
```

Report generation uses already-saved measurements; it does not run scientific predictors. The endpoint helper checks declared observations and seals, not molecular validity or experimental improvement. Validation supports populated input manifests and concise input-provenance notes in run.json. Original per-call SCI histories remain outside the repository.

Task-specific entry points below use the full required flags. The two prompt text files are optional manual templates; the explicit launcher is the reproducible starting point.

## Checks performed — 27 November 2026

All 19 configuration/run packages, 461 result artifact hashes and 322 scientific filename declarations validate. Nineteen regression checks pass, including traversal/symlink rejection, missing-field mismatches, wrong native parameter references, duplicate usage and assisted/agent-alone benchmark mixing. Validation also passes from an unrelated working directory. All six saved-data reports rebuild.

Native launch and bootstrap tests ran against the actual installed SCI runtime, including a real evaluator delegation, output-file verification and persisted native goal verdicts. These replace the earlier controlled CLI-only handoff evidence. The tests used an isolated profile and software-only fixtures; no scientific jobs were launched. See [review validation evidence](REVIEW_VALIDATION_20261127.md) for source revision, session IDs, checksums and the initial test interruption.

The migration verifier checks 490 original/current artifact pairs using immutable source Git commits: 414 files are byte-preserved and 76 are declared documentation/metadata updates. All 322 scientific artifacts are byte-preserved. Original and current paths/hashes are stored in each package's provenance; generate an optional review CSV with `python scripts/verify_migrated_artifacts.py --report /tmp/enzyme-migration-checksums.csv`. The destination must not already exist. Historical `source_sha256` values concern earlier source exports; the new `migration_evidence` explicitly identifies the published Git originals checked here.
