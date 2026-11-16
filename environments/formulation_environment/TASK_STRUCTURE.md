# Unified formulation task structure

Use a descriptive folder name for the work, with the same `folder_slug` under `tasks/`, singular `benchmark/` and `results/`. The current folder is **clarithromycin-500mg-ir-formulation-dissolution**. Its stable logical task ID remains **Task - 01** in the registry, records and CLI; folder names and numbering are separate fields.

```text
tasks/clarithromycin-500mg-ir-formulation-dissolution/README.md
benchmark/clarithromycin-500mg-ir-formulation-dissolution/README.md
results/clarithromycin-500mg-ir-formulation-dissolution/README.md
```

Task README: title, overall task, objective, input provenance, actual execution, scope, acceptance and links to matching benchmark/results. Benchmark README: comparator eligibility, frozen bounds, source data, metrics and what success does not mean. Results README: versioned artifacts, actual findings, failures, limitations and links back.

Task - 02 is [Ranolazine ER Tablet Dissolution Investigation](tasks/Task%20-%2002%20-%20Ranolazine%20ER%20Tablet%20Dissolution%20Investigation/README.md). It has task-specific folders under config/, tasks/, benchmark/, results/, scripts/, docs/, root research/ and root docs/decisions/. Python source and tests use identifier-safe `ranolazine_task02` subpackages. The shared registry records every ownership path, and explicit runner dispatch executes archive consistency checks only. Never overwrite Task - 01 or silently change its dose/method/model. Shared functionality belongs in `src/`, not duplicated task scripts. Keep old result versions; new runs need new directories.

Publishing rules: no personal paths, credentials, account-scoped exports, full copyrighted articles, SDK/cache directories or fabricated laboratory results. Preserve source citations and distinguish computed, literature-observed, planned and measured endpoints. Generated HTML/SVG artifacts retain byte-identical Matplotlib formatting; scoped `.gitattributes` disable whitespace checks only for those generated artifacts, not implementation or documentation. Run tests, offline replay and publication validation before pushing. Do not claim a main merge or review approval from a branch push.