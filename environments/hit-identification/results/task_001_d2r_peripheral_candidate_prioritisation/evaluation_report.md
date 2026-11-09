# D2R Agent Scientist execution and paper comparison

**Task:** `task_001_d2r_peripheral_candidate_prioritisation`  
**Reviewed submission:** `d2r_peripheral_final_deliverables.zip`  
**Execution evidence:** Matching `run_rsi` artifacts dated 8–9 November 2026  
**Review date:** 9 November 2026

The agent executed target-model prediction, property prediction, docking and a subset pose-prediction workflow, then delivered an eight-compound shortlist and selected **111 and 120** as its two priorities. The paper selected **128 and 381**. Numerical execution is supported by retained outputs; the agent's claimed peripheral-restriction rationale requires correction.

This report first describes the work performed and its outputs, then compares them with the paper. The original detailed [agent report](submitted/report.md), [assessment](submitted/assessment.json) and [ranked shortlist](submitted/ranked_candidates.csv) are preserved unchanged. Statements below distinguish the agent's interpretation from findings supported by the retained evidence.

## 1. Inputs used

- **Target:** Human DRD2, canonical 443-residue sequence P14416, with crystal reference 6CM4 for structure-based work.
- **Library:** 400 supplied source records, representing 398 distinct full InChIKeys. All 400 submitted IDs, ZINC IDs and source SMILES match the supplied inputs. Duplicate identity groups are 194/195 and 289/290.
- **Controls:** Risperidone and domperidone, with native risperidone coordinates for structural reference. IDs 2/3 are methylated analogues and distinct enantiomers, not risperidone control records.

## 2. Workflow executed by the agent

| Stage | What the agent did | Retained outcome |
| --- | --- | --- |
| Input handling and preparation | Checked the source library, paired compounds with DRD2 and prepared a chain-filtered 6CM4 receptor input | All source identities and 400 target-model sequence pairings reconcile; exact worker preparation remains incompletely documented |
| D2R target prediction | Used Boltzmann `global_binding_affinity` / NESSO on all library compounds and separately on controls | 400 library predictions and two control predictions retained; input was SMILES plus sequence, not receptor coordinates |
| Property assessment | Used Boltzmann `Property_Prediction` for primary ADME endpoints and additional properties, with separate control predictions | 400 primary rows; 398 numerical endpoint rows; IDs 195/290 returned `Invalid Smile` |
| Additional brain-access assessment | Called ADMETlab 3.0 directly after finding constant platform BBB/HIA labels; retried missing Tier-A results and queried controls | Retained successful responses cover 180 library IDs; all 30 Tier-A BCRP values can be reconciled |
| Structure-based docking | Used Boltzmann `Vina_basic_docking` for all 400 compounds, requesting ten poses each | 3,993 poses; all 400 best scores reproduce raw pose minima; automated interaction extraction failed |
| Contact analysis | Calculated closest-atom distances from returned Vina poses to Asp114 and Trp386 | Numerical distances retained; they do not by themselves verify salt bridges or π-stacking |
| Additional pose prediction | Used Boltzmann DiffDock for a 26-compound subset | Twenty compounds returned 200 numerical poses; six failure rows; five final-shortlist compounds have usable pose-confidence results |
| Integration and ranking | Integrated the outputs, defined a domperidone-relative NESSO Tier A, ranked primarily by NESSO, and annotated candidates using BCRP/Caco-2 predictions | Thirty Tier-A IDs; eight submitted candidates; final priorities 111/120; ranking order is reproducible, while the brain-access interpretation is unsupported |

The agent's primary Tier-A threshold was the domperidone score, approximately −0.938. This threshold and NESSO-primary ranking were agent choices, not requirements in task.md. The agent initially excluded IDs 2/3 as controls, then corrected their eligibility and included both in the final shortlist; some report/assessment sections still contain the earlier exclusion.

Actual provider provenance includes **direct ADMETlab API access outside Boltzmann**. The task itself does not impose a provider restriction. Compliance with a separate Boltzmann-only execution instruction cannot be certified from the submitted package.

## 3. Agent outputs

### 3.1 Ranked shortlist and final priorities

The following preserves the submitted order and flags. NESSO is a model score with unestablished physical units; the report's kcal/mol attribution is unsupported. Vina scores are in kcal/mol. The BCRP output is correctly labelled as **inhibitor probability**, rather than reproducing the agent's efflux interpretation.

