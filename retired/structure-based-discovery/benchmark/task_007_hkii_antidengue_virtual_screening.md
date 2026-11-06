# Evaluator specification — HKII virtual screening

**Task Format:** capability_workflow
**Grading Mode:** manual_review_required
**Visibility:** owner/evaluator only; do not include this file, generated reference metadata or the source-audit record in the agent execution bundle.

## Evaluation Policy

The agent-facing task defines the scientific problem and evidence requirements without naming a publication, prescribing software or exposing published hits/scores. The agent must independently discover and select verified capabilities from the Boltzmann small-molecule discovery suite.

Evaluate input identity/provenance, binding-site validity, independent library-analogue retrieval across all three query groups, contemporaneous reference controls, justified property filters, evidence-backed prioritisation, artifact completeness and honest completion status. This is screening of existing library members, not de novo molecular design; conformer preparation must preserve compound identity. Scientific completion and evidence quality require manual evaluation; a single docking-score threshold or the presence of output files cannot certify success.

Compare scores only within compatible engines/protocols and chemical identities. The historical numerical results below are contextual reference evidence, not universal thresholds for an independently chosen method. The reported box does not overlap native-frame 2NZT in the retained execution audit; the agent must establish a valid site in the actual prepared coordinate frame.

The benchmark runner must supply a frozen library, its membership/provenance manifest and unambiguous reference definitions. This document rewrite does not supply or recover the historical library. A controlled replacement dataset may define a separate run, but both arms of a comparison must use the specified inputs and historical hit recovery must not be claimed. Missing required inputs are NEEDS_INPUT, not permission to choose an easier library. Selection exceptions and required endpoint coverage must be declared before outcomes are reviewed.

The current workflow includes 3D shape/feature screening, up to 100 analogues per query, property filtering before docking, top-three selection per query and dynamics of the selected group leaders against their references. The task requires 100 ps restrained equilibration and 20 ns production per selected system, with recorded preparation and analysis definitions. Retain any candidate shortfall rather than treating an unsupported stage or insufficient evidence as a favourable outcome. Use execution-context resource limits rather than imposing a fixed benchmark working-time limit on this task.

The source audit linked below applies to the earlier paper-anchored task version, not to the current capability-based prompt. Exact tool availability, historical data completeness and paper reproducibility remain separate from task-format validation.

### Execution guidance

Additional input and execution checks belong in the run prompt or evaluator review, rather than being presented as scientific workflow stages reported by the source. These include checking coordinate-frame/box overlap, distinguishing pose-to-crystal from pose-to-best-mode displacement, establishing endpoint equivalence from model definitions, checking accepted-job state before retries and verifying duration against raw logs/trajectories. The agent-facing task retains the source-reported reference redocking and molecular-dynamics analyses, without prescribing their software implementation or adding a separate binding-site-validity stage.

### Workflow-fidelity review

| Requirement | Source location | Agent-facing treatment |
| --- | --- | --- |
| Target and queries | Methods 2.1.1 and 2.2.1 | HKII, 2NZT and all three named reference compounds remain explicit; identities and states require independent validation |
| Screening method and initial selection | Methods 2.1.1; Results 3.1.1 | 3D shape plus atom-feature similarity and up to 100 analogues/query are retained; 2D similarity alone is insufficient |
| Drug-likeness | Results 3.1.1; Tables 1–3 | Reported strict property limits are supplied; violations and justified exceptions must be explicit, and references remain controls |
| ADME/toxicity before docking | Methods 2.1.2–2.1.3; Figure 1 | Endpoint assessment and filtering precede docking; models/units/missing coverage must be recorded without supplying tool choices |
| Receptor/ligand preparation | Methods 2.2.1–2.2.2 | Preserve bound reference evidence, prepare a ligand/water-removed docking copy, assign hydrogens/charges and minimise; record repairs, representations and transformations |
| Binding assessment and selection | Methods 2.2.2; Results 3.2 | Dock candidates and controls, select top-three candidates per group and a leading candidate; derive a valid centre in the actual prepared frame while retaining stated box dimensions |
| Site interpretation | Methods 2.2.2; Tables 10–12; conflicting abstract | The task declares chain A/N-terminal as its target region, following the tabulated results; the abstract's chain B/C-terminal statement is not silently treated as equivalent |
| Dynamics preparation and duration | Methods 2.3 | 100 ps heavy-atom-restrained equilibration and 20 ns production remain required; unreported settings require justified choices |
| Dynamics comparison | Results 3.3; Figures 5–10 | Candidate/reference comparison includes backbone RMSD, residue RMSF, distances and hydrogen-bond behaviour; definitions/units must be consistent |
| Selection yields and outcomes | Abstract; Tables 1–12 | Historical retained counts, selected identities and docking scores remain evaluator-only; agents must not force those outcomes |

