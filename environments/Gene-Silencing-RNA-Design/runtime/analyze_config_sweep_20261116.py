"""Analyze every frozen sweep config and export task-indexed results and truthful trajectory figures.
No refitting; no claim of prospective validation or monotonic model convergence.
"""
import csv,json,math,pathlib,sys,statistics,hashlib,datetime
import numpy as np
from scipy.stats import rankdata,spearmanr,pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import config_sweep_20261116 as S
OUT=S.OUT;RUN=S.RUN;OLD=S.OLD
COLORS=['#606060','#0072B2','#D55E00','#CC79A7'];IDS=[c['config_id'] for c in S.CFG]
ACC={'HIF1A':'NM_001530.4','HPSE':'NM_001098540.3','HK2':'NM_000189.5','MYC':'NM_002467.6'}
PRIMARY=['HIF1A','HPSE','HK2'];image_metadata=[]

def auc(y,s):
 y=np.asarray(y,dtype=bool);s=np.asarray(s);a=int(y.sum());b=len(y)-a
 return float((rankdata(s)[y].sum()-a*(a+1)/2)/(a*b)) if a and b else None
def cor(x,y):return float(spearmanr(x,y).statistic) if len(x)>=3 and len(set(x))>1 and len(set(y))>1 else None
def metric(rr,seed=42):
 labels=np.array([float(r['label']) for r in rr]);scores=np.array([float(r['score']) for r in rr]);y=labels>=.7;n1=int(y.sum());n0=len(y)-n1
 v=auc(y,scores);boot=[];rng=np.random.default_rng(seed)
 if min(n0,n1)>=5:
  for _ in range(1000):
   ix=np.r_[rng.choice(np.where(y)[0],n1),rng.choice(np.where(~y)[0],n0)];boot.append(auc(y[ix],scores[ix]))
 order=np.argsort(-scores,kind='stable');k=min(10,len(rr))
 return {'n':len(rr),'n_positive':n1,'n_negative':n0,'auc':v,'spearman':cor(labels.tolist(),scores.tolist()),'pearson':float(pearsonr(labels,scores).statistic) if len(set(labels))>1 and len(set(scores))>1 else None,'precision_top10':float(y[order[:k]].mean()) if k else None,'auc_ci95_row_bootstrap':np.quantile(boot,[.025,.975]).tolist() if boot else None,'ci_caveat':'Exploratory within-cohort class-stratified row bootstrap; overlapping sites violate independence. No interval for fewer than five observations in either class.','reference':'Sciabola PMID 23241392; prior Run-3 same-cohort RN.Ai predictions. OligoFormer paper PMID 39321261 Mixset AUC .8163 is DIFFERENT cohort/protocol, not a matched superiority target.'}

def paired_delta(rr,bb):
 by={r['row_id']:r for r in bb};rr=[r for r in rr if r['row_id'] in by];y=np.array([float(r['label'])>=.7 for r in rr]);s=np.array([float(r['score']) for r in rr]);bs=np.array([float(by[r['row_id']]['score']) for r in rr]);obs=auc(y,s)-auc(y,bs) if y.any() and (~y).any() else None;delta=[];n1=int(y.sum());n0=len(y)-n1;rng=np.random.default_rng(42)
 if min(n0,n1)>=5:
  for _ in range(1000):
   ix=np.r_[rng.choice(np.where(y)[0],n1),rng.choice(np.where(~y)[0],n0)];delta.append(auc(y[ix],s[ix])-auc(y[ix],bs[ix]))
 return {'paired_n':len(rr),'auc_delta_vs_C00':obs,'auc_delta_ci95_exploratory':np.quantile(delta,[.025,.975]).tolist() if delta else None,'multiplicity':'Four fixed configs, exploratory intervals without multiplicity correction; do not infer confirmed superiority.'}

def savefig(fig,d,name='performance'):
 d=pathlib.Path(d);d.mkdir(parents=True,exist_ok=True);fig.canvas.draw()
 for ax in fig.axes:
  if ax.has_data():
   assert all(math.isfinite(v) for v in ax.get_xlim()+ax.get_ylim())
 fig.savefig(d/(name+'.png'),dpi=200,bbox_inches='tight',facecolor='white');fig.savefig(d/(name+'.svg'),bbox_inches='tight',facecolor='white');plt.close(fig)
 with Image.open(d/(name+'.png')) as im:
  im.verify()
 with Image.open(d/(name+'.png')) as im:meta={'path':str((d/(name+'.png')).relative_to(ROOT)),'width':im.width,'height':im.height,'format':im.format,'decoded':True}
 image_metadata.append(meta)

