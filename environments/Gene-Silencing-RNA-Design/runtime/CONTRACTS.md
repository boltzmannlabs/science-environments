# Runtime Contracts — backends, invocation, discipline

This package's runtime scripts (`immune_scan.py`, `rank_by_requirements.py`, `explore_design.py`) are stdlib-plus-adapters and run under the siRNA-Bench venv with the biotools conda env on PATH. Scientific backends are **referenced, not redistributed**; every invocation uses absolute interpreter/binary paths.

## Backend map (verified 2026-11-04; 11/12 components pass, E4e defective)

| Component | Location | Invocation |
| --- | --- | --- |
| Generation (OligoFormer/RNA-FM, research-use) | `~/.sci/profiles/imran/workspace/oligoformer-integration` | `venv/bin/python run_local.py --fasta <abs RNA/DNA fa> --out <new dir> --top N` |
| Harness (siRNA-Bench) | `~/IMRAN/OCT26/siRNA-Bench` | `.venv/bin/python inference.py --candidates <csv> --transcript <RNA fa> --job-id <id>` |
| Bio-tools (ViennaRNA 2.7.2, bowtie2 2.5.5) | `~/IMRAN/OCT26/siRNA-Bench/external/envs/biotools/bin` | absolute binary paths; GENCODE v50 index pinned |
| Efficacy adapters | siRNA-Bench `src/sirna_bench/adapters` | RN.Ai (Apache-2.0) default; RNAiSpline restricted-tier |
| Context APIs (ToolUniverse 1.5.7, 2,719 tools) | `~/.sci/environments/science-tooluniverse/.../venv` | keys in `~/.tooluniverse/.env` only |
| RNAhybrid (E4e) | biotools env | **broken for SIREN conventions — NOT_RUN(broken-binary)** |

## Binding rules

1. Never cross-install between envs; never put conda `bin` ahead of the venv python on PATH (documented failure mode).
2. Battery inputs: real transcript FASTA in **RNA (AUGC)**; candidates CSV per `config/candidate.schema.json`; blank optional cells omitted as columns.
3. Fresh output directory per run; inputs read-only; originals never rewritten.
4. Thresholds come from `config/thresholds.v1.0.frozen.json` (or its stamped successor); briefs tighten only.
5. Explorer budgets are declared and reported; constraint adaptations are PROPOSED with diagnosis and `rel_gate_only` marks.
6. Score outputs carry provenance; third-party code/weights never ship.

## Skill binding

The same protocol ships as the `sirna-design-specialist` skill (installed at `~/.sci/profiles/imran/skills/science/sirna-design-specialist`, frozen `engine-v1.2.0_protocol-v1.2`). This environment reuses its scripts verbatim; protocol versions must match across both copies.
