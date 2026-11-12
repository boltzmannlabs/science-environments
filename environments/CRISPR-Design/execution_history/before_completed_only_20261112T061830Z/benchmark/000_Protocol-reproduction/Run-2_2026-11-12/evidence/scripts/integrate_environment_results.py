"""Publish hash-bound evidence into the requested environment, preserving original sources.
Only new run directories are created; existing documentation is updated separately.
"""
import pathlib,json,csv,hashlib,shutil,gzip,datetime,math
import pandas as pd,numpy as np
from scipy.stats import spearmanr
SRC=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/Run_20261111T113324Z')
ENV=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/science-environments/environments/CRISPR-Design')
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env')
RUN='Run-2_2026-11-12';CAMP=ENV/'benchmark/000_Protocol-reproduction'/RUN
CAMP.mkdir(parents=True,exist_ok=False)
meta=json.loads((REPO/'04_workflow_runs/LATEST_SESSION_ARCHIVE.json').read_text());EX=pathlib.Path(meta['latest_run'])
# Freeze pre-update repository documents, including pre-existing uncommitted edits.
for p in ENV.rglob('*'):
 if p.is_file() and (p.suffix in ['.md','.yaml'] or p==ENV/'tests/validate_spec.py') and CAMP not in p.parents:
  dest=CAMP/'pre_update_snapshot'/p.relative_to(ENV);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
# Verify all corrected RF fits, held-out disjointness and prediction-label consistency independently.
rf=SRC/'predictions/cas13_RFcombined_source_audited_v2';metrics=pd.read_csv(SRC/'reports/cas13_RFcombined_1000_resampling_metrics.csv');assert len(metrics)==1000 and set(metrics.replicate)==set(range(1000))
maxdiff=0.;nchecks=0
for i in range(1000):
 record=json.loads((rf/f'replicate_{i:04d}.json').read_text());pred=pd.read_csv(rf/f'replicate_{i:04d}_predictions.csv.gz');part=pd.read_csv(rf/f'replicate_{i:04d}_partition.csv.gz')
 assert len(part)==2918 and part.row.is_unique and set(part.partition)=={'train','test'}
 tr=set(part.loc[part.partition=='train','row']);te=set(part.loc[part.partition=='test','row']);assert not tr&te and set(pred.row)==te
 rho=float(spearmanr(pred.truth,pred.prediction).statistic);expected=float(metrics.loc[metrics.replicate==i,'spearman'].iloc[0]);diff=abs(rho-expected);assert diff<1e-9
 # jsonlite JSON defaults round values; full CSV used as numerical authority.
 maxdiff=max(maxdiff,diff);nchecks+=1
summary=json.loads((SRC/'reports/cas13_RFcombined_verified_summary.json').read_text());assert summary['replicates']==1000
loso=pd.read_csv(SRC/'reports/cas13_RFcombined_leave_screen_out.csv');assert set(loso.screen)=={'CD46','CD55','CD71','GFP'}
verification={'status':'PASS','replicates_verified':nchecks,'per_replicate_partition_rows':2918,'all_partition_train_test_disjoint':True,'all_test_predictions_match_partition':True,'max_recomputed_spearman_difference':maxdiff,'median_spearman_full_precision':float(metrics.spearman.median()),'mean_spearman_full_precision':float(metrics.spearman.mean()),'split_refit_interval':metrics.spearman.quantile([.025,.975]).to_list(),'interval_type':'split/refit percentiles; NOT an independent-target confidence interval','LOSO':loso.to_dict('records'),'source_json_rounding':'Original summary JSON rounded by jsonlite; full-precision CSV and this recomputation are retained','pilot':'Rejected initial globally-scaled pilot is excluded'}
(CAMP/'cas13_completion_verification.json').write_text(json.dumps(verification,indent=2))
manifest=[]
def copy(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);a=hashlib.sha256(src.read_bytes()).hexdigest();b=hashlib.sha256(dest.read_bytes()).hexdigest();assert a==b
 manifest.append({'source':str(src),'destination':str(dest.relative_to(ENV)),'sha256':a,'bytes':dest.stat().st_size})