| Rank | ID | Submitted priority flag | NESSO score | Vina score | Vina rank / 400 | Caco-2 | BCRP inhibitor probability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 | QUALIFIED-3RD | -2.369 | -11.6 | 54 | -4.98 | 0.267869 |
| 2 | 5 | no | -2.3618 | -11.266 | 88 | -4.88 | 0.000194 |
| 3 | 111 | YES | -2.2137 | -11.043 | 119 | -4.87 | 0.647566 |
| 4 | 2 | QUALIFIED-3RD | -2.1912 | -12.425 | 3 | -4.98 | 0.121681 |
| 5 | 19 | no | -2.1662 | -12.155 | 7 | -4.9 | 0.002372 |
| 6 | 25 | no | -2.1568 | -11.612 | 50 | -4.98 | 0.000064 |
| 7 | 120 | YES | -2.122 | -9.841 | 288 | -4.87 | 0.583225 |
| 8 | 10 | no | -2.0897 | -11.561 | 57 | -5.02 | 0.000252 |


The agent labelled 111/120 as final priorities and the 2/3 enantiomer pair as a third qualified option. Its argument was that high BCRP probabilities imply strong efflux and restricted brain access. The returned endpoint actually predicts **inhibition**, so the numerical probabilities do not establish the submitted peripheral/CNS labels or fold-efflux claims. Those labels remain agent claims, not supported benchmark conclusions.

### 3.2 Reference controls and absorption

| Record | NESSO score | Boltzmann Caco-2 |
| --- | --- | --- |
| Separately predicted risperidone control | −2.5971775 | −4.90 |
| Separately predicted domperidone control | −0.9375722 | −5.28 |
| Priority 111 | −2.2137372 | −4.87 |
| Priority 120 | −2.1219869 | −4.87 |

The library's risperidone-identical ID 1 has NESSO −2.5494745, distinct from the separately scored control. Keep the chosen comparison record explicit. Lower NESSO scores follow the tool's internal convention and are not measured potency differences.

Under a common log10-Papp interpretation, higher Caco-2 values mean greater apparent permeability. The same-provider values therefore permit a limited relative-permeability comparison after correcting the report. Its prose reverses the sign and uses domperidone −4.71 from ADMETlab in part of the comparison. Values from different predictors should not be directly compared as the same scale. None of these predictions is measured intestinal absorption.

### 3.3 Structure-based results

The retained Vina box is a 23 Å cube centered at (9.925, 5.846, −9.582), with exhaustiveness 16. There are ten poses for 394 compounds, nine for five compounds and eight for one compound. All 3,993 score rows reconcile with the SDF pose count and the 400 best-score rows.

All first exported poses retain source heavy-atom topology, but only 274/400 retain the molecular formula and 271/400 the full InChIKey. Five reported shortlist exports—2, 3, 5, 19 and 25—have formula differences. The risperidone export is C23H29FN4O2 versus source C23H27FN4O2. These files establish an exported-state discrepancy, but do not show whether it arose before scoring or during conversion. Same-species reference redocking RMSD is not established.

The returned automated interaction fields report 70 residues with missing heavy atoms. This documents interaction-preparation failure; it does not alone recover the exact preparation used by the docking worker.

| Priority | Closest ligand N–Asp114 O, Å | Closest aromatic ligand C–Trp386 ring C, Å | Submitted DiffDock minimum | Correct best DiffDock maximum |
| --- | --- | --- | --- | --- |
| 111 | 3.3045 | 3.7222 | −1.9753312 | −1.2722191 |
| 120 | 4.1736 | 5.3756 | −2.2019875 | −0.8961285 |

Distances are geometric observations; charge and ring orientation were not established sufficiently to certify the claimed interaction types. The retained Trp-related distance for 120 is about 5.38 Å, not the alternative 4.95 Å in parts of the original report.

The agent selected **minimum** DiffDock confidence as best for all 20 compounds. Raw Rank 0 and the official implementation select the **maximum**. Numerical DiffDock data cover final IDs 5, 19, 25, 111 and 120: five of eight, not seven. IDs 10, 21, 22, 23, 32 and 37 have failure rows. Confidence concerns pose quality and does not confirm affinity or antagonism.

### 3.4 Coverage, failures and unresolved work

| Item | Confirmed retained evidence | Limitation |
| --- | --- | --- |
| Target-model prediction | 400 matching sequence/compound rows | Units unestablished; no experimental activity implied |
| Primary property prediction | 398 numerical library records | IDs 195/290 failed despite matching valid source identities elsewhere |
| BBB/HIA labels | BBB=1.0 and HIA=1.0 for all 398 numerical library rows | Constant, unverified class directions; no candidate discrimination |
| ADMETlab responses | Attempts represented for 228 library IDs; successes for 180 | Whole-library successful coverage is not substantiated |
| Tier-A BCRP | All 30 values recoverable across retained files | Submitted strict audit has 29 numbers; missing ID 97 value is present elsewhere |
| Docking | 400 compounds, 3,993 poses | Export-state and preparation limitations above |
| DiffDock | 20 numerical compound results out of 26 attempts | Six explicit failures; summary direction was wrong |
| Alternative BBB model | Agent reports failed BBBP/MoleculeNet/DeepChem downloads | No completed alternative model validation retained |
| Molecular dynamics | Not performed | Excluded from task scope; no completion penalty |

