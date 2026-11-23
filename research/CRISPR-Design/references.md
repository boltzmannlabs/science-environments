# CRISPR Design — references

All entries verified from primary sources during the 2026-11-10 curation sweep
(three research agents, per-URL verification; UNVERIFIED flagged in the source
workspace docs at `~/IMRAN/NOV26/cirspr-sci-env/01_tools/open_source/`).

## On-target activity (nuclease KO)

| Reference | Citation | Role |
|---|---|---|
| Rule Set 1 | Doench JG et al. Rational design of highly active sgRNAs for CRISPR-Cas9–mediated gene inactivation. *Nat Biotechnol* 32:1262–1266 (2014). doi:10.1038/nbt.3026. Data: SRA SRP045596 | first on-target regression (1,841 sgRNAs) |
| Rule Set 2 / Azimuth | Doench JG, Fusi N et al. Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nat Biotechnol* 34:184–191 (2016). PMID 26780180; PMC4744125 | GBRT on 4,390 sgRNAs; CFD off-target matrix |
| Rule Set 3 | DeWeirdt PC et al. Optimization of AsCas12a for genome editing in human cells. — **verified as**: DeWeirdt PC et al. *Nat Commun* 13:5255 (2022). doi:10.1038/s41467-022-33024-2; PMC9448816. Data: SRA PRJNA832308 | LightGBM RS3-Sequence/Target; 46,526 train + 84,609 tiling validation |
| SSC | Xu H et al. Sequence determinants of high CRISPR-Cas9 editing efficiency. *Genome Biol* 16:187 (2015) | SVM baseline |
| DeepSpCas9 | Kim HK et al. SpCas9 activity prediction by DeepSpCas9. *Science Advances* 5:eaax9249 (2019). PMID 31723604. Data: SRA SRP150719; code github.com/MyungjaeSong/Paired-Library | reference dataset: 12,832 paired measurements |
| DeepHF | Wang D et al. Optimized CRISPR guide RNA design for two SpCas9 variants. *Nat Commun* 10:4284 (2019). Data: SRA PRJNA522677; code github.com/izhangcd/DeepHF | WT/eSpCas9(1.1)/SpCas9-HF1; 80,263 pairs |
| CRISPRon | Xiang X et al. Enhancing CRISPR-Cas9 gRNA efficiency prediction by sequentially integrating a deep learning network and energy features. *Nat Commun* 12:3238 (2021). Data: GSE173708; code github.com/RTH-tools/crispron | CNN+ΔGB; ρ 0.80 internal |
| DeepCRISPR | Chuai G et al. DeepCRISPR: optimized CRISPR guide RNA design by deep learning. *Genome Biol* 19:80 (2018). code github.com/bm2-lab/DeepCRISPR (Apache-2.0) | cautionary baseline (non-transfer documented) |
| Lindel | Chen W et al. Massively parallel profiling and predictive modeling of the outcomes of CRISPR/Cas9-mediated double-strand break repair. *Nat Biotechnol* 37:213–219 (2019) | indel outcome/frameshift model; local backend verified |
| CRISPOR | Haeussler M et al. Evaluation of off-target and on-target scoring algorithms and integration into the guide RNA selection tool CRISPOR. *Genome Biol* 17:148 (2016). PMID 27380939 | meta-tool + first independent benchmark |
| CHOPCHOP v3 | Labun K et al. CHOPCHOP v3: expanding the CRISPR web toolbox beyond editing. *NAR* 47:W171–W174 (2019). doi:10.1093/nar/gkz365 | multi-nuclease design (incl. plant genomes) |
| DeepCpf1 | Kim HK et al. Deep-learning-guided design of AsCpf1 guide RNAs. *Nat Biotechnol* 36:239–241 (2018) | Cas12a activity (~15k targets) |
| DeepCpf1 (Luo) | Luo M et al. DeepCpf1: a convolutional neural network for predicting Cpf1 guide RNA activity. *BMC Bioinformatics* 20:332 (2019). PMC6567654; code github.com/lje00006/DeepCpf1 | distinct same-named method; AUC 0.846 |
| Hart screen evaluation | Hart T et al. Evaluating and Designing Genome-Wide CRISPR/SpCas9 Knockout Screens. *Nat Biotechnol* 35:568 (2017); Hart 2015 *Cell* 163:1515 (PMID 26627737) | screen-level guide-efficacy context (NOT an RS3 paper) |

### Cross-tool on-target benchmarks

