# SARS-CoV-2 Mpro Hit Prioritisation — Scientific Report

**Task:** sars_cov2_mpro_hit_prioritisation
**Date:** 2026-11-13
**Tool:** Boltzmann `Vina_basic_docking` (AutoDock Vina, rigid-receptor)
**Job:** `6af701d99030bff4164443dc` — *Molecular Docking - SARS-CoV-2 Mpro (6LU7) - 20261113-122601Z - 92fadb*

---

## 1. Objective

Identify and rank promising compounds from two supplied libraries as candidate inhibitors of the SARS-CoV-2 main protease (Mpro, nsp5), using remdesivir and ritonavir as reference controls. Assess each candidate by (i) predicted binding score relative to the controls docked in the same run and (ii) engagement of the co-crystal-defined active site, including its catalytic residues and pocket contacts. Deliver a ranked top-20 shortlist and 3 final priority candidates with supporting evidence.

## 2. Inputs

| Item | File | Notes |
|---|---|---|
| Target structure | `inputs/targets/6LU7_crystal_complex.pdb` | 6LU7, Mpro + N3 co-crystal inhibitor |
| Target registry | `inputs/targets/target_registry.csv` | Confirms 6LU7 chain A; N3 bound control |
| Co-crystal inhibitor | `inputs/targets/6LU7_N3_ligand_native.pdb` | N3, native pose; defines active site (49 heavy atoms) |
| Approved-drug library | `inputs/library/approved_drugs.csv` + `.sdf` | 281 records (DB-prefixed) |
| Ritonavir-derivative library | `inputs/library/ritonavir_derivatives.csv` + `.sdf` | 117 records (MOL-prefixed) |
| Control: remdesivir | `inputs/controls/remdesivir.sdf` | Clinical reference |
| Control: ritonavir | `inputs/controls/ritonavir.sdf` | Known Mpro/HIV-Pr inhibitor |
| Control registry | `inputs/controls/control_registry.csv` | Maps N3 to 6LU7 chain C |

**Note on target location:** the task text places the N3 inhibitor in `inputs/controls/`, but the file actually resides in `inputs/targets/6LU7_N3_ligand_native.pdb`; `control_registry.csv` confirms this (row `N3,6LU7,C,...`). This is an input-location discrepancy, not a data error.

**Prepared receptor:** `prepared/6LU7_protein_chainA.pdb` — chain A protein only (2367 ATOM, 0 HETATM), ligand removed.

## 3. Approach and Settings

