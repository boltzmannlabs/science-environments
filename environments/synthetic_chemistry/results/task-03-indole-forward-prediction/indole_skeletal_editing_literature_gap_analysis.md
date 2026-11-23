# Research audit: forward predictions for indole skeletal editing

## Update: primary supporting information supplied and examined

After the initial audit, the user supplied `science.aec3587_sm (1).pdf` (335 PDF pages). The PDF text extractor `read_file` failed, but Poppler `pdftotext -layout` successfully extracted the text. SI page numbers below refer to the document's printed pages. The main article full text remains inaccessible. The source document's molecular diagrams were not fully recoverable from text extraction, so isotope identity and intermediates below are interpreted conservatively.

**Corrections to earlier audit:** (1) The substrate and product headings in the SI now independently substantiate all ten reaction/product associations and the substituent connectivities in the user-supplied SMILES; this was a comparison of chemical names and SMILES, not an automated digitization of the paper's graphical structures. (2) The actual reaction was not just UV and solvent: all ten products cite procedure A with TFA, inert atmosphere and irradiation. (3) An earlier secondary-source-based comparison erroneously combined nine steps with 17.8%; SI Table S2 instead lists **13 steps, 17.8%** for ref. 80 and **nine steps, 15.6%** for ref. 86. (4) The full paper and SI were not sent to any predictor and no jobs were rerun.

### Verified outcome and prediction comparison

The yield values are isolated product yields in SI pp. 55–58, **not** model predictions, and the preparation yields are separate yields for amide substrate preparation in SI pp. 14–18. All product examples reference procedure A. Counts, nearest-candidate ranks and scores derive from manually transcribed model outputs; they await structured-output reconciliation.

| Input ID → SI product | Reported amide preparation yield | Photochemical isolated product yield | Candidates | Exact match in transcribed candidates | Closest similarity (original output rank) |
|---|---:|---:|---:|---|---|
| 1a → 2a, phenyl | 87% | 87% | 29 | No | 0.5333 (2) |
| 1b → 2b, p-methylphenyl | 88% | 88% | 28 | No | 0.5000 (10) |
| 1c → 2c, 3,5-dimethylphenyl | 65% | 96% | 31 | No | 0.4062 (15) |
| 1d → 2d, p-tert-butylphenyl | 85% | 71% | 30 | No | 0.4898 (3) |
| 1e → 2e, p-biphenyl | 54% | 95% | 29 | No | 0.5106 (3) |
| 1f → 2f, p-fluorophenyl | 75% | 93% | 30 | No | 0.4898 (4) |
| 1g → 2g, p-chlorophenyl | 72% | 83% | 30 | No | 0.4898 (4) |
| 1j → 2j, o-methoxyphenyl | 78% | 65% | 30 | No | 0.4706 (9) |
| 1k → 2k, m-methoxyphenyl | 73% | 91% | 30 | No | 0.4444 (15) |
| 1l → 2l, p-methoxyphenyl | 75% | 83% | 30 | No | 0.4706 (8) |

These single reported yields do not establish reproducibility, statistical significance, general electronic trends or a fair route-to-route comparison. The product descriptions each include NMR and HRMS. The named structure with the corresponding phenyl substituent agrees with each provided reference SMILES. The similarity score is a fingerprint resemblance, not a success probability or yield.

### Published conditions and controls (SI pp. 51–54)