Saved records also contain ambiguous property submissions and a timed-out P-gp attempt. The existing ledger does not establish whether those attempts created remote records or charges. P-gp inhibitor predictions do not recover missing P-gp substrate status. No new submission or authoritative platform status refresh was made by this review.

## 4. Comparison with the original paper

### 4.1 Workflow and selection outcomes

The reference is Kim et al., [PLOS One, DOI 10.1371/journal.pone.0355997](https://doi.org/10.1371/journal.pone.0355997). The paper used a fixed 400-record analogue library, pharmacokinetic filtering, receptor docking and interaction selection, followed by historical dynamics and further safety/selectivity predictions. The adapted task permits independent workflow choices and excludes dynamics.

| Item | Paper result | Agent result |
| --- | --- | --- |
| Input library | 400 records | Same 400 records |
| Docking coverage | 226 candidate rows; 225 numerical scores; 380 missing | 400 scored compounds |
| Eight selected IDs | 17, 21, 24, 27, 128, 321, 360, 381 | 3, 5, 111, 2, 19, 25, 120, 10 |
| Contact-selected four | 27, 128, 360, 381 | No directly equivalent mandatory stage |
| Final two | 128, 381 | 111, 120 |
| Brain-access conclusion | SwissADME-negative shortlist, with additional predictor disagreements | Claimed peripheral candidates based on misinterpreted inhibitor probability |
| Dynamics | Historical 100 ns analysis | Outside execution scope |

Shortlist overlap is **0/8** and priority overlap **0/2**. These describe different selections, not biological accuracy. The paper's selections are computational outputs, and matching their identities is not a requirement.

The paper's strict Vina comparison below risperidone −11.8 kcal/mol reproduces its eight candidates. Including equal-score IDs 10/309 gives ten instead. The agent was free to choose a different justified criterion.

### 4.2 Comparable candidate scores

“Not reported” means no numerical published candidate value is available. Vina scores use kcal/mol; NESSO scores have unestablished physical units. Values from these methods must not be subtracted or treated as calibrated equivalents.

| ID | Selected by | Paper BBB permeant | Paper Vina | Agent Vina | Agent NESSO |
| --- | --- | --- | --- | --- | --- |
| 17 | Paper | No | -12.4 | -12.041 | -0.1030 |
| 21 | Paper | No | -11.9 | -12.579 | -1.1296 |
| 24 | Paper | No | -11.9 | -11.214 | -0.8690 |
| 27 | Paper | No | -11.9 | -11.669 | 0.4615 |
| 128 | Paper | No | -12.3 | -10.943 | 0.5575 |
| 321 | Paper | No | -12.3 | -11.405 | -0.5667 |
| 360 | Paper | No | -11.9 | -11.023 | 0.8448 |
| 381 | Paper | No | -11.9 | -11.224 | 0.8129 |
| 3 | Agent | Yes | Not reported | -11.6 | -2.3690 |
| 5 | Agent | Yes | Not reported | -11.266 | -2.3618 |
| 111 | Agent | Yes | Not reported | -11.043 | -2.2137 |
| 2 | Agent | Yes | Not reported | -12.425 | -2.1912 |
| 19 | Agent | Yes | Not reported | -12.155 | -2.1662 |
| 25 | Agent | No | -11.5 | -11.612 | -2.1568 |
| 120 | Agent | Yes | Not reported | -9.841 | -2.1220 |
| 10 | Agent | No | -11.8 | -11.561 | -2.0897 |


Both agent priorities are BBB-positive in the paper's SwissADME table, while paper priorities 128/381 are BBB-negative. This is a prediction disagreement, not measured brain exposure. Agent Vina ranks 111/120 are 119/288, compared with 134/93 for paper priorities 128/381; the run's different primary score produces a different ranking.

### 4.3 Numerical agreement and preparation differences

| Paired outputs | n | Pearson r | Spearman ρ |
| --- | --- | --- | --- |
| Paper Vina versus agent Vina | 225 | 0.667273 | 0.652285 |
| Agent Vina versus NESSO | 400 | 0.330144 | 0.280076 |
| NESSO versus reported minimum DiffDock confidence | 20 | 0.195664 | 0.321805 |
| NESSO versus corrected maximum DiffDock confidence | 20 | 0.143958 | 0.016541 |

The paper reports a 30 Å cube centered approximately at (10, 5.9, −9.5) and an unavailable reconstructed receptor; the run retains a 23 Å cube and chain-filtered crystal input. Both report exhaustiveness 16. Exact preparation and original author poses are unavailable. These are descriptive comparisons across protocols; correlations do not establish experimental accuracy or three-method validation of binding.

### 4.4 Paper limitations relevant to comparison

- S1 prediction payloads for 51, 308, 327 and 354 duplicate the preceding different-identity record. Original source input SMILES remain usable; the associated historical predictions require flags.
- ID 380 has no numeric S2 score. Comparisons therefore use 225 numerical paper pairs, without filling missing values.
- Figure 2 captions and drawn identities conflict: B–E draw 17, 21, 24 and 27, while captions name 27, 128, 360 and 381. Original poses are unavailable to resolve attribution.
- Asp114/Trp386 map to the paper's Asp80/Trp373, but its phenylalanine mappings are inconsistent. The exact modeled receptor is not deposited.
- Reference redocking is stated as 0.458 Å in text and 0.48 Å in the caption; original redocked coordinates/mapping are absent. No verified equivalent run RMSD can be supplied from the chemically inconsistent export.
- The native-frame 6A93 off-target center and historical dynamics files/settings have unresolved reproducibility limits. Those optional stages are not used to penalise this task.

## 5. Evaluation findings

| Question | Finding |
| --- | --- |
| Did the agent execute scientific work? | Yes. Target predictions, properties, docking and subset pose outputs are retained and mapped |
| Were the requested main files delivered? | Yes: ranked_candidates.csv, assessment.json and the detailed report.md |
| Does the final order follow the stated primary model? | Yes, after excluding risperidone identity; some earlier exclusions remain stale in prose |
| Is restricted brain access supported as claimed? | No. BCRP inhibitor probability was misused as substrate/efflux evidence |
| Can absorption evidence be retained? | Partly. Same-provider numerical comparisons are recoverable after direction/source corrections |
| Do DiffDock results confirm strong binding? | No. Confidence is pose-quality evidence; the agent also selected the wrong confidence direction |
| Are the poses chemically and procedurally fully qualified? | No. Exported-state discrepancies and incomplete preparation provenance remain |
| Does disagreement with the paper itself fail the task? | No. The task allows an independent workflow and paper outcomes are computational references |

Domperidone BCRP inhibitor probability is 0.1237338; ID 2 is lower at 0.1216809. The literal Tier-A inhibitor-score bar retains 3/111/120, not 2. No quantified uncertainty supports relabelling ID 2 as passing, and the bar does not establish peripheral restriction in any case. IDs 2/3 remain two stereochemical entities, despite the report's single-compound count.

**Decision:** Retain the agent's shortlist and 111/120 priorities as its reported hypotheses. The submitted combined peripheral-selection conclusion is not supported as written. A defensible revision needs relevant, correctly interpreted brain-access evidence, matched absorption comparisons, corrected confidence/coverage summaries and explicit pose/preparation limitations. This does not establish that the molecules cannot work biologically and does not impose an experimental-validation prerequisite on the computational task.

## 6. Outputs and execution records

| Evidence | Location |
| --- | --- |
| Agent's complete detailed account | [submitted/report.md](submitted/report.md) |
| Original ranking and assessment | [ranked_candidates.csv](submitted/ranked_candidates.csv), [assessment.json](submitted/assessment.json) |
| Integrated outputs and delivered analyses | `submitted/`, including integrated_raw.csv, tierA_strict_audit.csv, diffdock_mapped.csv and vina_docking_results/vina_ranking.csv |
| Exact original archive and entry hashes | `source_submission.zip`, `submission_manifest.json` |
| Saved execution ledger | [job_ledger_as_saved.json](supporting/job_ledger_as_saved.json) |
| Additional matching raw evidence | `supporting/`; provenance recorded in [provenance.json](supporting/provenance.json) |
| All 400 paper–agent record comparisons | [compound_comparison.csv](benchmark_results/compound_comparison.csv) |
| Full-precision counts and correlations | [metrics.json](benchmark_results/metrics.json) |
| Stage and requirement findings | [stage_comparison.csv](benchmark_results/stage_comparison.csv), [task_compliance.csv](benchmark_results/task_compliance.csv) |
| Detailed correction register | [issues.csv](benchmark_results/issues.csv) |
| Recomputed identity, confidence, distance and control checks | `audit/` |
| Benchmark definitions | [Benchmark](../../benchmark/task_001_d2r_peripheral_candidate_prioritisation.md) |

The compact original ZIP omitted some referenced raw outputs; matching local evidence is labelled as separately recovered rather than claimed as original ZIP content. Exact worker versions, full original payloads and the execution conversation are not fully established. Earlier run outputs are not merged into this execution.

This evaluation uses saved artifacts and offline checks. It did not submit jobs, change the original task/results, invent a replacement shortlist, run dynamics, or commit/push repository changes.
