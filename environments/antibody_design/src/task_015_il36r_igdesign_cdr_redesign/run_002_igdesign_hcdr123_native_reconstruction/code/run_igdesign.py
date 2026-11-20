#!/usr/bin/env python
"""
Run genuine IgDesign inference from an arbitrary YAML config (task_015).

Wraps the genuine AbSciBio/igdesign modules (pinned revision 70431eef) so
configs can live outside the repo's configs/ directory. Hardware adaptation
(24 GB GPU / tight RAM): ESM2 loads fp16 straight to GPU; checkpoint streams
to GPU; PMpNN stays fp32; language path fp16 with casts at the refine_step
boundary. Same architecture, weights, masks and sampling as upstream.
"""
import os
import sys
import yaml
import pickle
import argparse
from datetime import datetime

import torch

# torch >= 2.6 defaults torch.load(weights_only=True), which breaks Lightning's
# checkpoint load (the PMpNN ckpt contains omegaconf.DictConfig). Default
# weights_only back to False when the caller does not specify it.
_orig_torch_load = torch.load


def _torch_load_compat(f, *a, **k):
    k.setdefault("weights_only", False)
    return _orig_torch_load(f, *a, **k)


torch.load = _torch_load_compat

from pytorch_lightning import seed_everything
import pandas as pd

REPO = "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign"
sys.path.insert(0, os.path.join(REPO, "src"))

from igdesign.model_wrapper import LMDesignIFWrapper
from igdesign.inference_utils import sample
from igdesign.utils import safe_to_device
from igdesign.data.datasets.pdb_antibody import PdbAntibodyDataset

# The language path runs in fp16 on this hardware; the genuine
# prevent_invalid_tokens writes -1e10 (overflows fp16). Apply the identical
# logic in fp32 and cast back.
import igdesign.inference_utils as _iu

_orig_prevent_invalid_tokens = _iu.prevent_invalid_tokens


def _prevent_invalid_tokens_dtype_aware(logits):
    return _orig_prevent_invalid_tokens(logits.float()).to(logits.dtype)


_iu.prevent_invalid_tokens = _prevent_invalid_tokens_dtype_aware


