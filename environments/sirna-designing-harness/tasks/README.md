# Agent task contracts

These JSON files specify tasks for Agent Scientist; they do not submit backend jobs. The technical CLI can validate the objective fields or display contracts, but does not impersonate a generator, predictor, literature service or experimental assay.

| Task | Scope | Expected boundary |
|---|---|---|
| `kras-shared-review.json` | Previously authorized four-reference human KRAS objective | Reuse verified historical evidence unless new work is explicitly authorized |
| `kras-mutation-blocked.json` | Comparative intake without a specified mutation | Shared work may proceed; mutation arm remains blocked, no mutant constructed |
| `audit.json` | Inspect actual completed artifacts, new output directory | No generation/inference/folding/screening repeats; source hashes unchanged |
| `sensitivity.json` | Preserved compatible scores | No imputation, new weights or biological claims from rank changes |
| `benchmark.json` | Measured dataset/provenance audit before testing | Fail closed if no auditable independent compatible test cohort |
| `literature-comparison.json` | Original-source selection versus computational priority | Pooled source ranges are not individual benchmark labels |

The associated `output_contracts.json` defines named minimum artifacts and status semantics. Do not invent expected numeric outputs for a new target. Experimental endpoints, reported sequences, labels and source identities must come from actual inspected artifacts.

`ISSUE_DRAFT.md` and `PR_DRAFT.md` are local review text because GitHub CLI authentication was unavailable. They are not claims of remote issue/PR creation, ownership assignment or review approval.
