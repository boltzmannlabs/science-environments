# Executive summary

IMPORTANT SPECIFICITY TRIAGE: 14 of the20 assessed shared-core panel have no detected perfect outside-KRAS match on either strand; 6 fail this additional optional sequence-exclusivity diagnostic. Failed IDs: NM_004985.5_site_1264, NM_004985.5_site_5140, NM_004985.5_site_312, NM_004985.5_site_5218, NM_004985.5_site_1033, NM_004985.5_site_249. Those entries are retained as flagged comparisons, not KRAS-exclusive recommendations. The exact-exclusive review subset is reference_exact_exclusivity_subset.csv; lack of a perfect match is not safety qualification. Exact outside-gene alignments and their strand/gene identities are in candidate_tool_outputs/exact_unintended_matches.csv.

14 of20 Ridge estimates are outside0–100. They are preserved raw, flagged as linear-model extrapolation, not literal knockdown percentages, and substantially limit confidence in the numeric ordering.

No HRAS/NRAS full19nt0–2 substitution matches detected in this20-candidate/both-strand/reference scope; this does not exclude seed-mediated RAS-family effects. KRASP1 near/exact hits are explicitly retained. Family-specific6/7/8nt seed opportunities are annotated separately in RAS_family_seed_annotations.csv.

Optional diagnostic FAILED does not silently change the frozen primary operational ranking or impose a new biological tolerance. The required specificity-acceptance gate is still BLOCKED_MISSING_EVIDENCE for all candidates. The six known diagnostic failures are separate from missing evidence and from native operational filter failures.

Shared-reference screening completed with 20 nonoverlapping research candidates passing the configured operational filters and exact coverage of all four declared references. This is a useful computational milestone, not experimental confirmation. Mutation arm remains BLOCKED_PENDING_MUTATION_SPECIFICATION with zero mutation-selective candidates.

{
  "primary_reference": "NM_004985.5",
  "declared_reference_count": 4,
  "generated_records": 5288,
  "unique_guides": 5288,
  "exact_shared_all_four_sites": 5243,
  "Ridge_scored": 5288,
  "native_OligoFormer_scored": 5288,
  "corrected_OligoFormer_scored": 100,
  "RN_Ai_success": 100,
  "RNAiSpline_success": 100,
  "native_assessed": 100,
  "shared_operational_passers_within_assessed": 81,
  "selected_shared_candidates": 20,
  "shared_screening_milestone": "COMPLETED",
  "both_strand_specificity_screened": 20,
  "reference_site_observations": 80,
  "Ridge_extrapolations_in_shortlist": 14,
  "perfect_reference_gene_exclusivity_pass": 14,
  "perfect_reference_gene_exclusivity_fail": 6,
  "mutation_arm_status": "BLOCKED_PENDING_MUTATION_SPECIFICATION",
  "mutation_selective_candidates_generated": 0,
  "fully_qualified": 0,
  "overall_scientific_status": "PARTIAL",
  "screening_failed_records": 2942,
  "downstream_not_run_records": 5188
}

# Objective and arm separation

Arm1: shared KRAS silencing against the four declared transcript sequences, primary coordinates NM_004985.5. Arm2: mutation-selective design is explicitly blocked until exact nucleotide/reference context and mutant-versus-wild-type objective are supplied. Shared transcript variants are not specified tumor mutations. No hypothetical mutant sequence or mutation-selective guide was created.

# Verified reference identities

NM_004985.5 | length 5306 | CDS 191–757 | protein NP_004976.2 | FASTA SHA256 ab88235bd19e809059a86916a5e5bd302e6508e92492a25ea6825e40715550b6 | NCBI source https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_004985.5&rettype=fasta&retmode=text
NM_033360.4 | length 5430 | CDS 191–760 | protein NP_203524.1 | FASTA SHA256 d0b991227e88818c4f002e1f34696bc19c89b892749415e3c956ce9793a24152 | NCBI source https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_033360.4&rettype=fasta&retmode=text
NM_001369786.1 | length 5417 | CDS 178–747 | protein NP_001356715.1 | FASTA SHA256 2d6e61349904a816902407738e37a471522d30ed9134c3c2f3931750bc0b9e5d | NCBI source https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_001369786.1&rettype=fasta&retmode=text
NM_001369787.1 | length 5293 | CDS 178–744 | protein NP_001356716.1 | FASTA SHA256 cd7f8a8a744c6b754806c90d5de7bda8e468088baf9cf56f2743d570fc491e6d | NCBI source https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_001369787.1&rettype=fasta&retmode=text

Original NCBI GenBank inventory bytes were revalidated by SHA and reused; fresh exact-accession FASTA bytes independently matched GenBank sequences, human KRAS identity and translated CDS annotation. Original/derived files and original retrieval times/URLs are in reference_raw/, references/, transcript_isoform_audit.csv and target_retrieval_manifest.json. No coordinates transplanted between versions.

# Shared regions and coordinate mapping

shared_block_1 | primary 1–164 | {"NM_004985.5": [1, 164], "NM_033360.4": [1, 164], "NM_001369786.1": [1, 164], "NM_001369787.1": [1, 164]}
shared_block_2 | primary 178–639 | {"NM_004985.5": [178, 639], "NM_033360.4": [178, 639], "NM_001369786.1": [165, 626], "NM_001369787.1": [165, 626]}
shared_block_3 | primary 640–5306 | {"NM_004985.5": [640, 5306], "NM_033360.4": [764, 5430], "NM_001369786.1": [751, 5417], "NM_001369787.1": [627, 5293]}

These are maximal collinear exact blocks in one explicit optimal alignment. Exact per19nt sequence lookup, including all occurrence positions, is authoritative for candidate coverage. Repeats can admit alternative alignment placements; all reported block substrings and all candidate sites were explicitly checked. CDS-versus-UTR classes are reference-specific. Reference-level mapping alone does not establish mutant or cell-context specificity.

# Tool ecosystem and scientific provenance

Existing local siRNA-only harness predicates and frozen Ridge model were reused, together with the actual native OligoFormer/RNA-FM job recorded in generation_manifest.json, native siRNA-Bench run(s) in batch_state.json, ViennaRNA, GENCODEv50, exact scanner and source seed annotations. No new models installed, no sequence upload to external prediction services and no cloud jobs. Native model/feature/source hashes and actual raw native job outputs are retained. Checkpoint absence for siRNADiscovery remains code_only, never successful inference.

# Generation and representation policy

