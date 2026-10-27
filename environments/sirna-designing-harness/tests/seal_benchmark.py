#!/usr/bin/env python3
"""Seal the selected KRAS report/result snapshot; no models, services, source writes or data recomputation."""
from pathlib import Path
import csv,json,hashlib,datetime,subprocess,sys
ENV=Path(__file__).resolve().parents[1];ROOT=ENV/'benchmark/KRAS'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def j(p):return json.loads(Path(p).read_text())
def rows(p):
 with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def writej(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def main():
 copy=j(ROOT/'copy_provenance.json');checks=[]
 def check(ok,name):
  assert ok,name
  checks.append(name)
 check(len(copy['selected_files'])==copy['copied_files']==85,'eightyfive_selected_source_artifacts')
 check(len({r['benchmark_relative_path'] for r in copy['selected_files']})==85,'unique_snapshot_file_paths')
 for r in copy['selected_files']:
  p=ROOT/r['benchmark_relative_path'];check(p.is_file() and sha(p)==r['source_sha256']==r['copied_sha256'] and p.stat().st_size==r['bytes'],'literal_copy_hash:'+r['benchmark_relative_path'])
 for r in copy['source_snapshot_before']:
  p=Path(r['source_path']);check(p.is_file() and sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],'original_source_unchanged:'+p.name)
 stage=ROOT/'01_shared_design';top=rows(stage/'top20_sequences.csv');review=rows(stage/'reference_exact_exclusivity_subset.csv');check(len(top)==20 and len(review)==14,'twenty_investigated_fourteen_conditional')
 check(sum(r['perfect_reference_gene_exclusivity']=='FAILED' for r in top)==6,'six_known_exclusivity_failures_not_hidden')
 check(j(stage/'qualification_results.json')['fully_qualified_count']==0,'no_qualified_construct_claim')
 audit=ROOT/'02_candidate_audit';check(len(rows(audit/'candidate_evidence_flat.csv'))==20 and len(rows(audit/'review_candidates14.csv'))==14,'audit_candidate_table_counts')
 check(len(rows(audit/'exact_failure_alignments.csv'))==12,'twelve_exact_alignment_rows_for_six_candidates')
 sensitivity=ROOT/'03_ranking_sensitivity';check(len(rows(sensitivity/'candidate_evidence_matrix.csv'))==14 and len(rows(sensitivity/'ranking_sensitivity.csv'))==291,'sensitivity_evidence_counts')
 bench=ROOT/'04_experimental_dataset_audit';check(j(bench/'split_manifest.json')['status']=='BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','independent_dataset_blocker_preserved')
 check(not rows(bench/'per_record_predictions.csv'),'independent_predictions_header_only_not_fabricated')
 metrics=rows(bench/'metric_summary.csv');check(len(metrics)==100 and all(r['status']=='BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET' and r['metric_value']=='' and r['n_predicted']=='0' for r in metrics),'null_metrics_not_zero_performance')
 comparison=ROOT/'05_literature_comparison';check(len(rows(comparison/'candidate_score_comparison.csv'))==22 and len(rows(comparison/'literature_to_harness_crosswalk.csv'))==2,'literature_case_comparison_counts')
 summary=j(comparison/'comparison_summary.json');check(summary['overall_biological_status']=='PARTIAL' and summary['mutation_arm_status']=='BLOCKED_PENDING_MUTATION_SPECIFICATION' and summary['exact_pair_overlap_conditional14']==0,'comparison_boundary_preserved')
 check(all(summary[name]==0 for name in ['new_generation_runs','new_predictor_inference_runs','new_folding_runs','new_transcriptome_screening_runs','mutant_sequences_constructed']),'no_new_scientific_execution_or_mutant')
 provenance=j(ROOT/'source_preservation.json');check(provenance['source_files_byte_unchanged'] and provenance['new_generation_inference_folding_screening_runs']==0,'source_preservation_receipt')
 excluded=j(ROOT/'external_artifact_index.json')['excluded_files'];check(len(excluded)==207,'external_artifact_index_scope')
 # Copy-only data are not transformed to make links/statuses convenient.
 files=[{'relative_path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name not in {'snapshot_manifest.json','snapshot_verification.json'}]
 check(all(not (ROOT/x['relative_path']).is_symlink() and x['bytes']<=524288 for x in files),'bounded_file_payloads')
 check(sum(x['bytes'] for x in files)<3*1048576,'snapshot_under_three_MiB')
 writej(ROOT/'snapshot_manifest.json',{'scope':'Selected historical KRAS results/reports and snapshot provenance; not complete original run archives','artifacts':files,'exclude':'self and snapshot_verification.json to avoid circularity','copy_provenance_sha256':sha(ROOT/'copy_provenance.json')})
 receipt={'verification':'PASSED','scope':'Copy integrity and key historical table/status semantics, not new science or independent model validation','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'copied_source_files':85,'snapshot_files_hashed':len(files),'snapshot_bytes':sum(x['bytes'] for x in files),'original_source_files_byte_unchanged':85,'assertions_passed':len(checks),'snapshot_manifest_sha256':sha(ROOT/'snapshot_manifest.json'),'biology':'PARTIAL','independent_benchmark_status':'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','mutation_arm_status':'BLOCKED_PENDING_MUTATION_SPECIFICATION','new_generation_inference_folding_screening_runs':0};writej(ROOT/'snapshot_verification.json',receipt)
 p=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-benchmark'],capture_output=True,text=True,timeout=60);check(p.returncode==0,p.stdout+p.stderr);print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