The invalid native-frame box centre is intentionally not supplied as an executable instruction. Platform method/control/endpoint gaps must be reported as unresolved or adapted, not hidden by a superficial tool-name match. The screening-library snapshot is part of the run inputs; using another snapshot cannot establish historical hit recovery. No scientific execution or platform capability verification is claimed by this document rewrite.

## Historical Source Provenance

The previous paper-anchored specification is retained below solely as a provenance record. Its tool lists, score anchors, historical output conventions, 240-minute limit and execution instructions do not prescribe the current agent workflow. The Evaluation Policy above and current agent-facing task take precedence.

---

# Task 007 — Structure-based discovery of human hexokinase II inhibitors for anti-dengue therapeutics

## Description

Identify candidate inhibitors of human hexokinase II (HKII) for anti-dengue therapeutics by screening analogues of alpha-D-glucose (GLC), beta-D-glucose-6-phosphate (BG6) and 2-deoxyglucose (2DG), assessing drug-likeness and ADME/toxicity, and docking candidates into HKII with AutoDock Vina. Select three ranked candidates per query and compare them with the corresponding reference. The paper assesses one finalist per query by 20 ns molecular dynamics; MD is optional for this task under the user's environment requirements (task adaptation, derived).

## Target

**Name:** Human hexokinase II (HKII)
**Protein:** Human hexokinase II; host metabolic enzyme, not a dengue-virus protein
**Disease:** Dengue
**Objective:** Identify HKII-binding candidates meeting the query-specific published Vina score anchors of −7.2, −7.8 and −6.8 kcal/mol for GLC-, BG6- and 2DG-derived candidates, respectively (benchmark criterion derived from Tables 10–12).
**Binding Region:** Chain A, N-terminal domain, following the headings of Tables 10–12 and Methods section 2.2.2.
**Data:** Query SDF structures from PubChem; ZINC compounds retrieved through USRCAT. Reported screening: 23.1 million molecules → 100 hits per query → 300 initial hits → 165 retained overall. Tables 1–3 give selected-compound identities, similarities and physicochemical properties; Tables 4–6 give ADME predictions; Tables 7–9 give toxicity predictions; Tables 10–12 give docking scores and interactions. The availability statement says data are in the article; no complete historical library snapshot, all-hit archive or raw pose/trajectory deposit is linked. Save the actual library and its provenance; new retrievals are not the original dataset snapshot.
**PDB:** 2NZT
**Structure and Context:** The paper describes two chains with N- and C-terminal domains. Its abstract mentions chain B/C-terminal results, whereas the tabulated docking scores are explicitly labelled chain A/N-terminal. Use the tabulated site for the task anchors and preserve this discrepancy in the run report.
**Reference Inputs:** Alpha-D-glucose (GLC), beta-D-glucose-6-phosphate (BG6) and 2-deoxyglucose (2DG); SDF structures with validated stereochemistry. Methods section 2.1.1 labels CHEBI identifiers as “PubChem ID” and misorders molecular formulae; resolve and record actual database identifiers before preparation.

## Design Constraints