All 5288 actual native generated rows are preserved. Native19nt guide/passenger cores,5to3, target-templated exact complementarity; no arbitrary overhangs or chemistry inferred. Shared eligibility was imposed by exact site presence in all four references. Source functionality/unique primary/full-context checks preceded bounded native evaluation; no new unscored generator replaced OligoFormer. Frozen Ridge selected evaluation order; no weights/thresholds fitted to KRAS outcomes.

# Executed assessment coverage

{
  "primary_reference": "NM_004985.5",
  "declared_reference_count": 4,
  "generated_records": 5288,
  "unique_guides": 5288,
  "exact_shared_all_four_sites": 5243,
  "Ridge_scored": 5288,
  "native_OligoFormer_scored": 5288,
  "corrected_OligoFormer_scored": 100,
  "RN_Ai_success": 100,
  "RNAiSpline_success": 100,
  "native_assessed": 100,
  "shared_operational_passers_within_assessed": 81,
  "selected_shared_candidates": 20,
  "shared_screening_milestone": "COMPLETED",
  "both_strand_specificity_screened": 20,
  "reference_site_observations": 80,
  "Ridge_extrapolations_in_shortlist": 14,
  "perfect_reference_gene_exclusivity_pass": 14,
  "perfect_reference_gene_exclusivity_fail": 6,
  "mutation_arm_status": "BLOCKED_PENDING_MUTATION_SPECIFICATION",
  "mutation_selective_candidates_generated": 0,
  "fully_qualified": 0,
  "overall_scientific_status": "PARTIAL",
  "screening_failed_records": 2942,
  "downstream_not_run_records": 5188
}

Only the actual100-record batch scope (or counts above if extended) has fresh RN.Ai/RNAiSpline/native Bench deep evidence; remaining records retain explicit NOT_RUN. Corrected OligoFormer reused the actual native RNA-FM feature arrays for that scope; no backbone rerun or overwrite of native train-mode scores. A tool-interface timeout at420s did not kill the original job: it was recovered and ingested at completion, not resubmitted.

# Ranked shared core designs

1 | NM_004985.5_site_280 | UAUUGUUGGAUCAUAUUCG | CGAAUAUGAUCCAACAAUA | Ridge 106.6131 | RN.Ai 87.22 | Spline 0.6897 | exact-reference exclusivity PASSED
2 | NM_004985.5_site_1264 | UAACUUUACAUUCAUCAGG | CCUGAUGAAUGUAAAGUUA | Ridge 105.0906 | RN.Ai 91.96 | Spline 0.6874 | exact-reference exclusivity FAILED
3 | NM_004985.5_site_1391 | UAUAAUAGUUUCCAUUGCC | GGCAAUGGAAACUAUUAUA | Ridge 104.8076 | RN.Ai 88.44 | Spline 0.6847 | exact-reference exclusivity PASSED
4 | NM_004985.5_site_5140 | UUUGAUAUGACCAACAUUC | GAAUGUUGGUCAUAUCAAA | Ridge 103.8096 | RN.Ai 90.82 | Spline 0.6873 | exact-reference exclusivity FAILED
5 | NM_004985.5_site_312 | UCAAUUACUACUUGCUUCC | GGAAGCAAGUAGUAAUUGA | Ridge 103.5458 | RN.Ai 87.76 | Spline 0.6851 | exact-reference exclusivity FAILED
6 | NM_004985.5_site_3954 | UAAAUAUCCCCUCAUAAGC | GCUUAUGAGGGGAUAUUUA | Ridge 103.261 | RN.Ai 90.8 | Spline 0.6841 | exact-reference exclusivity PASSED
7 | NM_004985.5_site_5218 | UUUUAGAUCACUUCACAGC | GCUGUGAAGUGAUCUAAAA | Ridge 102.3231 | RN.Ai 90.68 | Spline 0.6874 | exact-reference exclusivity FAILED
8 | NM_004985.5_site_1033 | AUAAGAAGUAAUCAACUGC | GCAGUUGAUUACUUCUUAU | Ridge 102.0255 | RN.Ai 86.64 | Spline 0.682 | exact-reference exclusivity FAILED
9 | NM_004985.5_site_1710 | UAAUAAGCUAUAACUGGCC | GGCCAGUUAUAGCUUAUUA | Ridge 102.0053 | RN.Ai 87.59 | Spline 0.6824 | exact-reference exclusivity PASSED
10 | NM_004985.5_site_2417 | UUGACAAAUAAGUGUAUCC | GGAUACACUUAUUUGUCAA | Ridge 101.9337 | RN.Ai 88.94 | Spline 0.6873 | exact-reference exclusivity PASSED
11 | NM_004985.5_site_4256 | UUAAAUAGAGCCUAGAAUG | CAUUCUAGGCUCUAUUUAA | Ridge 101.7049 | RN.Ai 90.47 | Spline 0.6828 | exact-reference exclusivity PASSED
12 | NM_004985.5_site_1494 | AUGGUUGCUAUAAUAAUCC | GGAUUAUUAUAGCAACCAU | Ridge 100.7198 | RN.Ai 89.68 | Spline 0.6857 | exact-reference exclusivity PASSED
13 | NM_004985.5_site_3802 | UUACAUAGAAGUUUCCUUG | CAAGGAAACUUCUAUGUAA | Ridge 100.4076 | RN.Ai 89.88 | Spline 0.6865 | exact-reference exclusivity PASSED
14 | NM_004985.5_site_3668 | UGAAUAUCUGACAUACACC | GGUGUAUGUCAGAUAUUCA | Ridge 100.2017 | RN.Ai 89.06 | Spline 0.6844 | exact-reference exclusivity PASSED
15 | NM_004985.5_site_2547 | UAAUAUGGAAGAAGAGUCC | GGACUCUUCUUCCAUAUUA | Ridge 99.7293 | RN.Ai 87.83 | Spline 0.676 | exact-reference exclusivity PASSED
16 | NM_004985.5_site_1912 | UUGAUUUGUCAGCAGGACC | GGUCCUGCUGACAAAUCAA | Ridge 99.708 | RN.Ai 87.28 | Spline 0.6842 | exact-reference exclusivity PASSED
17 | NM_004985.5_site_4174 | UUAAUGCCUAAGUCUAUGU | ACAUAGACUUAGGCAUUAA | Ridge 99.6074 | RN.Ai 83.94 | Spline 0.677 | exact-reference exclusivity PASSED
18 | NM_004985.5_site_2875 | UUAAAUUCUCCUUCCACUG | CAGUGGAAGGAGAAUUUAA | Ridge 99.0907 | RN.Ai 90.1 | Spline 0.6864 | exact-reference exclusivity PASSED
19 | NM_004985.5_site_1517 | UAGCAUGUAAAUAUAGCCC | GGGCUAUAUUUACAUGCUA | Ridge 98.8299 | RN.Ai 92.0 | Spline 0.6835 | exact-reference exclusivity PASSED
20 | NM_004985.5_site_249 | UUCUGAAUUAGCUGUAUCG | CGAUACAGCUAAUUCAGAA | Ridge 97.8858 | RN.Ai 86.62 | Spline 0.6856 | exact-reference exclusivity FAILED

