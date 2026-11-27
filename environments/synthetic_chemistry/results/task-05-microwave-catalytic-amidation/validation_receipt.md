# Task 05 — validation receipt

Date of packaging: 2026-11-27 (UTC).

## Checks performed

| Check | Method | Result |
|---|---|---|
| Matching folder identifier in all three sections | Directory listing | `task-05-microwave-catalytic-amidation` present under `tasks/`, `benchmarks/`, `results/` |
| Required READMEs | File existence | `README.md` present in each of the three folders |
| Benchmark links | Text check | benchmark README contains `../../tasks/task-05-microwave-catalytic-amidation/README.md` and `../../results/task-05-microwave-catalytic-amidation/README.md` |
| Comparison report | File + content | `results/.../comparison_report.md` exists and contains "literature" |
| JSON validity | `python -m json.tool` equivalent parse | `achieved_metrics.json`, `task_record.json`, `condition_summary.json`, `optimizer_campaigns.json` all parse |
| CSV consistency | Not applicable | No CSV artifacts in this task; tabular outputs are JSON and Markdown |
| Prior-task integrity | `git status` before commit | No files in task-01–04 folders modified |
| Local Markdown links | Repository test `test_workspace.py` | run below |
| Secrets / signed URLs / personal paths | Manual artifact review | None included; no raw service exports |
| Whitespace errors | `git diff --check` | run below |

## Commands and observed outcomes

```
python -m unittest discover -s tests -p 'test_*.py'   # from environments/synthetic_chemistry
```

Result: `Ran 16 tests ... OK`. Pytest could not be used with the profile interpreter (no pytest module); an alternate venv's pytest failed during plugin import on a cupy/numpy incompatibility before collection, so the repository's unittest-compatible suite was used instead and passed in full.

```
git diff --check
```

Result: no whitespace errors.

## Scope note

This receipt validates repository structure, links and artifact hygiene only. It does not validate chemical predictions, experimental performance or the identity of the designated benchmark paper, all of which remain unresolved as documented in the gaps plan.