| Reference | Citation | Finding |
|---|---|---|
| Haeussler 2016 | (CRISPOR paper, above) | all-scores non-training ρ 0.341–0.436; U6 vs T7/IVT split; replicate ceiling ~0.7 |
| Konstantakos 2022 | Konstantakos V et al. A guide to CRISPR reporter-free activity prediction using deep learning. *NAR* 50:3616–3637 (2022). doi:10.1093/nar/gkac209 | **key independent benchmark**: 6 training-disjoint datasets; DeepHF/DeepSpCas9 top; DeepCRISPR best on 1/6 only |
| CRISPRon comparison | Xiang 2021 (above) | cross-study correlation as low as 0.52 |
| Lukasiak 2024 | Lukasiak P et al. bioRxiv 2024.05.17.594311 (2024) | VBC vs RS3 screen-level utility; 3-guide score-based libraries match larger ones |

## Off-target / specificity

| Reference | Citation | Role |
|---|---|---|
| MIT score | Hsu PD et al. DNA targeting specificity of RNA-guided Cas9 nucleases. *Nat Biotechnol* 31:827–832 (2013). PMID 23873081 | first mismatch-penalty matrix |
| CFD | Doench 2016 (RS2 paper, above) | empirical type×position matrix; community standard |
| Elevation | Listgarten J et al. Prediction of off-target activities for the CRISPR-Cas9 system using machine learning. *Nat Biomed Eng* 2:38–47 (2018). PMC6037314; code github.com/MicrosoftResearch/Elevation (MIT) | pair + aggregate ML |
| CCTop | Stemmer M et al. CCTop: An Intuitive, Flexible and Reliable CRISPR/Cas9 Target Prediction Tool. *PLoS One* 10:e0124633 (2015) | mismatch+bulge scoring |
| CROP-IT | Singh R et al. Cas9-chromatin binding information enables more accurate CRISPR off-target prediction. *NAR* 43:118 (2015). doi:10.1093/nar/gkv575 | chromatin-aware (historical) |
| CRISOT | Chuai G et al. Genome-wide CRISPR off-target prediction and optimization using RNA–DNA interaction fingerprints. *Nat Commun* 14:7521 (2023). code github.com/bm2-lab/CRISOT (**CC BY-NC 2.0**); data Zenodo 10.5281/zenodo.8420032 | current SOTA pair scorer; non-commercial license |
| CRISPR-Net | Lin J, Wong K-C. Off-target predictions in CRISPR-Cas9 gene editing using machine learning. *Advanced Science* 7:1903562 (2020) | mismatch+indel aware NN |
| CRISPRme | Cancellieri E et al. Human genetic diversity alters off-target outcomes of therapeutic gene editing. *Nat Genet* 55:1901–1908 (2023). PMC10272994; doi:10.1038/s41588-022-01257-y | allele/population-aware off-target |
| CRISPRitz | Cancellieri E et al. CRISPRitz: rapid, high-throughput and variant-aware in silico off-target sites identification. *Bioinformatics* 36:3267–3268 (2020). PMC7141852 | VCF-aware search + bulges |
| FlashFry | McKenna A, Shendure J. FlashFry: a fast and flexible tool for large-scale CRISPR target design. *BMC Biol* 16:74 (2018) | fastest enumeration (no VCF) |

### Experimental off-target datasets

| Reference | Citation | Dataset |
|---|---|---|
| GUIDE-seq | Tsai SQ et al. GUIDE-seq enables genome-wide profiling of off-target cleavage by CRISPR-Cas9 nucleases. *Nat Biotechnol* 33:187–197 (2015). PMC4320685 | cell-based; 13 RGNs, 0–>150 OTs/guide |
| CIRCLE-seq | Tsai SQ et al. CIRCLE-seq: a highly sensitive in vitro screen for genome-wide CRISPR-Cas9 nuclease off-targets. *Nat Methods* 14:607–614 (2017). PMC5924695 | in-vitro; high-FP caveat |
| SITE-seq | Cameron DLW et al. Mapping the genomic landscape of CRISPR-Cas9 cleavage. *Nat Methods* 14:600–606 (2017). PMID 28459459 | biochemical; 12 sgRNAs / 2,047 OTs (CRISOT curation) |
| CHANGE-seq | Lazzarotto CR et al. CHANGE-seq reveals genetic and epigenetic effects on CRISPR-Cas9 genome-wide activity. *Nat Biotechnol* 38:1317–1327 (2020). PMC7652380 | **110 guides / 201,934 OTs**; SNVs affect ~15.2% |
| CHANGE-seq-BE | 2026, PMC13479990 | base-editor variant; supported an eIND |
| Kaufmann 2026 | Kaufmann KB et al. Systematic benchmarking of in silico off-target prediction tools. *Hum Gene Ther* (2026). PMID 42503868 | **key independent benchmark**: 14 tools, ~77% recall @ top-500 |

## Precision editing & regulation