Both strand sequences are5to3 RNA. Full evidence is in top_shared_candidates.csv; lean sequences in top20_sequences.csv. This is a Ridge-ordered computational review panel, not a statistically proved biological ordering. Numeric near-ties are exploratory.

# Critical candidate rationale and alternatives

## NM_004985.5_site_280 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAUUGUUGGAUCAUAUUCG
Passenger5to3: CGAAUAUGAUCCAACAAUA
Primary target positions 280–298; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=106.6131025423868; RN.Ai predicted inhibition=87.22%; RNAiSpline class probability=0.6897. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 1, "RN.Ai-Predict": 17, "RNAiSpline": 1, "OligoFormer_native": 8, "OligoFormer_corrected": 8, "siRNA-Bench": 15, "combined_frozen_v1": 7}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [280], "NM_033360.4": [280], "NM_001369786.1": [267], "NM_001369787.1": [267]}. Region classes by reference: {"NM_004985.5": "CDS", "NM_033360.4": "CDS", "NM_001369786.1": "CDS", "NM_001369787.1": "CDS"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.584567172631579; duplex deltaG=-26.5kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.584567172631579, "NM_033360.4": 0.584567172631579, "NM_001369786.1": 0.584567172631579, "NM_001369787.1": 0.584567172631579}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=1/3 (transcript alignments, not unique genes or measured repression). Guide genes=["KRASP1"]; passenger genes=["ENSG00000300059", "FAM120AOS"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=74214/59027. Source guide/passenger neutral-scaffold viability=81.1/69.8. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1264 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAACUUUACAUUCAUCAGG
Passenger5to3: CCUGAUGAAUGUAAAGUUA
Primary target positions 1264–1282; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=105.090578467834; RN.Ai predicted inhibition=91.96%; RNAiSpline class probability=0.6874. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 2, "RN.Ai-Predict": 2, "RNAiSpline": 2, "OligoFormer_native": 10, "OligoFormer_corrected": 12, "siRNA-Bench": 14, "combined_frozen_v1": 20}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1264], "NM_033360.4": [1388], "NM_001369786.1": [1375], "NM_001369787.1": [1251]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.49953380000000003; duplex deltaG=-26.8kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.49953380000000003, "NM_033360.4": 0.49953380000000003, "NM_001369786.1": 0.49953380000000003, "NM_001369787.1": 0.49953380000000003}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=57/15 (transcript alignments, not unique genes or measured repression). Guide genes=["C10orf88", "CACNB2", "DNAJA4", "USP3-AS1", "VWC2"]; passenger genes=["ETFRF1", "NBEAL1", "USP3"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=98551/113670. Source guide/passenger neutral-scaffold viability=79.5/81.8. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1391 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAUAAUAGUUUCCAUUGCC
Passenger5to3: GGCAAUGGAAACUAUUAUA
Primary target positions 1391–1409; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=104.80763209597012; RN.Ai predicted inhibition=88.44%; RNAiSpline class probability=0.6847. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 3, "RN.Ai-Predict": 12, "RNAiSpline": 11, "OligoFormer_native": 11, "OligoFormer_corrected": 13, "siRNA-Bench": 1, "combined_frozen_v1": 6}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1391], "NM_033360.4": [1515], "NM_001369786.1": [1502], "NM_001369787.1": [1378]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6186460421052631; duplex deltaG=-27.1kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6186460421052631, "NM_033360.4": 0.6186460421052631, "NM_001369786.1": 0.6186460421052631, "NM_001369787.1": 0.6186460421052631}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=30/3 (transcript alignments, not unique genes or measured repression). Guide genes=["BAALC", "BANK1", "CUBN", "DLGAP5", "SACS"]; passenger genes=["ENSG00000280088", "ERN1", "MSC-AS1"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=61446/89450. Source guide/passenger neutral-scaffold viability=95.0/75.6. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_5140 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUUGAUAUGACCAACAUUC
Passenger5to3: GAAUGUUGGUCAUAUCAAA
Primary target positions 5140–5158; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=103.80955571222447; RN.Ai predicted inhibition=90.82%; RNAiSpline class probability=0.6873. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 4, "RN.Ai-Predict": 3, "RNAiSpline": 4, "OligoFormer_native": 4, "OligoFormer_corrected": 3, "siRNA-Bench": 12, "combined_frozen_v1": 10}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [5140], "NM_033360.4": [5264], "NM_001369786.1": [5251], "NM_001369787.1": [5127]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5675875163157894; duplex deltaG=-27.0kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5675875163157894, "NM_033360.4": 0.5675875163157894, "NM_001369786.1": 0.5675875163157894, "NM_001369787.1": 0.5675875163157894}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=1/23 (transcript alignments, not unique genes or measured repression). Guide genes=["ENSG00000279209"]; passenger genes=["E2F3P2", "ETFRF1", "KLHL8"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=72740/90082. Source guide/passenger neutral-scaffold viability=89.6/81.2. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_312 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UCAAUUACUACUUGCUUCC
Passenger5to3: GGAAGCAAGUAGUAAUUGA
Primary target positions 312–330; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=103.54577509066698; RN.Ai predicted inhibition=87.76%; RNAiSpline class probability=0.6851. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 5, "RN.Ai-Predict": 14, "RNAiSpline": 10, "OligoFormer_native": 2, "OligoFormer_corrected": 2, "siRNA-Bench": 5, "combined_frozen_v1": 4}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [312], "NM_033360.4": [312], "NM_001369786.1": [299], "NM_001369787.1": [299]}. Region classes by reference: {"NM_004985.5": "CDS", "NM_033360.4": "CDS", "NM_001369786.1": "CDS", "NM_001369787.1": "CDS"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6613607210526316; duplex deltaG=-29.1kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6613607210526316, "NM_033360.4": 0.6613607210526316, "NM_001369786.1": 0.6613607210526316, "NM_001369787.1": 0.6613607210526316}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=10/0 (transcript alignments, not unique genes or measured repression). Guide genes=["KRASP1", "RUNX2", "XPOTP3"]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=51770/103586. Source guide/passenger neutral-scaffold viability=90.9/72.7. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_3954 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAAAUAUCCCCUCAUAAGC
Passenger5to3: GCUUAUGAGGGGAUAUUUA
Primary target positions 3954–3972; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=103.26102833083826; RN.Ai predicted inhibition=90.8%; RNAiSpline class probability=0.6841. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 6, "RN.Ai-Predict": 4, "RNAiSpline": 14, "OligoFormer_native": 7, "OligoFormer_corrected": 5, "siRNA-Bench": 8, "combined_frozen_v1": 3}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [3954], "NM_033360.4": [4078], "NM_001369786.1": [4065], "NM_001369787.1": [3941]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5893469684210526; duplex deltaG=-29.7kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5893469684210526, "NM_033360.4": 0.5893469684210526, "NM_001369786.1": 0.5893469684210526, "NM_001369787.1": 0.5893469684210526}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=0/2 (transcript alignments, not unique genes or measured repression). Guide genes=[]; passenger genes=["ZNRD2-DT"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=106024/48861. Source guide/passenger neutral-scaffold viability=97.1/84.7. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_5218 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUUUAGAUCACUUCACAGC
Passenger5to3: GCUGUGAAGUGAUCUAAAA
Primary target positions 5218–5236; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=102.32305519337467; RN.Ai predicted inhibition=90.68%; RNAiSpline class probability=0.6874. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 7, "RN.Ai-Predict": 5, "RNAiSpline": 2, "OligoFormer_native": 6, "OligoFormer_corrected": 6, "siRNA-Bench": 10, "combined_frozen_v1": 12}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [5218], "NM_033360.4": [5342], "NM_001369786.1": [5329], "NM_001369787.1": [5205]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.4170488894736842; duplex deltaG=-29.1kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.4170488894736842, "NM_033360.4": 0.4170488894736842, "NM_001369786.1": 0.4170488894736842, "NM_001369787.1": 0.4170488894736842}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=6/4 (transcript alignments, not unique genes or measured repression). Guide genes=["CELSR1", "LINC02241"]; passenger genes=["ETFRF1", "NF1"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=73577/119678. Source guide/passenger neutral-scaffold viability=90.7/69.6. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1033 — computational screening passed; exploratory shared-reference candidate

Guide5to3: AUAAGAAGUAAUCAACUGC
Passenger5to3: GCAGUUGAUUACUUCUUAU
Primary target positions 1033–1051; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=102.02550150659033; RN.Ai predicted inhibition=86.64%; RNAiSpline class probability=0.682. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 8, "RN.Ai-Predict": 18, "RNAiSpline": 18, "OligoFormer_native": 16, "OligoFormer_corrected": 18, "siRNA-Bench": 2, "combined_frozen_v1": 17}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1033], "NM_033360.4": [1157], "NM_001369786.1": [1144], "NM_001369787.1": [1020]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.767118852631579; duplex deltaG=-26.9kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.767118852631579, "NM_033360.4": 0.767118852631579, "NM_001369786.1": 0.767118852631579, "NM_001369787.1": 0.767118852631579}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=14/18 (transcript alignments, not unique genes or measured repression). Guide genes=["ENSG00000257060", "PDCD4"]; passenger genes=["ETFRF1", "HULC", "LCT", "NDFIP2", "RPL6P14", "USP9YP13", "USP9YP19", "USP9YP22", "USP9YP3", "USP9YP4", "USP9YP8"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=76547/80471. Source guide/passenger neutral-scaffold viability=80.2/71.6. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1710 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAAUAAGCUAUAACUGGCC
Passenger5to3: GGCCAGUUAUAGCUUAUUA
Primary target positions 1710–1728; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=102.00533214101146; RN.Ai predicted inhibition=87.59%; RNAiSpline class probability=0.6824. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 9, "RN.Ai-Predict": 15, "RNAiSpline": 17, "OligoFormer_native": 5, "OligoFormer_corrected": 7, "siRNA-Bench": 7, "combined_frozen_v1": 5}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1710], "NM_033360.4": [1834], "NM_001369786.1": [1821], "NM_001369787.1": [1697]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5991505578947368; duplex deltaG=-29.5kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5991505578947368, "NM_033360.4": 0.5991505578947368, "NM_001369786.1": 0.5991505578947368, "NM_001369787.1": 0.5991505578947368}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=8/0 (transcript alignments, not unique genes or measured repression). Guide genes=["LINC01102"]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=66082/85638. Source guide/passenger neutral-scaffold viability=92.9/50.9. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_2417 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUGACAAAUAAGUGUAUCC
Passenger5to3: GGAUACACUUAUUUGUCAA
Primary target positions 2417–2435; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=101.93369879773549; RN.Ai predicted inhibition=88.94%; RNAiSpline class probability=0.6873. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 10, "RN.Ai-Predict": 11, "RNAiSpline": 4, "OligoFormer_native": 9, "OligoFormer_corrected": 9, "siRNA-Bench": 11, "combined_frozen_v1": 1}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [2417], "NM_033360.4": [2541], "NM_001369786.1": [2528], "NM_001369787.1": [2404]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6427963368421054; duplex deltaG=-27.0kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6427963368421054, "NM_033360.4": 0.6427963368421054, "NM_001369786.1": 0.6427963368421054, "NM_001369787.1": 0.6427963368421054}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=2/2 (transcript alignments, not unique genes or measured repression). Guide genes=["PRXL2A"]; passenger genes=["ANXA2R-AS1", "RIOX2"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=110673/44590. Source guide/passenger neutral-scaffold viability=98.2/68.0. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_4256 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUAAAUAGAGCCUAGAAUG
Passenger5to3: CAUUCUAGGCUCUAUUUAA
Primary target positions 4256–4274; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=101.70490855234065; RN.Ai predicted inhibition=90.47%; RNAiSpline class probability=0.6828. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 11, "RN.Ai-Predict": 6, "RNAiSpline": 16, "OligoFormer_native": 12, "OligoFormer_corrected": 14, "siRNA-Bench": 3, "combined_frozen_v1": 15}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [4256], "NM_033360.4": [4380], "NM_001369786.1": [4367], "NM_001369787.1": [4243]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5301611215789473; duplex deltaG=-27.2kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5301611215789473, "NM_033360.4": 0.5301611215789473, "NM_001369786.1": 0.5301611215789473, "NM_001369787.1": 0.5301611215789473}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=2/27 (transcript alignments, not unique genes or measured repression). Guide genes=["KLHL35", "SPOPL-DT"]; passenger genes=["RNF152", "ZNF638"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=70654/57852. Source guide/passenger neutral-scaffold viability=90.2/73.7. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1494 — computational screening passed; exploratory shared-reference candidate

Guide5to3: AUGGUUGCUAUAAUAAUCC
Passenger5to3: GGAUUAUUAUAGCAACCAU
Primary target positions 1494–1512; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=100.7198178599586; RN.Ai predicted inhibition=89.68%; RNAiSpline class probability=0.6857. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 12, "RN.Ai-Predict": 9, "RNAiSpline": 8, "OligoFormer_native": 19, "OligoFormer_corrected": 20, "siRNA-Bench": 18, "combined_frozen_v1": 11}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1494], "NM_033360.4": [1618], "NM_001369786.1": [1605], "NM_001369787.1": [1481]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5835702789473685; duplex deltaG=-27.3kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5835702789473685, "NM_033360.4": 0.5835702789473685, "NM_001369786.1": 0.5835702789473685, "NM_001369787.1": 0.5835702789473685}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=21/1 (transcript alignments, not unique genes or measured repression). Guide genes=["INO80", "LAMTOR5-AS1", "LRP1B", "PARP6"]; passenger genes=["MFSD1P1"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=74475/62307. Source guide/passenger neutral-scaffold viability=90.0/63.2. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_3802 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUACAUAGAAGUUUCCUUG
Passenger5to3: CAAGGAAACUUCUAUGUAA
Primary target positions 3802–3820; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=100.40764074291847; RN.Ai predicted inhibition=89.88%; RNAiSpline class probability=0.6865. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 13, "RN.Ai-Predict": 8, "RNAiSpline": 6, "OligoFormer_native": 13, "OligoFormer_corrected": 11, "siRNA-Bench": 6, "combined_frozen_v1": 16}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [3802], "NM_033360.4": [3926], "NM_001369786.1": [3913], "NM_001369787.1": [3789]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5536166315789474; duplex deltaG=-26.7kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5536166315789474, "NM_033360.4": 0.5536166315789474, "NM_001369786.1": 0.5536166315789474, "NM_001369787.1": 0.5536166315789474}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=3/6 (transcript alignments, not unique genes or measured repression). Guide genes=["COP1-DT"]; passenger genes=["COPA"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=50938/169240. Source guide/passenger neutral-scaffold viability=78.4/92.3. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_3668 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UGAAUAUCUGACAUACACC
Passenger5to3: GGUGUAUGUCAGAUAUUCA
Primary target positions 3668–3686; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=100.20174472154835; RN.Ai predicted inhibition=89.06%; RNAiSpline class probability=0.6844. Ridge extrapolation flag=True. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 14, "RN.Ai-Predict": 10, "RNAiSpline": 12, "OligoFormer_native": 17, "OligoFormer_corrected": 16, "siRNA-Bench": 20, "combined_frozen_v1": 14}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [3668], "NM_033360.4": [3792], "NM_001369786.1": [3779], "NM_001369787.1": [3655]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.36462453157894736; duplex deltaG=-29.8kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.36462453157894736, "NM_033360.4": 0.36462453157894736, "NM_001369786.1": 0.36462453157894736, "NM_001369787.1": 0.36462453157894736}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=0/0 (transcript alignments, not unique genes or measured repression). Guide genes=[]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=58623/49171. Source guide/passenger neutral-scaffold viability=69.8/46.3. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_2547 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAAUAUGGAAGAAGAGUCC
Passenger5to3: GGACUCUUCUUCCAUAUUA
Primary target positions 2547–2565; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=99.72929014049728; RN.Ai predicted inhibition=87.83%; RNAiSpline class probability=0.676. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 15, "RN.Ai-Predict": 13, "RNAiSpline": 20, "OligoFormer_native": 18, "OligoFormer_corrected": 10, "siRNA-Bench": 4, "combined_frozen_v1": 9}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [2547], "NM_033360.4": [2671], "NM_001369786.1": [2658], "NM_001369787.1": [2534]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.7111382068421053; duplex deltaG=-29.7kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.7111382068421053, "NM_033360.4": 0.7111382068421053, "NM_001369786.1": 0.7111382068421053, "NM_001369787.1": 0.7111382068421053}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=10/3 (transcript alignments, not unique genes or measured repression). Guide genes=["DGKE"]; passenger genes=["AKR1C2"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=69155/76743. Source guide/passenger neutral-scaffold viability=88.0/44.0. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1912 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUGAUUUGUCAGCAGGACC
Passenger5to3: GGUCCUGCUGACAAAUCAA
Primary target positions 1912–1930; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=99.70797415945259; RN.Ai predicted inhibition=87.28%; RNAiSpline class probability=0.6842. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 16, "RN.Ai-Predict": 16, "RNAiSpline": 13, "OligoFormer_native": 20, "OligoFormer_corrected": 19, "siRNA-Bench": 13, "combined_frozen_v1": 19}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1912], "NM_033360.4": [2036], "NM_001369786.1": [2023], "NM_001369787.1": [1899]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5163983631578947; duplex deltaG=-33.5kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5163983631578947, "NM_033360.4": 0.5163983631578947, "NM_001369786.1": 0.5163983631578947, "NM_001369787.1": 0.5163983631578947}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=2/0 (transcript alignments, not unique genes or measured repression). Guide genes=["HS1BP3", "HTATIP2"]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=90172/121789. Source guide/passenger neutral-scaffold viability=80.0/61.3. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_4174 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUAAUGCCUAAGUCUAUGU
Passenger5to3: ACAUAGACUUAGGCAUUAA
Primary target positions 4174–4192; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=99.6074149122926; RN.Ai predicted inhibition=83.94%; RNAiSpline class probability=0.677. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 17, "RN.Ai-Predict": 20, "RNAiSpline": 19, "OligoFormer_native": 14, "OligoFormer_corrected": 17, "siRNA-Bench": 19, "combined_frozen_v1": 13}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [4174], "NM_033360.4": [4298], "NM_001369786.1": [4285], "NM_001369787.1": [4161]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6858776736842106; duplex deltaG=-27.8kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6858776736842106, "NM_033360.4": 0.6858776736842106, "NM_001369786.1": 0.6858776736842106, "NM_001369787.1": 0.6858776736842106}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=7/0 (transcript alignments, not unique genes or measured repression). Guide genes=["REPS2", "SERPINA12"]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=50987/51530. Source guide/passenger neutral-scaffold viability=61.2/75.5. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_2875 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUAAAUUCUCCUUCCACUG
Passenger5to3: CAGUGGAAGGAGAAUUUAA
Primary target positions 2875–2893; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=99.09067418822107; RN.Ai predicted inhibition=90.1%; RNAiSpline class probability=0.6864. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 18, "RN.Ai-Predict": 7, "RNAiSpline": 7, "OligoFormer_native": 1, "OligoFormer_corrected": 1, "siRNA-Bench": 9, "combined_frozen_v1": 18}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [2875], "NM_033360.4": [2999], "NM_001369786.1": [2986], "NM_001369787.1": [2862]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.5710490894736843; duplex deltaG=-28.9kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.5710490894736843, "NM_033360.4": 0.5710490894736843, "NM_001369786.1": 0.5710490894736843, "NM_001369787.1": 0.5710490894736843}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=52/23 (transcript alignments, not unique genes or measured repression). Guide genes=["CXCL13", "ENSG00000289177", "ENSG00000290729", "ENSG00000293385", "ENSG00000294129", "ETFDH", "LINC00174", "OFCC1", "RSL24D1", "STIL", "TDRD12"]; passenger genes=["DDX52", "LRATD2"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=93252/96697. Source guide/passenger neutral-scaffold viability=82.6/44.5. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_1517 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UAGCAUGUAAAUAUAGCCC
Passenger5to3: GGGCUAUAUUUACAUGCUA
Primary target positions 1517–1535; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=98.82985195812338; RN.Ai predicted inhibition=92.0%; RNAiSpline class probability=0.6835. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 19, "RN.Ai-Predict": 1, "RNAiSpline": 15, "OligoFormer_native": 15, "OligoFormer_corrected": 15, "siRNA-Bench": 16, "combined_frozen_v1": 2}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [1517], "NM_033360.4": [1641], "NM_001369786.1": [1628], "NM_001369787.1": [1504]}. Region classes by reference: {"NM_004985.5": "3prime_UTR", "NM_033360.4": "3prime_UTR", "NM_001369786.1": "3prime_UTR", "NM_001369787.1": "3prime_UTR"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6210482842105263; duplex deltaG=-29.7kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6210482842105263, "NM_033360.4": 0.6210482842105263, "NM_001369786.1": 0.6210482842105263, "NM_001369787.1": 0.6210482842105263}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=0/1 (transcript alignments, not unique genes or measured repression). Guide genes=[]; passenger genes=["MBTPS1"]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=90452/33648. Source guide/passenger neutral-scaffold viability=86.1/27.3. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=PASSED; disposition=REVIEW_NEAR_MATCH_SEED_AND_CONTEXT_RISK. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