- **Workflow:** validate 2NZT and the three query structures → USRCAT analogue screening of 23.1 million molecules → 100 hits per query (300 total) → similarity/drug-likeness/ADME/toxicity selection (165 retained overall) → AutoDock Vina docking → three ranked candidates per query → optional 20 ns MD of one finalist per query against its reference. The article reports docking results for nine analogues plus three references; it does not provide a complete docking-score table for all 165 retained compounds. Record actual stage counts and do not claim complete historical results from these selected tables.
- **Docking settings:** paper grid centre X = 43.567, Y = 35.439, Z = 36.27; box dimensions 26 × 24 × 22 Å. Centre coordinates are interpreted in Å for Vina (derived); the paper does not separately attach units to the centre tuple. It also gives an unexplained “measurement of space (1.000)” without naming an API parameter or unit; do not reinterpret this as a validated grid-spacing setting. Record the effective platform configuration. The paper does not specify exhaustiveness, random seed or Vina version; record actual settings rather than attributing defaults to the paper.
- **Receptor preparation:** retain a copy of the original complex; document chain/domain selection, removed waters and heteroatoms, hydrogen/charge preparation, and the prepared receptor actually submitted to docking. Use only preparation supplied through Boltzmann.
- **Reference validation:** the paper states that GLC and BG6 were extracted from the native complex and redocked, but gives no numerical pose-to-crystal RMSD or acceptance cutoff. Verify the actual PDB ligand identities before redocking; no independent audit of the 2NZT coordinates is claimed here. Process references and candidates with the same receptor/settings. Any reference-RMSD calculation requires a verified platform capability; Vina's pose-to-best-mode RMSD is not pose-to-crystal RMSD.
- **Drug-likeness:** the paper states HBD <5, HBA <10, MW <500 g/mol and logP <5. Report actual properties and individual violations. Table 2 gives six H-bond donors for the BG6 analogues, conflicting with the claim that all hits pass without violations; do not silently change those values.
- **ADME/toxicity:** record endpoint, units, model identity, prediction and available confidence. The Methods attributes ADME to SwissADME, while the Results includes endpoints not established as SwissADME outputs. Do not assign an endpoint or threshold to a model without evidence.
- **MD as secondary validation, optional:** Methods section 2.3 specifies GROMACS 5, GROMOS96 54a7, SPC water in a cubic box, ligand topology files from ATB, a 1.0 nm short-range Coulomb cutoff, statistical/energy data stored every 10 steps, v-rescale temperature coupling, Berendsen pressure coupling, 100 ps equilibration with heavy-atom restraints, LINCS bond constraints including hydrogen atoms and 20 ns production. Results section 3.3 instead names GROMACS 4.6.5 — paper-internal version conflict. Numerical temperature, pressure, integration timestep, salt concentration and box padding are not supplied in these methods; do not invent them. Use only an available Boltzmann MD workflow and record effective settings; OpenMM or changed force fields are adaptations, not exact GROMACS reproductions.
- **No additional QSAR, DFT, model training or wet lab:** these are task-scope constraints (derived). The paper uses pretrained prediction services; computational predictions do not establish enzyme inhibition or antiviral efficacy.

## Computational Tool Capabilities

Workflow stages and the evidence required from each. All scientific execution must use the Boltzmann small-molecule suite. Undocumented exact capabilities require verification; an unavailable required stage is reported as blocked rather than silently replaced.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Boltzmann receptor/ligand preparation; public PDB and compound records as data sources | Original and prepared structures, resolved query identities, provenance and preparation settings |
| 2. Analogue screening | Boltzmann similarity screening; verify exact USRCAT availability before claiming the paper's shape-screening method | Complete library manifest, query membership, method, scores, ranked candidates and filter counts; 2D similarity is not interchangeable with USRCAT |
| 3. Drug-likeness and ADME/toxicity | `Property_Prediction`, limited to verified available endpoints | Full property panel, model identities, units, pass/fail rules and unavailable endpoints |
| 4. Docking | Boltzmann AutoDock Vina docking; verify the current schema and effective engine/settings | Candidate and reference scores, downloadable poses and available interaction records |
| 5. MD validation, optional | Boltzmann GROMACS workflow, if its required parameterisation and controls are available | Prepared topology, simulation settings, trajectory and RMSD/RMSF/hydrogen-bond summaries; explicit omission reason if not run |
| 6. Select and report | Rank on the verified Vina protocol and report coverage against each query-specific anchor | Final ranked candidates, all Expected Output files, coverage and limitations |

**Boltzmann platform tools:**

| Tool | Role | Key Arguments |
|---|---|---|
| `Similarity_Screening` | Retrieve and rank analogues of the three reference queries; exact USRCAT method support requires verification | Query structure, library and method-specific controls; verify current schema |
| `Vina_basic_docking` | Existing task-document name for Vina docking; verify the current platform endpoint before use | Receptor, candidate/reference structures, centre coordinates and independent box dimensions; verify exposed controls |
| `Property_Prediction` | Drug-likeness and available ADME/toxicity endpoints | Compound structures and an explicit list of verified models/endpoints |
| `MDS_Gromacs`, if available | Catalogued GROMACS workflow; exact endpoint, version and parameterisation controls must be verified | Prepared complex, force field, water model, equilibration and 20 ns production |
| `MDS_openMM` | Optional MD adaptation if separately selected; not the source paper's engine | Prepared complex, supported parameterisation and 20 ns duration; verify current schema and identify engine change |

