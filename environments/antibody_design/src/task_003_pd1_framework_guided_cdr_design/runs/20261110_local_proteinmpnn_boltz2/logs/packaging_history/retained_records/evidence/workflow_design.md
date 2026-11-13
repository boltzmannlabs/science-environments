# Task 003 — PD-1 Framework-Guided CDR Design: Boltzmann Workflow Design & Selection

Date: 2026-11-10
Task: `task_003_pd1_framework_guided_cdr_design`
Source study: De novo design of epitope-specific antibodies via a structure-driven
computational workflow, Nat. Commun. (2025/2026), DOI 10.1038/s41467-025-67361-9,
PMC12815924 ("tFold system").

## 1. Target, framework, and input state

### Target (verified before design)
- **Protein:** human PD-1 (PDCD1), extracellular IgV domain.
- **Sequence:** 106 aa, taken from PDB 4ZQK chain B (deposited construct):
  `NPPTFSPALLVVTEGDNATFTCSFSNTSESFVLNWYRMSPSNQTDKLAAFPESRFRVTQLPNGRDFHMSVVRARRNDSGTYLCGAISLAPKAQIKESLRAELRVTE`
- **Structure origin:** PDB 4ZQK ("Structure of the complex of human programmed death-1
  (PD-1) and its ligand PD-L1"), chain B, residues 33–146. The D/E-loop segment
  `DRSQPGQDS` present in the canonical UniProt sequence (Q15116, legacy ID; Q5W5W0 is the
  current entry) is disordered/absent in the crystal construct — this is the construct the
  study's structural analysis (Fig. 2c) used.
- **Mature-protein mapping:** human PD-1 precursor IgV domain; deposited chain B starts at
  PD-1 residue 33 (construct numbering) and ends at 146.
- **Intended epitope:** the PD-1 ligand-binding surface (PD-L1 contact face), computed
  from native 4ZQK as chain-B residues with any heavy atom within 6.0 Å of a PD-L1
  (chain A) heavy atom. This defines competition-compatible binding; structural overlap
  supports a competition hypothesis, not demonstrated functional blockade.
- **Reference controls:** anti-PD-1-H965 (tFold final design, comparison only — NOT a
  design input) and D12 (published anti-PD-1, sequence comparator only).

### Framework (verified from study Table 1, Chothia numbering)
| Region | Sequence | Length |
|---|---|---|
| FR-H1 | EVQLLESGGGLVQPGGSLRLSCAAS | 25 |
| FR-H2 | AMSWVRQAPGKGLEWVSAI | 19 |
| FR-H3 | TYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK | 41 |
| FR-H4 (IGHJ4) | WGQGTLVTVSS | 11 |
| FR-L1 | DIQMTQSPSTLSASVGDRVTITC | 23 |
| FR-L2 | WYQQKPGKAPKLLIY | 15 |
| FR-L3 | GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC | 32 |
| FR-L4 (IGKJ1) | FGQGTKVEIK | 10 |

Editable CDR regions and allowed lengths (declared, from the same Table 1):
CDR-H1 = 7, CDR-H2 = 6, CDR-H3 = 7–18, CDR-L1 = 11, CDR-L2 = 7, CDR-L3 = 9–11.
J genes fixed: IGHJ4/IGKJ1. All framework residues are protected (zero-substitution gate).

### Stage-0 structural conditioning (shared by all workflows)
No experimental anti-PD-1 antibody complex on this framework exists. The only
study-provided structural context for the framework + PD-1 pair is the tFold reference
design pose: the Boltz2-predicted H965(VH)+H965(VL)+PD-1 complex (artifact
`evidence/reference/task003_h965_pd1.pdb`; H965 VH/VL sequences verified to carry the
exact Table-1 framework). From it we build:
- **framework.pdb** — VH (chain A) and VL (chain B) framework atoms only (CDR residues
  removed; the exact Table-1 FR sequences remain), in the reference frame.
- **pd1_target.pdb** — PD-1 (chain B, original 4ZQK resSeq 33–146) in the same frame.
Disclosure: the conditioning pose derives from the tFold reference design; no H965 CDR
sequence or identity is carried into any candidate. H965 remains a comparison control
evaluated with the identical Boltz2 protocol.

## 2. Boltzmann tool inventory (relevant jobs, active)

| Job | Module | Role | Key inputs |
|---|---|---|---|
| `rfdiffusion_proteinmpnn` (RF-Antibody) | target-aware antibody | Paired CDR backbone + sequence design vs target, one job | antibody framework PDB, antigen PDB, num_sequences, antibody_type |
| `epitope_abgen` (Epitope AbGen) | target-aware antibody | Epitope-conditioned CDR backbones (PDB branch; `.pt` branch execution-blocked) | antigen PDB, antibody framework PDB, mask_cdrs, chain IDs, epitope_residues, samples/seed/max_tokens |
| `agcdr_diff` (Antibody RFD3) | target-aware antibody | CDR backbone diffusion, framework+antigen preserved; does NOT dock | pre-positioned antibody PDB + antigen PDB, num_samples, num_steps |
| `AntiBMPNN` | target-aware antibody | Sequence-only redesign at declared positions on a supplied backbone | PDB/ZIP, chains_to_design, residue_positions_to_design, generation_count |
| `Antibody_Backbone_to_Sequence_Generation` | antibody generation | Backbone → sequence (mode H / L; chain A in every PDB) | ZIP of backbone PDBs, mode |
| `boltzgen` | antibody generation | De novo protein/antibody generation with ligand/structure constraints | general generation — framework-fixed paired design not expressible in its field set (flagged non-executable for this task) |
| `Random_Antibody_Generation`, `CDR_Generator`, `igdesign` | antibody generation | Target-free / complex-conditioned generation | igdesign requires an antibody–antigen complex as input (would redesign a known binder, not the framework template) — not applicable |
| `Boltz2` | structure prediction | Paired complex prediction with confidence + affinity | Protein_Sequences array (entities scheduled as pairs) |
| `ipsae-protein` (ipSAE) | structure prediction | Interface confidence from Boltz2 bundle (PAE+confidence+distance) | ZIP of structures + matching confidence/PAE, model_type=boltz2 |
| `Antibody_Prediction` | property prediction | Thermal stability (ProtBERT/ESM), solubility (ESM), CDR prediction (imgt) | CSV Heavy_chain/Light_chain, property_name[], scheme |
| `stability-binding-ddg` | property prediction | Stability-binding ΔΔG on declared CDR ranges | two-chain PDB (A/B), mutations ranges |
| `Antibody_Numbering` | toolbox | IMGT/Kabat/Chothia numbering | CSV Heavy_chain/Light_chain, scheme |
| `tm_align` | toolbox | TM-score/RMSD vs reference | design PDB/ZIP + one reference PDB |
| `Mol_Probity` | toolbox | Structural quality (measurement_only) | structure/ZIP |

## 3. Workflows

### W1 — RF-Antibody: target-aware paired CDR backbone + sequence (PRIMARY)
Stage graph:
1. [local] Stage 0: framework.pdb + pd1_target.pdb (above).
2. `rfdiffusion_proteinmpnn` (antibody_type=antibody, num_sequences=24): RFdiffusion
   antibody-finetuned CDR backbones against PD-1 + ProteinMPNN CDR-only sequences,
   paired VH/VL in one job.
3. [local] Validity gate: FR identity (zero substitutions), Chothia CDR split, declared
   length ranges, paired-domain integrity, Cys/developability flags, dedup.
4. `Boltz2` on top survivors (VH, VL, PD-1 entities → pair predictions) + `ipsae-protein`.
5. `Antibody_Prediction` (Thermal_Stability_Protbert, Thermal_Stability_ESM,
   Solubility_ESM, CDR_Prediction/imgt).
6. `stability-binding-ddg` on the final shortlist (raw values only).
7. Rank and shortlist (hard gates → orthogonal evidence tiers).
Strengths: single job yields paired backbones AND sequences (chain pairing preserved by
construction — matches the task's "paired heavy/light variable domains" requirement);
antibody-finetuned model; directly implements the tFold paradigm (fixed FR, CDR
generation vs target). Limitations: CDR lengths are model-sampled (post-filter to the
declared ranges); no explicit epitope-residue conditioning (target-conditioned only).

### W2 — Epitope AbGen: explicit ligand-binding epitope conditioning (COMPARISON)
Stage graph:
1. [local] Same Stage-0 inputs.
2. `epitope_abgen` (PDB-input branch; `input_path` .pt branch is execution-blocked per
   contract): mask_cdrs=all_cdrs, heavy_chain_id=A, light_chain_id=B,
   antigen_chain_ids=["B"], epitope_residues = the computed ligand-binding list,
   samples_per_task=8, seed=2026, max_tokens=384 → CDR backbones.
3. [local] Rename backbone chains so the chain to sequence is chain A in every PDB.
4. `Antibody_Backbone_to_Sequence_Generation` mode=H and mode=L (separate jobs).
5–7. Same downstream ladder as W1.
Strengths: explicitly conditions CDR geometry on the declared PD-1 ligand-binding
epitope — the closest match to the task's "epitope-directed CDR design compatible with
the PD-1 ligand-binding surface." Limitations: two-step (backbones, then sequencing);
paired-domain identity is not guaranteed by construction (VH/VL sequenced independently
on jointly sampled backbones — pairing check required); backbone-only output from stage 2.

### W3 — AgCDR-Diff: CDR backbone diffusion (EVALUATED, NOT SELECTED)
`agcdr_diff` on the pre-positioned framework + antigen (num_samples=8, num_steps=50),
then backbone-to-sequence. It does not dock the two inputs (they must already share a
frame — satisfied by Stage 0) and its added value over W1/W2 is incremental (same
backbone-diffusion family as RF-Antibody's backbone stage, with no paired-sequencing
convenience). Lower priority; would be selected only if W1/W2 backbones fail QC.

### W4 — AntiBMPNN: sequence-only refinement (CONDITIONAL REFINEMENT)
On top W1/W2 backbones, `AntiBMPNN` with chains_to_design=[A,B] and
residue_positions_to_design = the six CDR ranges (1-based), generation_count=10, to
expand sequence diversity per backbone. Not a stand-alone workflow for this input state
(it requires a CDR backbone, which the framework template lacks) — executed only as a
refinement if warranted by the design outputs.

### W5 — boltzgen / Random_Antibody_Generation / CDR_Generator / igdesign (FLAGGED)
- `boltzgen`: general de novo generation; the antibody protocol is not available through
  its field set alone (flagged non-executable for a framework-fixed paired design).
- `Random_Antibody_Generation` / `CDR_Generator`: target-free — cannot satisfy
  "epitope-directed ... against PD-1"; excluded.
- `igdesign`: conditions on an existing antibody–antigen complex — would be a redesign
  of a known binder (H965/D12 are controls, not inputs); excluded.

## 4. Decision matrix and selection

| Criterion | W1 RF-Antibody | W2 Epitope AbGen | W3 AgCDR-Diff | W4 AntiBMPNN |
|---|---|---|---|---|
| Framework-fixed, paired output | yes (one job) | partial (pairing check needed) | partial (backbones only) | no (needs backbones) |
| Epitope-directed | target-conditioned | explicit epitope residues | target-conditioned | backbone-conditioned |
| Sequences in same job | yes | no (extra step) | no | yes |
| Input compatibility (no CDR backbones in template) | yes | yes | needs positioned input | no |
| Executable per contract | yes | yes (PDB branch) | yes | yes (with backbones) |
| Expected performance | high (ab-finetuned, paired) | high for epitope overlap | medium (redundant with W1 backbone stage) | refinement only |

**Selected: W1 (primary) + W2 (comparison), pooled at one ranking step** — the
portfolio strategy of the fixed-framework workflow. W1 is the best single workflow
(paired output in one job, antibody-finetuned, directly implements the tFold
fixed-FR/CDR-generation paradigm); W2 is the best available match to the explicit
ligand-binding-epitope requirement and provides an independent backbone family for
comparison. W3 is a documented fallback; W4 is conditional refinement.

## 5. Shared evaluation ladder (all candidates)
1. Sequence validity: exact FR identity, CDR lengths in declared ranges, paired-domain
   integrity, Cys and developability flags, dedup (sequence identity per CDR and
   whole-domain).
2. `Antibody_Numbering` (imgt) for CDR annotation of survivors.
3. `Boltz2` (VH, VL, PD-1) → ipTM, pLDDT, pDE, per-pair ipTM; `ipsae-protein` on
   matching bundles.
4. `Antibody_Prediction`: thermal stability (ProtBERT, ESM), solubility (ESM),
   CDR_Prediction (imgt).
5. `stability-binding-ddg` on the shortlist (raw values; sign convention unresolved —
   ranking feature, never a hard gate).
6. Open-source validation (local GPU, sequential): Boltz-2 v2.2.1 re-prediction,
   Prodigy affinity estimate, TM-score framework preservation, interface contacts /
   clashes / buried area.
7. Hard gates before ranking: framework zero-substitution, lengths in range, foldable
   domains, acceptable interface confidence, epitope contact retained. Zero survivors is
   a valid outcome (export raw pool, empty shortlist).
8. Experimental validation is ground truth; no computational score is described as
   measured binding or neutralization.

## 6. Benchmark comparison plan
- **Candidate-level (new evidence):** Boltz2 confidence and ipSAE for each candidate vs
  the H965 reference (identical protocol, artifact
  `evidence/reference/task003_h965_pd1_confidence.json`), epitope contact analysis vs
  the native 4ZQK ligand-binding surface, sequence distance to H965 and D12.
- **Published aggregate metrics (scope-limited):** PD-1 virtual-screening AUROC 0.76
  (745-antibody panel, 27 positives), top-1% enrichment 7.41, design-campaign
  discrimination AUROC 0.95, epitope-informed CDR-H3 AAR 0.317 (SAbDab-22-DesignAb
  aggregate). These require the original labelled panel / dataset, which are not
  provided with the task; a single candidate cannot yield an AUROC or enrichment factor.
  They are reported as NOT REPRODUCIBLE with available inputs — not fabricated, and never
  assigned to an individual candidate.
- **Cross-workflow:** W1 vs W2 candidate families on the same downstream ladder; plus the
  previously executed local ProteinMPNN CDR-H3-only result (pair-ipTM 0.28–0.49) as a
  third comparison point.
- **Open-source vs Boltzmann:** local Boltz-2 vs platform Boltz2 confidence correlation;
  Prodigy ΔG vs platform Boltz2 affinity estimates.