## NM_004985.5_site_249 — computational screening passed; exploratory shared-reference candidate

Guide5to3: UUCUGAAUUAGCUGUAUCG
Passenger5to3: CGAUACAGCUAAUUCAGAA
Primary target positions 249–267; paired19nt RNA cores, no overhang/chemistry inference.

Why selected: exact coverage of all four declared references, unique primary site/full context, native functionality and unchanged operational filters pass, then diverse Ridge priority. Ridge=97.88577628713259; RN.Ai predicted inhibition=86.62%; RNAiSpline class probability=0.6856. Ridge extrapolation flag=False. None is measured knockdown.

Predictor ranks on identical20-candidate scope: {"Ridge": 20, "RN.Ai-Predict": 19, "RNAiSpline": 9, "OligoFormer_native": 3, "OligoFormer_corrected": 4, "siRNA-Bench": 17, "combined_frozen_v1": 8}. Different models/modes share development sources or checkpoint inputs; agreement is not independent confirmation. Corrected OligoFormer is separate eval mode, not proved biological superiority.

Exact mapped reference positions: {"NM_004985.5": [249], "NM_033360.4": [249], "NM_001369786.1": [236], "NM_001369787.1": [236]}. Region classes by reference: {"NM_004985.5": "CDS", "NM_033360.4": "CDS", "NM_001369786.1": "CDS", "NM_001369787.1": "CDS"}. Shared RNA sites can be CDS in one isoform and UTR in another. This does not establish mutation selectivity or uniform cellular efficacy.

