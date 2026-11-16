#!/usr/bin/env python3
"""W3: build and verify candidate Multimer payloads from candidate_designs.json (source of truth).

Writes payload_<CAND>.txt files; asserts [122,106,567] segment lengths and
existence in the design set; prints sha256 per segment for submit-time check.
"""
import json, hashlib, sys

ag = [s["proteinChain"]["sequence"] for s in json.load(open("ref.json"))[0]["sequences"]][2]
cand = {c["candidate"]: c for c in json.load(open(
    "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/"
    "task_005_gal3bp_glycan_aware_interface_refinement/gal3bp_w2_cdr_design/outputs/extracted/candidate_designs.json"))}

for name in sys.argv[1:]:
    x = cand[name]
    p = f"{x['vh']}:{x['vl']}:{ag}"
    segs = p.split(":")
    assert [len(s) for s in segs] == [122, 106, 567], f"{name}: bad lengths {[len(s) for s in segs]}"
    # self-check: re-split and confirm membership in design set
    assert any(c["vh"] == segs[0] and c["vl"] == segs[1] for c in cand.values()), f"{name}: VH/VL pair not found in design set"
    open(f"payload_{name}.txt", "w").write(p)
    h = [hashlib.sha256(s.encode()).hexdigest()[:12] for s in segs]
    print(f"{name}: segments 122/106/567 OK; sha256[:12] VH={h[0]} VL={h[1]} AG={h[2]}")
print("payload files ready")