- Each of the ten products is attributed to general procedure A: tertiary amide, TFA, 1,4-dioxane, argon and 280 nm LED irradiation at room temperature, then basic workup and purification. The SI distinguishes a nominal 280 nm LED from the separately measured device maximum 284.4 nm. Original benchmark input specified only substrate and dioxane; model calls contained only substrate SMILES, not dioxane, TFA, light, or atmosphere. A valid molecule-only submission is therefore not an experimental replication.
- In the 1a optimization screen, the authors report **no product in the dark** under their initial conditions. Relative to their initial 254 nm screen, changing acid, wavelength or atmosphere alters measured outcome. The nominal 280 nm optimized entry reports 90% by 1H NMR and 87% isolated; under air at 254 nm, TFA and 18 h, the NMR yield was 38%, versus 73% under the corresponding inert condition. These are separate screen entries; do not compare across multiple varying conditions as though a one-variable controlled experiment.
- General procedures B and C, with formic acid and different solvent/duration choices, support other substrate classes; the ten examples specifically cite A. The supplementary document alone does not establish that B or C improves any of these ten substrates.
- The paper's synthesis of the required tertiary amide precursors is a distinct preparative sequence: the substrates are not necessarily commercial, and the reported amide preparation yields are not the photoreaction yields. If the downstream target requires an unsubstituted primary side-chain amine, removal of N-neopentyl is an additional transformation; SI §3.3 reports 60% isolated for one 2a-derived deprotection example. It is not needed to produce 2a itself.

### Mechanism and competition (SI pp. 96–103)

The paper abstract proposes a [2+2] cycloaddition, retro-[2+2] opening, decarbonylation and cyclization cascade; the SI provides isotope-labeling, CO gas-detection, intermediate-detection, crossover and computational studies. GC and GC–MS were used to detect CO; the SI also reports a 13CO experiment. The isotope-scheme diagrams did not survive text extraction sufficiently for independent atom-by-atom verification, so do not claim the particular labeled atom's fate from this extraction alone. Unlabeled structure equality cannot demonstrate single-carbon replacement: distinct atom histories lead to the same molecular graph.

An **N-methylindole control 1cp**, not one of the ten inputs, gave a species designated 2cp detected by crude 1H NMR after irradiation; separate acid/air treatment gave an isolated derivative 3cp (80%). This is evidence for an experimentally probed competing intermediate family, not proof any selected beta-carboline was formed, nor a yield for the original ten. The SI includes computed competing cyclization and H-atom-transfer pathways; calculations and indirect characterizations should not be equated to observed concentrations or prove that an AI candidate is stable.

### Route comparison correction and limits

SI §4 reports its quebrachamine sequence with isolated step yields 80%, 90%, 51% and 85%, and SI Table S2 presents four steps, 31% overall. In that table the 17.8% comparator is **13 steps** (ref. 80), not nine. The nine-step 15.6% and 5.4% entries are different references. The SI table does not establish identical starting-material conventions, scale, cost or asymmetric synthesis; published (+)/(−) routes should not be treated as strictly comparable to the reported racemic target. None of the ten benchmark substrates is the reported quebrachamine key precursor, so those jobs did not test the total synthesis.

### Priority actions after SI review

1. Restore actual machine-readable job outputs and verify all 297 manually transcribed candidates, candidate order and exact-match calculations; do not re-submit. Benchmark extraction quality separately.
2. Record substrate-preparation steps, 280 nm nominal irradiation, TFA, dioxane, argon and product workup in a reaction schema. Use a condition-capable authorized predictor in a separately labeled experiment; the existing substrate-only runs cannot test condition sensitivity.
3. Evaluate photochemical reaction-family recognition and atom histories independently of graph-only exact matching. A prospective holdout of structurally diverse related photoreactions and negative controls is necessary for meaningful external accuracy estimates.
4. Compare any genuinely proposed alternative with the same target, specificity, scale, number of transformations, substrate availability, purification burden, environmental and safety profile. No model candidate has been demonstrated superior; the observed 65–96% isolated yields for these ten are a meaningful baseline, not a prediction of performance on other substrates.

---

## Initial audit (retained for provenance; superseded where the SI update above differs)

