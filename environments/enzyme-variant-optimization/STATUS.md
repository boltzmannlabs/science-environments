# Implementation status

**Maturity: In Progress.** This is the enzyme pod's first environment-package contribution, linked to [Issue #40](https://github.com/boltzmannlabs/science-environments/issues/40).

## Implemented in this contribution

- Explicit task/parent/catalytic contracts and computational or library-constrained candidate scope.
- Saved candidate histories, links to source files and jobs, and recorded research decisions.
- Input preparation, uploads, sequence/structure transfers, result matching, and combined reports.
- Separate specialist proposer and critic roles, the actual DiscoveryRSI research loop, and fixed/base/specialist execution modes.
- Portable source packaging, a bundled existing executor snapshot, synthetic examples, and environment-focused regression tests.

Fresh release-check evidence is recorded in [results/validation.md](results/validation.md). It concerns the exact package in this branch and does not import previous server test counts as current results.

## Work still required

- Finish the ongoing live pipeline checks and document their results separately.
- Prepare installation instructions and distribution for the separate host-support modules used by `native_episode.py`; test them together with the selected Agent-Scientist version and connector.
- Complete the comparison of the fixed workflow, base agent, and specialist in `science-benchmarking`, using equal resource limits and hidden experimental test answers.
- Resolve repository license selection, confirm dependency redistribution terms, and obtain maintainer/software/scientific review before public release.

We have not yet established that the specialist produces better enzyme candidates than the other approaches. The offline example also does not demonstrate the complete live specialist setup.
