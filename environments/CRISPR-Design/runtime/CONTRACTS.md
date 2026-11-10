# Runtime Contracts — backends, invocation, discipline

**Protocol version:** v0.1 (draft). The scoring runtime adapters are NOT yet implemented;
this document fixes the backend map (with the verified local evidence base), the
invocation discipline, and the liveness probe that gates every run. Adapters land in the
runtime phase and each adds its verified invocation here before first use.

## Backend map (local presence verified 2026-11-10; scoring liveness from the prior run)

| Component | Location | Status | Evidence |
| --- | --- | --- | --- |
| crisprDesign + crisprScore + crisprBase (Bioconductor) | `~/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38/reference_software/` (source) + `bootstrap/R-library` (installed) | **ACTIVE (prior-run evidence)** | KIF11 run 2026-11-05: guide enumeration + `getCRISPRaterScores`/`getLindelScores` executed end-to-end |
| Lindel model (crisprScoreData, ExperimentHub EH6128) | `runs/20261105T102927Z/lindel-runtime/` (dedicated python3.11 venv) | **ACTIVE (interface test PASS, 0.798)** | `model_verification.json` in that run dir |
| Bowtie 1.3.1 + GRCh38.p14 index | same run dir (`reference/`, `build_index.py`) | **ACTIVE** | checksum-verified primary-assembly FASTA; GENCODE 49; alignment smoke-tested at bootstrap |
| Transcript/CDS validation pipeline | `runs/20261105T102927Z/generate_and_score.R` + `prepare_annotation.py` | **ACTIVE (reusable recipe)** | spliced-exon sequence validation + CDS translation checks (stop-codon integrity) |
| Off-target policy v1.0 | `runs/20261105T102927Z/off_target_policy.yaml` | **ACTIVE (as prior-run convention)** | NGG · 20-nt spacer · 0–3 mismatches · both strands · intended-locus exclusion · bulges NOT_EVALUATED (disclosed cap) |
| CRISPRon / RS3 / Elevation / CRISPRitz / CRISPRme / PRIDICT2.0 / BEDICT2.0 / BE-dataHIVE | upstream repos (see [MODELS_AND_TOOLS](../MODELS_AND_TOOLS.md)) | **NOT_INSTALLED — runtime phase** | install paths + licenses documented in the curation registry |
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