for area in ['reports','protocols','scripts']:
 for p in (SRC/area).rglob('*'):
  if p.is_file():copy(p,CAMP/'evidence'/area/p.relative_to(SRC/area))
# Compact numeric primary outputs retained locally; very large inputs/weights indexed, not duplicated.
for name in ['cas9_fresh_shared_holdout_joined.csv','cas9_exact_notebook_multiplicity_replay.csv','BEHive_BE4_HEK293T_external_predictions.csv','DeepPrime_base_fixed_test_predictions.csv','specificity_v2_verified_pairs.csv','CRISPRi_window_heldout_phenotypes.csv','PRIDICT2_OOF/OOF_ensemble_predictions_with_labels.csv']:
 copy(SRC/'predictions'/name,CAMP/'evidence/predictions'/name)
for p in SRC.glob('downloads/*manifest*.json'):copy(p,CAMP/'evidence/manifests'/p.name)
# Archive reproducibility dependencies and all model/data files as verifiable handles; no bulk copies.
external=[]
for area in ['data','sources','environments','predictions/cas13_RFcombined_source_audited_v2']:
 for p in (SRC/area).rglob('*'):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts:
   # Hash scientific data/code and checkpoints, not thousands of environment package binaries.
   external.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if area!='environments' else None})
(CAMP/'EXTERNAL_ARTIFACT_INDEX.json').write_text(json.dumps(external,indent=2))
TASKS=[
('001','general','general-routing','SHARED_COMPONENT_BENCHMARKS','General routing example KIF11; shared Cas9 and specificity components evaluated, routing accuracy not measured.',['cas9_exact_published_protocol_metrics.csv','specificity_benchmark_source_concordant.json'],'No labeled modality-routing corpus; no complete all-mode workflow validation.'),
('002','knockout_gene_disruption','knockout','FRESH_CAS9_COMPONENT_EVALUATION','RS3 Sequence and CRISPRon fresh inference across six author-defined held-out cohorts; exact20mer four-model training exclusions; 23629 unique contexts.',['cas9_exact_published_protocol_metrics.csv','cas9_source_multiplicity_audit.json','cas9_exact_source_within_gene_rank_loss.csv','cas9_supplemental_per_gene_ndcg.csv','specificity_benchmark_source_concordant.json'],'Not original CRISPRon_v0 internal split or <=3mm exclusion replication; RS3 Sequence+Target absent; no knockout outcome validation for new KIF11/KRAS guides.'),
('003','therapeutic_in_vivo_editing','therapeutic-in-vivo','SPECIFICITY_COMPONENT_ONLY','WT SpCas9 assay-matched CFD:1684 assayed sites,108 positives,1576 negatives,9 guides.',['specificity_benchmark_source_concordant.json','specificity_v2_per_guide_recall_at_K.csv'],'No delivery, in-vivo efficacy, patient haplotypes, therapeutic safety or clinical detection limit validation.'),
('004','variant_correction_precision_repair','variant-correction','MATCHED_MODEL_COMPONENT_EVALUATIONS','PRIDICT2 grouped OOF and DeepPrime HEK293T/PE2 fixed-test components; BE4 any-edit efficiency separately.',['PRIDICT2_status.json','PRIDICT2_original_split_and_score_concordance.json','DeepPrime_base_heldout_metrics.json','BEHive_external_efficiency_metrics.json'],'Not allele-specific HBB repair or HDR validation; BE4 labels cannot validate BE4max intended purity.'),
('005','base_editing','base-editing','FRESH_BE4_EFFICIENCY_EXTERNAL_TEST','BE-Hive HEK293T/BE4 external library,n9975; Spearman0.165766, Pearson0.176357; conservative known training20mer/31nt exclusions.',['BEHive_external_efficiency_metrics.json'],'Weak transfer performance; do not use as validated BE4max correction/purity ranker. Bystander-genotype held-out evaluation NOT_RUN.'),
('006','prime_editing','prime-editing','FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS','PRIDICT2 intended-edit rho0.9056 HEK/0.8081 K562; source-fold mismatches0. DeepPrime PE2 conventional scaffold fixed test n28883 rho0.861474.',['PRIDICT2_status.json','PRIDICT2_target_cluster_confidence_intervals.csv','PRIDICT2_original_split_and_score_concordance.json','DeepPrime_base_heldout_metrics.json'],'Cell/editor matched only. Pretraining-overlap audit incomplete for PRIDICT2; unintended-edit score is not purity; PE3 nicking design not validated.'),
('007','crispr_regulation','regulation','CRISPRI_WINDOW_COMPONENT_TEST_ONLY','CRISPRi fixed TSS-window gate tested on3607 held-out guides/307 genes; recall0.7642, precision0.2546 for source normalized activity>=0.75.',['CRISPRi_component_phenotype_metrics.json'],'Full808-feature CRISPRi model and CRISPRa prediction NOT_RUN. No mammalian nuclease score substituted.'),
('008','epigenome_editing','epigenome-editing','BLOCKED_MATCHED_EPIGENETIC_ENDPOINT','Prior PCSK9 enumeration/TSS/CpG context exists; no matched durable-silencing performance evaluated.',[],'Functional methylation/durable repression labels and matched predictor adapter missing; GSE168012 metadata retrieval failed. CpG count is not methylation efficacy.'),
('009','rna_targeting_cas13','rna-targeting-cas13','COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION','1000 corrected RF refits verified; median rho%.6f; split/refit interval[%.6f,%.6f].'%(verification['median_spearman_full_precision'],*verification['split_refit_interval']),['cas13_RFcombined_1000_resampling_metrics.csv','cas13_RFcombined_leave_screen_out.csv','cas13_RFcombined_verified_summary.json','cas13_author_metric_reference.json'],'Paper2000trees/mtry12 retained; comparative source defaults/finalCV mtry10 differ. Precomputed features, inherited global feature selection; LOSO GFP only0.2947; no TIGER/full-transcriptome specificity validation.'),
('010','diagnostics_pathogen','diagnostics','REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY','Prior synthetic nonpathogen diagnostic geometry only. EasyDesign numeric-score replay attempt is incomplete; no diagnostic model validation accepted.',[],'Latest replay script encountered nonnumeric dash tokens; edits not rerun. Source prediction columns have unequal coverage. No clinical sensitivity/specificity/LoD; no new pathogen design/scoring.'),
('011','library_screen_design','library-screen-design','SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION','Shared Cas9 guide-level and within-gene rank-loss evidence; supplemental explicitly-defined nDCG retained.',['cas9_exact_source_within_gene_rank_loss.csv','cas9_supplemental_per_gene_ndcg.csv'],'No library-level essential-gene detection, enrichment, screen power, or target-diversity validation. Shared guides are not independent task benchmarks.'),
('012','plant_genome_editing','plant-editing','PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY','52 N.benthamiana guides across20/32-guide cohorts; author model scores replayed against actual plant mean InDel measurements.',['plant_assay_matched_score_replay.csv','plant_validation_status.json'],'Not fresh inference or species adapter validation; plant DESIGN remains inactive. No mammalian phenotype used as surrogate.'),
('013','microbial_crispr_design','microbial','BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY','MERF author gene/dataset-held-out scores:642 comparisons,median rho0.381385 versus paper rounded0.396.',['bacterial_source_faithful_replay.json','bacterial_source_faithful_gene_dataset_metrics.csv'],'Not fresh bacterial inference or independent9-gene assay; mismatch to paper headline retained. Bacterial CRISPRi depletion cannot validate lacZ nuclease knockout.')]
ledger=[]
for num,app,slug,status,finding,files,limits in TASKS:
 taskfile=next((ENV/'tasks').glob(num+'_*.md'));res=ENV/'results'/(num+'_'+app)/RUN;bench=ENV/'benchmark'/(num+'_'+slug)/RUN;res.mkdir(parents=True,exist_ok=False);bench.mkdir(parents=True,exist_ok=False)
 tasksrc=EX/'tasks'/num;copied=[];large=[]
 for p in tasksrc.rglob('*'):
  if p.is_file():
   if p.stat().st_size<=5_000_000:copy(p,res/'artifacts'/p.relative_to(tasksrc));copied.append(str(p.relative_to(tasksrc)))
   else:large.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 brief=tasksrc/'confirmed_test_input.json';assert brief.exists();copy(brief,res/'00_inputs/requirement_brief.json')
 rr=json.loads((tasksrc/'run_record.json').read_text());(res/'large_artifact_index.json').write_text(json.dumps(large,indent=2))
 for f in files:copy(SRC/'reports'/f,bench/f)
 record={'task_id':num,'task_spec':str(taskfile.relative_to(ENV)),'application':app,'run_id':RUN,'design_status':'AUDIT_ONLY_INACTIVE' if num=='012' else 'PARTIAL_COMPUTATIONAL_EXAMPLE','benchmark_status':status,'finding':finding,'limitations':limits,'best_design':None,'experimental_validation':False,'example_source':str(tasksrc),'benchmark_source':str(SRC),'source_run_record':rr,'shared_benchmark_not_independent_per_task':num in ['001','002','003','004','006','011']}
 (res/'provenance.json').write_text(json.dumps(record,indent=2));(bench/'provenance.json').write_text(json.dumps(record,indent=2))
 relative=lambda p,base:pathlib.Path(__import__('os').path.relpath(p,base)).as_posix()
 report=f'# Task {num}: {app} — {RUN}\n\nDesign status: {record["design_status"]}. Benchmark status: {status}.\n\n{finding}\n\n## What was delivered\n\nHistorical example outputs were copied byte-identically from the approved example run, not regenerated during this documentation integration. See artifacts/run_record.json for exact counts/stages and 00_inputs/requirement_brief.json for actual illustrative parameters.\n\n## Performance and limitations\n\n{limits}\n\nNo wet-lab validation. best_design=null. NEEDS_EXPERIMENTAL_VALIDATION. Passing computational checks is not biological success. Draft design gates were not calibrated/frozen by these benchmarks.\n\n[Task benchmark]({relative(bench/"README.md",res)}) · [Campaign report]({relative(CAMP/"REPORT.md",res)})\n'
 (res/'REPORT.md').write_text(report)
 btext=f'# Task {num} benchmark — {RUN}\n\n## Published reference | Run configuration | Result\n\nStatus: {status}.\n\n{finding}\n\n{limits}\n\n'
 btext+='Evidence files: '+(', '.join('['+f+']('+f+')' for f in files) if files else 'No completed matched-label evaluation; see explicit blockers above.')+'\n\n'
 btext+=f'[Result artifacts]({relative(res/"REPORT.md",bench)}) · [Shared protocol/methodology and sources]({relative(CAMP/"REPORT.md",bench)})\n\nFuture slot: NOT_EXECUTED — remaining full-modality validation; no inferred success.\n'
 (bench/'README.md').write_text(btext)
 ledger.append({k:v for k,v in record.items() if k not in ['source_run_record'] }|{'result_report':str((res/'REPORT.md').relative_to(ENV)),'benchmark_report':str((bench/'README.md').relative_to(ENV))})
(CAMP/'task_execution_status.json').write_text(json.dumps(ledger,indent=2))
with open(CAMP/'task_execution_status.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=list(ledger[0]));writer.writeheader();writer.writerows(ledger)
# Copy manifests after all task artifact copying.
(CAMP/'PROVENANCE.json').write_text(json.dumps(manifest,indent=2))
(CAMP/'PROVENANCE.sha256').write_text(''.join(r['sha256']+'  '+r['destination']+'\n' for r in manifest))
(CAMP/'README.md').write_text('# Protocol reproduction campaign\n\nStart with [REPORT.md](REPORT.md), [task ledger](task_execution_status.csv), and [RFcombined independent completion verification](cas13_completion_verification.json).\n\nByte-identical scientific artifacts are hash-bound in PROVENANCE.json and PROVENANCE.sha256. Large datasets, model weights, environments and1000 RF partitions/predictions remain at absolute source paths in EXTERNAL_ARTIFACT_INDEX.json. This is a local reproducibility package, not a self-contained portable distribution. Source scripts retain their original absolute paths; inspect their protocol/environment manifests before rerunning.\n')
print(json.dumps({'campaign':str(CAMP),'tasks':len(ledger),'copied_artifacts':len(manifest),'RF_verification':verification},indent=2))
