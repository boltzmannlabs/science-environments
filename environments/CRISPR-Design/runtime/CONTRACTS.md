# Runtime Contracts — backends, invocation, discipline

**Evidence note.** The knockout stack below has executed end-to-end (Run1, 2026-11-10).
Active benchmark evidence is the [completed-only
registry](../benchmark/BENCHMARK_RUNS.md) (seven native-model/endpoint evaluations;
model benchmarks, not application validation); older mixed evidence is preserved in
[execution_history](../execution_history/before_completed_only_20261112T061830Z/README.md).

**Protocol version:** v0.1 (draft). First executed runtime: **Run1 (2026-11-10, task
002/KIF11)** — `run_002_knockout.R` (enumerate → E1/E2/E4/E6) + `run_002_specificity.R`
(Bowtie E3 + CFD + gates + R2/R3 ranking) + `tests/test_first_run.py` (run validation:
determinism, Lindel regression anchor, coordinate integrity, off-target controls).
**Artifact retention:** only stage-1 outputs are retained in the repo copy
(`results/002_knockout_gene_disruption/Run1_20261110/` — candidate pool, endpoint
scores, CRISPRon outputs, Bowtie queries, stage-1 record); the stage-2 outputs
(`ranked_shortlist.csv`, `off_target_sites.csv`, `gate_log.csv`, `run_record_stage2.json`)
were not retained, so the run-validation checks that depend on them fail on file
presence — rerun `run_002_specificity.R` into a fresh run directory to regenerate them.
Remaining adapters (CRISPRon, Elevation, variant-aware layer, PE/BE/Cas13 models) land in
later phases; each adds its verified invocation here before first use.

## Backend map (verified 2026-11-10; first executed run Run1)

| Component | Location | Status | Evidence |
| --- | --- | --- | --- |
| crisprDesign + crisprScore + crisprBase (Bioconductor) | `~/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38/reference_software/` (source) + `bootstrap/R-library` (installed; R 4.5.3, crisprScore **1.17.2**, crisprDesign 1.15.10) | **ACTIVE (Run1 stage-1 executed 2026-11-10)** | 8,421 windows enumerated, 227 coding-valid scored. **Correction:** the prior KIF11 run verified backends only (Lindel interface, Bowtie smoke, reference fetch) — its full pipeline never completed: it crashes at transcript-coverage because the retained annotation has no `exon_number` column; fixed in `run_002_knockout.R` (synthesized `exon_index`) |
| Native-R scorers (no python) | via crisprScore 1.17.2 | **ACTIVE (Run1)** | `getRuleSet1Scores` (30-nt [4][20][NGG][3]) · `getCRISPRaterScores` (20-nt) · `getCRISPRscanScores` (35-nt [6][20][NGG][6]; T7/IVT context endpoint) · `getCFDScores`/`getMITScores` (off-target pairs) |
| RuleSet3-Sequence (python) | `~/IMRAN/NOV26/cirspr-sci-env/03_environment/rs3-env` (conda; exact pins per crisprScore `rs3-env.yml`: py3.8, pandas 1.3.5, sklearn 1.0.2, biopython 1.78, lightgbm 3.2.1, sglearn 1.2.5) | **ACTIVE (Run1)** | `getRuleSet3Scores(seq30, tracrRNA=Hsu2013\|Chen2013, condaEnv=…)`. Native units are a scaled score (can be negative) — never renormalized. lightgbm ≥4 breaks the RS3-era model (`_n_classes` TypeError): pin 3.2.1 |
| Lindel model (crisprScoreData, ExperimentHub EH6128) | `runs/20261105T102927Z/lindel-runtime/` (dedicated python venv) | **ACTIVE (interface PASS 0.798; Run1 regression anchor)** | 65-nt input: 13 up + 20 spacer + 3 PAM + 29 down |
| Bowtie 1.3.1 + GRCh38.p14 index | binary `bootstrap/runtime/bin/bowtie`; **index REBUILT in Run1** (`results/002_knockout_gene_disruption/Run1_20261110/reference/GRCh38.bowtie.idx`) — the prior run's genome index was not retained | **ACTIVE (Run1 stage-2)** | ungapped ≤3 mm, both strands, intended-locus exclusion, NGG-PAM filter on hits |
| **Absent from pinned crisprScore 1.17.2** (namespace-verified 2026-11-10): Azimuth/RS2, DeepSpCas9, DeepCpf1 — no such exports. Exported but env-pending: `getDeepHFScores`, `getEnPAMGBScores` (prime editing), `getCasRxRF` (Cas13 RF) — need `deephf-env`-class python (3.8 + TF + Theano + gpy + viennarna; heavy) | — | **CORRECTED / NOT_INSTALLED (backlog)** | exports are exactly: CasRxRF, CFD, CRISPRater, CRISPRscan, DeepHF, EnPAMGB, Lindel, MIT, RuleSet1, RuleSet3 |
| Off-target policy v1.0 | `runs/20261105T102927Z/off_target_policy.yaml` | **ACTIVE (convention)** | NGG · 20-nt spacer · 0–3 mismatches · both strands · intended-locus exclusion · bulges NOT_EVALUATED (disclosed cap) |
| CRISPRon / Elevation / CRISPRitz / CRISPRme / PRIDICT2.0 / BEDICT2.0 / BE-dataHIVE | upstream repos (see [MODELS_AND_TOOLS](../MODELS_AND_TOOLS.md)) | **NOT_INSTALLED — next phases** | install paths + licenses documented in the curation registry |
| ViennaRNA (Cas13 structure context) | siRNA-Bench `external/envs/biotools` (conda) | ACTIVE (cross-environment reuse; verify per run) | siRNA environment liveness audit 2026-11-05 |

