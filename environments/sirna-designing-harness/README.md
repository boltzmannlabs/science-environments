# siRNA Designing Harness

**Scope: siRNA design and technical validation.** The environment connects an Agent Scientist design workflow with portable sequence checks, recorded siRNA-Bench evidence review, candidate-property reporting and reproducibility/provenance checks.

**Technical reporting component: implemented and tested.** The included recorded KRAS assessment returns **14 of 14 candidates passed the declared technical gates**. Reports lead with this achieved milestone and each candidate's predicted/calculated properties, then retain candidate-specific review flags.

**Repository lifecycle: In Progress.** Scientific backends are separately installed/authorized integrations; the repository does not bundle models or submit jobs. Maintainer review and new-host scientific deployment remain separate from the implemented technical reporting component.

## Quick start — runnable without scientific dependencies

Python 3.10+ and its standard library are sufficient. From this directory:

```bash
python3 -B scripts/run.py describe
python3 -B scripts/run.py check-project
python3 -B scripts/run.py check-skill
python3 -B scripts/run.py verify-benchmark
python3 -B scripts/run.py verify-technical-case
python3 -B scripts/run.py technical-report \
  --bundle results/case_studies/KRAS_14_technical_validation/bundle.json \
  --policy config/technical_gate_policy.json \
  --out /absolute/path/to/NEW-report-directory
python3 -B tests/run_validation.py --scratch /absolute/approved/scratch
```

`technical-report` reads recorded evidence, verifies checksums and computes technical gate decisions. It does not execute models. It refuses an existing output directory. The expected included-case result is `PASSED_DECLARED_TECHNICAL_GATES`, with 14 submitted and 14 technical passes.

A successfully executed example is included at [results/technical_validation_KRAS14/technical_report.md](results/technical_validation_KRAS14/technical_report.md). The matching JSON preserves raw gates, model statuses, properties, flags and reproducibility differences. This is a deterministic report replay of actual recorded runs, not fresh prediction or a synthetic result.

## The design workflow

1. Define the organism, exact transcript.version, isoform objective and experiment.
2. Verify reference identity, orientation, annotations and source provenance.
3. Discover approved scientific tools and execute the selected generator once.
4. Preserve generated pairs and native scores; select a declared assessment cohort.
5. Evaluate compatible candidates through separately configured siRNA-Bench/tools.
6. Review both-strand/isoform evidence, apply declared filters and rank transparently.
7. Produce a technical gate report with properties and candidate-specific flags.
8. Hand off the defined next evidence requirements for the intended application.

DESIGN, TECHNICAL_VALIDATION, AUDIT, SENSITIVITY and BENCHMARK contracts are in [tasks/](tasks/README.md). The bundled [workflow skill](skills/sirna-harness/SKILL.md) describes scientific orchestration; it is not an installed predictor. Use [config/README.md](config/README.md) to distinguish portable reporting from external deployment.

The exercised scope is human RefSeq NM_ coding-mRNA references and exact paired 19-nt RNA cores. CDS and UTR target sites are allowed according to the declared objective. Other species, lengths, modifications and mismatch-selective models require reviewed adapters. Final overhangs and chemistry are not silently inferred.

## What a technical pass means

The new command enforces seven mandatory categories:

- Exact supplied sequence identity and 19-nt guide/passenger complementarity.
- Unique primary target mapping, complete source flanks and all declared reference coverage.
- Actual successful statuses for required efficacy models.
- Explicit numeric property/annotation criteria in [technical_gate_policy.json](config/technical_gate_policy.json).
- Review of native passed, failed and missing-evidence fields.
- Agreement with a distinct recorded earlier job within the declared tolerance.
- SHA-256-bound evidence inputs and retained source-job provenance.

Missing mandatory evidence cannot pass; an explicit failure takes precedence over missing evidence. Metadata-only orientation gaps are retained and distinguished from independently verified pairing/mapping. Native experimental/translational Booleans are not reinterpreted as evidence where measurements are absent.

**Scope statement:** Technical validation covers the declared computational checks; biological efficacy, safety and delivery are separate evaluation stages.

## Properties and review flags

Reports show RN.Ai-Predict's predicted percent endpoint, RNAiSpline effective-class probability, calculated duplex energy and accessibility, native priority and the original Ridge annotation. These endpoints retain separate meanings.

The included KRAS14 report preserves nine Ridge extrapolation flags, four low passenger-seed source annotations, native missing-evidence fields and the known POTS percentile-direction limitation. A technical pass never removes these flags or converts a source-scaffold annotation into measured duplex toxicity. Native priority is operational, not a calibrated efficacy probability.

## Included evidence

- [Recorded KRAS14 assessment](results/case_studies/README.md): bounded actual inputs/native outputs, four small derived reference records, an earlier-job comparison and source hashes. The portable report reproduces the declared technical result without the original host or models.
- [Historical KRAS archive](benchmark/KRAS/README.md): the unchanged 85-file snapshot spanning design, candidate audit, ranking sensitivity, independent-data audit and literature comparison. Its source receipts remain historical and byte-identical.

The earlier full repeat generated 5,288 guides, assessed 100, obtained 81 operational passers, selected 20 nonoverlapping sites and retained 14 after the explicit perfect-outside-gene-match diagnostic. A later standalone Bench run assessed those exact 14. These observations are documented in the [central evidence list](../../research/sirna-designing-harness/references.md), not assumed test answers for new targets.

No scientific job is rerun to package or replay these records. The `benchmark/` name does not imply an independent measured efficacy benchmark. Mutation-selective work requires an exact mutation/reference and WT-sparing objective; no hypothetical mutant is included.

## Repository structure

```text
sirna-designing-harness/
  README.md
  ENVIRONMENT_SPEC.md
  STATUS.md
  config/                  # explicit gate policy, dependencies and output contracts
  tasks/                   # design, technical validation, audit and evaluation contracts
  tests/                   # executable positive/negative tests and sealing
  scripts/                 # technical checks, reports and bounded evidence importer
  skills/sirna-harness/     # original portable workflow/helpers and their MIT notice
  benchmark/KRAS/          # unchanged historical report/result archive
  results/
    case_studies/          # source-bound recorded KRAS14 evidence
    technical_validation_KRAS14/  # executed technical report replay
    history/               # prior project receipts retained before updates
```

Research lives in [research-notes.md](../../research/sirna-designing-harness/research-notes.md) and [references.md](../../research/sirna-designing-harness/references.md). See the [environment specification](ENVIRONMENT_SPEC.md), [status/evidence](STATUS.md) and [architecture decision](../../docs/decisions/sirna-designing-harness.md).

## Contribution and rights

Work is on `feat/sirna-technical-validation-environment`. Authenticated read-only issue lookup found no siRNA-titled issue at update time. No remote issue, PR, assignment, commit, push or merge was requested/performed; [local issue](tasks/ISSUE_DRAFT.md) and [PR](tasks/PR_DRAFT.md) drafts document the outstanding governance steps. Previous unauthenticated lookup claims are retained only in historical receipts where applicable, not asserted as the current state.

Repository-wide license selection remains pending. The original bundled helpers retain their separate MIT notice. No third-party scientific implementation, model weights, embeddings, transcriptome indices, raw papers, restricted datasets or credentials are distributed. Four small original-accession sequence views are explicitly derived reference inputs for the recorded replay, not a bundled screening database.