This table is a documentation-based platform mapping (derived), not a validated API payload. The Key Arguments column describes required information rather than asserting JSON key names. Older task documents use the spelling `exhaustivness`; use it only if confirmed by the current schema. Live account access, engine versions, independent box controls, exact USRCAT screening and endpoint-model equivalence have not been established. The local user manual describes Similarity Screening as 2D screening, which does not establish support for USRCAT's shape/atom-type method. DiffDock, binding-affinity prediction and MM/GBSA are not required: they are not stages of this paper's workflow.

**Other standard tools:** paper dependencies listed below are provenance only; scientific execution remains restricted to Boltzmann.

**Paper tools (verbatim):** USRCAT, SwissADME, ProTox-II, Open Babel (also misspelled OpenBable/Open Bable in the text), PyMOL, MGLTools 1.5.7, Avogadro, AutoDock Vina, GROMACS (Methods: version 5; Results: 4.6.5), Automated Topology Builder (ATB), VMD and Xmgrace. Provenance only; this list does not establish Boltzmann availability.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Initial screening | 23.1 million molecules → 100 analogues per query → 300 total initial hits → 165 retained overall; historical counts, not evidence of a deposited complete dataset |
| GLC analogue docking, Table 10 | Top-three scores −7.2, −7.0 and −6.10 kcal/mol; GLC reference −7.2 kcal/mol |
| BG6 analogue docking, Table 11 | Top-three scores −7.8, −7.4 and −7.0 kcal/mol; BG6 reference −7.9 kcal/mol |
| 2DG analogue docking, Table 12 | Top-three scores −6.8, −6.3 and −6.3 kcal/mol; 2DG reference −6.0 kcal/mol |
| Score consistency | Table 10 gives the leading GLC analogue −7.2 kcal/mol, while one Results sentence says −7.0 kcal/mol; Table 10 is the anchor |
| Docking interactions, leading GLC analogue | Table 10: 7 H-bonds; Glu260, Gln291, Phe156, Asn208, Lys173 and Asp209 listed as interacting residues |
| Docking interactions, leading BG6 analogue | Table 11: 11 H-bonds; Gly87, Asn89, Thr232, Arg91, Asp84 and Lys173 listed as interacting residues |
| Docking interactions, leading 2DG analogue | Table 12: 4 H-bonds; Asp209, Asn208, Glu294, Thr172, Thr232 and Lys173 listed as interacting residues; residue-list length is not an H-bond count |
| Interaction interpretation | Counts and residue names above are Table 10–12 transcriptions, not independently verified contacts or compulsory atom-level grading criteria; figure captions give different contact descriptions |
| GLC-group ADME, Table 4 | Candidate intestinal absorption 59.316–59.79%; logBB −0.900 to −0.786; logPS −3.552 to −3.192; CYP2D6/CYP1A2 and renal OCT2 entries all No |
| BG6-group ADME, Table 5 | Candidate intestinal absorption 0–26.376%; logBB −1.032 to −0.928; logPS −3.604 to −3.460; CYP2D6/CYP1A2 and renal OCT2 entries all No; poor absorption must not be relabelled as uniformly favourable ADME |
| 2DG-group ADME, Table 6 | Candidate intestinal absorption 86.764–87.984%; logBB −0.265 to −0.025; logPS −3.254 to −3.147; CYP2D6/CYP1A2 and renal OCT2 entries all No |
| Toxicity, Tables 7–9 | All nine listed candidates are labelled class 6; GLC-group LD50 2300–14,388 mg/kg; BG6/2DG-group LD50 5500–15,900 mg/kg; reported carcinogenicity, immunotoxicity, mutagenicity and cytotoxicity entries are Inactive. Class 6 alongside 2300 mg/kg conflicts with the text's class-VI definition of LD50 >5000 mg/kg; retain the discrepancy |
| Optional MD backbone RMSD, Results section 3.3 | GLC-group finalist approximately ±5.0 Å; BG6-group approximately ±4.0 Å; 2DG-group approximately ±0.5 Å, compared with their references; these summaries are not universal stability thresholds |
| Optional MD plot/prose conflict | Figures 7A and 8A display curves around 0.4–0.5 on axes labelled RMSD (Å), whereas Results section 3.3 reports approximately ±4.0 Å and ±5.0 Å. Plot values are visual estimates (derived), not digitised data. Preserve the conflict; do not infer corrected units or use these values for pass/fail grading. The paper's ± notation is retained as reported, not interpreted as negative RMSD |
| Optional MD H-bonds, Results section 3.3 | GLC-group finalist/reference averages 6/4; BG6-group 7/5; 2DG-group 3/6. Distinguish these MD values from docking counts and the abstract's different summaries |