### 3.1 Workflow choice
AutoDock Vina basic (rigid-receptor) docking was selected because:
- It produces a **quantitative docking score** directly comparable to the controls docked in the same run (the task's primary criterion).
- The 6LU7 co-crystal structure provides a **well-defined active site**, so a rigid, defined-box search is appropriate and higher-throughput than blind docking.
- The task **excludes molecular dynamics**, so static docking is the highest-fidelity option available.
- DiffDock (blind) was not primary because it yields no Vina energy score and is less targeted for a known site.

### 3.2 Binding box
Centered on the **centroid of the N3 co-crystal inhibitor's 49 heavy atoms**: `(-10.729, 12.418, 68.816)`, radius `14.121 Å` = max ligand extent (12.121 Å) + 2.0 Å padding. Verified independently from the native PDB (matches `results/pocket_settings.json`).

### 3.3 Other settings
- Exhaustiveness: `16` (supported values 8/16/32; 16 balances pose quality and runtime for ~400 ligands).
- `upload_sdf=True` (poses retained for engagement analysis).
- Up to 10 poses per ligand; the **best (lowest-score) pose** is used.
- Ligand CSV: exactly `SMILES,NAMES` columns (Vina contract requirement), 399 rows = 397 candidates + 2 controls.

## 4. Execution and Coverage

The job was accepted and completed (runtime ~7 h 39 m). **All 399 submitted compounds returned a Vina score** (3876 pose rows).

| Metric | Count |
|---|---|
| Submitted | 399 |
| Docked with score | 399 |
| Library candidates | 397 |
| Reference controls | 2 |
| Excluded pre-submission | 1 (DB04421, empty SMILES — unparseable) |
| CSV-scored but missing SDF pose | 7 |

**Excluded:** DB04421 (approved_drugs) has an empty SMILES and was dropped before submission.

**SDF artifact gap:** 7 compounds have a valid CSV score but no pose file in the returned zip: DB00152, DB00188, DB00355, DB00462, DB00495, DB00558, DB03070. None are in the top-20; their scores remain valid.

**Duplicate identities** (identical SMILES, distinct identifiers; all docked independently, none in top-20):
- approved_drugs: DB00247=DB00589; DB00270=DB00343; DB01601=DB001601 (mixed casing)
- ritonavir_derivatives: MOL143=MOL146

## 5. Reference Controls (same run)

| Control | Vina score | Catalytic dyad | Oxyanion hole | Role |
|---|---|---|---|---|
| remdesivir | **-7.664** | CYS145 | GLY143 | Stronger binding control (primarily NS5 inhibitor) |
| ritonavir | **-7.239** | CYS145, HIS164 | GLY143 | Known Mpro inhibitor; specificity control (both catalytic residues) |

Ritonavir, the more relevant specificity control, contacts **both** catalytic residues — a useful benchmark for what "good" Mpro engagement looks like. Both controls set the bar: every top-20 candidate scores substantially better than either.

## 6. Results

### 6.1 Ranking method
1. **Primary:** Vina score (lower = stronger predicted binding), same run as controls.
2. **Specificity qualifier:** contact with a catalytic-dyad residue (CYS145/HIS164). A high score *without* catalytic contact is flagged lower-confidence.
3. **Secondary:** breadth of active-site engagement (distinct residues) and H-bond count.

The top-20 is the 20 lowest scores among candidates; the 3 priorities are selected within it by the composite of score + catalytic engagement + pocket breadth + H-bonds.

### 6.2 Top-20 shortlist

| # | ID | Library | Score | vs rem | vs ritonavir | Catalytic | Oxyanion | Res | H-bonds |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DB12457 | approved | -9.127 | -1.463 | -1.888 | none | GLY143 | 9 | 1 |
| 2 | **DB03363** ★ | approved | -9.030 | -1.366 | -1.791 | CYS145 | GLY143 | 13 | 5 |
| 3 | DB12318 | approved | -9.013 | -1.349 | -1.774 | CYS145 | GLY143 | 8 | 1 |
| 4 | DB14773 | approved | -8.951 | -1.287 | -1.712 | CYS145 | GLY143 | 7 | 0 |
| 5 | DB00696 | approved | -8.928 | -1.264 | -1.689 | none | GLY143 | 8 | 1 |
| 6 | DB13345 | approved | -8.824 | -1.160 | -1.585 | none | GLY143 | 10 | 0 |
| 7 | DB11878 | approved | -8.774 | -1.110 | -1.535 | CYS145 | — | 9 | 0 |
| 8 | DB000320 | approved | -8.569 | -0.905 | -1.330 | none | — | 9 | 1 |
| 9 | DB11913 | approved | -8.561 | -0.897 | -1.322 | CYS145 | GLY143 | 8 | 1 |
| 10 | **DB04023** ★ | approved | -8.521 | -0.857 | -1.282 | CYS145,HIS164 | GLY143 | 16 | 6 |
| 11 | DB06455 | approved | -8.497 | -0.833 | -1.258 | HIS164 | — | 9 | 1 |
| 12 | DB02498 | approved | -8.494 | -0.830 | -1.255 | CYS145 | — | 14 | 1 |
| 13 | DB14859 | approved | -8.421 | -0.757 | -1.182 | CYS145 | GLY143 | 9 | 2 |
| 14 | **DB00303** ★ | approved | -8.406 | -0.742 | -1.167 | CYS145 | GLY143 | 13 | 4 |
| 15 | DB00673 | approved | -8.386 | -0.722 | -1.147 | CYS145 | GLY143 | 11 | 1 |
| 16 | DB00402 | approved | -8.371 | -0.707 | -1.132 | CYS145 | GLY143 | 11 | 0 |
| 17 | DB00203 | approved | -8.369 | -0.705 | -1.130 | CYS145 | GLY143 | 11 | 0 |
| 18 | DB01232 | approved | -8.362 | -0.698 | -1.123 | none | — | 10 | 1 |
| 19 | DB06590 | approved | -8.348 | -0.684 | -1.109 | CYS145 | GLY143 | 14 | 3 |
| 20 | DB12760 | approved | -8.344 | -0.680 | -1.105 | none | GLY143 | 10 | 2 |

★ = final priority. All 20 outperform both controls. Six of the 20 (DB12457, DB00696, DB13345, DB000320, DB01232, DB12760) lack catalytic-dyad contact and are lower-confidence. The top-20 happens to be entirely from the approved-drug library; the best ritonavir-derivative score is MOL4 (-7.651), below the top-20 threshold.

### 6.3 Three final priority candidates

1. **DB03363** (score -9.030) — Highest Vina score among candidates with strong catalytic engagement: CYS145 contact, 5 H-bonds, 13 active-site residues, oxyanion (GLY143) contact. Best combination of affinity and engagement.
2. **DB04023** (score -8.521) — Most complete active-site engagement in the library: contacts **both** catalytic residues (CYS145+HIS164, mirroring the ritonavir control), 16 residues, 6 H-bonds. Highest-confidence engagement profile.
3. **DB00303** (score -8.406) — Robust balance: CYS145 contact, 4 H-bonds, 13 residues, GLY143 contact. Strong affinity with solid pocket engagement.

## 7. Ranking Rationale and Trade-offs

- **Score vs. specificity:** Pure score ranking puts DB12457 (-9.127, no catalytic contact) at #1. We retain it in the score-ranked top-20 (transparency) but do **not** promote it to a priority because it lacks catalytic-dyad engagement — a hallmark of true Mpro recognition. This is the central trade-off: Vina score is necessary but not sufficient; catalytic engagement is the specificity gate.
- **Why DB04023 over a higher-scorer for a priority slot:** DB04023 scores lower than DB03363/DB12318 but is the only top candidate contacting *both* catalytic residues with the most contacts and H-bonds. For inhibitor selection, complete catalytic engagement is weighted heavily.
- **Why DB00303 over DB12318 for the 3rd slot:** DB12318 has a higher score (-9.013) but weaker engagement (8 residues, 1 H-bond) vs DB00303 (13 residues, 4 H-bonds). Engagement is more predictive of Mpro inhibition than a marginal score difference.
- **Controls:** all priorities beat ritonavir (-7.239) by >1.1 kcal/mol and remdesivir (-7.664) by >0.7 kcal/mol on the same Vina scale.

## 8. Supporting Evidence and Artifacts

| Artifact | Path |
|---|---|
| Docking results (JSON) | `outputs/6af701d99030bff4164443dc_docking_results.json` |
| Docked poses (SDF zip) | `outputs/6af701d99030bff4164443dc_docking_sdf.zip` |
| Docking scores + interactions (CSV) | `outputs/6af701d99030bff4164443dc_docking_res.csv` |
| Per-compound analysis | `results/docking_analysis.json` |
| Binding-box settings | `results/pocket_settings.json` |
| Ranked top-20 + priorities | `ranked_candidates.csv` |
| This assessment | `assessment.json` |
| Receptor used | `prepared/6LU7_protein_chainA.pdb` |
| Ligand CSV submitted | `prepared/all_compounds.csv` |

All paths relative to `/home/boltzmann4/.sci/profiles/cov/workspace/sars_cov2_mpro`.

## 9. Workflow Decisions, Failures, Unresolved Work

- **Decision:** used the verified prior-prepared receptor and binding box (independently re-checked against N3) rather than regenerating; excluded DB04421 pre-submission.
- **Failure:** DB04421 unparseable (empty SMILES) — excluded.
- **Artifact gap:** 7 compounds scored in CSV but lack SDF pose files (not in top-20).
- **Unresolved (noted, not acted on):** 5 prior unknown-state submissions from earlier attempts remain in the receipt store with no doc_id (untrackable). They were not polled or retried; the current job is authoritative. No duplicate submission was made.
- **Not performed (per task):** molecular dynamics, ADMET/solubility, experimental binding.

## 10. Limitations and Uncertainty

- Vina scores are **computational estimates**, not measured affinities or experimental inhibition; controls are on the same Vina scale, not experimental.
- Rigid-receptor docking ignores receptor flexibility / induced fit.
- The box is N3-derived; alternate binding modes outside the box are missed.
- No ADMET, solubility, or off-target assessment.
- Docking score ≠ IC50/Ki; ranking is a prioritisation, not a potency measurement.
- SDF pose artifact incomplete for 7 compounds (scores still valid).
- Predictions should be confirmed experimentally (e.g., enzymatic Mpro inhibition assay) before any biological interpretation.

## 11. Completion Status

**Complete.** All 399 submitted compounds docked; top-20 shortlist and 3 priorities delivered with evidence, controls, and limitations. One input (DB04421) was excluded pre-submission; 7 pose artifacts are missing (scores valid). Deliverables: `ranked_candidates.csv`, `assessment.json`, `report.md`.
