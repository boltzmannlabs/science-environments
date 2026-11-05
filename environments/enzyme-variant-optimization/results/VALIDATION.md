# Local Software Validation

Validation scope: the local implementation prepared on 4 November 2026. No scientific jobs or paid model calls were used for these checks.

| Component | Command or path | Result |
| --- | --- | --- |
| Environment | `python -B -m unittest discover -s environments/enzyme-variant-optimization/tests -v` | 13 tests passed, including real-file CLI comparison/seal checks, a changing-file regression, package navigation and per-task section/workflow/output/limit checks. Repeated with Python 3.14.7. |
| Companion native SCI examples | `scripts/run_tests.sh tests/sci_cli/test_enzyme_variant_specialist_examples.py tests/sci_cli/test_specialist_commands.py tests/agent/test_specialist_store.py tests/agent/test_specialist_permissions.py tests/agent/test_specialist_input_scope.py -j 2 --file-retries 0 -v` | 14 tests passed, 0 failed, using an isolated PM-built Python 3.14.7 test environment. |
| Whitespace | `git diff --check` in both worktrees | Passed for the reviewed changes. |

The companion checks exercise actual saved-definition parsing, native import/review, A→B→A profile isolation, fresh-session gating, capability restrictions, context assembly and child limits without invoking a live model. The environment checks exercise consistent numerical declarations, missing evidence, eligibility, parent identity, units, protocols, duplicate sequences and selection seals using synthetic values.

These are software tests, not validation of molecular predictions, scientific tool availability, task execution, historical numerical reproduction or specialist performance. The five scientific cases have not been run under this workflow version.

All five task files now use the same section structure as the repository's antibody design tasks. Each includes its own full eight-stage capability table, execution profile, evaluation metrics/rules and output artifacts. The additional task checks establish document coverage and configuration consistency, not scientific adequacy or execution.

A separate read-only implementation review identified and verified fixes for specialist input-path grants and a selection-file reread race. Regression tests cover both. The follow-up review found no remaining substantive issue in those fixes; this is not a scientific peer review.

Source baselines: Science Environments `e3e09f744308c86925bf032999f65efd8cac51be`; Agent-Scientist `e4f8f39c000ad1c0245d0044ddd3341c336990d1`. The environment's working branch is `team/enzyme-variant-optimization`, based on `dev` at the Science Environments baseline above; its later PR destination is `dev`, as confirmed by the owner. Specialist examples remain local on `feat/enzyme-variant-design-specialists`. No scientific run, PR, merge or installed-profile update is part of this software validation.
