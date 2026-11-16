#!/usr/bin/env python
"""Preflight: verify IgDesign dataset truncation + CDR position mapping on the
task_005 reference complex (A=VH 122, B=VL 106, C=Gal-3BP 567)."""
import sys, os, json
sys.path.insert(0, "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign/src")
sys.path.insert(0, "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign")
from igdesign.data.datasets.pdb_antibody import PdbAntibodyDataset

PDB = "/home/boltzmann10/.sci/cache/scratch/gal3bp_run/igdesign_input_complex.pdb"
cfg = {
    "pdb": "ref_rank1_clean", "pdb_path": PDB,
    "heavy": {"chain": "A", "has_sequence": True, "has_coords": True, "sequence": None},
    "light": {"chain": "B", "has_sequence": True, "has_coords": True, "coords": None},
    "antigens": [{"chain": "C", "has_sequence": True, "has_coords": True, "sequence": None}],
    "epitopes": {}, "num_samples": 1, "name": "ref_rank1_clean",
}
ds = PdbAntibodyDataset([cfg], include_light_chains=True, ag_crop_method="none")
item = ds[0]
tok = item.tokenized_sequences if hasattr(item, "tokenized_sequences") else None
# introspect
from igdesign.features.feature import Feature
def show(obj, prefix="", depth=0):
    if depth > 2: return
    if isinstance(obj, dict):
        for k, v in obj.items(): show(v, f"{prefix}.{k}", depth+1)
    elif hasattr(obj, "encoded_data"):
        t = obj.encoded_data
        print(f"{prefix}: type={type(t).__name__}", getattr(t, "shape", ""))
toks = None
for attr in ("tokenized_sequences",):
    if hasattr(item, attr):
        t = getattr(item, attr)
        print(attr, type(t))
if isinstance(item, dict):
    print("item keys:", list(item.keys()))
    for k in item:
        v = item[k]
        desc = getattr(v, "shape", type(v).__name__)
        print(" ", k, desc)
