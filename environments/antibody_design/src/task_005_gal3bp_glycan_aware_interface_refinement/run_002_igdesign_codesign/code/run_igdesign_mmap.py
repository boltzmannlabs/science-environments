#!/usr/bin/env python
"""
Wrapper to run IgDesign inference with GPU-direct, memory-safe model loading.

Two OOM hazards on this 24 GB-GPU / ~10 GB-free-RAM host:
  1. The Lightning LMDesign checkpoint (~11.5 GB) would be materialized on CPU
     by a plain torch.load. -> patch torch.load to map_location='cuda:0'.
  2. The 3B ESM language model is built by EsmForMaskedLM.from_pretrained in
     fp32 (~12 GB CPU). -> patch load_language_model to build it in fp16 with
     low_cpu_mem_usage; it is moved to GPU by model.cuda() and immediately
     overwritten by the checkpoint's trained ESM weights (load_state_dict).

Peak GPU during load: fp16 base ESM (6 GB) + fp32 checkpoint (11.5 GB) ~ 17.5 GB.

Usage: python run_igdesign_mmap.py <config.yaml>
"""
import sys
import os

# --- Patch 1: torch.load -> GPU-direct (before any model loading) ---
import torch
_orig_torch_load = torch.load

def _cuda_torch_load(*args, **kwargs):
    kwargs["map_location"] = "cuda:0"
    kwargs["weights_only"] = False  # Lightning ckpt contains omegaconf DictConfig globals (trusted local file)
    return _orig_torch_load(*args, **kwargs)

torch.load = _cuda_torch_load

# --- Add IgDesign to the path ---
IGDESIGN_ROOT = "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign"
sys.path.insert(0, os.path.join(IGDESIGN_ROOT, "src"))
sys.path.insert(0, IGDESIGN_ROOT)

# --- Patch 2: fp16, low-CPU-peak ESM base model ---
import igdesign.models.lmdesign_model as _lm_mod

def _fp16_load_language_model(cfg):
    from transformers import EsmForMaskedLM
    return EsmForMaskedLM.from_pretrained(
        cfg["pretrained_language_model_name_or_path"],
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

_lm_mod.load_language_model = _fp16_load_language_model

# --- Run ---
import yaml
import predict
from predict import run_inference

# --- Patch 3: cast the whole model to fp16 after loading (the ESM base is built
#     fp16 but the adapter/PMNN/to_logits stay fp32 -> cross-attention dtype
#     mismatch). fp16 inference is the memory-safe operating point here. ---
_orig_load_model = predict.load_model


def _half_load_model(cfg):
    model = _orig_load_model(cfg)
    model = model.half()
    return model


predict.load_model = _half_load_model

# --- Patch 4: cast the input batch's float tensors to fp16 to match the fp16
#     model (the PMNN embedding otherwise sees fp32 inputs -> dtype mismatch).
#     Integer tensors (chain_ids, tokenized_sequences) are left untouched. ---
_orig_load_single_example = predict.load_single_example


def _cast_fp16(obj):
    """Recursively cast float tensors (incl. nested dicts/lists and igdesign
    Feature objects) to fp16. Integer/long tensors (EMBED/ONEHOT indices,
    chain_ids, tokenized_sequences) are left untouched."""
    if torch.is_tensor(obj):
        return obj.half() if obj.is_floating_point() else obj
    if isinstance(obj, dict):
        return {k: _cast_fp16(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_cast_fp16(v) for v in obj)
    # igdesign Feature object: cast its float encoded_data / raw_data in place
    if hasattr(obj, "encoded_data"):
        ed = obj.encoded_data
        if torch.is_tensor(ed) and ed.is_floating_point():
            obj.encoded_data = ed.half()
        rd = obj.raw_data
        if torch.is_tensor(rd) and rd.is_floating_point():
            obj.raw_data = rd.half()
        return obj
    return obj


def _fp16_load_single_example(model, cfg):
    batch = _orig_load_single_example(model, cfg)
    for k in batch:
        batch[k] = _cast_fp16(batch[k])
    return batch


predict.load_single_example = _fp16_load_single_example

# --- Patch 5: run inference under torch.autocast(fp16). The PMNN body and
#     feature encoders contain fp32 constants/masks (e.g. embedding radii,
#     attention masks) that would otherwise promote fp16 activations to fp32
#     mid-forward. autocast handles every fp32/fp16 boundary automatically.
#     predict.py imports `sample` directly, so patch the predict namespace. ---
_orig_sample = predict.sample


@torch.no_grad()
def _autocast_sample(model=None, cfg=None, batch=None, save_root=None):
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        return _orig_sample(model=model, cfg=cfg, batch=batch, save_root=save_root)


predict.sample = _autocast_sample

# --- Patch 6: fp16-safe prevent_invalid_tokens. The original writes -1e10 into
#     the logits, which overflows fp16 (max ~65504). Use a dtype-aware large
#     negative instead (exp() still underflows to 0 for sampling). ---
import re as _re
import igdesign.inference_utils as _iu


def _fp16_prevent_invalid_tokens(logits):
    valid_idxs = [
        idx for token, idx in _iu.AA_TO_IDX.items() if _re.match("[A-Z]|<pad>", token)
    ]
    invalid_idxs = [
        idx for idx in range(logits.shape[-1]) if idx not in valid_idxs
    ]
    fill = torch.finfo(logits.dtype).min / 10 if logits.is_floating_point() else -1e10
    logits[:, :, invalid_idxs] = fill
    return logits


_iu.prevent_invalid_tokens = _fp16_prevent_invalid_tokens


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_igdesign_mmap.py <config.yaml>")
        sys.exit(1)
    config_path = sys.argv[1]
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    print(f"Running IgDesign with config: {config_path}")
    print(f"  region_order: {cfg['region_order']}")
    print(f"  samples: {cfg['lmdesign_num_decoding_orders']}x{cfg['lmdesign_num_pmpnn_seqs']}x{cfg['lmdesign_num_lm_seqs']}")
    run_inference(cfg=cfg)
    print("DONE")


if __name__ == "__main__":
    main()
