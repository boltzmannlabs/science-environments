# results/ — run outputs

One directory per attempt: `results/<task_id>/<run_name>/` (e.g. `results/task_001/run1/`).

A run directory must contain every expected output file listed in the task's **Expected Output** table, plus a `metrics.json` with at least:

```json
{
  "best_docking_score": -8.4,
  "engine": "Vina_basic_docking",
  "task_id": "task_001"
}
```

- `best_docking_score` is the graded number (kcal/mol, platform Vina). Additional keys (ADMET rows, MD summaries, second-engine scores) are welcome; the grader reads `best_docking_score` → `best_score` → `docking_score` → `score` → `best_hit_score`, first numeric hit.
- ADMET and MD rows are human-reviewed; the automated grader checks output-file presence and the docking anchor only.

Grade a run:

```
python3 scripts/grade_run.py task_001 results/task_001/run1
```
