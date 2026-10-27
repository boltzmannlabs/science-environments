# KRAS case study: skill-driven design versus literature-guided selection

## 1. Executive decision
Use the workflows together rather than declaring a winner. Retain the verified14-candidate computational review panel and add the two literature-supported shared-KRAS cores as separately labelled comparators for potential future assessment. No candidate is newly biologically qualified. Overall status remains PARTIAL.

The original article reports Seq2/Seq3 and their experiments; the follow-up uses the same named pan-KRAS controls.[14][1] The published pairs map into our original generated pool, but neither is in the original20 or conditional14. This is disagreement between selection policies, not a head-to-head efficacy result.

## 2. Target and comparison design
Human KRAS; primary NM_004985.5; coverage NM_033360.4, NM_001369786.1 and NM_001369787.1. Original exact-version references and computational outputs are reused after hash verification, not newly retrieved/scored references. WorkflowA is the previously executed local harness; WorkflowB is fresh literature retrieval/curation and local four-reference mapping, not another de novo generation model.

## 3. What ran versus what was reused
New: targeted web and EuropePMC discovery, original-article retrieval, source text/sequence extraction, citation checking, exact four-reference mapping and preserved-score joins. Reused: all original generation, native/eval predictors, folding, transcriptome/seed screening and original qualification. No new generation, predictor inference, folding or transcriptome screening. No local candidate/reference sequences uploaded externally.

## 4. Literature coverage and retrieval failures
Three web searches returned limited discovery pages. EuropePMC broad search returned178 hits but only15 records were retrieved/screened; targeted queries returned empty/error responses. This is not exhaustive or a systematic review. FullTextXML failed for the four selected PMCs; web extraction was partial/challenged for some sources. Original Pecot article body was recovered via NCBI BioC and Papke via retrieved article HTML. A nominal DOCX download was HTML; a valid supplementary ZIP contained only a zero-byte GIF. These are not successful supplementary-data acquisitions. Raw responses and semantic quality classifications are retained.

## 5. Literature-supported sequences
The following are the literal19nt sense/antisense pairs reported in the original paper, not newly synthesized or optimized designs.[14]

| Source label | Reported antisense5to3 | Reported sense5to3 | NM_004985.5 coordinates | Reused Ridge | Reused native OligoFormer |
|---|---|---|---|---|---|
| Pecot_Seq2 | UCGAGAAUAUCCAAGAGAC | GUCUCUUGGAUAUUCUCGA | 342–360 | 82.2502 | 1.025836 |
| Pecot_Seq3 | AAUGAUUCUGAAUUAGCUG | CAGCUAAUUCAGAAUCAUU | 254–272 | 90.7691 | 0.986377 |

Both pairs independently map exactly once to each declared reference in CDS. Seq2 maps342–360/342–360/329–347/329–347 in primary, NM_033360.4, NM_001369786.1, NM_001369787.1 order. Seq3 maps254–272/254–272/241–259/241–259. This is reference mapping, not mutant selectivity. All source sequence quotes and mappings are machine-readable in literature_candidates.json and literature_to_harness_crosswalk.csv.

## 6. Source evidence and endpoint limits
The original paper describes20nM Seq2/Seq3 screening and greater than90% protein knockdown by Western blot in its named cell models.[14] The follow-up reports86–95% mRNA downmodulation for Seq2/Seq3 across its stated KRAS contexts, with Figure3a specifying40nM and24h in NIH/3T3 cells expressing human KRAS constructs.[1] These are distinct studies/endpoints/conditions, not two interchangeable scalar labels. Do not assign either range to every individual candidate/cell or equate protein reduction with mRNA knockdown.

The follow-up explicitly cites the previously described control sequences.[1] These studies share research lineage and do not establish independent laboratory reproducibility or independence from pretrained model development. Published support attaches to the reported experimental constructs and conditions; full final chemistry/overhang equivalence to a core-only proposal is not established.

## 7. WorkflowA findings retained
Historical coverage:5288 generated cores;100 deep assessed;81 operational passers;20 investigated;14 conditional no-perfect-outside-match review candidates. The six exact-exclusivity failures remain flagged comparisons, not restored recommendations. Fourteen of20 Ridge values are extrapolations; nine of the conditional14 have this warning. Original scoring/gates and raw outputs remain unchanged.


