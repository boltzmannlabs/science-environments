import pathlib,json,pandas as pd,numpy as np
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
cols=['wide_initial_target','wide_mutated_target','PBSlength','RTlength','group','PRIDICT2.0 HEK293T','PRIDICT2.0 K562','test_split_hek','test_split_k562']
a=pd.read_excel(ROOT/'data/PRIDICT2_published_results_with_test_splits.xlsx',usecols=cols);b=pd.read_csv(ROOT/'sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv');assert len(a)==len(b)==22956
assert a.wide_initial_target.equals(b.wide_initial_target) and a.wide_mutated_target.equals(b.wide_mutated_target);assert np.array_equal(a['group'],b.grp_id)
f=json.loads((ROOT/'data/PRIDICT2_original_grouped_folds.json').read_text());nativefold=np.full(len(b),-1,dtype=int)
for fold,part in f.items():nativefold[part['test']]=int(fold)
oof=pd.read_csv(ROOT/'predictions/PRIDICT2_OOF/OOF_ensemble_predictions_with_labels.csv');report={'data_row_and_group_identity_match':True,'conditions':{}}
for cell,col,scorecol in [('HEK','test_split_hek','PRIDICT2.0 HEK293T'),('K562','test_split_k562','PRIDICT2.0 K562')]:
 values=set(a[col].dropna().astype(int));assert values in [set(range(5)),set(range(1,6))],values;base=1 if values==set(range(1,6)) else 0
 valid=a[col].notna();mismatch=int((a.loc[valid,col].astype(int).to_numpy()-base!=nativefold[valid.to_numpy()]).sum())
 z=oof[oof.dataset_name==cell].set_index('seq_id');pred=z.loc[b.seq_id,'pred_averageedited'].to_numpy()*100;ref=a[scorecol].to_numpy();mask=np.isfinite(ref)
 r={'source_fold_ids':sorted(values),'source_index_base':base,'fold_assignment_mismatches':mismatch,'n_source_assigned_rows':int(valid.sum()),'comparison_rows':int(mask.sum()),'max_abs_native_vs_published_intended_score_percent_units':float(np.max(np.abs(pred[mask]-ref[mask]))),'mean_abs_score_difference_percent_units':float(np.mean(np.abs(pred[mask]-ref[mask])))};report['conditions'][cell]=r
 assert mismatch==0,'Original published fold assignment mismatch'
(ROOT/'reports/PRIDICT2_original_split_and_score_concordance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
