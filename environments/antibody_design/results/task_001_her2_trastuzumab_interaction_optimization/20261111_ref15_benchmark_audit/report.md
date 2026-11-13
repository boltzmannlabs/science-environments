# Task 001 — HER2/trastuzumab benchmark audit and independent validation

Task: `task_001_her2_trastuzumab_interaction_optimization`  
Audit run: `20261111_ref15_benchmark_audit`  
Design source run: `20261110_antibmpnn_her2_prodigy`

[Execution record](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261111_ref15_benchmark_audit/execution.md) · [Provenance](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261111_ref15_benchmark_audit/provenance.json)

## Scope and verdict

This report concerns only the current HER2/trastuzumab task and its five existing shortlisted pairs: AB_04, AB_05, AB_08, AB_13 and AB_20. No other task was evaluated, and no new antibody sequences were generated.

**None of the five candidates can currently be declared to outperform, match, or fall below the published REF15 benchmark. The exact REF15 evaluation remains uncomputed.** The independent work completed here supplies real antibody models, local CDR conformation/uncertainty, interface/geometry evidence and an explicitly exploratory Prodigy cross-check. It also invalidates the earlier claim that an approximate reconstructed structure demonstrated improved binding.

## 1. Correct benchmark and attributable controls

The corresponding local benchmark is `benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md`. Its source is Sampaio et al., *Ab-SELDON: Leveraging Diversity Data for an Efficient Automated Computational Pipeline for Antibody Design*, JCIM, 2026, DOI **10.1021/acs.jcim.5c01924**. Supporting methods: DOI **10.1021/acs.jcim.5c01924.s001**. Released HER2 data: DOI **10.5281/zenodo.15803983**.

The complete 4,098,846,633-byte optimization archive was retrieved. Its MD5, `f699da97a28fc35a7e82c0d9128712a2`, matches Zenodo metadata. The SI PDF MD5, `3da64f51a13e30467c9a7e6544abeb85`, matches the article's supplementary-file metadata. The archive's actual paper-v6.2 scripts and configurations were retained; the newer GitHub implementation was not substituted for the paper version.

The correct HER2 experiment is **16 optimization runs: eight diversity-guided and eight random-arm runs**. All initial/final values were independently parsed from the specified per-run energy logs, not copied from the older package and not taken from the discrepant `aligned_energies.csv` table. This verifies source transcription; it does not recompute Rosetta energies.

| Source endpoint | Starting REF15, REU | Final REF15, REU | Final minus starting, REU |
|---|---:|---:|---:|
| Diversity run 6, best diversity endpoint | -49.6996131409 | -94.8662817755 | -45.1666686346 |
| Random run 4, best random endpoint | -48.9576164097 | -92.6946566782 | -43.7370402685 |

The source endpoint names are `FINAL_001_1n8z-frk-reduced_div6_000024.anarci` and `FINAL_001_1n8z-frk-reduced_ran4_000015.anarci`. Initial energies are run-specific, not a universal trastuzumab baseline. All 16 endpoint records are in [published_endpoints.csv](published_endpoints.csv).

## 2. Exact original method and why the old comparison did not match

The original scoring protocol is:

1. Model paired VH/VL with **ABodyBuilder2**, using **Martin numbering**, with `check_for_strained_bonds=False` when saving the antibody.
2. Align the modeled antibody to the current complex with **PyMOL**, replace the prior antibody, then apply **ImmuneBuilder complex refinement**.
3. Protonate at pH 7 with **PDB2PQR/PROPKA**. Prepare Amber topology using **ff14SBonlysc**, **mbondi3** radii and **hydrogen mass repartitioning**.
4. Minimize using **Amber pmemd.cuda**, implicit solvent `igb=8`, `ntb=0`, `maxcyc=99999`, `ncyc=1000`, `cut=1000`, `gbsa=3`, `surften=0.007`, `saltcon=0.1`.
5. Load the minimized complex and separated antibody/antigen into **PyRosetta**, initialize with `-mute all`, and evaluate `get_fa_scorefxn()`:

   `E_interaction = E_complex - E_antibody - E_antigen`

6. Compare candidate-minus-reference interaction energy in **Rosetta energy units**, retaining the same construct, preparation, scorer and control identity.

This is neither an InterfaceAnalyzer `dG_separated` protocol nor a measured binding free energy. OpenMM potential energy and Prodigy cannot be renamed REF15.

### Construct correction

The paper uses **VH 120 aa + VL 107 aa + HER2 residues 486–607, 122 aa**. The missing HER2 epitope loop was reconstructed from **PDB 8FFJ**. We recovered the exact released input and optimized controls instead of guessing or rebuilding that loop differently.

The old result structures instead contain **full Fab chains of 220/214 residues and a 581-residue HER2 chain**, without the paper's restored-loop construct. Thus, even an identical numerical scorer on the old files would not be a matched reproduction.

