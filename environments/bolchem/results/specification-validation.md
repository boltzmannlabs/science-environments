# BolChem specification validation

Date: 5 November 2026. Contribution: environment specification/documentation.
Related issue: #46. **This report does not validate scientific execution.**

## Checks performed

| Check | Result |
| --- | --- |
| Required overview, specification, status, tool inventory and reference index | Present |
| Separate de novo and optimization modules, each with its task directory | Present |
| Internal links within new environment/research documents | All resolve |
| Current task copies match the separately reviewed source drafts | Byte-identical |
| Literature names, citations, URLs and reference search algorithms in task files | None found |
| De novo target scope | Single p38α target and 1A9U context; no 3GCS or gene-name confusion |
| Optimization contract | Explicit objective variants, immutable original reference and strict joint qualification |
| Lifecycle claims | Specification; no implementation/scientific-validation claim |
| Payload scope | Markdown only; no scientific artifacts, model binaries or credentials included |
| Empty placeholder/runtime directories | Not created |
| Markdown whitespace in new files | No trailing whitespace |
| Tracked index diff whitespace | git diff --check passed |

The two author repository pages, RCSB 1A9U record and official Smina project were
accessible through the web tool during packaging. Publication identities and
scientific protocols retain the earlier source/critic review; not every DOI or
binary-download URL was rechecked in this packaging step. Binary loading,
dependency installation, target preparation and model inference were not tested.

## Task copy hashes

| File | SHA-256 |
| --- | --- |
| `small-molecule-de-novo-design/tasks/p38alpha-design.md` | `50b70111fc27a74cb648b6f47cb2fbb2b8667d9be5995eaf185cbffb193418b4` |
| `small-molecule-optimization/tasks/drd2-optimization.md` | `3bab02a2b3b062d3bd7bd7a6a8c1257b61de23274ff5408f7bd021823f9e1013` |

## Review evidence and limits

Earlier protocol, execution and critic subagents reviewed the task definitions.
The critic's final document-level review found no critical drafting issues.
This is not maintainer approval, an implementation test, or a scientific result.
A human scientific/maintainer reviewer has not been assigned in this contribution.

Prepared structural/scorer bundles, optimization input identities/model loading,
actual execution limits and the independent evaluator remain required. The two
runtime tasks have not been run here. Executable tests are not applicable to this
Markdown-only packaging contribution.

## Git workflow state

Local branch: `Bolchem`, created in a separate worktree from available main snapshot
`85ebef7517534010df31f4b8e12e1676e3455e41`. It now tracks `origin/Bolchem`, not main.
The branch was initially published without the new content; the owner subsequently
authorized committing and pushing this specification increment. Actual publication
is recorded in branch history. No PR, maintainer approval or merge is claimed.

Fetching the newer remote main was rejected by automatic approval review under
the user's explicit fetch/pull permission restriction. It remains a pending
future review-branch prerequisite rather than a claim that this branch uses the latest main.
Existing modified main/BoltChem checkouts were not edited by this contribution.

## Folder organization update

The task files were moved into separate `small-molecule-de-novo-design/tasks/` and `small-molecule-optimization/tasks/`
directories without changing task contents. Module overviews and navigation links
were added/updated. The owner subsequently authorized a BolChem-only branch
snapshot and the module names `small-molecule-de-novo-design` and
`small-molecule-optimization`. Inherited files are removed only from this working
snapshot by an ordinary commit. History remains intact; a future PR must use a
fresh main-based branch containing only the BolChem additions, not these deletions.
