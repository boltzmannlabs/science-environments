"""Score the editor/cell-matched external library with the unchanged released BE-Hive regressor.
Actual31nt model-used context is supplied directly; absent unused50nt flanks are never fabricated.
"""
import pathlib,sys,json,hashlib
import numpy as np,pandas as pd,sklearn,Bio
from Bio.SeqUtils import MeltingTemp as mt
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
sys.path.insert(0,str(ROOT/'sources/be_efficiency'));import predict as be
be.init_model(base_editor='BE4',celltype='HEK293T')
def feature31(seq):
 vals=be.__one_hot_encode(seq)+be.__dinucleotide_encode(seq)
 vals += [seq.count('A'),seq.count('C'),seq.count('G'),seq.count('T'),seq.count('G')+seq.count('C')]
 vals += [mt.Tm_NN(seq),mt.Tm_NN(seq[-5:]),mt.Tm_NN(seq[-13:-5]),mt.Tm_NN(seq[-21:-13])]
 return np.asarray(vals,dtype=float)
checks=pd.read_csv(ROOT/'data/BEHive_feature_concordance_examples.csv')
for r in checks.to_dict('records'):
 zero=int(r['zero_index']);real50=r['context'][zero-19:zero+31];assert len(real50)==50
 native=be.__featurize(real50).reshape(-1);own=feature31(r['feature31']);assert np.array_equal(native,own)
print('NATIVE_FEATURE_CONCORDANCE',len(checks),'cases','dimension',len(native))
x=pd.read_csv(ROOT/'data/BEHive_external_heldout.csv');X=np.vstack([feature31(z) for z in x.feature31]);pred=be.model.predict(X);assert np.isfinite(pred).all();x['BEHive_predicted_logit_score']=pred
x[['name','guide','feature31','Y','Y_weight','BEHive_predicted_logit_score']].to_csv(ROOT/'predictions/BEHive_BE4_HEK293T_external_predictions.csv',index=False)
identity={'python':sys.version,'sklearn':sklearn.__version__,'numpy':np.__version__,'pandas':pd.__version__,'biopython':Bio.__version__,'model_class':str(type(be.model)),'source_model_sha256':hashlib.sha256((ROOT/'sources/be_efficiency/params/HEK293T_12kChar_BE4_bestmodel.pkl').read_bytes()).hexdigest(),'model_parameters':be.model.get_params(),'feature_concordance_cases':len(checks),'feature_count':X.shape[1],'finite_predictions':len(pred),'no_test_calibration':True}
(ROOT/'protocols/BEHive_model_identity.json').write_text(json.dumps(identity,indent=2));print(json.dumps(identity,indent=2));print('BEHIVE_EXTERNAL_FRESH_DONE',len(x))