The released input also numbers its H chain sequentially after L, rather than using Martin residue IDs directly. A fresh ANARCI-derived source-to-Martin map was required before CDR selection. The corrected scoring script explicitly requires positive, equal C-alpha counts for every compared loop. See `evidence/mappings/benchmark_martin_mapping.json`.

## 3. New tools actually executed

| Tool | Executed version/settings | Work completed | Comparability |
|---|---|---|---|
| ImmuneBuilder / ABodyBuilder2 | 1.2; four published network weights; Martin; CPU; Torch seed 37; four inference threads | Six VH/VL predictions: five designs plus native control | Same method family as paper; paper tested 1.0.1/1.1.1, so not version-identical |
| PyMOL open-source | 3.2.0a; whole-Fv all-atom `align`; loop CA `rms_cur`, matchmaker=4 | Six independent conformation checks | Paper tested 2.6.0a0/3.0; published gates are stage-specific, not outcome means |
| ImmuneBuilder refinement / OpenMM | ImmuneBuilder 1.2 / OpenMM 8.4.0.post2; complex refinement on CPU, two threads | Six complex refinements returned success | This is the benchmark's pre-Amber refinement stage, **not** its final Amber minimization |
| Prodigy | 2.4.0; 5.5 A contact cutoff; accessibility threshold 0.05; 25 C; one process | 15 successful invocations: six new models, three published controls/input, six legacy reproducibility checks | Exploratory cross-scoring only; not the published metric |
| Biopython / NumPy / SciPy | 1.85 / 1.26.4 / 1.13.1 in analysis environment | Sequence/mask, geometry, mapping, diversity and interface audit | Explicit diagnostics, not invented benchmark thresholds |
| PyRosetta | Not installed in inspected environments | No score computed | Required for exact REF15 |
| Amber `tleap`, `pmemd.cuda`, `parmed` CLI | Required executables unavailable | No Amber topology/HMR/igb8 minimization | Required for exact preparation |

All scientific computations ran sequentially on CPU with CUDA hidden. The GPU was already occupied (~16.2 GiB used of 24 GiB at the initial check). No GPU inference or GPU minimization was launched. No OOM occurred in the executed CPU checks. Configurations, model-weight hashes, code snapshots and Prodigy stdout/stderr are in the source run.

## 4. Independent candidate results

Native remodeled-control Prodigy ΔG: **-10.1 kcal/mol**. The two released optimized controls, independently rescored here with Prodigy, both give **-13.8 kcal/mol**. Those are **newly calculated control scores**, not published Prodigy benchmarks. They are not comparable to the paper's -94.8663/-92.6947 REU results.

| Candidate | H3 CA RMSD, A | Largest other-CDR RMSD, A | New Prodigy ΔG, kcal/mol | Delta vs remodeled native | Delta vs rescored published winners | Native epitope recall |
|---|---:|---:|---:|---:|---:|---:|
| AB_04 | 1.810 | 0.852 | -9.4 | +0.7 | +4.4 | 0.875 |
| AB_05 | 1.791 | 1.012 | -10.9 | -0.8 | +2.9 | 0.875 |
| AB_08 | 1.576 | 0.926 | -10.5 | -0.4 | +3.3 | 1.000 |
| AB_13 | 1.698 | 0.938 | -11.8 | -1.7 | +2.0 | 0.875 |
| AB_20 | 1.562 | 0.887 | -10.5 | -0.4 | +3.3 | 0.875 |

### Interpretation

- All five H3 values meet the **3.0 A H3-grafting gate** configured in the released paper workflow.
- All five H3 values exceed the **1.5 A stricter conformation-check gate**. Every other measured loop is below 1.5 A. The original gate compares each proposed modification to that optimization stage's current parent; here the released native input is the reference. Therefore these are method-aligned stage-gate diagnostics, not a literal replay of the paper's acceptance decisions.
- Newly predicted ABodyBuilder2 uncertainty is the square root of four-model positional dispersion in A. It is **not pLDDT**. Loop-level values are in [cdr_conformation.csv](cdr_conformation.csv).
- All six new refined complexes have zero antibody–antigen heavy-atom pairs below 2 A. This is a severe-distance diagnostic, **not a MolProbity clashscore** and not proof of perfect geometry.
- Epitope recall uses the same 122-position target and a 5.5 A heavy-atom definition against the remodeled native control. Pose retention is conditioned by template alignment; it is not independent docking validation.
- Prodigy numerically favors AB_13 over the remodeled native, while all five designs score less favorably than the two rescored published optimized controls. This does **not** establish REF15 outperformance or experimentally improved affinity: the published controls underwent Amber minimization, while our new complexes stopped after OpenMM refinement.

No final binding winner is certified. AB_13 is the most favorable **exploratory Prodigy** result but has an edit-scope conflict described below. AB_08 retains the full measured native epitope set under this model. These are separate observations, not a combined validated ranking.

## 5. Prior evidence defects and missing-metric inventory

