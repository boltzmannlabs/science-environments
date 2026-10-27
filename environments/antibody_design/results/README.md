# Antibody Design Result Bundle

This environment evaluates computational monoclonal-antibody design runs. It does not execute wet-lab assays. A run may cite historical or externally generated assay records, but those must be identified as such and bound to the exact candidate and target construct.

## Bundle layout

```text
08_results/
├── designed_sequences.fasta
├── metrics.json
├── shortlist.csv
├── report.md
├── assay_records/                 # optional, externally sourced records
└── evidence/                      # native computational outputs
```

The DENV-2/DV87.1 profile uses `config/metrics.schema.json`. Target-agnostic monoclonal requests use `config/generic-antibody-metrics.schema.json`. Both preserve paired heavy/light chains, sequence-bound evidence, explicit missing values, reproducible ordering, and computational resource accounting.

## Paired sequence output

The FASTA contains exactly two records for each shortlisted candidate, in shortlist order:

```text
>candidate_id|H
HEAVY_CHAIN_SEQUENCE
>candidate_id|L
LIGHT_CHAIN_SEQUENCE
```

Only candidates that pass every required protocol rule belong in the FASTA. The reference is assessed alongside candidates for reference-guided tasks but never appears as a designed candidate. An empty FASTA is valid only for a completed, justified zero-candidate result.

## Metrics and evidence

`metrics.json` records request/protocol hashes, task, design mode, sequence scope, stop reason, missing requirements, candidate identities, paired-sequence hashes, every rule result, exclusions, shortlist, resource use, and provenance. Every resolved numeric rule includes units, scale, method ID, scope, sequence hash, and accessible evidence artifacts. Use `null` with `UNRESOLVED` and a reason when required evidence is missing.

Generic computational runs also record provider/model revision, Agent-Scientist harness revision, task/system prompt hashes, enabled-tools manifest hash, execution backend, environment digest, isolated workspace ID, and fixed seed. Report a score as a model-plus-harness-plus-tools result, not as a model-only outcome.

Optional files in `assay_records/` follow `config/mab-assay-record.schema.json`. They preserve candidate and target hashes, assay type/endpoint, measured value or censoring state, replicate count, conditions, controls, source, and raw-data artifacts. The bundle validator confirms identity and provenance; it does not reproduce the assay.

Predicted binding energy, interface confidence, ELISA EC50, measured Kd, functional potency, and neutralization are separate endpoints. Computational passes do not establish experimental binding, Fc function, product developability, immunogenicity, clinical efficacy, or safety.

## Statuses

- `NEEDS_INPUT`: a required target, reference, construct, or input artifact is missing or inconsistent.
- `PROTOCOL_REQUIRED`: no qualified protocol or version-compatible method lock is available.
- `BLOCKED`: a declared computational dependency or infrastructure requirement failed.
- `QUALIFIED`: the requested number of unique candidates passed all required computational rules.
- `PARTIAL`: one or more, but fewer than requested, candidates passed.
- `NO_QUALIFYING_DESIGNS`: all assessed candidates have a verified required failure.
- `INCOMPLETE`: unresolved work prevents a completed positive or negative result.
- `CANCELLED`: execution stopped by cancellation; preserve the evidence already produced.

Preflight bundles contain `metrics.json` only and may not claim candidate or assay results. Completed or interrupted computational runs include the full bundle, exact stop reason, and actual resource use. Missing resource measurements cannot be replaced by zero.