Conditional14 core designs retained from WorkflowA (all5to3 RNA; numerical priority is not biological order):

|Candidate|Guide|Passenger|Primary interval|Ridge raw|
|---|---|---|---|---|
|NM_004985.5_site_280|UAUUGUUGGAUCAUAUUCG|CGAAUAUGAUCCAACAAUA|280–298|106.6131|
|NM_004985.5_site_1391|UAUAAUAGUUUCCAUUGCC|GGCAAUGGAAACUAUUAUA|1391–1409|104.8076|
|NM_004985.5_site_3954|UAAAUAUCCCCUCAUAAGC|GCUUAUGAGGGGAUAUUUA|3954–3972|103.2610|
|NM_004985.5_site_1710|UAAUAAGCUAUAACUGGCC|GGCCAGUUAUAGCUUAUUA|1710–1728|102.0053|
|NM_004985.5_site_2417|UUGACAAAUAAGUGUAUCC|GGAUACACUUAUUUGUCAA|2417–2435|101.9337|
|NM_004985.5_site_4256|UUAAAUAGAGCCUAGAAUG|CAUUCUAGGCUCUAUUUAA|4256–4274|101.7049|
|NM_004985.5_site_1494|AUGGUUGCUAUAAUAAUCC|GGAUUAUUAUAGCAACCAU|1494–1512|100.7198|
|NM_004985.5_site_3802|UUACAUAGAAGUUUCCUUG|CAAGGAAACUUCUAUGUAA|3802–3820|100.4076|
|NM_004985.5_site_3668|UGAAUAUCUGACAUACACC|GGUGUAUGUCAGAUAUUCA|3668–3686|100.2017|
|NM_004985.5_site_2547|UAAUAUGGAAGAAGAGUCC|GGACUCUUCUUCCAUAUUA|2547–2565|99.7293|
|NM_004985.5_site_1912|UUGAUUUGUCAGCAGGACC|GGUCCUGCUGACAAAUCAA|1912–1930|99.7080|
|NM_004985.5_site_4174|UUAAUGCCUAAGUCUAUGU|ACAUAGACUUAGGCAUUAA|4174–4192|99.6074|
|NM_004985.5_site_2875|UUAAAUUCUCCUUCCACUG|CAGUGGAAGGAGAAUUUAA|2875–2893|99.0907|
|NM_004985.5_site_1517|UAGCAUGUAAAUAUAGCCC|GGGCUAUAUUUACAUGCUA|1517–1535|98.8299|

## 8. WorkflowB sequence reporting ambiguity
Seq1 is preserved verbatim as retrieved: sense GUGCAAUGAAGGGACCAGUA (20nt), antisense UACUGGUCCCUCAUUGCAC (19nt). These are not an exact complementary19nt pair. The discrepancy may be in the publication or extraction; do not silently repair it. Antisense-only reference mapping is a diagnostic, not approval of a corrected literature construct. It is excluded from the paired-core comparison.

## 9. Generation coverage versus prioritization
Both included literature pairs are exact members of the5288-candidate generated pool; neither is in the20 investigated or14 conditional panel. Therefore generation covered them, but prioritization did not retain them. An overlap of zero with a selected panel is not zero efficacy or a sensitivity/recall estimate for all active siRNAs. The literature examples are positively selected, not a representative measured test set.

## 10. Heuristic disagreement exposed
Seq3/site254 has inherited native functionality code4, identified in the actual generator source as the palindrome criterion, so it was not eligible for the assessment queue. The reference-checked motif diagnostic is recorded separately; it is not new model inference. Seq2/site342 has functionality code0 but lower Ridge priority than the100 assessed sites. Neither has historical RN.Ai/RNAiSpline/eval OligoFormer or exact-core full/seed-screen results. A nearby assessed guide cannot supply those missing findings.

Source-reported knockdown for Seq3 shows that the code4 rule can exclude a source-supported construct in these conditions.[14][1] That does not prove a universal filter false-negative rate, establish safety, or justify silently relaxing thresholds. It motivates explicit prospective criterion review with compatible measured data.