Structure: primary local accessibility=0.6299359315789473; duplex deltaG=-28.7kcal/mol. Per-reference accessibility: {"NM_004985.5": 0.6299359315789473, "NM_033360.4": 0.6299359315789473, "NM_001369786.1": 0.6300448315789474, "NM_001369787.1": 0.6300448315789474}. Features are computed support, not measured accessibility/knockdown.

Specificity: unintended guide/passenger0–2 substitution alignment counts=2/0 (transcript alignments, not unique genes or measured repression). Guide genes=["KRASP1", "RAC1P8"]; passenger genes=[]. Family/pseudogene details in RAS_family_hits.csv. Skipped ambiguity, gaps/variants, reference/annotation completeness and expression limit conclusions.

Seed risk: guide/passenger7nt unintended transcript counts=125377/69940. Source guide/passenger neutral-scaffold viability=81.5/68.0. Low source viability is an adverse annotation, not measured toxicity of this duplex, and passenger loading is unknown.

Why an alternative could be preferable: perfect-reference gene-exclusivity diagnostic=FAILED; disposition=NOT_KRAS_EXCLUSIVE_PERFECT_OUTSIDE_GENE_MATCH. A failure means a perfect outside-KRAS match exists and this is not a KRAS-exclusive sequence recommendation; acceptance is unresolved rather than presumed safe. Another candidate may have lower full/seed burden, more favorable passenger annotations or greater predicted accessibility despite lower Ridge. No target-specific calibration or measured efficacy supports a precise biological ordering. Context, chemistry, normal-cell KRAS effects and experimental results could reverse preference.