def aucplot(task,records,title,selection=None):
 d=ROOT/'results'/task/RUN
 fig,axs=plt.subplots(1,2,figsize=(12,4.7),layout='constrained')
 x=np.arange(len(records));vals=[r['auc'] for r in records]
 axs[0].plot(x,vals,color='#555555',linewidth=1)
 for i,r in enumerate(records):
  axs[0].scatter(i,r['auc'],color=COLORS[i],s=65,zorder=3)
  if r.get('auc_ci95_row_bootstrap'):
   lo,hi=r['auc_ci95_row_bootstrap'];axs[0].errorbar(i,r['auc'],yerr=[[max(0,r['auc']-lo)],[max(0,hi-r['auc'])]],color=COLORS[i],capsize=4)
 axs[0].axhline(.5,color='black',linestyle=':',label='Chance AUC')
 axs[0].set(ylim=(0,1.05),ylabel='Measured-cohort ROC AUC',xticks=x,xticklabels=['C00','C01','C02','C03'],xlabel='Fixed config order (not training epochs)')
 if selection:
  axs[1].plot(x,[r['retrospective_loto_selected_macro_auc'] for r in selection],'-o',color='#0072B2',label='Leave-one-target-out selected endpoint')
  axs[1].plot(x,[r['fixed_config_macro_auc'] for r in selection],'--s',color='#D55E00',label='Actual fixed-config macro AUC')
  axs[1].set(ylabel='Macro AUC over HIF1A, HPSE and HK2',ylim=(0,1.05));axs[1].legend(fontsize=8,loc='lower left')
 else:
  kk=min(10,records[0]['n'])
  axs[1].plot(x,[r['precision_top10'] for r in records],'-o',color='#0072B2');axs[1].set(ylabel=f'Measured positives among top {kk} / {kk}',ylim=(0,1.05))
 axs[1].set(xticks=x,xticklabels=['C00','C01','C02','C03'],xlabel='All tried configs retained')
 fig.suptitle(title,fontsize=13)
 fig.supxlabel('C00 RN.Ai source guide | C01 RN.Ai first-19 core | C02 RNAiSpline core | C03 cached OligoFormer core\nRetrospective, previously examined cohorts; no guaranteed convergence or biological validation.',fontsize=8)
 savefig(fig,d)


def rank_panel(task,cfg):
 # All numeric and application gates remain the original Run-3 task decisions. Only efficacy ordering changes.
 old=ROOT/'results'/task/OLD
 if not (old/'gate_decisions.csv').exists():return None
 good={r['candidate_id'] for r in S.readcsv(old/'gate_decisions.csv') if r['gate_pass']=='True'}
 rows=[r for r in S.readcsv(old/'per_dimension_evidence.csv') if r['candidate_id'] in good]
 brief=json.loads((old/'00_inputs/requirement_brief.json').read_text());w=brief['priorities']['weights']
 col=['eff_RN.Ai-Predict','eff_RN.Ai-Predict','eff_RNAiSpline','oligoformer_native_score'][cfg['ordinal']]
 dims={'efficacy':(col,1),'specificity':('pots_seed_percentile',-1),'seed_tox':('seed_tox_viability_avg_human',1),'stability':('guide_target_duplex_delta_g_kcal_mol',-1)}
 norm={}
 for dim,(key,sgn) in dims.items():
  vals=np.array([float(r[key]) for r in rows]);assert np.isfinite(vals).all();p=(rankdata(vals)-1)/max(1,len(rows)-1);norm[dim]=p if sgn>0 else 1-p
 def choose(weights):
  score=sum(weights.get(dim,0)*values for dim,values in norm.items());order=np.argsort(-score,kind='stable');picked=[];seeds=set();starts=[]
  for idx in order:
   r=rows[idx];seed=r['guide_sequence'][1:8];start=int(float(r['target_start']))
   if seed in seeds or any(abs(start-s)<19 for s in starts):continue
   seeds.add(seed);starts.append(start);picked.append({**r,'selected_primary_efficacy_column':col,'selected_native_efficacy_score':float(r[col]),'requirement_preference_score':float(score[idx]),'evidence_status':'NEEDS_EXPERIMENTAL_VALIDATION'})
   if len(picked)>=brief['constraints']['panel_size']:break
  return picked
 panel=choose(w);base={r['candidate_id'] for r in panel};sens={}
 for dim,value in w.items():
  for scale in [.75,1.25]:
   ww=dict(w);ww[dim]=value*scale;other={r['candidate_id'] for r in choose(ww)};sens[dim+str(scale)]=len(base&other)/len(base|other) if base|other else None
 return panel,{'n_gate_survivors':len(rows),'n_panel':len(panel),'primary_efficacy_column':col,'stability_post_diversity_jaccard':sens,'mean_panel_jaccard_pm25pct':float(np.mean(list(sens.values()))) if all(v is not None for v in sens.values()) else None,'immune_dimension':'Hard filters inherited; weighted immune component absent and explicitly contributes zero.','gates_recomputed':False,'gate_decision_source':str((old/'gate_decisions.csv').relative_to(ROOT)),'gate_source_sha256':S.sha(old/'gate_decisions.csv'),'new_model_inference':False,'interpretation':'Fresh reranking of previously evaluated gate-clean candidates, not fresh generation or a new battery. No efficacy endpoints averaged. Missing application-context stages remain unrun.','best_design':None}


