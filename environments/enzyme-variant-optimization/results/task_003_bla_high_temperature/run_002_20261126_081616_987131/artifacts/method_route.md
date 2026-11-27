# BLA high-temperature optimization — executable 8-stage method route (enzyme-method advice)

Parent executes all submissions. This document is a method decision, not a submitted job.
**MLDE `Insilico_Directed_Evolution` is explicitly excluded — do not submit it at any stage.**

Frozen construct: PDB 1BLI chain A, 483 aa (parent.fasta), engineered N190F/Q264S/N265Y retained.
PDB numbering == FASTA position (verified D231/E261/D328). Metals 3×Ca + 1×Na retained; no Cys.

## Editable mask (derived from 1BLI chain A structure)

Protected (27 positions, never edit): catalytic **D231,E261,D328**; metal ligands **N104,D161,A181,D183,D194,D200,I201,D202,D204,H235,G300,Y302,H406,D407,D430**; sugar-contact **W13,Y56,H105,W263,S264,H327,L335**; engineered identity **F190,Y265** (S264 already protected).

Editable mask (18 positions): **114,123,126,127,128,132,134,148,152,168,169,170,172,188,250,374,417,464**
- Domain B (104–206), flexible exposed surface: 114,123,126,127,128,132,134,148,152,168,169,170,172,188
- Domain A periphery: 250,374,417,464
- Criteria: relative SASA ≥0.40 (Domain B) / ≥0.50 (A periphery), CA B-factor ≥17/≥20, ≥8 Å from any ion, ≥10 Å from sugar-contact residues, ≥12–15 Å from catalytic atoms, ≥2 residues sequence-separated from protected sites, non-Gly/non-Pro. Computed with a Shrake–Rupley probe on `parent_chainA_with_ions.pdb` including all four ions; catalytic/sugar/metal sites verified buried or excluded.
- Zero-based `indices` for `Random_Controlled_Mutagenesis` (protected, 27): `[12,55,103,104,160,180,182,189,193,199,200,201,203,230,234,260,262,263,264,299,301,326,327,334,405,406,429]`
- Full complement (454 positions) remains theoretically mutable, but only the 18-position mask is authorized for this run.

## Budget ledger (parent enforces at each transition)

≤24 unique sequences including parent; ≤8 substitutions per variant; ≤2 revision rounds; ≤60 submissions total; ≤5 final candidates; ≥1 results-driven redesign round (Stage 7).
Plan: Round 0 ≤12 new sequences + parent = 13; Round 1 (Stage 7) ≤8 new = 21 cumulative; finalists ≤5. Reject any candidate exceeding 8 substitutions or touching a protected position.

## The 8 stages

### Stage 1 — Freeze inputs and compliance CSVs (no Boltzmann submission)
Prepare: `parent.fasta`; `parent_chainA_with_ions.pdb` (holo); protein-only PDB if a bare backbone is needed; protected/mask lists above.
Build reviewing copies with **exact headers**: `screen.csv` = `Seq_id,Sequences` (for Enzymes); `sol.csv` = `Sequences` (for Netsolp); `struct.csv` = `seq_id,sequences` (for Protein_Structure_Prediction); `cat.csv` = `Seq_id,Sequences,SMILES` (for Cat_Pred) with maltose SMILES from CHEMISTRY.md line 12; ZIP of one PDB per candidate (no nested ZIPs) for Thermal_MPNN.
Checks: parent length 483; all protected residues match parent; ions present in holo file; no lowercase header aliases.

### Stage 2 — Initial generation (Round 0)
**Primary generator:** `Random_Controlled_Mutagenesis`
experiment_data: `seq` (parent FASTA as a STRING, not list), `n_samples` (≤12), `file_format="csv"`, `indices` = 27 zero-based protected positions above, **`mutaions_per_epoch`** (API TYPO — correct spelling is rejected; set ≤8).
**Structure-conditioned generator:** `Ligand_MPNN`
experiment_data: `input_path` (uploaded holo PDB; requires backbone N/CA/C), `num_sequences` (≤8). No mask field — designs must be filtered post hoc.
Handoff: generation CSV/FASTA → Stage 3.
Transition checks: deduplicate; length 483; protected positions identical; ≤8 substitutions vs parent; cumulative ≤24 unique. Discard over-mutated or mask-violating Ligand_MPNN outputs.

### Stage 3 — Structure build
`Protein_Structure_Prediction`: `input_csv` = uploaded `struct.csv` (`seq_id,sequences`), optional `property_name="monomer_structure_prediction"`. Returns confidence table + PDB ZIP.
Optional holo/binding sanity: `Boltz2` with `Protein_Sequences:[<parent or variant FASTA>]`, `SMILES:[<maltose>]`, `DNA_Sequences:[]`, `RNA_Sequences:[]`. Note: Boltz2 schedules entities as **pairs**; Ca/Na cannot be supplied as ion atoms through this schema (ligands are SMILES only), so metal retention is verified against the parent PDB, not inferred from Boltz2.
Handoff: predicted PDBs → Stage 4 ZIP and Stages 5/6 structures.
Checks: one model per candidate; chain A present; coverage 483; pLDDT/confidence inspected; no truncated outputs.

### Stage 4 — PRIMARY STABILITY ENDPOINT
`Enzymes` with `property_name=["tmPred_enzymes"]` (primary endpoint, sequence-level predicted stability) using `Seq_id,Sequences` CSV; optionally add `"enzyme_solubility"` in the same array (secondary).
Orthogonal structure-based ddG: `Thermal_MPNN` with `zip_path` = candidate PDB ZIP (nested dirs OK, no nested ZIPs), `chain="A"` (omit → first chain), **omit `model_path`**.
Handoff: stability table → Stage 7 ranking and Stage 8 freeze.
Checks: confirm the returned CSV actually contains the requested `tmPred_enzymes` column (platform Success ≠ requested property evaluated); for ThermoMPNN confirm residue indexing and the deployed sign of `ddG_pred` before ranking — do **not** assume a favorable direction without inspecting worker metadata. These are computed scores, not measured Tm/half-life.