Qualification remains blocked only for the explicitly listed missing evidence: specificity_risk_acceptance, immune_risk, final_duplex_chemistry, delivery_and_assay_context, experimental_efficacy, independent_validation. Shared targeting is not mutant-selective and need not spare wild-type KRAS. A future mutation intersecting a site could also change binding; no mutation was constructed or tested.

# Transcript coverage and context-specific evidence

{
  "reference_site_observations": 80,
  "distinct_new_efficacy_inputs": 0,
  "distinct_new_structure_contexts": 1,
  "new_structure_contexts": [
    {
      "folder": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/KRAS_siRNA_case_study/shared_arm_20261021T061324Z/candidate_tool_outputs/cross_isoform_accessibility/context_1",
      "input_sha256": "de760efa0317906c36815deeed4babee94c403b6656dfbcf4fd843833e1ca269",
      "region_relative": [
        81,
        99
      ]
    }
  ],
  "source_model_input_reuse": "only exact guide+57nt sequence identity; not independent confirmation or uniform measured efficacy",
  "mutation_arm": "BLOCKED_PENDING_MUTATION_SPECIFICATION"
}

All sites are independently mapped to each exact reference. Identical guide+57nt inputs reuse actual primary efficacy outputs; no repeated inference is counted as independent confirmation. A distinct folding context was evaluated only when needed. RNA-context model equivalence does not prove uniform biological knockdown or expression of these isoforms in an intended tumor.

