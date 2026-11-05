# Research Notes — Small-Molecule Virtual Screening (paper-anchored benchmark tasks)

**Topic:** small-molecule-virtual-screening · **Period:** 2026-11-03 → 2026-11-05 · **Status:** Complete

## 1. Problem definition

Build benchmark tasks in which an agent must independently execute a published virtual-screening campaign — target/structure preparation, ligand or pharmacophore screening, molecular docking, ADMET/drug-likeness profiling, MD validation — and **meet the paper's own quantitative pass bar** without ever consulting the paper's hit lists. Each task therefore needs a source paper that is: fully computational (no wet lab), simple in workflow (single chain, no QSAR/DFT/ML stages, MD as secondary validation only), human-disease target, and reproducible from public data at the file level.

## 2. Methodology

1. **Stage scoping.** Mapped computational drug-discovery stages (hit generation → hit-to-lead → lead optimization) and constrained tasks to the hit-generation stage: target → screening → docking → ADMET → (secondary) MD.
2. **Literature search.** Europe PMC REST full-text search with ADMET tool names embedded in the query so that hits structurally include an ADMET stage:
   `"virtual screening" AND "molecular docking" AND "molecular dynamics" AND (SwissADME OR pkCSM OR admetSAR) AND (ZINC OR PubChem OR ChEMBL) NOT ("natural product" OR "FDA-approved" OR QSAR OR repurposing OR "density functional")`, `OPEN_ACCESS:y`, `PUB_YEAR:[2023 TO 2026]` → 178 hits for the final replacement round (~1,100 papers screened overall across rounds).
3. **Title triage, then full-text trap scan.** Abstracts are never sufficient — MD stages, wet-lab sections and library provenance routinely hide below the abstract. Every candidate received a full-text scan (Europe PMC `fullTextXML`/text) before acceptance.
4. **Hard exclusion rules** (see §4 trap catalog): flora/natural-product libraries, repurposing (FDA/DrugBank libraries or lead provenance), QSAR/DFT/ML stages, wet-lab stages, non-human-disease targets, gated data without a public substitute, wrong-PMC attribution.
5. **Supplement verification at the file level.** Supplements downloaded via Europe PMC REST `/PMCxxxx/supplementaryFiles` and contents inspected (not just the data-availability statement). A paper passes only if hits/SMILES/poses are actually recoverable — in-article, in-supplement, or via a public repository.
6. **Claim extraction → task-doc build → audit chain.** Every accepted paper got: claim-by-claim extraction → task document → independent verbatim audit → rule-compliance validation → exhaustive per-doc critique → closing re-audit (and for the two replacement papers, an additional independent second-agent re-audit).
7. **Engine anchoring policy.** Derived from observed paper engines: same-engine bars where the paper used AutoDock Vina; engine-relative bars (explicit caveat) where the paper used Glide/AutoDock 4/LibDock-CDOCKER; self-calibrating bars where the agent must out-dock a reference ligand in its own engine. Cross-engine kcal/mol scales are never treated as interchangeable.

## 3. Final roster (12 tasks, 2 environments)

