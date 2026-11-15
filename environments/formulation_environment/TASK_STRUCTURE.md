# Unified formulation task structure

Use the exact same registered identifier under `tasks/`, singular `benchmark/` and `results/`. The requested first identifier is literally **Task - 01**, including spaces and hyphen. Its descriptive title is in its README and `config/tasks.json`; do not rename IDs when titles evolve.

```text
tasks/Task - 01/README.md
benchmark/Task - 01/README.md
results/Task - 01/README.md
```

Task README: title, overall task, objective, input provenance, actual execution, scope, acceptance and links to matching benchmark/results. Benchmark README: comparator eligibility, frozen bounds, source data, metrics and what success does not mean. Results README: versioned artifacts, actual findings, failures, limitations and links back.

For Task - 02, create the three matching folders, add its registry entry, implement explicit dispatch and tests, and record its scientific boundary. Never overwrite Task - 01 or silently change its dose/method/model. Shared functionality belongs in `src/`, not duplicated task scripts. Keep old result versions; new runs need new directories.

Publishing rules: no personal paths, credentials, account-scoped exports, full copyrighted articles, SDK/cache directories or fabricated laboratory results. Preserve source citations and distinguish computed, literature-observed, planned and measured endpoints. Generated HTML/SVG artifacts retain byte-identical Matplotlib formatting; scoped `.gitattributes` disable whitespace checks only for those generated artifacts, not implementation or documentation. Run tests, offline replay and publication validation before pushing. Do not claim a main merge or review approval from a branch push.