# Full-length specificity and RAS-family risk

{
  "reference": "/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/references/gencode.v50.transcripts.fa",
  "reference_sha256": "179bbe798a0e455d05b9456ab5f7ef51bffdcab6118d4697ea3219181c5e7c93",
  "release": "GENCODE v50",
  "global_seed_table": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/features/global_seeds.csv",
  "global_seed_sha256": "ff8d0f3dbdd4fc07604933227462aba2a07937d7d42de9b81579f8e65476abda",
  "intended_scope": "all annotated KRAS transcripts; declared four-reference coverage assessed independently; other KRAS isoforms recorded as on-gene",
  "intended_reference_count": 30,
  "primary_full_sequence_reference_matches": 1,
  "scanner": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/exact_matches",
  "scanner_sha256": "1e3a163056082da7203fce03221255e95aa95fb91df17f01ecf05967c285eec9",
  "scope": "forward-reference ungapped19nt exact0/1/2 substitution windows of both strand-binding queries; non-ACGT windows skipped, no gaps/genomic variants, transcript alignment counts not expression/repression",
  "seed_definition": "reverse complement of strand positions2..7/8/9; overlapping whole-transcript occurrences/transcript counts, not UTR-only; all annotated KRAS gene counts subtracted",
  "shortlist_count": 20,
  "RAS_family_hit_count": 3
}

Both strands were screened at0/1/2 substitutions on forward unambiguous transcript windows. Raw hits and HRAS/NRAS/KRAS-related non-KRAS matches are retained separately. All annotated KRAS is on-gene for this shared arm; the declared four-reference coverage is a separate requirement. Counts are transcript alignments and not measured repression, unique-gene counts, or expression-weighted risk. Ambiguous windows, indels, personal genomic variants and genes missing from the reference limit sensitivity. No off-target-free claim.

IMPORTANT SPECIFICITY TRIAGE: 14 of the20 assessed shared-core panel have no detected perfect outside-KRAS match on either strand; 6 fail this additional optional sequence-exclusivity diagnostic. Failed IDs: NM_004985.5_site_1264, NM_004985.5_site_5140, NM_004985.5_site_312, NM_004985.5_site_5218, NM_004985.5_site_1033, NM_004985.5_site_249. Those entries are retained as flagged comparisons, not KRAS-exclusive recommendations. The exact-exclusive review subset is reference_exact_exclusivity_subset.csv; lack of a perfect match is not safety qualification. Exact outside-gene alignments and their strand/gene identities are in candidate_tool_outputs/exact_unintended_matches.csv.

14 of20 Ridge estimates are outside0–100. They are preserved raw, flagged as linear-model extrapolation, not literal knockdown percentages, and substantially limit confidence in the numeric ordering.

No HRAS/NRAS full19nt0–2 substitution matches detected in this20-candidate/both-strand/reference scope; this does not exclude seed-mediated RAS-family effects. KRASP1 near/exact hits are explicitly retained. Family-specific6/7/8nt seed opportunities are annotated separately in RAS_family_seed_annotations.csv.

Optional diagnostic FAILED does not silently change the frozen primary operational ranking or impose a new biological tolerance. The required specificity-acceptance gate is still BLOCKED_MISSING_EVIDENCE for all candidates. The six known diagnostic failures are separate from missing evidence and from native operational filter failures.

RAS-family seed scope: {
  "gene_transcript_counts": {
    "NRAS": 7,
    "KRASP1": 1,
    "HRAS": 38
  },
  "annotation_rows": 360,
  "perfect_gene_exclusivity_pass": 14,
  "perfect_gene_exclusivity_fail": 6,
  "clinical_risk_thresholds_introduced": false,
  "mutation_selective_candidates_generated": 0
}

# Seed annotations and structural evidence

Exact strand positions2..7/8/9 seed complements were counted as overlapping whole-transcript motifs; cached global counts were reused only after reference/table SHA checks, with all annotated KRAS gene counts subtracted. This is not a UTR-only repression model. Guide/passenger viability is a neutral-scaffold cancer-cell annotation; passenger loading and duplex toxicity remain unknown. Accessibility uses declared RNAplfold W80/L40/u1 at37C; mean marginal unpaired probabilities and ideal duplex energies are supporting computed features, not measured cellular response.

# Ranking disagreement and uncertainty

Seven methods are compared only on the identical deeply characterized selected cohort in ranking_comparison.csv. The frozen combined comparator retains five equally weighted rank-utility domains: grouped RN.Ai/Spline, accessibility, both-strand near-match burden, six seed-burden utilities, guide viability. It is not calibrated efficacy. Native Bench POTS percentile direction and Bowtie score-floor issues remain disclosed. Native/corrected OligoFormer share a checkpoint, and historical predictor sources overlap; agreement is not independent confirmation. No measured-label accuracy, Precision@K/NDCG or biological confidence interval is invented.

# Failed filters versus missing qualification

Failed known research checks are in failed_screening_checks.csv and per-record filter_decisions.csv. Unperformed dependent assessments are in not_run_assessments.csv. Those are not the same as predicted biological failure. All shortlisted candidates pass the executed configured screening and exact four-reference coverage. Their full qualification remains BLOCKED_MISSING_EVIDENCE for the enumerated context/immune/specificity acceptance/chemistry/delivery/experimental requirements; fully qualified count is0.

Failed optional diagnostic gates: failed_qualification_gates.csv. These do not change the frozen initial filter thresholds.

# Mutation-selective arm: required inputs and future evidence