## Binding rules (all runs)

1. **Absolute paths**: never cross-install between envs; R sessions prepend
   `bootstrap/R-library` to `.libPaths()` (prior-run recipe); the Lindel python runtime
   is invoked by its absolute interpreter path, never from `PATH`.
2. **Fresh run directories**: one output directory per run; inputs read-only; originals
   never rewritten. Delivered designs land in `results/00N_<application>/<RunID>_<date>/`.
3. **Reference pinning**: GRCh38.p14 primary assembly + GENCODE 49 (both checksum-verified
   in the prior run); any bump invalidates the Bowtie index and is a new protocol event.
4. **DNA/RNA alphabets**: genome tasks use DNA (ACGT; PAM included); Cas13 tasks use RNA
   (ACGU) transcript references; orientation checked, never silently swapped.
5. **Off-target discipline**: intended locus excluded by verified coordinates; Bowtie-1
   is ungapped (no bulges) — the cap is stated in every off-target deliverable; variant-
   aware layers (CRISPRitz/CRISPRme) are required for tasks 003/004 and are
   NOT_IMPLEMENTED until installed.
6. **Thresholds**: from [thresholds.v0.1.draft.json](../config/thresholds.v0.1.draft.json)
   (copy-on-use, version-stamped); briefs tighten only. No gate freeze before the
   calibration runs listed there.
7. **Endpoints never averaged**; every score column carries model identity + version;
   `NOT_RUN(reason)` / `NOT_IMPLEMENTED` marks are deliverable content, not errors.
8. **Licenses**: CRISOT (CC BY-NC 2.0) and no-license repos (DeepBE, yachielab,
   Cas13design mirror) — research-internal use only, never redistributed; outputs carry
   provenance only. deepcrispr.info/PRIDICT web — research use.
9. **No safety claims**: off-target output is prioritization; therapeutic framing
   requires the E3c variant-aware layer and the assay-hierarchy statement.

## Liveness probe

`probe_backends.py` (stdlib) reports per-backend presence (ACTIVE / NOT_FOUND /
NOT_INSTALLED) from the map above and fails loudly when a required backend for a
requested stage is absent. It never fabricates scores; a missing backend means the
dependent stage runs as `NOT_RUN(backend-absent)`.

## Skill binding (future)

When the runtime phase lands, the same scripts ship as the environment's agent skill;
copies stay byte-identical and hash-verified (convention inherited from the siRNA
environment's three-copy sync rule).