This audit compares 10 original single-substrate model calls with the subsequently user-supplied reference SMILES. Primary publication: Zhang, Lang, Luo, Han, Zeng and Li, “Precision indole skeletal editing for single-carbon replacement,” Science 392, 512–518 (2026), DOI https://doi.org/10.1126/science.aec3587. The publisher-provided abstract was accessible through Crossref (https://api.crossref.org/works/10.1126%2Fscience.aec3587); Science's full-text page returned HTTP 403. NSFC secondary coverage is https://www.nsfc.gov.cn/english/site_1/news/A2/2026/07-07/550.html. Related publication conclusions below are derived from their indexed abstracts, not full-text experimental procedures. The supplied https://github.com/boltzmannlabs/science-environments/blob/Rebolt/environments/Tasks/task2_forward_prediction_indole_skeletal_editing.md is a proposed benchmark outline that expressly says detailed ground truth must be filled from the paper/SI; it is not itself an independently verified scope table.

The separate supplied literature-product file is treated as user-supplied reference, not authenticated against paper figures or SI. Do not infer per-substrate isolated yields, scope success, product codes, spectral assignments, wavelength, irradiation dose, duration, apparatus, catalyst, concentration, temperature, scale, reaction or purification procedures. Paper figures/SI are needed to establish whether the IDs refer to substrates or product labels and to verify conditions and yields.

## Executive results

All 10 unique substrates were submitted once, with `forward_reaction` and `target_mol` containing the exact substrate SMILES. All returned completed. The schema offered no solvent or light-condition field, so 1,4-dioxane and UV were not encoded. The user supplied dioxane but did not supply light in the original blind task. Thus the execution was operationally valid for a deliberately context-free benchmark but not a faithful simulation of the published photochemistry. Unchanged substrate and chemically divergent answers are possible in this underdetermined setting.

RDKit identity checks for selected predictions and manually transcribed returned candidates show 0/10 exact matches against the user-provided references. The first reaction had 29 candidates; the other nine had 268 total. Their candidate counts in reference order are 29, 28, 31, 30, 29, 30, 30, 30, 30, 30: 297 transcribed candidate entries overall. Top-1 and top-3 matches are also 0/10 under the same caveat. The manual transcription must be independently reconciled to the original structured records. The model's scores are not validated probabilities of feasibility, conversion, yield or photochemical selectivity. The top-1 output for 1a, 1f and 1j was starting material, not the agent-selected cyclic product; the initial 1d selected cyclic structure did not appear in its returned list.

Mechanistic source evidence: the primary abstract reports photoactivated pendant-amide, C2 single-carbon replacement and substitution, isotope labeling and a cascade involving [2+2] cycloaddition, retro-[2+2] ring opening, decarbonylation, and cyclization. NSFC describes UV irradiation. It reports a four-step quebrachamine synthesis at 31% overall yield versus a prior nine-step route at 17.8%, but independent verification of the prior comparison, experimental scope, and route matching needs the full paper and original cited route.

Each reactant formula minus its supplied reference formula is exactly CO (validated using RDKit). This is consistent with net decarbonylation and shows the product is not simply a carbon-deletion outcome: the source reports replacement of one indole skeleton carbon, but gross formula does not prove which atom becomes CO, the source of the new ring carbon, a mechanistic order, or detect carbon-isotope exchange. Verify atom origins with the authors' isotope experiments and an atom-mapped reaction validated against the SI.

## Reaction-by-reaction comparison

All matches below refer only to exact structures in the user-provided reference file, not independent paper validation. Predicted selected cyclic structures uniformly contain one more carbon and one more ring than references; their formulas differ by +C. A shared molecular formula is not enough for identity, and the selected cyclic products are not observed or proven stable intermediates.

|ID| Aryl group carried by amide and in supplied reference | Returned candidates | Exact candidate match | Nearest Morgan Tanimoto (original rank) | Agent-selected candidate's provenance |
|---|---|---:|---|---|---|
|1a|Phenyl|29|none|0.5333 (2)|returned rank 4|
|1b|p-Methylphenyl|28|none|0.5000 (10)|returned rank 1|
|1c|3,5-Dimethylphenyl|31|none|0.4062 (15)|returned rank 1|
|1d|p-tert-Butylphenyl|30|none|0.4898 (3)|not returned; agent-extrapolated|
|1e|p-Phenylphenyl|29|none|0.5106 (3)|returned rank 17|
|1f|p-Fluorophenyl|30|none|0.4898 (4)|returned rank 3|
|1g|p-Chlorophenyl|30|none|0.4898 (4)|returned rank 5|
|1j|o-Methoxyphenyl|30|none|0.4706 (9)|returned rank 4|
|1k|m-Methoxyphenyl|30|none|0.4444 (15)|returned rank 1|
|1l|p-Methoxyphenyl|30|none|0.4706 (8)|returned rank 1|