| Reference | Citation | Role |
|---|---|---|
| BE-Hive | Arbab J, Shen MW, Mok B et al. Determinants of Base Editing Outcomes from Target Library Analysis and Machine Learning. *Cell* 182:463–480 (2020). PMC7384975; bystander CLI github.com/maxwshen/be_predict_bystander | 38,538 targets, 11 editors; outcome R≈0.9 |
| DeepABE/DeepCBE | Song M et al. Sequence determinants of base editing outcomes from a base-editor target library. *Nat Biotechnol* 38:1037–1043 (2020). doi:10.1038/s41587-020-0573-5; WS deepcrispr.info/DeepBaseEditor | 13,504 ABE + 14,157 CBE endogenous |
| BE-Designer | Hwang GH et al. Web- and database-based guide RNA design for CRISPR base editing. *BMC Bioinformatics* 19:542 (2018) | design-only web tool |
| BE-DICT | Marquart KF et al. Predicting base editing outcomes with an attention-based deep learning model trained on thousands of product sequences. *Nat Commun* 12:5766 (2021). doi:10.1038/s41467-021-25375-z; code github.com/uzh-dqbm-cmi/crispr | 28,294 lentiviral targets |
| DeepBE | Kim N et al. Prediction and design of base-editor outcomes with deep learning. *Nat Biotechnol* 42:484–497 (2024). doi:10.1038/s41587-023-01792-x; code github.com/NahyeKim/DeepBE (no license ⚠) | 63 editors (7 BE × 9 Cas9) |
| Sakata suite | Sakata MK et al. Base editing out-of-frame and bystander mutation prediction and optimization. *Nat Biotechnol* 38:1677–1683 (2020). code github.com/yachielab/base-editing-prediction (no license ⚠) | 13 probabilistic editor models |
| BEDICT2.0 | Kissling L et al. BEDICT 2.0 — deep-learning-based adenine base editor prediction in mammalian cells. *Genome Biol* 26:115 (2025). WS bedict.app | ABE across contexts, R 0.60–0.94 |
| BE-dataHIVE | BE-dataHIVE: harmonized base-editing datasets. *BMC Bioinformatics* 25:330 (2024). be-datahive.com; PyPI be_datahive | 460,000+ combos, 5 studies harmonized |
| DeepPE | Kim HK et al. Deep learning improves prediction of prime editing efficiency and pegRNA design. *Nat Biotechnol* 39:198–206 (2021). doi:10.1038/s41587-020-0677-y | PE2; 54,836 pairs; ρ 0.47–0.81 |
| PRIDICT v1 | Koeppel J et al. Prediction of prime editing insertion efficiencies in human cells. *Nat Biotechnol* 41:1446–1456 (2023). PMC10567557 | 3,604 insertions; R 0.70 |
| PRIDICT2.0 | Mathis N et al. Prediction of prime editing efficiencies across sequence contexts in human cells. *Nat Biotechnol* (2023, online Aug; print 42:1097, 2024). doi:10.1038/s41587-022-01613-7; WS pridict.it; CLI github.com/uzh-dqbm-cmi/PRIDICT2 | **92,423 pegRNAs; ρ 0.85/0.78** |
| ePRIDICT | Mathis N et al. *Nat Protoc* 21(4) (2026, online Aug 2025). doi:10.1038/s41596-025-01244-7 | ≤40-bp edits; chromatin features |
| DeepPrime | Yu G et al. Engineered prime editors with enhanced processivity and editing scope. *Cell* 186:2256–2272 (2023). doi:10.1016/j.cell.2023.03.034; code github.com/hkimlab/DeepPrime | 338,996 pairs; 8 PE systems × 7 cell types |
| OptiPrime | Hsu A, Chen PJ et al. Mechanistic machine learning for prediction of prime editing outcomes. *Nat Biotechnol* (online 2026-08-12). doi:10.1038/s41587-026-03261-7 | mechanistic ML (Liu lab) |
| PrimeDesign | Hsu JY et al. PrimeDesign software for rapid and simplified design of prime editing guide RNAs. *Nat Commun* 12:5442 (2021) | design-only |
| Richardson HDR rules | Richardson CD et al. Enhancing homology-directed genome editing by catalytically active and inactive CRISPR-Cas9 using asymmetric donor DNA. *Nat Biotechnol* 34:339–344 (2016). doi:10.1038/nbt.3481 | asymmetric ssODN donor rule |
| CUNE | O'Brien AR et al. Prediction of CRISPR spacer and homology-directed repair outcome using machine learning. *Sci Rep* 9:2788 (2019). PMC6391469 | HDR classifier; n=30 (thin) |
| Horlbeck CRISPRi | Horlbeck MA et al. Compact and highly active CRISPRi libraries for human and mouse cell lines. *eLife* 5:e19760 (2016). PMC5094855; code github.com/mhorlbeck/ScreenProcessing | TSS-window + chromatin activity rules |
| Sanson libraries | Sanson KR et al. Optimized libraries for CRISPR-Cas9 genetic screening with multiple modalities. *Nat Commun* 9:5416 (2018). PMC6303322 | Dolcetto/Calabrese |
| CRISPRoff | Nuñez JK et al. Genome-wide programmable transcriptional memory by CRISPR-based epigenome editing. *Cell* 184:2503–2519 (2021). doi:10.1016/j.cell.2021.03.025. Data: GEO GSE168012 | 3 design rules; ~116k tiling |