def main():
 if not (OUT/'inference_summary.json').exists():raise RuntimeError('Execute frozen inference first')
 if (OUT/'sweep_summary.json').exists():raise RuntimeError('Report already complete; do not overwrite a sweep')
 allrows=S.readcsv(OUT/'all_measured_predictions.csv');by={(c['config_id'],g):[r for r in allrows if r['config_id']==c['config_id'] and r['gene']==g] for c in S.CFG for g in ACC}
 table=[]
 for cfg in S.CFG:
  for gene in ACC:
   rr=by[cfg['config_id'],gene];m=metric(rr);m.update(config_id=cfg['config_id'],gene=gene,ordinal=cfg['ordinal']);m.update(paired_delta(rr,by[IDS[0],gene]));table.append(m)
 S.dump(OUT/'measured_metrics.json',table);S.csvout(OUT/'measured_metrics.csv',[{k:v for k,v in r.items() if not isinstance(v,(list,dict))} for r in table])
 lookup={(r['config_id'],r['gene']):r for r in table}
 selection=[]
 for prefix in range(1,len(IDS)+1):
  folds=[]
  for held in PRIMARY:
   train=[g for g in PRIMARY if g!=held];cid=max(IDS[:prefix],key=lambda c:np.mean([lookup[c,g]['auc'] for g in train]));folds.append({'held_gene':held,'selection_genes':train,'chosen_config':cid,'selection_macro_auc':float(np.mean([lookup[cid,g]['auc'] for g in train])),'held_gene_auc':lookup[cid,held]['auc'],'held_gene_baseline_auc':lookup[IDS[0],held]['auc']})
  selection.append({'step':prefix-1,'new_config':IDS[prefix-1],'fixed_config_macro_auc':float(np.mean([lookup[IDS[prefix-1],g]['auc'] for g in PRIMARY])),'retrospective_loto_selected_macro_auc':float(np.mean([f['held_gene_auc'] for f in folds])),'folds':folds,'warning':'Previously exposed data, not a clean holdout. Leave-target-out protects this config-selection step only; no claim that pretrained checkpoints were trained without these cohorts.'})
 S.dump(OUT/'retrospective_target_out_selection.json',selection)
 # Main multicohort task uses precisely the same 301 rows for every configuration.
 general=[]
 for cfg in S.CFG:
  rr=[r for r in allrows if r['config_id']==cfg['config_id'] and r['gene'] in PRIMARY];m=metric(rr);m.update(config_id=cfg['config_id'],macro_auc=float(np.mean([lookup[cfg['config_id'],g]['auc'] for g in PRIMARY])));general.append(m)
 # Anchor ranks are diagnostic only, never used to choose the efficacy config.
 ttr=S.readcsv(OUT/'ttr_pool_predictions.csv');anchors=json.loads((S.OLD_B/'ttr_same_side/site_rank_comparison.json').read_text())
 oldanchors=S.readcsv(S.OLD_B/'ttr_same_side/per_dimension_anchor_evidence.csv');ar=[]
 for cfg in S.CFG:
  rr=[r for r in ttr if r['config_id']==cfg['config_id']];ranks=rankdata([-float(r['score']) for r in rr]);n=len(rr)
  for name in ['patisiran','vutrisiran']:
   guide=next(r['guide_sequence'] for r in oldanchors if r['candidate_id']==name+'_derived_19nt_core');i=next(i for i,r in enumerate(rr) if r['guide_source']==guide)
   ar.append({'config_id':cfg['config_id'],'ordinal':cfg['ordinal'],'anchor':name,'rank':float(ranks[i]),'pool_n':n,'percentile':100*(1-(ranks[i]-1)/(n-1)),'native_score':float(rr[i]['score']),'label':'Known projected 19-nt core; no clinical potency labels; do not optimize to anchor recovery.'})
 S.csvout(OUT/'TTR_anchor_metrics.csv',ar)
 dup=S.readcsv(OUT/'htt_duplex_predictions.csv');dm=[]
 for cfg in S.DUPLEX:
  rr=[r for r in dup if r['config_id']==cfg['config_id']];unc=[r for r in rr if r['censored']=='False'];dm.append({'config_id':cfg['config_id'],'ordinal':cfg['ordinal'],'n':len(rr),'n_uncensored':len(unc),'spearman_ddg_vs_logDR':cor([float(r['ddg']) for r in unc],[float(r['log10_DR']) for r in unc]),'temperature_c':37,'interpretation':'Physical-model sensitivity, NOT biological optimization; default salt=1.021 M retained; no claim of patient allele selectivity.'})
 neuro=S.readcsv(OUT/'htt_context_control_predictions.csv');nm=[]
 for cfg in S.NEURO:
  rr=[r for r in neuro if r['config_id']==cfg['config_id']];nm.append({'config_id':cfg['config_id'],'ordinal':cfg['ordinal'],'n':len(rr),'spearman_vs_neglog10_ic50':cor([float(r['score']) for r in rr],[-math.log10(float(r['ic50_match_nM'])) for r in rr]),'interpretation':'All configs lack genuine flanks. No CNS design, no valid-context efficacy improvement claim or selected optimum.'})
 S.dump(OUT/'HTT_duplex_metrics.json',dm);S.dump(OUT/'HTT_context_metrics.json',nm)
 # Write every tried config into its task result folder, keeping configurations immutable.
 taskstatus=[];configledger=[]
 for task in S.TASKS:
  if task in S.SKIP:
   taskstatus.append({'task':task,'configs_executed':0,'status':'SKIPPED_NO_MATCHED_BENCHMARK','reason':S.SKIP[task]});continue
  d=ROOT/'results'/task/RUN;records=[]
  for cfg in S.configset(task):
   cid=cfg['config_id'];cd=d/cid;cd.mkdir(exist_ok=False)
   cf=ROOT/'config'/task/RUN/cid/'benchmark_config.json';(cd/'benchmark_config.json').write_bytes(cf.read_bytes())
   if task.startswith('004'):
    result=next(r for r in dm if r['config_id']==cid);rr=[r for r in dup if r['config_id']==cid]
   elif task.startswith('007'):
    result=next(r for r in nm if r['config_id']==cid);rr=[r for r in neuro if r['config_id']==cid]
   elif task.startswith(('003','006')):
    result={'config_id':cid,'ordinal':cfg['ordinal'],'status':'ANCHOR_DIAGNOSTIC_ONLY','n':598,'anchors':[r for r in ar if r['config_id']==cid],'selection':'No anchor-based best config selected; not measured efficacy.'};rr=[r for r in ttr if r['config_id']==cid]
   elif task.startswith('001'):
    result=general[cfg['ordinal']]|{'ordinal':cfg['ordinal'],'retrospective_loto_selected_macro_auc':selection[cfg['ordinal']]['retrospective_loto_selected_macro_auc']};rr=[r for r in allrows if r['config_id']==cid and r['gene'] in PRIMARY]
   else:
    gene='MYC' if task.startswith('010') else 'HK2';result=dict(lookup[cid,gene]);rr=by[cid,gene]
    if gene=='HK2':
     held=next(f for f in selection[-1]['folds'] if f['held_gene']=='HK2');result['external_gene_selection']=held
   S.dump(cd/'metrics.json',result);S.csvout(cd/'predictions.csv',rr)
   rerank=rank_panel(task,cfg) if not task.startswith(('004','007')) else None
   if rerank:
    panel,stability=rerank;S.csvout(cd/'panel.csv',panel);S.dump(cd/'panel_stability.json',stability);result.update(panel_size=len(panel),mean_panel_stability=stability['mean_panel_jaccard_pm25pct']);S.dump(cd/'metrics.json',result)
   S.dump(cd/'provenance.json',{'config_sha256':S.sha(cf),'frozen_plan_sha256':S.sha(OUT/'frozen_plan.json'),'shared_measured_predictions':str((OUT/'all_measured_predictions.csv').relative_to(ROOT)),'analysis_script_sha256':S.sha(__file__),'original_sources_unchanged':True,'best_design':None,'status':'EXECUTED_BENCHMARK_ANALYSIS_OR_EXPLICIT_SCORE_REUSE','generation_rerun':False,'models_ensembled':False})
   records.append(result);configledger.append({'task':task,'config_id':cid,'ordinal':cfg['ordinal'],'config_path':str(cf.relative_to(ROOT)),'config_sha256':S.sha(cf),'results_path':str(cd.relative_to(ROOT)),'status':'EXECUTED','performance_metric':'AUC' if 'auc' in result else ('anchor_rank' if task.startswith(('003','006')) else 'Spearman'),'full_application_complete':False})
  S.dump(d/'performance_history.json',records)
  if task.startswith('001'):aucplot(task,general,'General efficacy benchmark: matched 301-row cohort',selection)
  elif task.startswith(('002','009','010','011')):
   gene='MYC' if task.startswith('010') else 'HK2';aucplot(task,records,gene+' — '+task+'\n'+('n=7, one positive: descriptive only; no meaningful convergence claim' if gene=='MYC' else 'n=95; exploratory class-stratified row-bootstrap intervals'))
  elif task.startswith(('003','006')):
   fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
   for name,color in [('patisiran','#0072B2'),('vutrisiran','#D55E00')]:
    rr=[r for r in ar if r['anchor']==name];ax.plot([r['ordinal'] for r in rr],[r['percentile'] for r in rr],'-o',color=color,label=name+' projected core')
   ax.set(xticks=range(4),xticklabels=['C00','C01','C02','C03'],ylim=(0,103),ylabel='Percentile rank among 598 native-score windows',xlabel='Fixed endpoint configs; anchor ranks NOT an optimization objective',title='TTR known-site recovery — '+task);ax.legend();fig.supxlabel('Unmodified 19-nt cores; no clinical efficacy comparison. Flat C00/C01 is expected: identical 19-nt inputs.',fontsize=8);savefig(fig,d)
  else:
   metricname='spearman_ddg_vs_logDR' if task.startswith('004') else 'spearman_vs_neglog10_ic50';fig,ax=plt.subplots(figsize=(9,5),layout='constrained');xx=list(range(len(records)));yy=[r[metricname] for r in records];ax.plot(xx,yy,'-o',color='#0072B2');ax.axhline(0,color='#555555',linestyle=':');ax.set(xticks=xx,xticklabels=[r['config_id'].split('_')[0] for r in records],ylim=(-1,1),ylabel='Spearman correlation with published reporter outcomes',xlabel='Frozen physical/input sensitivity configs',title=task+' — descriptive sensitivity only');fig.supxlabel('No hyperparameter promotion; shared reporters and missing reference/context prevent a design-validation claim.',fontsize=8);savefig(fig,d)
  taskstatus.append({'task':task,'configs_executed':len(records),'status':'EXECUTED_RETROSPECTIVE_ANALYSIS' if task.startswith(('001','002','009','011')) else 'EXECUTED_DESCRIPTIVE_SENSITIVITY','full_application_complete':False})
  (d/'REPORT.md').write_text('# '+task+' '+RUN+'\n\nAll '+str(len(records))+' frozen configurations are retained in their own result folders; see performance_history.json and performance.png/SVG.\n\n'+('Retrospective matched measured-cohort evaluation; no untouched holdout or biological validation.' if task.startswith(('001','002','009','011')) else 'Descriptive anchors, small-n cohort or physical/context sensitivity only; no selected clinical/design optimum.')+'\n\nOriginal generation pools and gate decisions are reused explicitly; no new generation or full application completion is claimed. Native efficacy endpoints are never averaged. Panels, when present, are reranked gate-clean prior candidates and remain NEEDS_EXPERIMENTAL_VALIDATION.\n')
  S.csvout(d/'performance_history.csv',[{k:v for k,v in r.items() if not isinstance(v,(list,dict))} for r in records])
 # Overview image is copied to general results as the easy-to-open entry point.
 fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
 for gene,color in zip(PRIMARY,['#0072B2','#D55E00','#009E73']):axs[0,0].plot(range(4),[lookup[c,gene]['auc'] for c in IDS],'-o',label=gene,color=color)
 axs[0,0].set(title='Matched published-cohort ordering by target',ylabel='AUC',ylim=(0,1.05));axs[0,0].legend(fontsize=8)
 axs[0,1].plot(range(4),[s['fixed_config_macro_auc'] for s in selection],'--o',label='Each actual config',color='#D55E00');axs[0,1].plot(range(4),[s['retrospective_loto_selected_macro_auc'] for s in selection],'-s',label='Other-target-selected config',color='#0072B2');axs[0,1].set(title='Retrospective cross-target selection trajectory',ylabel='Macro AUC',ylim=(0,1.05));axs[0,1].legend(fontsize=8)
 for name,color in [('patisiran','#0072B2'),('vutrisiran','#D55E00')]:axs[1,0].plot(range(4),[r['percentile'] for r in ar if r['anchor']==name],'-o',label=name,color=color)
 axs[1,0].set(title='TTR anchor diagnostics, not measured efficacy',ylabel='Core-site percentile',ylim=(0,103));axs[1,0].legend(fontsize=8)
 axs[1,1].plot(range(4),[r['spearman_ddg_vs_logDR'] for r in dm],'-o',color='#0072B2');axs[1,1].axhline(0,linestyle=':',color='#555555');axs[1,1].set(title='HTT physical-model sensitivity (not optimization)',ylabel='Spearman vs log discrimination ratio',ylim=(-1,1))
 for i,ax in enumerate(axs.flat):ax.set(xticks=range(4),xticklabels=['D00','D01','D02','D03'] if i==3 else ['C00','C01','C02','C03'],xlabel='Every tried config retained');ax.grid(alpha=.2)
 fig.suptitle('siRNA workflow configuration trajectories — '+RUN,fontsize=15)
 fig.supxlabel('C00 RN.Ai native | C01 RN.Ai core19 | C02 RNAiSpline core19 | C03 cached OligoFormer\nFixed retrospective grid; not training convergence. No guarantee of monotonic improvement or superiority over a different published cohort.',fontsize=9)
 savefig(fig,OUT,'performance_overview');gd=ROOT/'results/001_general'/RUN
 for ext in ['png','svg']:(gd/('performance_overview.'+ext)).write_bytes((OUT/('performance_overview.'+ext)).read_bytes())
 S.csvout(OUT/'config_execution_ledger.csv',configledger);S.dump(OUT/'task_status.json',taskstatus);S.dump(OUT/'figure_validation.json',image_metadata)
 best=max(IDS,key=lambda c:np.mean([lookup[c,g]['auc'] for g in PRIMARY]));summary={'run_id':RUN,'task_folders':len(S.TASKS),'tasks_with_executed_configs':sum(r['configs_executed']>0 for r in taskstatus),'task_config_results':len(configledger),'unique_efficacy_configs':len(S.CFG),'unique_physical_configs':len(S.DUPLEX),'unique_missing_context_configs':len(S.NEURO),'skipped_tasks':S.SKIP,'figures_original_png':len(image_metadata),'frozen_configs_sha256':S.sha(OUT/'frozen_plan.json'),'baseline_macro_auc':selection[0]['fixed_config_macro_auc'],'best_observed_fixed_config':best,'best_observed_fixed_macro_auc':float(np.mean([lookup[best,g]['auc'] for g in PRIMARY])),'retrospective_loto_selected_macro_auc_final':selection[-1]['retrospective_loto_selected_macro_auc'],'selection_claim':'Exploratory retrospective improvement only; all cohorts previously examined; no production default automatically changed.','full_application_tasks_completed':0,'new_models_trained':0,'new_generation_runs':0,'all_native_endpoints_separate':True,'old_results_preserved':True}
 S.dump(OUT/'sweep_summary.json',summary);print(json.dumps(summary,indent=2));print('TARGET_METRICS',json.dumps([{k:r[k] for k in ['gene','config_id','auc','auc_delta_vs_C00']} for r in table],indent=2))

if __name__=='__main__':main()