| Env | Task | Target (disease) | Paper | Docking anchor |
|---|---|---|---|---|
| molecular-design-and-generation | task_001 | CAII (glaucoma) | Front Chem 2025 · 10.3389/fchem.2025.1627793 · PMC12528100 | ≤ −8.0 kcal/mol (engine-relative) + top-3 MM-GBSA rank |
| molecular-design-and-generation | task_002 | ROCK2 (cancer) | PLoS ONE 2025 · 10.1371/journal.pone.0323781 · PMC12074392 | ≥2 hits ≤ −9.89 kcal/mol (Glide SP ref; engine-relative) |
| molecular-design-and-generation | task_003 | KHK-C (NAFLD/NASH) | Front Pharmacol 2025 · 10.3389/fphar.2025.1531512 · PMC12009819 | < −7.76 kcal/mol (Glide XP ref; engine-relative) |
| molecular-design-and-generation | task_004 | FoxM1 + Hsp70 (cancer, dual) | Res Pharm Sci 2023 · 10.4103/1735-5362.359431 · PMC9872178 | beat FDI-6 AND VER-155008 (self-calibrating) |
| molecular-design-and-generation | task_005 | FGFR2 (cancer) | Sci Rep 2024 · 10.1038/s41598-024-69850-1 · PMC11339395 | ≤ −11.7 kcal/mol (same-engine Vina) + full ADMET/PAINS |
| molecular-design-and-generation | task_006 | GSK-3β (Alzheimer's) | Sci Rep 2026 · 10.1038/s41598-026-56505-6 · PMC13396737 | < −6.80 kcal/mol (same-engine Vina) + BBB permeant |
| structure-based-discovery | task_001 | EGFR (cancer) | PLoS ONE 2024 · 10.1371/journal.pone.0311527 · PMC11627428 | out-dock R85/known inhibitors + QikProp ranges |
| structure-based-discovery | task_002 | TrkB agonist pharmacophore (CDKL5-deficiency) | Bioinform Biol Insights 2023 · 10.1177/11779322231158254 · PMC9989394 | beat 7,8-DHF (−7.1 kcal/mol) + high GI absorption |
| structure-based-discovery | task_003 | MMP-9 (cerebral ischemia) | PLoS ONE 2026 · 10.1371/journal.pone.0346627 · PMC13175377 | −9.96 kcal/mol (Glide SP ref; engine-relative) + MM-GBSA < −45.17 |
| structure-based-discovery | task_004 | PI5P4Kγ allosteric (cancer) | Sci Rep 2025 · 10.1038/s41598-025-07480-x · PMC12485083 | beat same-engine DVF redock (−9.26/−10.4) + MM-PBSA < −68.44 kJ/mol |
| structure-based-discovery | task_005 | PI3Kα (NSCLC) | RSC Adv 2022 · 10.1039/D2RA03451D · PMC9346375 | ≤ −3.941 kcal/mol (Glide XP ref; engine-relative) + MMGBSA ≤ −42.58 |
| structure-based-discovery | task_006 | VEGFR-2 + c-Met (cancer, dual) | Front Pharmacol 2025 · 10.3389/fphar.2025.1534707 · PMC11926154 | < −60 kJ/mol both kinases |

**Retired (kept in `science-environments/retired/<environment>/`):**
- CDK1 (Med Oncol 2022, PDB 6GU7, AutoDock 4.2.6) — dropped for perceived workflow complexity despite a verifiably complete supplement (100 analogs with CIDs in Table S1; all 73 docked scores in Table S2).
- H1 antihistamine pharmacophore (Russ J Bioorg Chem 2022, PDB 7DFL) — supplement is 2D depictions only, no SMILES anywhere: an execution blocker for an independent agent.

## 4. Trap catalog (hard-won exclusion patterns)

- **Flora/natural products:** ZINC natural-products subsets, InterBioScreen/Marine/SuperNatural libraries, COCONUT, TCM libraries, curcumin/alkaloid/stilbenoid libraries, phytochemical databases, Huperzine-A analogs. (Found in: SHP2 2024/2026, mPGES-1, STAT3, HER2, ROS1, TRPV4, AChE, aromatase candidates.)
- **Repurposing:** "FDA-approved drugs as", DrugBank screens, or final hits "identified in DrugBank" (HDAC6/MPO ACS Omega — both leads were DrugBank-sourced even though the screen passed).
- **QSAR/DFT/ML:** QSAR descriptor stages, Gaussian/DFT even for descriptors, ensemble ML, AI/diffusion docking, ML-guided VS.
- **Wet lab:** integrated synthesis, enzymatic or cell-assay stages, hit-to-lead JMC-style papers.
- **Complexity:** multi-domain workflows, expression/survival-analysis preludes, cascade counts far beyond the simple chain.
- **Provenance/data traps:** data "available on request"; gated libraries without a public substitute; supplements containing figures only.
- **Wrong-PMC attribution:** PubMed summary PMCIDs frequently come from reference lists — always resolve via Europe PMC REST `EXT_ID:<pmid> AND SRC:MED`.
- **Reference-context false positives:** keywords like "phytochemical" or "machine learning" in references/intro/future-work do not disqualify (GSK-3β paper hits were all reference-list artifacts) — classify context before rejecting.

## 5. Supplement-verification findings (file level)

- 9/12 tasks fully public including supplements or complete in-article tables (CAII, KHK-C, FGFR2, PI5P4Kγ, MMP-9 [Figshare 10.6084/m9.figshare.31425299 incl. poses + scripts], TrkB, FoxM1, ROCK2, EGFR).
- Mitigated: PI3Kα (RSC ESI = top-10 3D diagrams only; retrievable via Europe PMC), VEGFR-2/c-Met (ChemDiv catalogue not bulk-downloadable — public-substitute clause in-doc), GSK-3β (hits are 2D depictions with no IDs — pass bar is score-anchored, not hit-identity-anchored).
- Supplements must be **inspected, not trusted**: CDK1's supplement was complete yet the paper was retired on complexity; H1's data statement looked fine but no SMILES existed anywhere.

## 6. Paper-internal conflicts policy

Papers frequently contradict themselves (200-vs-100 ns MD, 7-vs-6 pharmacophore features, text-vs-table label inversions, out-of-order table rows, methods-promised metrics never reported, kcal/mol vs kJ/mol units). Policy: **annotate every conflict in the task document — never silently resolve it.** Ground truth defaults: tables over prose; Methods quotes kept verbatim with the conflict flagged.

## 7. Assumptions and limitations

- Grading is meet-or-beat: workflow completion + quantitative bar, never reproduction of the paper's exact hit lists.
- 240 minutes of agent working time; long platform jobs may finish asynchronously.
- All docking through Boltzmann platform tools (`Vina_basic_docking` + `Diffdock` second-engine); no local docking engines in graded runs.
- Platform MD ion sets may not include Na⁺ (paper NaCl 0.15 M) — KCl substitution noted as derived where relevant.
- Auditor table-readings of flattened HTML tables can mis-assign columns; column recounts against headers are required before accepting table-derived audit findings (one medium MMP-9 finding was rejected this way: Table 4 BBB is Yes for all 10 compounds; the auditor had read the PPB column).

## 8. Unresolved questions

- None blocking. Open item: confirm live platform `MDS_openMM` ion-type options with a single API call when the platform is reachable (affects verbatim NaCl reproduction in MMP-9 and dual-kinase tasks).
