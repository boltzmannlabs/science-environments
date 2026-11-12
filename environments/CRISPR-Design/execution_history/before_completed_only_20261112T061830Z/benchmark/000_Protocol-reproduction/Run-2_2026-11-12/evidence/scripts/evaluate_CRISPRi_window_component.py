"""CRISPRi window-rule component test on original held-out genes and real phenotypic labels.
This is explicitly not a reproduction of Horlbeck's808-feature chromatin/sequence model.
"""
import pathlib,json,pandas as pd,numpy as np
from sklearn.metrics import precision_score,recall_score,roc_auc_score
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
D=ROOT/'sources/crispria/data_files';info=pd.read_csv(D/'CRISPRi_trainingdata_sgRNAInfoTable.txt',sep='\t');truth=pd.read_csv(D/'CRISPRi_trainingdata_activityScores.txt',sep='\t',header=None,names=['sgId','normalized_activity']);lib=pd.read_csv(D/'CRISPRi_trainingdata_libraryTable.txt',sep='\t')
assert info.sgId.to_list()==lib.sgId.to_list();parts=json.loads((ROOT/'data/CRISPRi_author_train_test_indices.json').read_text());train=set(info.iloc[parts['train']].gene_name);test=set(info.iloc[parts['test']].gene_name);assert not train&test
x=info.merge(truth,on='sgId',how='left',sort=False,validate='one_to_one');assert x.sgId.to_list()==info.sgId.to_list();x=x.iloc[parts['test']].copy()
tss=pd.read_csv(D/'human_tssTable.txt',sep='\t');groups={g:z for g,z in tss.groupby('gene')}
protocol={'model':'Project CRISPRi PAM/TSS-window gate only','window_bp':[-75,200],'positive_phenotype':'source normalized guide activity >=0.75; not75% knockdown','input_annotation':'source human hg19/FANTOM/Ensembl-fallback TSS point positions, all annotated TSSs per gene, source coordinates retained without assembly conversion','test_split':'original source test indices; train/test gene sets disjoint, verified','n_heldout_genes':len(test),'source_model_NOT_reproduced':'Full Horlbeck808-feature model, chromatin transformation and learned weights are not substituted by this geometric rule','nuclease_activity_scores':'NOT_USED','frozen_before_computing_metrics':True}
(ROOT/'protocols/CRISPRi_window_component.json').write_text(json.dumps(protocol,indent=2))
rows=[];missing=0
for r in x.to_dict('records'):
 g=groups.get(r['gene_name'])
 if g is None or pd.isna(r['normalized_activity']):missing+=1;continue
 dist=(float(r['pam coordinate'])-g.position.to_numpy())*np.where(g.strand.to_numpy()=='+',1,-1)
 eligible=bool(((dist>=-75)&(dist<=200)).any());rows.append({'sgId':r['sgId'],'gene':r['gene_name'],'activity':r['normalized_activity'],'phenotype_high':r['normalized_activity']>=.75,'in_project_TSS_window':eligible,'TSS_count':len(g)})
z=pd.DataFrame(rows);z.to_csv(ROOT/'predictions/CRISPRi_window_heldout_phenotypes.csv',index=False);assert len(z)>100 and z.phenotype_high.nunique()==2
precision=float(precision_score(z.phenotype_high,z.in_project_TSS_window,zero_division=0));recall=float(recall_score(z.phenotype_high,z.in_project_TSS_window));roc=float(roc_auc_score(z.phenotype_high,z.in_project_TSS_window.astype(int)))
idx=[g.index.to_numpy() for _,g in z.groupby('gene')];boots=[]
for b in range(1000):
 rng=np.random.RandomState(b);i=np.concatenate([idx[j] for j in rng.choice(len(idx),len(idx),replace=True)]);a=z.iloc[i];boots.append([precision_score(a.phenotype_high,a.in_project_TSS_window,zero_division=0),recall_score(a.phenotype_high,a.in_project_TSS_window)])
s={'status':'COMPLETED_COMPONENT_ONLY_PHENOTYPIC_TEST','n':len(z),'genes':z.gene.nunique(),'excluded_missing_annotation_or_label':missing,'n_high_activity':int(z.phenotype_high.sum()),'n_window_positive':int(z.in_project_TSS_window.sum()),'precision_for_high_normalized_activity':precision,'recall_for_high_normalized_activity':recall,'binary_window_AUROC':roc,'gene_bootstrap_precision_ci95':np.quantile(np.array(boots)[:,0],[.025,.975]).tolist(),'gene_bootstrap_recall_ci95':np.quantile(np.array(boots)[:,1],[.025,.975]).tolist(),'full_CRISPRi_model_validated':False,'limits':['A fixed window gate is not the learned CRISPRi activity model or an essential-gene screen','Source-coordinate distances retained; no claim of validating the modern GENCODE49 adapter on these hg19 annotations','No mammalian nuclease activity score used as a repression surrogate']}
(ROOT/'reports/CRISPRi_component_phenotype_metrics.json').write_text(json.dumps(s,indent=2));print(json.dumps(s,indent=2))
