# HKII capability-task review — 2026-11-06

## Scope and sources

This review covers the task_007 rewrite, its evaluator metadata and supporting parser/validation/grading changes. It is a document and implementation review, not a scientific execution or capability certification.

Sources checked:

- Tanbin et al., DOI [10.3390/biotech10010001](https://doi.org/10.3390/biotech10010001), original 28-page PDF and PMC9245486 XML: Methods 2.1–2.3, Results 3.1–3.3, Tables 1–12 and figure evidence retained in the earlier source audit.
- Main-branch [bispecific cellular mechanism assessment task](https://github.com/boltzmannlabs/science-environments/blob/7fba071a17c0d7184962aeb8ef20468459138978/environments/antibody_design/tasks/bispecific_assessment/bispecific_cellular_mechanism_assessment.md).
- User requirements: preserve the scientific workflow, let the agent reason about suite/tool selection, omit paper identity/verbatim tools/published outcomes from the task, retain scientific constraints and review before push.
- Existing HKII execution evidence, including the native-frame structure audit and recorded platform-contract limitations.

## Findings and resolutions

| Area | Critique | Resolution |
| --- | --- | --- |
| Workflow fidelity | Generic similarity permits a different screening method; optional dynamics omits a source stage | Require 3D shape/feature screening, filtering before docking, candidate selection and dynamics validation |
| Scientific parameters | Removing tool prescriptions must not remove required experimental-design constraints | Retain three queries, up to 100 analogues/query, strict initial property limits, declared binding region/box size, 100 ps heavy-atom-restrained equilibration and 20 ns production |
| Input control | Agent-selected libraries make runs and historical comparisons incomparable | Require a frozen run-supplied library/manifest and validated reference definitions; unresolved required data produce NEEDS_INPUT |
| Selection integrity | Exceptions introduced after outcomes permit result-driven selection | Require exception policies and endpoint coverage before reviewing outcomes; reconcile unique identities and repeated query entries separately |
| Coordinate validity | The published centre contains no protein atoms in native 2NZT | Require derivation/validation of a centre in the actual prepared frame; retain the source discrepancy in evaluator provenance |
| Source ambiguity | Incorrect identifiers, contradictory property compliance, site descriptions, score statements, versions and RMSD summaries cannot be made authoritative by copying them | Keep source details/conflicts evaluator-only; require independently validated inputs and method-defined results |
| Tool agency | A named-software/API recipe supplies the implementation choice | Agent task lists only capabilities and scientific evidence; agent selects and justifies actual suite tools |
| Discovery scope | “Generate candidates” can imply de novo molecular design, which the source workflow does not perform | Specify retrieval/screening of existing fixed-library members and preserve molecular identity during conformer preparation |
| Answer leakage | Published identities/scores and source identifiers can become shortcuts | Move original provenance to the same-named evaluator Markdown file; agent bundle excludes evaluator/source-reference material |
| Evidence quality | Score similarity does not establish pose recovery, endpoint equivalence or completed dynamics | Distinguish pose-to-crystal from pose-to-best-mode displacement, check endpoint definitions and require trajectory/log duration evidence |
| Output contract | Dynamics must have explicit machine-readable completion/measurement evidence | Add per-system dynamics results and preserve native artifacts; missing measurements remain missing |
| Completion semantics | Missing outputs or predictions can be disguised as no qualifying candidates | Restrict negative-outcome status to actual completed screening/filtering; complete runs require all groups and no unresolved required stages |
| Legacy compatibility | Old validators require publication/tool strings and a 240-minute limit inside the task | Support a capability-task format with owner-side provenance and execution-context budgets while preserving legacy task records |
| Grading | A single favourable score and file presence cannot certify a multi-stage workflow | Refuse legacy automatic grading for capability workflows and require scientific review; regression test exercises the false-pass case |
| Scope preservation | Other task definitions and existing benchmark entries must not change | Compare their file hashes and the original six generated records against the parent commit |

## Validation and residual limitations

The release gate comprises the full structure-based-discovery validator, negative tests for source/tool leakage and missing evaluator metadata, a regression against false single-score certification, checks of source identifiers/output metadata, whitespace review and preservation of other task files and original task_001–task_006 generated entries.

Review result: all three validator groups passed (task structure, config/benchmark synchronisation and README synchronisation). Standalone structure and config tests passed, including the negative leakage/provenance cases and false-certification regression. Direct primary-XML checks confirmed the screening scale, box dimensions and equilibration/production constraints; output metadata has seven evidence criteria and ten required result files. Hash checks preserved all 16 other task/readme files, and deep comparisons preserved the original six configuration and benchmark entries. These checks apply to the rewrite before publication, not to scientific runtime outcomes.

The benchmark runner must still supply the neutral fixed input bundle. This rewrite does not recover the historical screening library or make its prepared coordinate frame available. Current catalog evidence does not certify exact 3D screening, independent box controls, endpoint equivalence or MD restraint/protocol support. The agent must verify those capabilities and report unsupported required stages honestly. Scientific execution and full platform feasibility remain unverified; document validation must not be reported as an end-to-end run.
