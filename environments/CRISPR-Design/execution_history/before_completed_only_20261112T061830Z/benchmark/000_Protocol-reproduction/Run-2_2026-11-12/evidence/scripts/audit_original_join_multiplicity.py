import pathlib,pandas as pd,json
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'predictions/cas9_fresh_shared_holdout_joined.csv')
cp=pd.read_csv(ROOT/'sources/rs_dev/data/external/crispron_rs_dev_all_sgrnas.csv')
multiplicity=cp.groupby('30mer').size();print('AUTHOR_CP_ROWS',len(cp),'UNIQUE_CONTEXTS',cp['30mer'].nunique(),'DUPLICATES',int((multiplicity-1).sum()))
x['original_CP_join_multiplicity']=x['sgRNA Context Sequence'].map(multiplicity);assert x.original_CP_join_multiplicity.notna().all()
expanded=x.loc[x.index.repeat(x.original_CP_join_multiplicity.astype(int))].reset_index(drop=True)
print('EXPANDED_COUNTS',expanded.groupby('dataset').size().to_dict());print('EXPANDED_ROWS',len(expanded),'UNIQUE',expanded['sgRNA Context Sequence'].nunique())
expected={'Aguirre2016':7828,'Behan2019':7025,'Chari2015':1130,'Kim2019_test':518,'Koike-Yusa2014':6718,'Shalem2014':3968}
match=expanded.groupby('dataset').size().to_dict()==expected
report={'author_prediction_table_rows':len(cp),'unique_prediction_contexts':cp['30mer'].nunique(),'extra_rows_from_repeated_prediction_keys':int((multiplicity-1).sum()),'source_no_dedup_join_matches_cached_counts':match,'source_rows':len(expanded),'unique_contexts':expanded['sgRNA Context Sequence'].nunique(),'counts':expanded.groupby('dataset').size().to_dict(),'explanation':'Official notebook merges the raw CRISPRon score table without deduplicating identical context/prediction keys. Our first pass deliberately made that join many-to-one. Exact source-row replay and deduplicated sensitivity must be reported separately; duplicates must not be silently presented as independent biological observations.'}
(ROOT/'reports/cas9_source_multiplicity_audit.json').write_text(json.dumps(report,indent=2))
if match:expanded.to_csv(ROOT/'predictions/cas9_exact_notebook_multiplicity_replay.csv',index=False)
print(json.dumps(report,indent=2))
