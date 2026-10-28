"""Optional tiny-checkpoint test in an isolated scientific Python runtime."""
import os
from pathlib import Path
import subprocess

import pytest


@pytest.mark.skipif(not os.environ.get('SRG_YIELD_TEST_PYTHON'), reason='scientific runtime explicitly selected by host')
def test_strict_used_weights_without_unused_language_model_head(tmp_path):
    worker = Path(__file__).resolve().parents[1] / 'src/synthesis_route_gym/reactiont5_worker.py'
    script = r'''
import hashlib, json, runpy, sys
from pathlib import Path
import torch
from transformers import T5Config, T5ForConditionalGeneration
from safetensors.torch import save_file
from tokenizers import Tokenizer, models
root=Path(sys.argv[1])
worker=runpy.run_path(sys.argv[2])
config=T5Config(d_model=8,d_ff=16,d_kv=8,num_layers=1,num_decoder_layers=1,num_heads=1,
                vocab_size=5,decoder_start_token_id=0,tie_word_embeddings=False)
config.to_json_file(root/'config.json')
base=T5ForConditionalGeneration(config)
state={'model.'+key:value.clone() for key,value in base.state_dict().items() if key!='lm_head.weight'}
for name,shape in {'fc1':(8,4),'fc2':(8,4),'fc3':(8,8),'fc4':(8,8),'fc5':(8,1)}.items():
 for key,value in torch.nn.Linear(*shape).state_dict().items():
  state[name+'.'+key]=value.clone()
Tokenizer(models.WordLevel({'<pad>':0,'</s>':1,'<unk>':2,'C':3,'O':4},unk_token='<unk>')).save(str(root/'tokenizer.json'))
for name in ['tokenizer_config.json','special_tokens_map.json']:
 (root/name).write_text('{}')
def manifest(values):
 save_file(values,str(root/'model.safetensors'))
 files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
 return {'model_dir':str(root),'files':files,'runtime_versions':{},'device':'cpu','num_threads':1}
encode,infer,unknown=worker['load_backend'](manifest(state))
assert encode('C')==[3] and unknown==2
assert isinstance(infer([3]),float)
for bad in ({key:value for key,value in state.items() if key!='fc5.weight'},
            {**state,'unexpected.weight':torch.zeros(1)}):
 try:
  worker['load_backend'](manifest(bad))
 except RuntimeError:
  pass
 else:
  raise AssertionError('Incomplete or unexpected used weights must fail strict loading')
print('strict_used_weights_verified')
'''
    result = subprocess.run([os.environ['SRG_YIELD_TEST_PYTHON'],'-c',script,str(tmp_path),str(worker)],
                            capture_output=True,text=True,timeout=60,check=False)
    assert result.returncode == 0, result.stderr
    assert 'strict_used_weights_verified' in result.stdout