## Cas13, diagnostics, libraries

| Reference | Citation | Role |
|---|---|---|
| Cas13design | Wessels HH et al. Massively parallel Cas13 screens reveal constraints on targeting, lability and transcript knockdown. *Nat Biotechnol* 38:1342–1351 (2020). PMID 32518401; WS cas13design.nygenome.org; code gitlab.com/sanjanalab/cas13 | 24,460 guides; spacer nt 15–21 intolerance |
| TIGER | Wessels HH, Stirn K et al. *Nat Biotechnol* (2023). doi:10.1038/s41587-023-01830-8; WS huggingface.co/spaces/Knowles-Lab/tiger | ~200,000 RfxCas13d guides with systematic mismatches/indels; CNN; current Cas13 reference |
| EasyDesign | Huang J et al. EasyDesign: machine-learning-aided crRNA design for CRISPR-Cas12a-based diagnostics. *iMeta* (2024). doi:10.1002/imt2.214; PMC11316927; WS crispr.zhejianglab.com | ρ 0.812 on 11,496 cases |
| PrimedSherlock | Mann T et al. PrimedSHRLOCK: automated design and evaluation of primed Sherlock assays. *BMC Bioinformatics* 23:185 (2022). PMC9569017 | rule-based Cas12 assay design |
| WGE | Hodgkins A et al. WGE: a CRISPR guide database and design tool. *Bioinformatics* 31:3688–3690 (2015). doi:10.1093/bioinformatics/btv308 | paired-guide + exome off-targets |
| Kuscu 2019 | Kuscu C et al. *Genome Res* (2019) — multi-gene targeting / mismatch tolerance confounds pooled screens (title string not re-verified; content per curation sweep) | multi-targeting avoidance |
| Pérez 2021 CSC | Pérez AR et al. CSC software. *Bioinformatics* (2021). PMC8578331 | off-target-mediated gRNA-depletion correction |
| Álvarez 2022 | Álvarez MM et al. TP53-dependent toxicity — *Genome Biol*/PMC9352712 (2022) | cut-toxicity confound in screens |
| GuideScan2 | GuideScan2 (2022) — complete guide catalog with multi-locus-binding exclusion (citation UNVERIFIED) | library design |
| CRISPR-GATE | *Brief Bioinform* 26(5):bbaf575 (2025) | curated tool repository/guide |

## Therapeutic anchors

| Reference | Citation | Public content |
|---|---|---|
| exa-cel SBRA | FDA OBRR Cellular, Tissue and Gene Therapies Advisory Committee briefing, 2023-10-31 / SBRA PDF fda.gov/media/175179/download (2023-12-08) | guide "SPY101" (100-nt synthetic sgRNA, SpCas9, BCL11A erythroid enhancer GATA1-motif); sequence redacted (b)(4); off-target assessment incl. CPS1-intron candidate |
| exa-cel BLA | BLA 125787 review, fda.gov/media/173414/download | in-silico + cellular off-target assessment record |
| NTLA-2001 | Fontana M et al. *NEJM* (2024). PMID 39555828; phase update *NEJM* (2025). doi:10.1056/NEJMoa2510209 | LNP Cas9-mRNA + TTR guide; sequence patent-bound (WO2020/172823 family, UNVERIFIED directly) |
| VERVE-101 | Musunuru K et al. *NEJM* (2023); Lee RG et al. *Circulation* 148:706 (2023). doi:10.1161/CIRCULATIONAHA.122.062132 | PCSK9 splice-disrupting ABE; exact guide sequence UNVERIFIED in open text |
| VERVE-102 | *NEJM* (2026). doi:10.1056/NEJMoa2601283 | GalNAc-LNP successor |

## Local installation evidence

| Asset | Location | Verified |
|---|---|---|
| crisprDesign/crisprScore/crisprBase + R library | `~/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38/reference_software/` + `bootstrap/R-library` | run 2026-11-05 (KIF11) |
| Lindel model (crisprScoreData EH6128) | `runs/20261105T102927Z/lindel-runtime/` | interface test PASS (score 0.798) |
| Bowtie 1.3.1 + GRCh38.p14 index + GENCODE 49 | same run dir | checksum-verified FASTA; off-target policy v1.0 |
