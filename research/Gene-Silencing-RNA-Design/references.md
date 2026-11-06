# Gene Silencing RNA Design — central sources

## Local installations inspected and reused (read-only)
- siRNA-Bench platform `~/IMRAN/OCT26/siRNA-Bench` — 23-model audited registry (`models/model_registry.yaml`), evaluation harness, GENCODE v50 index, siSPOTR/6merDB tables.
- OligoFormer/RNA-FM integration `~/.sci/profiles/imran/workspace/oligoformer-integration` — generation backend, checkpoint hashes pinned in the source workspace freeze manifests.
- ToolUniverse 1.5.7 (mims-harvard/Zitnik Lab) — arXiv:2509.23426, Apache-2.0; 2,719 API tools; RNAcentral/Ensembl/VEP/ClinVar/dbSNP/GTEx/HPA/PubMed/OpenTargets subset documented.
- Original skill lineage: `sirna-harness` v2.0.0 and `task-specific-siRNA-Design` v0.4 (governance/taxonomy inheritance; independence-gate history).

## Retrieved scientific literature (verified via PubMed/PMC during curation)
- Bai Y et al. OligoFormer. Bioinformatics 2024. PMID 39321261 (paper AUC 0.8163 reference).
- Pelossof R et al. SplashRNA. Nat Biotechnol 2017. PMID 28263295.
- Hornung V et al. Nat Med 2005. PMID 15723075 (UGUGU/TLR7). Judge AD et al. Nat Biotechnol 2005. PMID 15778705.
- Kleinman ME et al. Nature 2008. PMID 18368052 (TLR3 length class effect).
- Hornung V et al. Science 2006. PMID 17038590 (5'ppp/RIG-I).
- Gao K et al. Nat Commun 2018. PMID 30283072 (6merDB seed viability).
- Kusenda M et al. NAR 2012. PMID 22941647 (siSPOTR POTS).
- Sciabola M et al. 2013 (Simone/Sciabola-322 cohort, Hep3B; local dataset with transcripts).
- Naito Y et al. siDirect. BMC Bioinformatics 2009, PMID 19948054; server v2.1 verified live 2026-11-03.
- Approved siRNA drug sequences: FDA GINAS API (precision.fda.gov/ginas) + EMA EPAR systematic names + patent corroboration; full per-drug source lines in the source workspace `02_benchmarks/published_designs_and_datasets.md` §A1.

## Full curation detail
Source workspace: `~/IMRAN/NOV26/siRNA-Design-Task-Specific` — 64-tool registry
(`01_tools/TOOL_REGISTRY.csv`), five verified curation reports, heuristics audit, validation
program, benchmark reports, and protocol freeze manifests v1.0–v1.2.
