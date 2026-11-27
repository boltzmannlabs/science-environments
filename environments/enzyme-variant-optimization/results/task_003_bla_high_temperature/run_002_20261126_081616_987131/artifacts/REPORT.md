# task_003_bla_high_temperature — BLA high-temperature variant optimization

all 8 required stages executed; independent artifact-backed review completed (`evaluation.json`: `completed_with_limitations`). **No experimental improvement is claimed.**

## Parent and frozen protocol

Parent: PDB 1BLI chain A, 483 aa, engineered N190F/Q264S/N265Y (engineered identities retained); catalytic **D231 / E261 / D328** verified in PDB numbering; holo state **3 Ca²⁺ (A500/600/700) + 1 Na⁺ (A800)** retained; no Cys → no disulfides. WP_061576039.1 reconciled (signal peptide 1–29 + mature sequence with 5 substitutions vs 1BLI). Carbohydrate proxy: **maltose** (α-D-Glcp-(1→4)-D-Glcp), a defined starch fragment. Modeled condition: holo metal state identical for parent and candidates. Primary endpoint frozen before design: `tmPred_enzymes` (TemBERTureTm v1, °C, maximize); safeguards: ThermoMPNN ddG, Netsolp, CatPred (maltose), structure confidence, MolProbity, catalytic geometry. Mask: 18 surface positions; 27 protected positions; ≤8 substitutions; ≤24 unique sequences; ≤2 revision rounds; ≤60 submissions; ≤5 finalists; MLDE excluded. See `RUN_PLAN.json`, `inputs/CHEMISTRY.md`.

## Baseline and numerical comparison (common protocol, final re-score)

| ID | edits | tmPred (°C) | Δ vs parent (°C) | NetsolP sol. | CatPred kcat (s⁻¹, proxy) | pLDDT |
|---|---|---|---|---|---|---|
| parent | 0 | 51.934 | — | 0.575 | 101.3 | 98.5 |
| **BLA_R0A** | 8 | **53.356** | **+1.421** | 0.554 | 86.3 | 98.2 |
| **BLA_R0B** | 5 | **52.471** | **+0.536** | 0.556 | 87.1 | 98.5 |
| BLA_R0C | 3 | 51.866 | −0.069 | 0.557 | 91.7 | 98.4 |
| BLA_R1A | 8 | 51.711 | −0.223 | 0.567 | 91.6 | 98.6 |
| BLA_R1B | 5 | 51.710 | −0.224 | 0.575 | 98.1 | 98.6 |
| BLA_R1C | 3 | 51.698 | −0.236 | 0.573 | 95.3 | 98.6 |

Helper result (`evaluation_helper_output.json`): **scored**; 2/5 selected numerically improved; mean signed improvement +0.288 °C. Critically, replicate standard deviations are ~6 °C and the native tool states it is "not calibrated for small mutant ΔTm" — **all deltas are within predictor noise**; they are numerical changes only, not significant or experimental gains.

## Results-driven optimization

Round 0 used the best per-position ddG from a native ThermoMPNN scan; it produced a tmPred lead (R0A) but proline-rich substitutions reduced solubility and kcat. Round 1 (required revision) used the second-best per-position substitutions (no Pro): solubility recovered (0.567–0.575) and kcat improved (up to 98.1 s⁻¹), but the tmPred gain disappeared — a transparent trade-off. Combined variants were scored directly; no assumption of additivity.

## Generation recovery (honest disclosure)

Three native generators failed their task-specific constraints: RCM (347–452 substitutions, variable length), Ligand_MPNN (~185–208 substitutions, length 481, two catalytic edits), AntiBMPNN (terminal validation: zero heavy/VHH domains). Under ENVIRONMENT_SPEC §32, variants were generated in Python by applying the **native Thermal_MPNN per-position edit list** (job `6b07f38d…`) with a deterministic rule frozen in `RUN_PLAN.json` before generation. The independent evaluator re-executed the rule and verified exact reproduction of R0A/R1A edits; provenance judged **acceptable**.

## Structural / functional safeguards

- All 7 structures: 483 residues, sequence matches FASTA, catalytic D/E/D intact, pLDDT 98.2–98.6, pTM 0.957–0.958 (`structure_evidence/sequence_verification.json`).
- Catalytic triad distances (D231–E261 ~6.3–6.5 Å) measured descriptively, no gross disruption (`catalytic_geometry_summary.json`). **Metal-coordination checks invalid for candidate AF models (ion-free)**; ion retention verified against parent holo PDB, not candidate models.
- MolProbity measured all candidates; early R0A/R0B have elevated clashscores (20.6/18.2) vs parent 5.7; R1B/R0C show high bond-outlier counts in AF models. Quality ≠ function.
- **Unresolved:** act_seek submission returned an ambiguous server error (`freezedCredits=NaN`, no job ID; not resubmitted); Boltz2 parent–maltose complex failed on a backend `FileNotFoundError`; no experimental activity or Tm data exist.

## Verification and accounting

Sealed `selection.csv` SHA-256 matches `selection_seal.json`; ranks 1–5 contiguous; parent excluded; no duplicates. Independent evaluator verified edit/mask compliance, provenance, hashes, helper arithmetic and all native outputs. 21 submission attempts recorded in `jobs.json`; specialist calls (method, round-0 interpretation, recovery, evaluator) recorded in `usage.json`; cost reported as returned by native billing (unknown for failed jobs).

## Conclusion

A complete, evidence-backed in-silico workflow produced six eligible variants and a sealed five-candidate shortlist. Two candidates show small positive predicted-Tm changes that are **within model noise**; the revision round reveals a stability/function trade-off. No claim of improved high-temperature catalysis, Tm, half-life, or experimental performance is supported. Next step requires wet-lab validation (e.g. differential scanning fluorimetry and starch-hydrolysis assays with Ca²⁺) before any performance claim.
