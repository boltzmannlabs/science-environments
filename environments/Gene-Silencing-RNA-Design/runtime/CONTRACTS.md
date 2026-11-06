# Runtime Contracts — backends, invocation, discipline

This package's runtime scripts (`immune_scan.py`, `rank_by_requirements.py`, `explore_design.py`) are stdlib-plus-adapters and run under the siRNA-Bench venv with the biotools conda env on PATH. Scientific backends are **referenced, not redistributed**; every invocation uses absolute interpreter/binary paths.

**Protocol version:** v1.2.1 (scope-explicit E4a). All three copies — this environment, the workspace skill (`~/IMRAN/NOV26/siRNA-Design-Task-Specific/agent_skill/sirna-design-specialist/scripts/`), and the SCI install (`~/.sci/profiles/imran/skills/science/sirna-design-specialist/scripts/`) — must remain byte-identical (verified by hash).

## Backend map (verified 2026-11-05 liveness audit; 11/12 components pass, E4e defective)

| Component | Location | Invocation | Verified by |
| --- | --- | --- | --- |
| Generation (OligoFormer/RNA-FM, research-use) | `~/.sci/profiles/imran/workspace/oligoformer-integration` | `venv/bin/python run_local.py --fasta <abs fa> --out <new dir> --top N` | mutation test (232/283 windows re-scored); clean label-tracking AUC 0.58–0.76 |
| Harness (siRNA-Bench) | `~/IMRAN/OCT26/siRNA-Bench` | `.venv/bin/python inference.py --candidates <csv> --transcript <RNA fa> --job-id <id>` | cross-path exact agreement (50/50 guides, duplex/viability exact, POTS ≤0.005) |
| Bio-tools (ViennaRNA 2.7.2, bowtie2 2.5.5) | `~/IMRAN/OCT26/siRNA-Bench/external/envs/biotools/bin` | absolute binary paths; GENCODE v50 index pinned | positive control (TTR guide → 20 TTR transcripts @0 mm); negative control (sense strand → 0) |
| Efficacy adapters | siRNA-Bench `src/sirna_bench/adapters` | RN.Ai (Apache-2.0) default; RNAiSpline restricted-tier | top/bottom-20 measured separation: RN.Ai AUC 0.810; RNAiSpline 0.769 (narrow range, documented) |
| Context APIs (ToolUniverse 1.5.7, 2,719 tools) | `~/.sci/environments/science-tooluniverse/.../venv` | keys in `~/.tooluniverse/.env` only | live Ensembl round-trip: TTR cDNA identical to local GENCODE transcript |
| RNAhybrid (E4e) | biotools env | **broken for SIREN conventions — NOT_RUN(broken-binary)** | errors visibly (never silently fake); quarantined (backlog #4) |

### ToolUniverse API notes (verified 2026-11-05)

- Correct tool name for transcript sequence retrieval: `ensembl_get_sequence` (NOT `ensembl_sequence_tool`)
- Ensembl REST requires **versionless** IDs (`ENST00000237014`, not `ENST00000237014.8`)
- Other verified tools: `ensembl_lookup_gene`, `ensembl_get_variants`, `ensembl_get_variation`

## Binding rules (all runs)

1. **Absolute paths**: never cross-install between envs; never put conda `bin` ahead of the venv python on PATH (documented failure mode).
2. **RNA alphabet**: battery inputs require transcript FASTA in **RNA (AUGC)**; candidates CSV per `config/candidate.schema.json`; blank optional cells omitted as columns (NaN rejects).
3. **E4a scope-explicit (v1.2.1)**: always pass `--target-gene` to `explore_design.py` and `target_gene` to `full_length_hits()` calls. **Warning fires if omitted** — same-gene isoform hits will silently count as off-targets (the 2026-11-05 scoping artifact). The gene symbol must match GENCODE exactly (e.g., `HIF1A`, not `HIF1AN`).
4. **Gene-symbol correctness**: verify against GENCODE/RefSeq before writing candidates CSVs; a silently-unmatched symbol disables gene-scoping without any error.
5. **Fresh run directories**: one output directory per run; inputs read-only; originals never rewritten.
6. **Thresholds**: from `config/thresholds.v1.0.frozen.json` (or its stamped successor); briefs tighten only — never loosen.
7. **Explorer discipline**: budgets declared and reported; constraint adaptations are PROPOSED with diagnosis and `rel_gate_only` marks; selection never consults measured/published outcomes.
8. **Provenance**: score outputs carry tool versions + hashes; third-party code/weights never ship.
9. **Results convention**: delivered designs land in `results/00N_<application>/<RunID>_<date>/`; Run IDs match `benchmark/BENCHMARK_RUNS.md`.

## Skill binding and cross-copy sync

The same protocol ships as the `sirna-design-specialist` skill, frozen at `engine-v1.2.0_protocol-v1.2` + the v1.2.1 scope-explicit patch. Three copies must remain identical:

| Copy | Location | Sync mechanism |
| --- | --- | --- |
| This environment | `runtime/*.py` | source of truth for the env package |
| Workspace skill | `~/IMRAN/NOV26/siRNA-Design-Task-Specific/agent_skill/sirna-design-specialist/scripts/` | source of truth for development |
| SCI install | `~/.sci/profiles/imran/skills/science/sirna-design-specialist/scripts/` | deployed copy used by `agent-sci` |

**Sync rule:** after any script change, `cp` the workspace version to all three locations, then verify with `md5sum` across copies. The validator's `runtime_import` check exercises all three scripts but does not check cross-copy identity — do that manually or via the source workspace's `08_e2e_validation/run_checks.py`.