### Stage 5 — Solubility and catalytic-function proxy safeguards
`Netsolp`: `input_path` = uploaded `Sequences`-column CSV, `prediction_type="SU"` (uppercase; FASTA not supported).
`Cat_Pred`: `input_path` = `Seq_id,Sequences,SMILES` CSV (maltose SMILES); predicts kcat/Km/Ki for function retention. Alternative `kcat_km` uses `seq_id,Sequences,smiles` + `prediction_type="kcat"` (or `"km"`) + worker `job_name` label (omit → connector supplies experiment_name).
Checks: verify requested property columns are present; sustained activity proxy relative to parent; no catastrophic solubility drop.

### Stage 6 — Structural safeguards and quality
`Catalytic_Geometry`: `input_path` (PDB/ZIP), `reaction_template` (**uploaded UTF-8 .json**, not inline on live FastAPI), `template_binding` (**uploaded .json required by live FastAPI even though local worker treats it as optional**), optional `mapping_path` — **must be JSON; Node rejected CSV with HTTP 400**, `input_source="mutagenesis"` (or `ligandmpnn`), `execution_mode="measurement_only"`. Do not send legacy `rules_path`. Template must be a user-defined geometry-preservation check (D231/E261/D328 + metals), not a claimed experimental criterion.
`act_seek`: `input_path` (PDB/ZIP), `reference_path` (parent PDB), `active_sites="231_A,261_A,328_A"` (comma-separated `residue_chain` tokens; all must exist in reference).
`Mol_Probity`: `input_path` (structure or ZIP), `execution_mode="measurement_only"` — **omit `quality_thresholds` entirely** (do not send frontend all-zero defaults); use `validation` only with an explicit nonempty chosen-threshold object/file.
Checks: inspect `candidate_summary.csv`, `geometry_measurements.csv`, `invalid_candidates.csv`, `evidence_report.json`, `manifest.json`; distinguish measured/passed/rejected/invalid. MolProbity measures quality, not function. Historical MolProbity pending status is a disclosed uncertainty, not a completed result.

### Stage 7 — RESULTS-DRIVEN REVISION (Round 1; the required redesign round)
Use Stage 4–6 measured outputs (per-position ddG, geometry pass/fail, solubility, activity proxy) to re-weight the editable mask: drop positions with adverse ddG/geometry, retain beneficial substitutions, and regenerate the second round.
Generators for the revised round: `Ligand_MPNN` (`input_path` = best Round-0 holo model PDB, `num_sequences` ≤8) and/or `Function_Based_Enzyme_Generation` (`label="3.2.1.1"` alpha-amylase EC, `n_samples`, optional `file_format="csv"`). Function-Based is de novo and **does not preserve the parent scaffold** — treat output only as diversity, and gate it through the same ≤8-substitution, 483-length, protected-position and safeguard filters; exclude if it cannot be aligned to the parent numbering. MLDE remains excluded.
Then re-run Stages 3–6 on the revised candidates with identical settings.
Checks: revision count ≤2; new unique sequences keep cumulative ≤24; document the evidence that drove each re-mask decision.

### Stage 8 — Final common-protocol evaluation and freeze
Re-score all finalists (≤5) plus parent control through the **identical** Stage 4–6 protocol, same versions/thresholds/input formats: `Enzymes["tmPred_enzymes"]`, `Thermal_MPNN`, `Netsolp`, `Catalytic_Geometry`, `act_seek`, `Mol_Probity`. Selection: rank on primary stability endpoint (Stage 4), require all safeguards (Stages 5–6) satisfied; tie-break by orthogonal ThermoMPNN ddG and quality.
Freeze candidate list and selection-time evidence before independent review. Handoff: final evidence table + artifact paths to parent/evaluator.
Checks: property columns match requests; receipts/job IDs retained for every submission; counts verified from actual downloaded artifacts; partial/incompatible outputs are decision points, not passes.

## Cross-cutting contract pitfalls
- Job names are exact/case-sensitive: `Random_Controlled_Mutagenesis`, `Ligand_MPNN`, `Protein_Structure_Prediction`, `Boltz2`, `Enzymes`, `Thermal_MPNN`, `Netsolp`, `Catalytic_Geometry`, `act_seek`, `Mol_Probity`, `Cat_Pred`, `kcat_km`, `Function_Based_Enzyme_Generation`; excluded `Insilico_Directed_Evolution`.
- `experiment_name` omitted unless explicitly supplied; connector generates one — report the returned label. Never place runtime IDs/keys in `experiment_data`.
- Upload local files with `boltzmann_upload` using exact job name + `input_field` + reviewed `experiment_data`; substitute returned storage references. Accepted ≠ completed; retain job name + doc ID; poll only that job; never resubmit an ambiguous/pending job.
- Header rules are exact and case-sensitive per tool: `Seq_id,Sequences` (Enzymes), `Sequences` (Netsolp), `seq_id,sequences` (structure), `Seq_id,Sequences,SMILES` (Cat_Pred), `seq_id,Sequences,smiles` (kcat_km). Never silently rename columns.
- Sign conventions: verify ThermoMPNN `ddG_pred` and CatPred/kcat outputs against documented model direction before labeling favorable; stability-binding-ddg sign is contradictory across docs and is not used here.