## 11. Score comparability and ranking
Ridge and native OligoFormer are the only already-computed endpoints available across the literature pairs and original panel. Raw scores and all-generated ranks are retained; no new ensemble or score-to-percent calibration was fitted. Missing deeper outputs remain NOT_RUN/null. Ridge estimates/native scores are predictions, not measurements; do not compare a Ridge value directly to the pooled86–95% range as an error metric. No correlation/MAE/Precision@K/NDCG is valid from the present pooled positive-only prose evidence.


Descriptive common-input score comparisons (not measured performance):
- original20_plus_literature2 (n=22), Ridge vs native OligoFormer Spearman 0.181, top3 overlap 0/3.
- original20_plus_literature2 (n=22), Ridge vs native OligoFormer Spearman 0.181, top5 overlap 2/5.
- conditional14_plus_literature2 (n=16), Ridge vs native OligoFormer Spearman 0.194, top3 overlap 1/3.
- conditional14_plus_literature2 (n=16), Ridge vs native OligoFormer Spearman 0.194, top5 overlap 3/5.
All scores already existed. No boundary ties occurred for these K values. Restricting to inputs with both scores does not validate either ranking.

## 12. Specificity and mutation boundary
WorkflowA contains both-strand specificity evidence for its20 investigated candidates and the14 subset still has near/seed concerns. WorkflowB has source experimental support but no equivalent fresh reference-wide full/seed screen for Seq2/Seq3 in this study; it is not automatically safer. No shared construct is labelled off-target-free.

The exosome article explicitly describes a KRASG12D-directed siRNA with TT overhangs, a different objective/representation.[10] It is recorded as out-of-scope context, not used to create a hypothetical mutant or select a mutation. Mutation-selective arm remains BLOCKED_PENDING_MUTATION_SPECIFICATION.

## 13. Workflow trade-offs
WorkflowA is systematic across the transcript, machine-auditable and specificity-aware but prioritization/heuristics remain exploratory and experimental labels absent. WorkflowB supplies context-linked experiments and can expose overly strict computational rules, but is vulnerable to positive-publication selection, incomplete sequence/chemistry reporting, inaccessible supplements and limited matched quantitative data. Neither proves biological superiority of its panel. workflow_comparison.csv provides the dimension-by-dimension comparison.

## 14. Integrated research recommendation
Retain the conditional14 panel without changing prior gates/ranks. Add Seq2/Seq3 as separately labelled literature-supported comparator cores for a future experimental/computational comparison, not as newly qualified top designs. First resolve exact delivered construct, intended cells/assay/dose/time, specificity criteria and final chemistry. Future deeper inference/screening for the two cores is optional new work requiring a declared scope; it was not performed here. No winner is forced.

## 15. Qualification and unsupported conclusions
Overall biology remains PARTIAL. Source efficacy does not establish current construct safety, immune tolerance, delivery, therapeutic window, wild-type sparing or new-cell efficacy. Historical independent predictor benchmark remains BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET. This targeted case study is not a replacement independent benchmark or cross-laboratory replication.

## 16. Reproducibility
input_hashes.json and input_hashes_after.json bind all original case/audit/benchmark files. discovery/retrieval/extraction manifests preserve actual requests/errors and semantic checks. literature_candidates, crosswalk, experimental_evidence, score and workflow comparisons retain source-specific distinctions. output_manifest.json and verification_receipt.json bind new outputs; verification is technical, not biological validation.

Technical verification PASSED: source preservation, literal sequence and endpoint claims, independent coordinate/rank checks and citation evidence were verified. This is not biological validation.

## Sources

[1] https://pmc.ncbi.nlm.nih.gov/articles/PMC8033609 — Silencing of Oncogenic KRAS by Mutant-Selective Small Interfering ...
[10] https://pmc.ncbi.nlm.nih.gov/articles/PMC5538883 — Exosomes facilitate therapeutic targeting of oncogenic KRAS in pancreatic cancer
[14] https://pmc.ncbi.nlm.nih.gov/articles/PMC4416486 — Therapeutic Silencing of KRAS using Systemically Delivered ...
