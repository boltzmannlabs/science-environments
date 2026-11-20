#!/usr/bin/env python
"""Preflight for task_009 run_002_igdesign_local: load the combined complex
(A=VH 123, B=VL 107, C=TREM2 126) through the IgDesign dataset, dump the
region layout IgDesign derives (to convert our 1-based chain positions into
the 0-based variable-domain indices the config needs), and verify no OOM."""
import sys, os, json
sys.path.insert(0, "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign/src")
sys.path.insert(0, "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign")
from igdesign.data.datasets.pdb_antibody import PdbAntibodyDataset

PDB = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_009_trem2_scfv_design/run_002_igdesign_local/inputs/igdesign_input_complex.pdb"
cfg = {
    "pdb": "trem2_hl_ag", "pdb_path": PDB,
    "heavy": {"chain": "A", "has_sequence": True, "has_coords": True, "sequence": None},
    "light": {"chain": "B", "has_sequence": True, "has_coords": True, "coords": None},
    "antigens": [{"chain": "C", "has_sequence": True, "has_coords": True, "sequence": None}],
    "epitopes": {}, "num_samples": 1, "name": "trem2_hl_ag",
}
ds = PdbAntibodyDataset([cfg], include_light_chains=True, ag_crop_method="none")
item = ds[0]
info = {}
for attr in dir(item):
    if attr.startswith("_"):
        continue
    v = getattr(item, attr)
    if callable(v):
        continue
    t = type(v).__name__
    if hasattr(v, "shape"):
        info[attr] = f"{t} shape={tuple(v.shape)}"
    elif isinstance(v, (str, int, float, bool, list)) and len(str(v)) < 300:
        info[attr] = str(v)[:200]
print(json.dumps(info, indent=1))

# raw_data region info from features
def walk(obj, prefix="", depth=0):
    out = []
    if depth > 3:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += walk(v, f"{prefix}.{k}", depth + 1)
    elif hasattr(obj, "raw_data"):
        rd = obj.raw_data
        if hasattr(rd, "shape"):
            out.append((prefix, tuple(rd.shape)))
        elif isinstance(rd, (list, tuple)):
            out.append((prefix, f"len={len(rd)}"))
    return out

if isinstance(item, dict):
    print("item keys:", list(item.keys()))
elif hasattr(item, "features"):
    try:
        feats = item.features
        if isinstance(feats, dict):
            for k, v in feats.items():
                for p, s in walk(v, k):
                    print("feature", p, s)
        else:
            for p, s in walk(feats, "features"):
                print("feature", p, s)
    except Exception as e:
        print("features walk failed:", e)

# find the annotation that defines CDR regions (aa_regions)
try:
    from igdesign.data.utils.annotation import annotate_chain
    print("annotate_chain available")
except Exception as e:
    print("annotate_chain import:", e)
