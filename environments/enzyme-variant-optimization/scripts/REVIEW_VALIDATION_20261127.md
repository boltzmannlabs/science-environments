# PR #225 review validation — 27 November 2026

Changes apply only to the enzyme variant environment. Original scientific jobs and native campaign histories were not replayed.

## Review checks

| Review point | Change and evidence |
|---|---|
| Configuration paths | `environment.yaml` declares `path_base: environment_file_directory`. References resolve from their declaring directory, independent of cwd. Environment/package escapes, absolute paths and escaping symlinks are rejected. |
| Usage scope | All 19 run records distinguish parent continuation usage, linked delegated-specialist usage and their deduplicated sum. Single-parent and older operator snapshots remain separate. Session membership, snapshot time, exclusions and token definitions are explicit. Reasoning is not counted twice. |
| Artifact metadata | Missing-field declarations must exactly match the filename's `unreported`/null components. Calendar timestamps, original basename/path, run identity, native job identity and recorded parameter entry references are checked. |
| Benchmark scope | All six reports explicitly use their historical agent-alone run. Structured provenance and linked run/result identities are validated. Assisted outputs remain in separate result records. |
| Native runtime | Fresh agent-alone and assisted software fixtures used the actual SCI CLI constructor, bootstrap, slash routing, native goals, tools and persistence. The assisted fixture used the native installed evaluator. No CLI substitute was used for these runs. |
| Migration checksums | 25 packages contain 490 original/current artifact pairs. Every original is a retrievable blob at an immutable Git commit/path. 414 pairs are byte-identical; 76 are documentation/metadata updates. All 322 scientific data/image files are byte-identical. |

## Reproduce the offline checks

From `environments/enzyme-variant-optimization` in a checkout with the PR's Git history:

```bash
python scripts/check_record_validation.py
python scripts/validate_run_records.py
python scripts/verify_migrated_artifacts.py --report /tmp/enzyme-migration-checksums.csv
python scripts/build_reports.py
python scripts/validate_run_records.py
python scripts/verify_migrated_artifacts.py
```

The optional CSV lists the original Git commit, original path, current path, both SHA-256 values and whether bytes were preserved. Existing report files are never overwritten. Without `--report`, verification prints only counts. If source blobs are unavailable in a shallow/partial checkout, fetch the PR history and retry; missing originals are errors, not skipped checks.

Path validation was also run from `/tmp` using the validator's absolute path. It validated the same 19 runs. Nineteen regression checks cover bad references, provenance declarations, calendar timestamps, incorrect native parameter references, overlapping/count-corrupted usage and misleading benchmark attribution.

## Actual SCI runtime evidence

- SCI source revision: `2ecef925e090c61c106eb6342d402f76ccb1cf3e`.
- Interpreter: SCI-managed Python 3.14.7.
- Dedicated fresh profile: `enzyme-pr225-runtime-check`; only its model-provider credential was provisioned. Scientific credentials, MCP connections and original profile histories were not copied.
- Model: `hy4-flash-free`, provider `opencode-go`, reasoning `xhigh`.
- Native package installer installed and reviewed `enzyme-method`, `enzyme-recovery` and `enzyme-evaluator` 1.2.0. No dependency installation was required. The reviewed coordinator 1.2.0 skill was installed in this profile.
- Both final tests persisted `max_turns: 20`, one native goal turn and `last_verdict: done` in their session's native goal metadata.

| Fixture | Parent session | Linked evaluator session | Observed output |
|---|---|---|---|
| Agent-alone | `20261127_131704_fff427` | None | `READY.txt`, exact bytes `READY\n`; native goal verdict `done` |
| Assisted | `20261127_131813_a7fb9f` | `20261127_131841_54de6c` | Completed evaluator receipt, `READY.txt`, exact bytes `READY\n`; native goal verdict `done` |

Expected marker SHA-256: `3dfa3fb239f56c778a1e9b33eb31328349edd155a95806dac4378904e88527e5`.

Launcher bytes tested:

| Script | SHA-256 |
|---|---|
| `launch_task.py` | `88cb8c139283104d9f01864da9d0c33739d827384604f321fa878ef0c42672ae` |
| `start_goal.py` | `5bdef3d3ffa90829df06fa9bde92c72f77747b1b3fb6fa07e058787bdcf8a8a3` |

To repeat without launching an enzyme campaign, copy these two scripts unchanged into a temporary fixture environment. Give it `tasks/task_999_runtime_agent_alone/task.md` and an assisted equivalent, plus `ENVIRONMENT_SPEC.md` and `MODELS_AND_TOOLS.md`. Define the entire task as writing the exact marker `READY\n`; for the assisted case, also request one saved evaluator review of that fixed token and save the actual receipt. Explicitly prohibit scientific jobs, network tools, installations and private-history reads. Use a fresh dedicated SCI profile with the reviewed packages and model credentials, and explicit JSON launch settings for that task, approach, model, provider, reasoning and `goal.max_turns=20`.

Prepare with the real copied `launch_task.py` and the same flags documented in [scripts/README.md](README.md), pointing to that fixture task/settings and a new empty workspace. Execute its printed `start_goal.py` command in a PTY. Check `LAUNCH_INTENT.json`, actual output bytes, the native delegation result/child session for the assisted case, and persisted native goal state. No SCI constructor or CLI method is replaced. Finished fixture processes were closed; native histories and receipts remain available in the isolated profile.

### Initial test observation

Before clarifying the launch text, agent-alone session `20261127_131121_f97fcd` tried to inspect SCI internals to satisfy the instruction to verify its active goal. It also encountered failures attempting inline Python through the runtime's terminal shim. The operator interrupted this software test before a marker or final goal verdict; it is not counted as a successful test. Initial assisted session `20261127_131312_1feb44` completed with an evaluator receipt and native `done` verdict.

The launcher now states that it checks the retained turn setting and native SCI displays goal activity; application/profile inspection is outside the task. Both final fresh fixtures above completed. These checks establish software startup, delegation, persistence and file handoff on the stated revision. They do not test live scientific connectors or establish scientific qualification.
