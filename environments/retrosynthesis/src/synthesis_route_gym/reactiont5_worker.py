"""Isolated local inference for the published ReactionT5v2 yield architecture.

The linear-head architecture follows sagawa/ReactionT5v2-yield (MIT). Model
assets contain data only; no model-repository Python or pickle is executed.
"""
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys


def run_predictions(rows, encode, infer, *, max_tokens, unknown_id):
    """Single-row inference preserves the published decoder's padding semantics."""
    predictions = []
    for row in rows:
        ids = encode(row['text'])
        raw = None
        reason = None
        if len(ids) > max_tokens:
            reason = 'token_limit_exceeded'
        elif unknown_id is not None and unknown_id in ids:
            reason = 'unknown_token'
        else:
            raw = float(infer(ids))
            if not math.isfinite(raw):
                raw, reason = None, 'nonfinite_prediction'
        predictions.append({'id':row['id'],'raw_yield_percent':raw,'reason':reason})
    return predictions


def _verify(manifest):
    for name, expected in manifest['files'].items():
        digest = hashlib.sha256()
        with (Path(manifest['model_dir']) / name).open('rb') as handle:
            for chunk in iter(lambda:handle.read(1024*1024),b''):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise ValueError('Model asset digest mismatch')
    for package, expected in manifest['runtime_versions'].items():
        if importlib.metadata.version(package) != expected:
            raise ValueError('Scientific runtime version mismatch')


def load_backend(manifest):
    """Initialize from JSON config, then strictly load every safetensors tensor."""
    import torch
    from safetensors.torch import load_file
    from tokenizers import Tokenizer
    from transformers import T5Config, T5ForConditionalGeneration

    _verify(manifest)
    root = Path(manifest['model_dir'])
    torch.set_num_threads(manifest['num_threads'])
    config = T5Config.from_dict(json.loads((root / 'config.json').read_text()))

    class YieldNetwork(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.model = T5ForConditionalGeneration(config)
            # Published yield weights omit the unused text-generation projection.
            # Yield inference calls only encoder/decoder; all used tensors load strictly.
            self.model.lm_head = torch.nn.Identity()
            width = config.d_model
            self.fc1 = torch.nn.Linear(width,width//2)
            self.fc2 = torch.nn.Linear(width,width//2)
            self.fc3 = torch.nn.Linear(width,width)
            self.fc4 = torch.nn.Linear(width,width)
            self.fc5 = torch.nn.Linear(width,1)

        def forward(self, ids):
            encoder = self.model.encoder(input_ids=ids,attention_mask=torch.ones_like(ids))[0]
            start = torch.full((1,1),config.decoder_start_token_id,dtype=torch.long,device=ids.device)
            decoder = self.model.decoder(input_ids=start,encoder_hidden_states=encoder)[0]
            first = self.fc1(decoder.view(-1,config.d_model))
            second = self.fc2(encoder[:,0,:].view(-1,config.d_model))
            return self.fc5(self.fc4(self.fc3(torch.hstack((first,second)))))*100

    model = YieldNetwork()
    model.load_state_dict(load_file(str(root / 'model.safetensors')),strict=True)
    model.to(manifest['device']).eval()
    tokenizer = Tokenizer.from_file(str(root / 'tokenizer.json'))
    tokenizer.no_padding()
    tokenizer.no_truncation()
    if tokenizer.get_vocab_size() != config.vocab_size:
        raise ValueError('Tokenizer vocabulary differs from model embeddings')
    def encode(text):
        return tokenizer.encode(text).ids
    def infer(ids):
        with torch.inference_mode():
            values = torch.tensor([ids],dtype=torch.long,device=manifest['device'])
            return model(values).item()
    return encode, infer, tokenizer.token_to_id('<unk>')


def main():
    raw = sys.stdin.buffer.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Worker input exceeds bound')
    payload = json.loads(raw)
    manifest = payload['manifest']
    rows = payload['rows']
    if not isinstance(rows,list) or not 1 <= len(rows) <= 100:
        raise ValueError('Worker candidate bound exceeded')
    encode,infer,unknown_id = load_backend(manifest)
    predictions = run_predictions(rows,encode,infer,max_tokens=manifest['max_tokens'],unknown_id=unknown_id)
    sys.stdout.write(json.dumps({'predictions':predictions},allow_nan=False))


if __name__ == '__main__':
    main()
