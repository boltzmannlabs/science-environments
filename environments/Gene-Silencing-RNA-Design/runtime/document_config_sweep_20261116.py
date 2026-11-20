"""Document and register the completed sweep without editing checksum-bound historical run files."""
import pathlib,json,csv,sys,math,textwrap,statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import config_sweep_20261116 as S
import analyze_config_sweep_20261116 as A
OUT=S.OUT;RUN=S.RUN

def main():
 if (OUT/'documentation_complete.json').exists():raise RuntimeError('Documentation already frozen; create a new run instead of overwriting tried configs/results')
 summary=json.loads((OUT/'sweep_summary.json').read_text());metrics=json.loads((OUT/'measured_metrics.json').read_text());taskstatus=json.loads((OUT/'task_status.json').read_text());ledger=S.readcsv(OUT/'config_execution_ledger.csv');sel=json.loads((OUT/'retrospective_target_out_selection.json').read_text())
 # Regenerate only the corrected short-cohort precision-axis figure; no inference or selection rerun.
 task='010_gene-regulation';history=json.loads((ROOT/'results'/task/RUN/'performance_history.json').read_text());A.aucplot(task,history,'MYC — '+task+'\nn=7, one positive: descriptive only; no meaningful convergence claim')
 snapshots=[]
 for task in S.TASKS:
  if task in S.SKIP:continue
  d=ROOT/'results'/task/RUN;history=json.loads((d/'performance_history.json').read_text())
  for idx,item in enumerate(history):
   fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained');prefix=history[:idx+1];x=list(range(idx+1))
   if task.startswith(('003','006')):
    for name,color in [('patisiran','#0072B2'),('vutrisiran','#D55E00')]:ax.plot(x,[next(a['percentile'] for a in z['anchors'] if a['anchor']==name) for z in prefix],'-o',label=name,color=color)
    ax.set(ylabel='Projected core percentile among 598 windows',ylim=(0,103));ax.legend(fontsize=8)
   else:
    key='macro_auc' if task.startswith('001') else ('spearman_ddg_vs_logDR' if task.startswith('004') else ('spearman_vs_neglog10_ic50' if task.startswith('007') else 'auc'))
    ax.plot(x,[z[key] for z in prefix],'-o',color='#0072B2');ax.set(ylabel=key,ylim=(-1,1) if 'spearman' in key else (0,1.05))
   ax.set(xticks=x,xticklabels=[z['config_id'].split('_')[0] for z in prefix],xlabel='Tried config history through this step',title=textwrap.fill(task+' | '+item['config_id'],65));ax.grid(alpha=.2)
   fig.supxlabel('Retrospective fixed grid; not training convergence. No efficacy ensemble or clinical validation.',fontsize=8)
   p=d/item['config_id']/'performance_until_this_config.png';fig.savefig(p,dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)
   with Image.open(p) as im:im.verify()
   with Image.open(p) as im:snapshots.append({'path':str(p.relative_to(ROOT)),'width':im.width,'height':im.height,'steps_shown':idx+1,'decoded':True})
   cf=ROOT/'config'/task/RUN/item['config_id'];S.dump(cf/'execution.json',{'status':'EXECUTED','frozen_config_sha256':S.sha(cf/'benchmark_config.json'),'results':str((d/item['config_id']).relative_to(ROOT)),'metrics_sha256':S.sha(d/item['config_id']/'metrics.json'),'history_snapshot':str(p.relative_to(ROOT)),'note':'benchmark_config.json remains immutable PLANNED intent; this sidecar records actual execution, including explicit historical/identical-input reuse.'})
 S.dump(OUT/'snapshot_image_validation.json',snapshots)
 summary.update(per_config_snapshot_pngs=len(snapshots),png_files_including_copied_overview=len(list((ROOT/'results').glob('*/'+RUN+'/**/*.png')))+len(list(OUT.glob('*.png'))),no_claim_of_confirmed_improvement=True)
 S.dump(OUT/'sweep_summary.json',summary)
 # Machine-readable plotting values and cumulative best-observed diagnostic; never presented as a holdout curve.
 trajectory=[];best=-math.inf
 for z in sel:
  best=max(best,z['fixed_config_macro_auc']);trajectory.append({'step':z['step'],'config_id':z['new_config'],'actual_macro_auc':z['fixed_config_macro_auc'],'best_observed_so_far_macro_auc':best,'other_target_selected_macro_auc':z['retrospective_loto_selected_macro_auc'],'warning':'Best-so-far is a retrospective observed maximum, not evidence of training/generalization convergence.'})
 S.csvout(OUT/'performance_trajectory.csv',trajectory)
 rows=[]
 for task in S.TASKS:
  status=next(r for r in taskstatus if r['task']==task);rows.append('| '+task+' | '+str(status['configs_executed'])+' | '+status['status']+' |')
 # One local registry for this sweep avoids invalidating a historical manifest that hashes a mutable root index.
 report=['# siRNA fixed configuration sweep — '+RUN,'','## Outcome','',
'All 11 task-specific configuration folders were created. Nine tasks have executable benchmark/evaluation configurations; 35 task-config result bundles were saved. These reuse 11 unique scientific configurations (four efficacy endpoints/input conventions, four physical-model settings, three degraded-context controls), not 35 independent models or datasets. PCSK9 and TNF performance tuning was skipped for lack of matched efficacy labels.','',
'Observed mean AUC over the three eligible targets increased from '+f'{summary["baseline_macro_auc"]:.4f}'+' (C00) to '+f'{summary["best_observed_fixed_macro_auc"]:.4f}'+' (C01). This is an exploratory retrospective difference. Other-target config selection yielded '+f'{summary["retrospective_loto_selected_macro_auc_final"]:.4f}'+', versus the '+f'{summary["baseline_macro_auc"]:.4f}'+' baseline: no transferable improvement was demonstrated. Paired target-specific delta intervals for C01 include zero. No config is automatically promoted into production defaults.','',
'## Published reference','',
'The measured target cohorts are derived from Sciabola et al., PMID 23241392, DOI 10.1093/nar/gks1191, with the same locally supplied transcript and outcome records used in Run-3. OligoFormer paper PMID 39321261, DOI 10.1093/bioinformatics/btae577, reports Mixset inter-dataset AUC 0.8163 on a different protocol/cohort; it is cited as context, not a matched superiority threshold. Primary full-text snapshots and detailed source provenance remain in benchmark/011_Campaign-reproduction/Run-3_2026-11-11/sources/.','',
'HTT reporter sequences and mismatch identities come from Pfister et al., PMID 19361997, DOI 10.1016/j.cub.2009.03.030, Table 2. TTR anchors use the previously hash-bound patisiran/vutrisiran projected cores; clinical outcomes are not sequence-level potency labels.','',
'## Run configuration','',
'C00: RN.Ai with source-verbatim guide, 21 nt for measured cohort and 19 nt for generated TTR cores.','C01: RN.Ai with explicitly projected first-19-nt core; guide tokens 20/21 zero-padded.','C02: RNAiSpline with its documented first-19-nt core input.','C03: hash-bound cached OligoFormer native scores, joined by exact coordinate AND guide identity; no new OligoFormer forward pass.','',
'All four efficacy configurations are single, independent endpoints. Native outputs are never averaged or converted into each other. C00/C01 TTR inputs are identical 19-mers and share predictions explicitly. All root-level example configs, frozen biological gates, upstream model code/checkpoints and prior result bundles are unchanged. Historical 24-candidate gate-clean sets are reranked for application panels; no new safety battery or generation is implied.','',
'RNAduplex D00/D01/D02/D03 vary dangles 2/0/1 and the noLP flag, keeping temperature 37 C and default salt 1.021 M fixed. This is physical-model sensitivity, not biological condition optimization. HTT N00/N01/N02 vary input representation when genuine flanks are absent: they are negative/sensitivity controls, not valid-context CNS efficacy tuning.','',
'Execution uses the previously user-approved pinned local backends. Current Boltzmann siRNA contracts were inspected, but do not expose these RN.Ai/RNAiSpline feature-level or physical-model controls. No additional remote submission, installation, training, checkpoint download, or overwrite of another profile was performed.','',
'## Benchmark metrics','',
'| Target | n | C00 RN.Ai native | C01 RN.Ai core19 | C02 RNAiSpline | C03 cached OligoFormer |','|---|---|---|---|---|---|']
 for gene in ['HIF1A','HPSE','HK2','MYC']:
  vals=[next(r for r in metrics if r['gene']==gene and r['config_id']==c['config_id']) for c in S.CFG];report.append('| '+gene+' | '+str(vals[0]['n'])+' | '+' | '.join(f'{r["auc"]:.4f}' for r in vals)+' |')
 report+=['', 'MYC has only seven rows and one positive; AUC=1.0 is degenerate and does not prove robust discrimination. It is excluded from config selection. HIF1A/HPSE/HK2 provide the common 301-row main comparison; OligoFormer common coverage including MYC is 308 rows. The other endpoints additionally score the complete 322-row cohort, but unmatched rows are not silently imputed for OligoFormer.','',
'All three C01-minus-C00 exploratory paired AUC confidence intervals cross zero. Row-bootstrap intervals use 1000 class-stratified paired resamples; overlapping sites, shared genes, previously examined labels and multiple comparisons limit inference. The leave-one-target-out procedure chooses only using the other two genes, but this is not an untouched prospective holdout or proof of pretrained-model training independence.','',
'HTT RNAduplex correlations remain approximately -0.30 across the four physical-model configs. Missing-context RN.Ai correlations are approximately 0.259–0.273; these do not establish a better CNS predictor. Five censored reporter discrimination ratios are retained in the data and excluded from exact-value correlations. No physical/input config is selected as a clinical optimum.','',
'## Task coverage','', '| Task | Config bundles | Status |','|---|---|---|',*rows,'',
'General/oncology/functional-genomics/drug-target-validation frames share target-level datasets; systemic-LNP and total-lowering frames share TTR anchors. They are not independent biological validations. Full application tasks remain incomplete where expression/orthogonal/context annotations or reference/variant requirements were previously unrun.','',
'## Tool improvement','',
'Added runtime/sirna_context_audit.py: it requires an exact first-19-nt guide target match before using the upstream tokenizer, preventing the upstream find==-1 path from constructing meaningless flank features. It records actual known flank coverage and duplicate sites instead of trusting a length-only in_domain label. Batched RN.Ai execution is checked against native single-row inference. The new baseline reproduces all 322 prior RN.Ai scores exactly. This is a correctness/traceability improvement; it is not a newly trained model or demonstrated biological efficacy gain.','',
'## Figures and history','',
'Overview: results/001_general/'+RUN+'/performance_overview.png (also SVG). Each active task has performance.png/SVG and performance_history.csv/JSON; each tried config has performance_until_this_config.png. All points, including flat or worse results, remain visible. The order is a frozen experiment grid, not training epochs. PNG decoding, dimensions and finite plotted axes are checked programmatically; no claim of manual visual review is made.','',
'## Reproduction and audit','',
'Original example JSON files are preserved at config root and copied under their task folders. Per-config benchmark_config.json files are frozen intent; execution.json sidecars record actual execution. Root config/README.md is the index. Results configs are hash-identical to the frozen configs. Use the pinned siRNA-Bench interpreter for runtime/config_sweep_20261116.py and runtime/analyze_config_sweep_20261116.py; existing run directories refuse inference/report overwrite. To start a new experiment, create a new versioned run rather than editing a tried config.','',
'Run registry: benchmark/012_Config-sweep/BENCHMARK_RUNS.md. The historical root run registry is intentionally not edited because the old Run-3 manifest includes it; all 341 historical Run-3 checksum entries can therefore still be verified. All new scientific artifacts are under the requested repository.','',
'## Evidence status','',
'No newly generated design, assay result or measured efficacy is invented. No model ensemble, label-tuned gate, prospective superiority or clinical equivalence is claimed. Panels remain NEEDS_EXPERIMENTAL_VALIDATION and best_design=null.']
 (OUT/'REPORT.md').write_text('\n'.join(report)+'\n')
 (OUT.parent/'README.md').write_text('# Fixed configuration sweeps\n\n## Published reference\n\nSciabola PMID 23241392, OligoFormer PMID 39321261, Pfister PMID 19361997; matched and unmatched comparisons are distinguished in the run report.\n\n## Run configuration\n\nFour fixed efficacy configs plus physical/input sensitivity controls; all frozen gates and historical runs preserved.\n\n## Benchmark metrics\n\n| Run | Outcome |\n|---|---|\n| ['+RUN+']('+RUN+'/REPORT.md) | Observed macro AUC 0.7115 -> 0.7203; no demonstrated cross-target selection gain |\n\nSee [run registry](BENCHMARK_RUNS.md) and the per-task result folders.\n')
 (OUT.parent/'BENCHMARK_RUNS.md').write_text('# Configuration-sweep run registry\n\n| Run | Config delta | Published comparison | Results |\n|---|---|---|---|\n| '+RUN+' | RN.Ai native/core19, RNAiSpline core19, cached OligoFormer; explicit context audit; frozen physical/context controls | Matched measured targets and TTR anchors; not a Mixset/clinical superiority claim | ['+RUN+'/REPORT.md]('+RUN+'/REPORT.md) |\n\nHistorical engine/gates and root registry unchanged. This sweep is retrospective; no automatic production promotion.\n')
 index=['# Task-specific configuration index','','Original root-level examples, schemas and frozen gates are retained. Every task folder has an immutable copy of its original example(s). Tried configs are in `<task>/'+RUN+'/<config_id>/benchmark_config.json`; execution.json links actual results.','','| Task | Executed configs | Scope |','|---|---|---|']
 for r in taskstatus:index.append('| ['+r['task']+']('+r['task']+'/README.md) | '+str(r['configs_executed'])+' | '+r['status']+' |')
 index+=['','Sweep report: [REPORT](../benchmark/012_Config-sweep/'+RUN+'/REPORT.md). Config aliases across application frames are not independent fits. Never edit tried configs; add a new config/run.']
 (ROOT/'config/README.md').write_text('\n'.join(index)+'\n')
 # Task-indexed benchmark evidence pointers; original case READMEs remain unchanged.
 cases={'001_general':'000_Simone-independent-evaluation','002_oncology':'002_Oncology-HPSE-HK2-cohorts','003_genetic-disease-total-lowering':'003_TTR-approved-drugs-cohort','004_genetic-disease-allele-selective':'004_Allele-selective-duplex','006_systemic-lnp':'006_Systemic-LNP','007_neuro-cns':'007_Neuro-HTT-evaluate','009_functional-genomics':'009_Functional-genomics-panels','010_gene-regulation':'010_Gene-regulation-MYC-cohort','011_drug-target-validation':'011_Drug-target-validation'}
 for task,case in cases.items():
  d=ROOT/'benchmark'/case/RUN;d.mkdir(exist_ok=False)
  S.dump(d/'comparison_manifest.json',{'task':task,'run_id':RUN,'results':str((ROOT/'results'/task/RUN).relative_to(ROOT)),'metrics':'performance_history.json','frozen_plan_sha256':S.sha(OUT/'frozen_plan.json')})
  (d/'README.md').write_text('# '+task+' config comparison\n\n## Published reference\n\nSee [sweep report](../../012_Config-sweep/'+RUN+'/REPORT.md) for published sources and comparison limits.\n\n## Run configuration\n\nImmutable per-config files under config/'+task+'/'+RUN+'/; no ensemble/refit or gate relaxation.\n\n## Benchmark metrics\n\n| Artifact | Location |\n|---|---|\n| Performance history | [JSON](../../../results/'+task+'/'+RUN+'/performance_history.json) |\n| Config trajectories | [PNG](../../../results/'+task+'/'+RUN+'/performance.png) |\n')
 S.dump(OUT/'documentation_complete.json',{'status':'COMPLETED','config_result_bundles':len(ledger),'snapshot_pngs':len(snapshots),'all_configs_retained':True})
 print(json.dumps({'snapshot_pngs':len(snapshots),'task_config_bundles':len(ledger),'report':str(OUT/'REPORT.md'),'main_image':str(ROOT/'results/001_general'/RUN/'performance_overview.png')},indent=2))

if __name__=='__main__':main()