## Expected Output

**Format:** `small_molecule_vs_bundle` (environment convention, derived)
**Directory:** `results/task_007/<run>/` (environment convention, derived)

The following output filenames are required by this benchmark design; they are not claimed to be files deposited by the paper's authors.

| File | Content |
|---|---|
| `input_manifest.json` | Library source/version/retrieval date, checksums, query identities, receptor provenance and exact-method coverage |
| `input_library.csv` | Every candidate input, with stable identifier, SMILES and query membership |
| `reference_ligands.sdf` | Validated structures of all three reference queries |
| `input_receptor.pdb` | Original receptor submitted to the platform; record chain selection and preparation separately |
| `screening_results.csv` | Complete analogue-screen results, method-specific similarity scores, filtering decisions and stage counts |
| `docking_scores.csv` | Candidate/reference identifiers, query group, rank, Vina score, pose file and protocol identifier |
| `docked_poses.zip` | Downloaded candidate and reference docking poses |
| `admet_panel.csv` | Property and toxicity predictions, units, model identifiers, filter rules and missing endpoints |
| `metrics.json` | Query-specific best scores, contemporaneous reference scores, anchor comparisons, stage counts, scientific completion status and optional-MD status |
| `run_report.md` | Candidate-selection rationale, effective settings, input/output inventory, paper discrepancies, platform adaptations and unresolved capabilities |

Retain all platform-exported preparation files in their original formats and record their filenames in the manifest. An exported prepared-receptor PDB is not assumed to exist. If MD is run, retain its available input settings, topologies, trajectories and analysis files; explicitly flag any required artifact that the platform does not export.

**Pass bar:** identify at least 1 candidate per query group scoring at or below −7.2 kcal/mol (GLC), −7.8 kcal/mol (BG6), and −6.8 kcal/mol (2DG), respectively, using AutoDock Vina at the tabulated chain A/N-terminal site, with complete input/pose provenance and documented drug-likeness and ADME/toxicity assessment. These one-sided query-specific criteria are benchmark-design choices derived from Tables 10–12, not author-defined pass criteria. Mark exact paper reproduction blocked if the required screening method, endpoints or docking controls are unavailable. MD omission alone is not a failure under this task's optional-MD rule.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it; environment convention, derived).
- **Reference Policy:** use the inputs and workflow in this task; do not consult the publication to obtain its selected-hit identities or copy its ranked results during a benchmark run.
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; source settings and unresolved details are identified in this document.
- **Execution:** only Boltzmann small-molecule tools; public databases are input sources. Do not call external scientific services or run standalone scientific software to fill missing capabilities.
- **Evaluation Integrity:** freeze candidate selection and rankings before comparing against the published anchors. Record every effective setting and preserve raw platform downloads. A structural validation pass is not a completed scientific benchmark.

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables during execution; the numerical anchors already supplied here may be used for evaluation.
- Report unavailable inputs or required capabilities explicitly. Do not invent datasets, prediction endpoints, platform tool names, completed jobs or reproducibility claims.

## Publication

Tanbin, S.; Ahmad Fuad, F. A.; Abdul Hamid, A. A. **Virtual Screening for Potential Inhibitors of Human Hexokinase II for the Development of Anti-Dengue Therapeutics.** BioTech 2021, 10(1), 1; published 28 December 2020. [DOI: 10.3390/biotech10010001](https://doi.org/10.3390/biotech10010001). [PMC9245486](https://pmc.ncbi.nlm.nih.gov/articles/PMC9245486/).

Source audit: original 28-page publisher PDF and PMC full-text XML, including Tables 1–12 and visual inspection of Figures 5, 7 and 8. The [document audit record](../../../research/small-molecule-virtual-screening/hkii-task007-source-audit-2026-11-06.json) distinguishes checked transcriptions from unresolved source, data and platform issues.
