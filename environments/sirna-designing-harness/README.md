# siRNA Designing Harness

**Lifecycle: In Progress.** This repository contribution implements a portable technical-check environment and an Agent Scientist workflow specification. It is **not** a newly bundled end-to-end predictor or a biologically validated design service. Scientific backends, licenses, weights and references must be separately configured and verified.

## Purpose

Take an explicitly specified human transcript through reference-verified siRNA design, compatible computational assessment, critical ranking and evidence-qualified reporting. Support four operating modes: **DESIGN**, **AUDIT**, **SENSITIVITY**, and **BENCHMARK**. Keep successful computational screening separate from experimental efficacy and biological qualification.

The default exercised envelope is human RefSeq coding mRNA and paired 19-nt RNA cores, not order-ready chemically specified duplexes. Other species, strand lengths, modified/asymmetric constructs and mismatch-selective models require separate validated adapters.

## Quick start: no installation or model download

Python 3.10+ is sufficient for the included standard-library technical helpers:

```bash
cd environments/sirna-designing-harness
python3 scripts/run.py --help
python3 scripts/run.py describe
python3 scripts/run.py check-project
python3 scripts/run.py check-skill
python3 scripts/run.py verify-benchmark
python3 scripts/run.py preflight --config config/environment.example.json
python3 scripts/run.py validate-objective --objective tasks/kras-shared-review.json
python3 -B tests/run_validation.py --scratch /absolute/approved/scratch
```

The preflight template intentionally reports missing assets and exits 2. Objective validation checks intake, **not** authoritative reference identity. Most examples are not runnable scientific jobs until explicitly configured. Do not install into SCI's runtime or use auto-approval to bypass scientific execution permissions.

For real design, load `skills/sirna-harness/SKILL.md` into the intended SCI profile using its local operating manual. Configure approved existing tools separately. See [configuration guide](config/README.md) and [task contracts](tasks/README.md). The portable skill installer refuses existing destinations; this repository does not modify profiles automatically.

## Project structure

```text
sirna-designing-harness/
  README.md
  ENVIRONMENT_SPEC.md
  STATUS.md
  config/                 # dependency/capability contracts and incomplete templates
  tasks/                  # design/audit/sensitivity/benchmark contracts
  tests/                  # software and structural validation, no fabricated efficacy
  scripts/                # executable technical environment interface
  skills/sirna-harness/    # original portable workflow and stdlib helpers; own MIT notice
  benchmark/KRAS/         # frozen reports/result tables from five historical KRAS stages
  results/                # project tests/receipts; earlier project receipts preserved in history/
```

Research is maintained in [research-notes.md](../../research/sirna-designing-harness/research-notes.md) and the central [references.md](../../research/sirna-designing-harness/references.md). See [architecture decision](../../docs/decisions/sirna-designing-harness.md).

## Included KRAS reports and results

Browse [benchmark/KRAS/README.md](benchmark/KRAS/README.md) for the shared-target report, candidate evidence tables, exact-match failures, ranking sensitivity, blocked experimental-data audit and literature comparison. The 85 selected source files are copied byte-identically with source/copy hashes. The snapshot is intentionally partial; large/raw source artifacts are retained externally and indexed. Historical receipts are labelled `source_*` so they are not confused with current snapshot verification.

Run `python3 scripts/run.py verify-benchmark` without original data/model dependencies to verify the included snapshot. No scientific analyses are rerun. The `benchmark` folder name does not imply independent experimental validation.

## Evidence and present limitations

The verified historical KRAS study generated 5,288 unique cores, deep-assessed 100, investigated 20, and retained a conditional 14-candidate review subset. The literature comparison recovered two shared-KRAS paired cores already in the full pool but absent from that shortlist. One source-supported core carried an inherited palindrome heuristic flag. This motivates criterion review, not silent threshold changes or a superiority claim. [Evidence and sources](../../research/sirna-designing-harness/references.md).

Historical independent experimental validation remains `BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET`. The shared computational arm remains complete; overall biology remains `PARTIAL`. The mutation arm remains `BLOCKED_PENDING_MUTATION_SPECIFICATION`. No hypothetical mutant is included or constructed by the technical CLI.

## What is executable here

- Structural/project contract checks.
- Portable skill payload integrity checks.
- Environment file/checksum preflight, without invoking backends.
- Objective format/scope checks.
- Supplied 19-nt pair/coordinate/unique-site/flank validation.
- Fail-closed gate review and minimal measured-table audit.
- Optional read-only historical-receipt verification with an explicitly supplied evidence root.

What is **not** executed by `scripts/run.py`: candidate generation, learned-model inference, folding, transcriptome/seed screening, literature crawling, biological experiments, or an independent efficacy benchmark. Those are agent-orchestrated tasks using separately installed/authorized scientific tools. A missing required assessment blocks its conclusion, not unrelated valid checks.

## Validation and contribution status

Current software/structure checks and reproduction commands are recorded in [STATUS.md](STATUS.md) and `results/validation_receipt.json` after execution. These are technical checks, not predictor-accuracy or biological validation.

Local branch: `feat/sirna-designing-harness`. GitHub CLI was unauthenticated while preparing this contribution; issue discovery/creation and PR creation could not be completed. Draft [issue](tasks/ISSUE_DRAFT.md) and [PR](tasks/PR_DRAFT.md) are supplied. No owner/reviewer approval, remote submission, commit, push or merge is claimed. The issue-first governance step is outstanding; this is a local review draft, not a fully completed repository contribution.

Repository-wide license selection remains pending. The copied original skill/helpers retain their separate MIT notice; no license is asserted for the whole repository. No third-party code, weights, reference indices, raw papers, experimental datasets or credentials are bundled.