[metric_gaps.csv](metric_gaps.csv) covers every audited metric category with its exact method, relevant reference and result/blocker. [benchmark_comparison.csv](benchmark_comparison.csv) contains candidate-level numerical comparisons and explicit comparability decisions.

### Problems found in the earlier result

- Legacy fixed-pose structures lack backbone carbonyl O atoms at **every altered residue**: AB_04 10, AB_05 12, AB_08 7, AB_13 12, AB_20 9. Their side-chain coordinates were hand-entered approximations, not an accepted rotamer/modeling method. The old Prodigy values reproduce numerically but are rejected as evidence for improved binding.
- Legacy backbone CA RMSD is exactly zero by construction. It cannot serve as independent structure validation.
- Every design introduces one additional heavy-chain cysteine. Preservation of the original cysteines does not establish correct pairing of this extra cysteine; it remains a developability risk.
- All five satisfy the **executed AntiBMPNN mask**. However, **AB_13 B:S97A** lies outside the earlier retained design-scope declaration. Both masks are preserved; the conflict is unresolved, not silently normalized away.
- Five paired sequences are unique; their ten pairwise Hamming distances range from 2 to 9. No published diversity cutoff makes this an automatic pass.

### Remaining unresolved metrics

1. **Absolute REF15 and energy components:** missing PyRosetta and exact Amber preparation; values remain null/blank.
2. **REF15 delta vs native and vs published endpoints:** cannot be calculated without compatible native/candidate REF15. No REU–kcal/mol conversion is attempted.
3. **Full-complex ipTM/pTM/PAE/pLDDT:** historical Boltz2 pair outputs are not full paired-Fv/HER2 confidence on the correct construct. ABodyBuilder2 has no complex PAE/ipTM; no score is fabricated.
4. **Calibrated thermal stability, solubility and aggregation:** historical Antibody_Prediction fields exist, but this HER2 benchmark supplies neither matching target-specific endpoints nor a calibration converting them to measured Tm/solubility. They are retained as raw model outputs, not compared with arbitrary ranges.
5. **Folding or binding ddG:** not provided by this HER2 optimization benchmark. REF15 is not a folding ddG method; no unrelated ddG benchmark is imported.
6. **Experimental affinity and repeated-run statistical uncertainty:** no assay outcomes for these five designs and no replicated Amber/REF15 calculations. A network ensemble is not repeated experimental or protocol replication.

SKEMPI classification statistics, AF3Score aggregate accuracy/F1, OAS repertoire diversity and Gal-3BP heated-MD outcomes elsewhere in the paper were deliberately **not** used as candidate-level HER2 benchmarks. They concern different evaluated populations or targets and cannot be transferred to these five designs.

## 6. Reproducibility and artifacts

- [published_endpoints.csv](published_endpoints.csv): all 16 source-log initial/final energies.
- [predictions.csv](predictions.csv): five-candidate audit panel; REF15 missing fields stay empty.
- [sequence_geometry_audit.csv](sequence_geometry_audit.csv): old-coordinate defects, edited masks and cysteine liability.
- [prodigy_crosscheck.csv](prodigy_crosscheck.csv): all 15 actual Prodigy outputs, scope and input hashes.
- [cdr_conformation.csv](cdr_conformation.csv): all six loops and local ensemble uncertainty for six predictions.
- `structures/`: independently modeled VH/VL, template-pose assemblies and successfully refined complexes; filenames distinguish contexts.
- `evidence/reference/`: exact published native/optimized controls and Martin-renumbered reference.
- `evidence/mappings/`: source-to-Martin numbering.
- `evidence/raw/`: execution status, ensemble arrays, construct comparison and detailed diagnostics.
- Source run `configs/`: exact evaluation settings, weight hashes and code snapshot.
- [Validation](evidence/validation.json): packaging/identity/execution checks; separate from scientific reproduction status.

**Bottom line:** The source benchmark and missing metrics are now audited, independent structure/conformation validation was actually run, and exploratory control rescoring was completed. The primary REF15 comparison is still blocked, so the defensible benchmark verdict is **undetermined**, not “better than the benchmark.”

## Primary references

1. Task-specific benchmark Markdown at `benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md`.
2. Sampaio et al. (2026), DOI 10.1021/acs.jcim.5c01924; PMCID PMC12892330.
3. Supporting Information, DOI 10.1021/acs.jcim.5c01924.s001; original PDF `ci5c01924_si_001.pdf`, retrieved from publisher-associated Figshare article 31102358.
4. Zenodo record 15803983, `ab_seldon_trastuzumab_optimization_tests_v2.tar.gz`; original paper-v6.2 code and per-run HER2 logs.
5. Authors' source repository SFBBGroup/Ab-SELDON, inspected revision `9f5df3cadc96a64d78c977b426ae87c108bce4ba`; archived paper-v6.2 implementation was the scoring authority.
6. ImmuneBuilder: Abanades et al. (2023), DOI 10.1038/s42003-023-04927-7; installed implementation and four Zenodo 7258553 weights, hashes retained.
