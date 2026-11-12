import pathlib,pandas as pd,json
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();R=pathlib.Path(ROOT)
for p in (R/'sources/Cas13_original/PredictiveModel_AllScreens/data').glob('*.csv'):
 x=pd.read_csv(p);print(p.name,x.shape,list(x.columns)[:12])
 if p.name in ['CompleteFeatureSet.csv','ModelInputFeatures_AllScreens_PerfectMatch.csv']:
  print(x[['Screen','normCS']].groupby('Screen').size().to_dict() if 'normCS' in x else 'NO normCS')
  native=pd.read_csv(R/'data/cas13_feature_table.csv')
  if 'normCS' in x and len(x)==len(native):print('NORMCS EXACT ROW ORDER',x.normCS.equals(native.normCS),'MAX_ABS',float((x.normCS-native.normCS).abs().max()))
print('PRIDICT TRAINED GROUPS')
for p in (R/'sources/PRIDICT2_release').rglob('trained_models'):
 for d in p.iterdir():
  if d.is_dir():print(d.name,[x.name for x in d.iterdir() if x.is_dir()])