{
  "arm": "Mutation-selective silencing",
  "status": "BLOCKED_PENDING_MUTATION_SPECIFICATION",
  "mutation_selective_candidates_generated": 0,
  "mutation_sequence_constructed": false,
  "required_inputs": [
    {
      "field": "exact_mutation",
      "requirement": "Transcript-linked HGVS c. or equivalent exact reference/alternate nucleotide change, with protein consequence if available; preserve supplied identifier and verify reference allele"
    },
    {
      "field": "reference_context",
      "requirement": "Exact accession.version and mutant sequence or variant source; relevant flanking sequence and any linked variants/haplotype"
    },
    {
      "field": "allelic_objective",
      "requirement": "Which mutant allele to silence, whether/how much wild-type KRAS must be spared, and whether other KRAS variants should be spared"
    },
    {
      "field": "biological_context",
      "requirement": "Cell/tumor model, expressed transcript isoforms, genotype/zygosity and relevant allele-expression information when available"
    },
    {
      "field": "assay_acceptance",
      "requirement": "Mutant knockdown endpoint and acceptable wild-type suppression under specified dose/time/chemistry/delivery conditions"
    }
  ],
  "future_evidence": [
    "Exact mutant and matched wild-type site mappings and mismatch positions",
    "Both-strand transcriptome and seed specificity including HRAS/NRAS and related/pseudogene transcripts",
    "A mismatch-discrimination assessment with demonstrated applicability; ordinary perfect-match potency scores are not an allele-selectivity model",
    "Sequence/chemistry-linked mutant and wild-type experimental response under intended conditions"
  ],
  "warnings": [
    "Shared-arm candidates are not mutation-selective designs",
    "No mutant FASTA, hypothetical variant or mutation-selective candidate generated"
  ]
}

To unlock sequence design, supply an exact mutation linked to its transcript/reference nucleotide context (or a verified mutant sequence), and the desired mutant-versus-wild-type objective. Protein notation alone may not identify a unique nucleotide substitution. Cell context, chemistry, assay thresholds and delivery are separately needed for dependent qualification; their absence should not block context-independent sequence work once the mutation is truly specified. A perfect mutant match versus wild-type mismatch supports only sequence discrimination, not demonstrated allele-selective RNAi. No allele-selective candidates were generated.

# Existing measured evidence and training provenance

{
  "potential_source_records": 0,
  "matching_core_evidence_records": 0,
  "exact_construct_experimental_validation_established": false,
  "training_overlap_counts": {
    "Ridge_exact_training_equivalent": 0,
    "OligoFormer_released_sequence_equivalent": 0,
    "RNAiSpline_released_sequence_equivalent": 0
  },
  "source_inputs": [
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/benchmark_20261019T074243Z/raw/oligoformer/data/Hu.csv",
      "sha256": "fa0e5ae9c9c6afa609b458bd39762f3f8f83d1de8d248262795d7ad9eef268a0"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/benchmark_20261019T074243Z/raw/oligoformer/data/Mix.csv",
      "sha256": "10c34deaa5a02e5a168e6951edbd7144fe9025ad40a679c3defb8fe726620c87"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/benchmark_20261019T074243Z/raw/oligoformer/data/Taka.csv",
      "sha256": "221672544ee0bd7e4c8029d9e8f5d7463c90aa9f5623976002b5e68c35300b2f"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/RNAiSpline/data/Hu.csv",
      "sha256": "a484891924e0459cefa4cf8de1ffb1403e1e0a8f738c4d75f7d8209de4d4282a"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/RNAiSpline/data/Mix.csv",
      "sha256": "2f10eb19ef410e0f5482bdf03e3a493d8553b4b17ebbb01a52740f88eabb022e"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/RNAiSpline/data/Taka.csv",
      "sha256": "6cb5978172a216570f40fb0aea55f4ba035a50f105eb3b9d504df570c24b9b2e"
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/benchmark_20261019T074243Z/canonical_dataset.csv",
      "sha256": "a413bce94b3b0d70405feeae71bdbe54315d492dfc2e650908da53378f6b78b4",
      "rows": 3544
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/phase1_derived/Shabalina_valid_records.csv",
      "sha256": "9f8fa7307391399cd3dc6bb22af1d04fd87af0f5a04a6a2559acad74e101c588",
      "rows": 653
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/phase1_raw/extended_data_raw_sciabola2013_extra.csv",
      "sha256": "e3b3430674e711eb261192cf12ad67f2be4ecec6a6ed19d99d954f3e5eebbeab",
      "rows": 356
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/phase1_raw/extended_data_raw_davis2025_extra.csv",
      "sha256": "09c8b52766dd7aa3803175b235446b7236a2467cb31bb8a1c0aa803840c5592b",
      "rows": 1011
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/phase1_raw/extended_data_raw_shabalina_extra.csv",
      "sha256": "ccafd25f411c7b5d667c967e587df79ee09e8a7306cce00f6a94281bf705b7ae",
      "rows": 269
    },
    {
      "path": "/home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/results/sirna_benchmark/completion_20261019T090640Z/phase1_raw/extended_data_raw_monopoli_extra.csv",
      "sha256": "f750f137467b39bc2a27e4d58c08fe59f6ea443e17552bfe2de6338771cc19a6",
      "rows": 20
    }
  ],
  "limitation": "Exact/reverse-complement equivalence to released training references is not complete checkpoint provenance; nonmatching references do not prove independence. No current mutant allele supplied or evaluated."
}

The audited source scope is limited to the named local retained datasets. Zero source matches is not a claim that KRAS experiments do not exist elsewhere. Zero equivalence to released training references is not complete final checkpoint membership or independent validation. No exact current construct measurements were supplied.

# Reproducibility and verification

Raw reference responses, actual generation and native assessment outputs, corrected-feature hashes, both-strand hit TSV and per-reference mapping results are retained. Inputs/outputs and source versions are bound in reproducibility_manifest.json and artifact_index.csv; verify_case.py independently checks the case. Verification PASSED concerns implementation/artifact integrity, not clinical readiness. See reporting_execution_events.json for the preserved timeout/recovery and any wrapper corrections.

# Recommended next actions

Review the shared-reference shortlist and both-strand/seed risks; select intended tumor/cell, assay, final chemistry and delivery context and agree on acceptance criteria. Obtain exact-construct measured efficacy and relevant safety evidence. For Arm2, complete mutation_specification_template.json before any mutant sequence construction or design. Shared KRAS targeting has no wild-type-sparing guarantee and may affect normal KRAS-expressing cells; therapeutic window and mutant-allele coverage remain unassessed.