For 1a,1b,1d,1e,1f,1g,1j,1k,1l the highest fingerprint similarity belongs to the same secondary amine without the C2 aryl substituent: `CC(C)(C)CNCCc1c[nH]c2ccccc12`. It retains indole, side-chain and N-neopentyl motifs but does not make the key bond. For 1c the highest-scoring related structure retains the benzamide and has C2-formyl rather than C2-aryl substitution. The fingerprints are Morgan radius 2/2048 bits, Tanimoto; they are not chemical yields. Full table and SMILES are in `indole_literature_similarity_all_candidates.csv` for 1b–1l; 1a was independently checked in the preceding analysis. Canonical comparisons ignore isotope-replacement provenance when structures are supplied unlabeled.

## Assessment of predicted alternative chemistry

1. **Agent-selected beta-carboline-like products:** graph-valid but have a new C–C bond from indole C2 to the former amide carbonyl carbon, loss of O, and amide carbonyl carbon retained. This is not the paper's decarbonylative replacement outcome. It resembles a Pictet–Spengler-type carbon framework, but the original N-acyl tertiary amide is not the ordinary free tryptamine/aldehyde precursor. A separate tryptamine + aldehyde route is a different synthesis, not evidence for this direct conversion. The asymmetric Pictet–Spengler abstract at https://doi.org/10.1021/ja057444l demonstrates the general condensation class, not these specific tertiary-N structures. Distinguish cyclic product from potential transient; neither observed intermediate nor feasible final outcome under Zhang conditions established.
2. **Open-chain deacylated amine:** chemically recognizable and, as a fragment, scored close; it omits the defining aryl group and does not by itself furnish the desired product. Alternative deacylation chemistry requires suitable reagents/conditions or photochemical pathway; it was not shown experimentally by the cited paper in the accessible abstract.
3. **Amide-to-benzyl amine candidates:** graph-valid formal deoxygenation/reduction products; plausible only with appropriate reducing chemistry and selectivity demonstration, not evidenced from dioxane alone or by the Science abstract. They place aryl on the amine via CH2, not on indole C2.
4. **Indole C2 halogenation/thionation/N-methylation entries:** require atom or fragment sources not provided in input, and the model was not given such reagents. Corresponding formal transformations can exist under other reagent sets, but scores do not establish these conditions or predicted selectivity. Some scores rank high even when required reagent is unspecified.
5. **Unchanged substrate:** a reasonable explicit competing outcome without light or complete conditions, not automatically the dominant experimental outcome under irradiation.
6. **Other photochemical families:** the paper's reference https://doi.org/10.1021/jo1002714 reports photochemical tryptamine-linked alkylidene-malonate cycloaddition/retro-Mannich cascades leading to spiro and oxindole structures; this is distinct substrate and outcome, not proof for these amides. https://doi.org/10.1021/ol052955y reports a related enaminone photocycloaddition/retro-Mannich pathway. Both demonstrate a reason to explore reaction networks, not interchangeable evidence for the current outputs.
7. **Other single-atom edits:** https://doi.org/10.1038/s41557-024-01468-2 reports fluoroalkyl-carbene indole edits including carbon insertion and other outcomes; https://doi.org/10.1038/s41557-024-01680-0 reports asymmetric dearomative insertion forming trifluoromethylated 3,4-dihydroquinolines; https://doi.org/10.1126/science.add1383 reports nitrene N insertion to quinazoline/quinoxaline products. These use different reagent classes and give different scaffold edits; they are not direct substitutes for Zhang's C2 replacement/arylation without further route planning and evaluation.
8. **Tertiary-amide bond chemistry:** https://doi.org/10.1002/anie.202202794 reports acid/iodide catalyzed transamidation of unactivated tertiary amides with amines. It is not a demonstration of photodeacylation or this desired product.