def setup_cfg(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    if any(r in cfg["region_order"] for r in ["lcdr1", "lcdr2", "lcdr3"]):
        cfg["condition_on_light_chain"] = False
        cfg["predict_light_chain"] = True
    cfg["batch_size"] = 1
    return cfg


def check(cfg):
    for field in cfg["region_order"]:
        assert field in cfg["regions"], f"{field} missing in regions"
    assert not (cfg["condition_on_light_chain"] and cfg["predict_light_chain"])
    assert os.path.exists(cfg["structure_path"]), "structure_path missing"
    assert os.path.exists(cfg["lmdesign_checkpoint"]), "lmdesign ckpt missing"
    assert os.path.exists(cfg["pmpnn_checkpoint"]), "pmpnn ckpt missing"


def load_model(cfg):
    # Hardware adaptation (recorded, not a method change): 24 GB GPU.
    # (a) ESM2 loads fp16 directly to GPU (~5.5 GB) via device_map;
    # (b) the IgDesign checkpoint streams to GPU (11.5 GB);
    # (c) GPU->GPU weight copy; ESM2 stays fp16, IgDesign/PMpNN stay fp32.
    import torch as _torch
    import igdesign.models.lmdesign_model as lmd

    real_ecls = lmd.EsmForMaskedLM

    class _GpuFp16Esm(real_ecls):
        @classmethod
        def from_pretrained(cls, *a, **k):
            k["torch_dtype"] = _torch.float16
            k["device_map"] = "cuda:0"
            return super().from_pretrained(*a, **k)

    lmd.EsmForMaskedLM = _GpuFp16Esm
    try:
        ckpt = _torch.load(cfg["lmdesign_checkpoint"], map_location="cuda",
                           weights_only=False)
        hp = ckpt["hyper_parameters"]
        model = LMDesignIFWrapper(
            hp["cfg"],
            res_dim_hidden=hp["res_dim_hidden"],
            pair_dim_hidden=hp["pair_dim_hidden"],
            pmpnn_path=cfg["pmpnn_checkpoint"],
        )
        model = model.cuda()
        model.load_state_dict(ckpt["state_dict"], strict=False)
        del ckpt
        _torch.cuda.empty_cache()
    finally:
        lmd.EsmForMaskedLM = real_ecls

    model = model.eval()
    # PMpNN (structure_model) stays fp32. Everything else runs fp16.
    model.model.structure_model.float().cuda()
    model.model.language_model.half().cuda()
    for mname, mod in model.model.named_children():
        if mname not in ("language_model", "structure_model"):
            mod.half().cuda()
    for mname, mod in model.named_children():
        if mname != "model":
            mod.half().cuda()

    _orig_refine = model.model.refine_step

    def _refine_fp16(sequence, structure_node_feats, structure_logits, **kw):
        return _orig_refine(
            sequence,
            structure_node_feats.half(),
            structure_logits.half(),
            **kw,
        )

    model.model.refine_step = _refine_fp16
    return model


def load_batch(model, cfg):
    pdb_path = cfg["structure_path"]
    pdb_name = pdb_path.split("/")[-1].split(".")[0]
    epitope = {} if cfg["epitope_idxs_or_all"] == "all" else {
        cfg["antigen_chain_id"]: {"indices": cfg["epitope_idxs_or_all"]}}
    dataset_cfg = {
        "pdb": pdb_name, "pdb_path": pdb_path,
        "heavy": {"chain": cfg["heavy_chain_id"], "has_sequence": True,
                  "has_coords": True, "sequence": None},
        "light": {"chain": cfg["light_chain_id"], "has_sequence": True,
                  "has_coords": True, "coords": None},
        "antigens": [{"chain": cfg["antigen_chain_id"], "has_sequence": True,
                      "has_coords": True, "sequence": None}],
        "epitopes": epitope, "num_samples": 1, "name": pdb_name,
    }
    if cfg["epitope_idxs_or_all"] == "all":
        dataset = PdbAntibodyDataset([dataset_cfg], include_light_chains=True,
                                     ag_crop_method="none")
    else:
        dataset = PdbAntibodyDataset([dataset_cfg], include_light_chains=True)
    batch = [dataset[idx] for idx in range(1)]
    batch = safe_to_device(batch, model.device)
    collated = model.collate(batch, precollate=dataset.collate)
    collated["tokenized_sequences"] = collated["tokenized_sequences"].long()
    return collated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cfg = setup_cfg(args.config)
    check(cfg)
    t0 = datetime.now()
    model = load_model(cfg)
    print(f"Model loaded {datetime.now()-t0}")
    seed_everything(cfg["random_seed"])
    batch = load_batch(model, cfg)
    light_offset = (batch["chain_ids"][0] == 0).sum().item()
    for region in cfg["regions"]:
        pos = cfg["regions"][region]["positions"]
        cfg["regions"][region]["positions"] = torch.LongTensor(pos)
        if cfg["regions"][region]["chain"] == "heavy":
            cfg["regions"][region]["offset_positions"] = cfg["regions"][region]["positions"]
        else:
            cfg["regions"][region]["offset_positions"] = cfg["regions"][region]["positions"] + light_offset
    save_path = cfg["save_path"]
    df = sample(model=model, batch=batch, cfg=cfg, save_root=None)
    df[cfg["region_order"]] = df.sampled_seq.apply(lambda x: pd.Series(x.split("|")))
    df = df.drop(columns=["sampled_seq"])
    df = df[cfg["region_order"] + [c for c in df.columns if c not in cfg["region_order"]]]
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    with open(save_path.replace(".csv", "_config.pkl"), "wb") as f:
        pickle.dump(cfg, f)
    print(f"Saved {len(df)} samples to {save_path}")


if __name__ == "__main__":
    main()
