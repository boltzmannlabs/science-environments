import csv, hashlib, json, os, pathlib, sys, time
import numpy as np
import torch
from Bio.PDB.Polypeptide import index_to_one

R=pathlib.Path(__file__).resolve().parent
O=R/'results/local/task_005_sun_leh_pythia/v2/assisted/fresh-20261120'
S=pathlib.Path('retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433')
sys.path.insert(0,str(S))
from pythia.masked_ddg_scan import get_torch_model
from pythia.pdb_utils import read_pdb_to_protbb,get_neighbor
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
man=json.loads((O/'INPUT_MANIFEST.json').read_text())
assert sha(O/'original_1NWW.pdb')==man['input_pdb_sha256']
assert sha(O/'monomer_A.pdb')==man['monomer_A_pdb_sha256']
for f,h in {**man['source_files_sha256'],**man['checkpoints_sha256']}.items(): assert sha(S/f)==h, f
mapping=list(csv.DictReader((O/'residue_map.csv').open()))
torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(0)
assert not torch.cuda.is_available() or torch.version.cuda is None
models={c:get_torch_model(str(S/f'pythia/pythia-{c}.pt'),'cpu') for c in ('c','p')}
assert all(not x.training for x in models.values())
probes={}
for context,path in [('monomer_A',O/'monomer_A.pdb'),('dimer_AB',O/'original_1NWW.pdb')]:
    prot=read_pdb_to_protbb(str(path)); node,edge,seq=get_neighbor(prot,neighbor=32,noise_level=0.0,train=False)
    records=[r for r in mapping if r['context']==context and r['eligible']=='True']
    assert len(records)==len(seq)==node.shape[1]==edge.shape[1]
    assert tuple(node.shape)==(32,len(records),28) and tuple(edge.shape)==(32,len(records),27)
    assert bool((node[0,:,21]==1).all()) and bool((node[0,:,:21]==0).all())
    assert all(int(r['retained_index_1based'])==i+1 and index_to_one(int(seq[i]))==r['wt'] and int(prot.resseq[i])==int(r['pdb_resseq']) for i,r in enumerate(records))
    cross=int((edge[:,:,26]!=0).sum().item())
    if context=='dimer_AB': assert cross>0
    else: assert cross==0
    if context=='monomer_A':
        with torch.no_grad():
            x,y=models['c'](node[:,:2].float(),edge[:,:2].float())
            assert x.shape==(2,21) and torch.isfinite(x).all()
            probs=torch.softmax(x,dim=-1); native=seq[:2]
            scores=-torch.log(probs/probs[torch.arange(2),native,None]); assert torch.all(scores[torch.arange(2),native]==0)
    probes[context]={'node_shape':list(node.shape),'edge_shape':list(edge.shape),'retained_residues':len(records),'cross_chain_neighbor_count':cross,'mapping_and_mask_verified':True}
import Bio, pandas, scipy, pytorch_lightning, torchmetrics, joblib
v={'python':sys.version,'interpreter':sys.executable,'packages':{m.__name__:{'version':m.__version__,'origin':m.__file__} for m in (torch,Bio,np,pandas,scipy,pytorch_lightning,torchmetrics,joblib)},'checkpoint_load_c_and_p':'strict passed','models_eval':True,'diagnostic_forward':'C model, 2 monomer positions only; not full inference','contexts':probes,'device':'cpu','torch_threads':torch.get_num_threads(),'source_and_input_hashes':'passed'}
(O/'preflight.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