## Recommendations and route-level comparison

- Preserve and audit exact inputs, distinct job IDs, complete structured model outputs, candidate rank, score type and selection policy. Disclose that 1d was an agent extrapolation. Do not rely on manually copied output when original machine-readable records can be retrieved with authorized tools.
- Separate blind molecule-only evaluation from a condition-aware test using the documented UV parameters, solvent and full inputs. If the selected forward predictor has no condition field, do not silently pretend it models them; select an authorized condition-aware predictor only after a provider/workflow decision. Do not rerun the same job with references as inputs and label the result blinded.
- Ask for the actual paper and SI, then build a reaction-level table linking exact figure/product identifier to substrate, isolated product, yield, analytical evidence, photon wavelength/dose, reaction scale, workup and controls. Verify source mappings before reporting experimental scope trend or top-k evaluation.
- Map atoms and byproducts in a consistent isotopically aware graph pipeline; enumerate predicted C2 substitution with carbon-replacement pathway as distinct from direct C2 functionalization and ring closure. Validate predicted isotope placements against the primary paper. Unlabeled product identity alone cannot test skeletal replacement.
- Apply molecule/reagent inventory and atom conservation checks; flag missing halogenating agents, sulfur sources, methylating agents, oxidants and reductants. Add photon/photochemical activation as a distinct condition, not a reactant atom. Do not discard all missing-reagent candidates as inherently impossible—mark condition-dependent.
- Report raw ranked top-k and agent selection separately, including unchanged substrate, extraction errors, invalid structures, formula differences and ties; use an external holdout, record model version/cutoff, and assess calibration, not unverifiable leakage assumptions. A single 10-case closely related substrate set is insufficient for a general performance estimate; Spearman model-score vs isolated-yield is not valid without paired confirmed yields and validation of the model score's meaning.
- Treat competing paths as target-specific hypotheses. If ring-closed beta-carbolines are desired, compare an independently documented tryptamine/aldehyde Pictet–Spengler design; if the supplied C2-aryl amine is desired, compare the published photochemical edit to appropriate documented C2 arylation or indole-assembly strategies on compatible substrates, accounting for protection, regiospecificity, isotope fate, stages, yields and waste. No claim of superiority is justified without direct comparative data.
- If the original goal is quebrachamine, obtain exact structures and routes for four-step 31% vs nine-step 17.8%, document counting conventions, stereochemical and scale comparability, purity and bottlenecks. No quebrachamine intermediate was submitted in these 10 jobs, so that benchmark objective remains untested.
- Photochemical development needs qualified review of UV exposure, reactor geometry/light distribution, controls, and potential carbon-monoxide release under local protocols. Model output does not provide operating parameters.

## References

1. Zhang et al., Science (2026), primary abstract: https://doi.org/10.1126/science.aec3587; accessible metadata/abstract https://api.crossref.org/works/10.1126%2Fscience.aec3587.
2. NSFC report of Zhang et al. (secondary source): https://www.nsfc.gov.cn/english/site_1/news/A2/2026/07-07/550.html.
3. Intramolecular photocycloaddition/retro-Mannich tryptamine study: https://doi.org/10.1021/jo1002714.
4. Enaminone photocycloaddition/retro-Mannich: https://doi.org/10.1021/ol052955y.
5. Fluoroalkyl-carbene divergent indole edits: https://doi.org/10.1038/s41557-024-01468-2.
6. Asymmetric dearomative indole/pyrrole edits: https://doi.org/10.1038/s41557-024-01680-0.
7. Indole nitrogen insertion: https://doi.org/10.1126/science.add1383.
8. Catalytic asymmetric Pictet–Spengler: https://doi.org/10.1021/ja057444l.
9. Transamidation of unactivated tertiary amides: https://doi.org/10.1002/anie.202202794.
