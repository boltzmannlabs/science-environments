# Scripts

Run commands from the environment directory. These scripts use native SCI for execution; they do not implement a separate scientific runner.

| Script | Purpose | Dependencies |
|---|---|---|
| `launch_task.py` | Prepare a new task and print its native goal command; starts only with explicit `--start`. | Python standard library; reviewed SCI needed to start. |
| `start_goal.py` | Start the prepared `/goal` in an interactive terminal with the selected SCI runtime/profile. | Reviewed SCI runtime and enabled capabilities; assisted runs require the three 1.2.0 packages and coordinator. |
| `evaluate_results.py` | Compare sealed selections and reviewer-supplied numerical observations. | Python standard library. |
| `build_reports.py` | Rebuild six historical comparison reports and linked figures from saved data. | Matplotlib. |
| `validate_run_records.py` | Check configuration schemas, input references, run/result links and artifact hashes. | PyYAML and jsonschema. |

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
python scripts/build_reports.py
python scripts/evaluate_results.py --help
```

Report generation uses already-saved measurements; it does not run scientific predictors. The endpoint helper checks declared observations and seals, not molecular validity or experimental improvement. Validation supports populated input manifests and concise input-provenance notes in run.json. Original per-call SCI histories remain outside the repository.

Task-specific entry points below use the full required flags. The two prompt text files are optional manual templates; the explicit launcher is the reproducible starting point.

## Checks performed — 27 November 2026

All script modules compile and CLI help works. All six reports rebuild; 19 configuration/run packages and 461 output hashes validate. A saved sealed LEH comparison runs successfully. Fresh launch preparation, malformed/mismatched settings rejection, and native-runtime imports were checked. A controlled CLI substitute verified `/goal` handoff, the configured ToolUniverse name and duplicate-start rejection; this was a software test, not live scientific execution.

Scientific artifact names and explicit historical fallbacks are checked by the validator. Legacy input names are resolved through per-result provenance, and a changed rendered figure cannot silently overwrite its checksum-based identity. The naming policy is documented in the environment README.
