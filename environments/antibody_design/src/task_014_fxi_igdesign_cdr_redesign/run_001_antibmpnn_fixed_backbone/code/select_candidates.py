#!/usr/bin/env python3
"""S4a: select candidates for structural evaluation (run_001 AntiBMPNN).

Predeclared rule (workflow.md): dedupe by full VH identity; rank by scope,
then number of CDR substitutions (asc), then AntiBMPNN score (asc, lower =
higher model probability); structural evaluation budget = up to 5 distinct
candidates per scope. Shared native reference job reused from run_002
(identical VH/VL sequences).
"""
import hashlib
import json
import os

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
RES = os.path.join(A, "results/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone")
R2 = os.path.join(A, "results/task_014_fxi_igdesign_cdr_redesign/run_002_igdesign_native_reconstruction")
SUB = os.path.join(A, "src/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone/inputs/submitted_requests")

REF_VH = ("EVQLLESGGGLVQPGGSLRLSCAASGFTFSQYGMDWVRQAPGKGLEWVSGIGPSGGSTVYADSVK"
          "GRFTISRDNSKNTLYLQMNSLRAEDTAVYYCTRGGPYYYYGMDVWGQGTTVTVSS")
REF_VL = ("DIQMTQSPSSLSASVGDRVTITCQASQDISNYLNWYQQKPGKAPKLLIYDASNLETGVPSRFSG"
          "SGSGTDFTFTISSLQPEDIATYYCQQANSFPVTFGGGTKVEIK")
NATIVE = {"hcdr1": REF_VH[25:33], "hcdr2": REF_VH[50:58], "hcdr3": REF_VH[96:109]}
POS = {"hcdr1": list(range(25, 33)), "hcdr2": list(range(50, 58)),
       "hcdr3": list(range(96, 109))}


def main():
    data = json.load(open(os.path.join(RES, "mask_gate_results.json")))
    selected = {}
    for scope in ("hcdr3_scope", "hcdr123_scope"):
        rows = data["rows"][scope]
        # dedupe by VH, keep best-score representative per unique sequence
        best = {}
        for r in rows:
            k = r["vh"]
            if k not in best or r["scrmpnn_score"] < best[k]["scrmpnn_score"]:
                best[k] = r
        uniq = sorted(best.values(), key=lambda r: (r["n_substitutions"], r["scrmpnn_score"]))
        top = uniq[:5]
        for rank, r in enumerate(top, 1):
            cid = r["candidate_id"]
            cdrs = r["cdrs"]
            per_cdr_aar = {c: round(sum(a == b for a, b in zip(cdrs[c], NATIVE[c])) / len(NATIVE[c]), 4)
                           for c in ("hcdr1", "hcdr2", "hcdr3")}
            selected.setdefault(scope, []).append({
                "candidate_id": cid, "rank": rank, "sample": r["sample"],
                "vh": r["vh"], "vl": REF_VL, "cdrs": cdrs,
                "n_substitutions": r["n_substitutions"],
                "per_cdr_aar": per_cdr_aar,
                "designed_scope_aar": r["designed_scope_aar"],
                "scrmpnn_score": r["scrmpnn_score"],
                "global_score": r["global_score"],
                "sequence_hash": hashlib.sha256((r["vh"] + "|" + REF_VL).encode()).hexdigest()[:16]})
    json.dump(selected, open(os.path.join(RES, "selected_candidates.json"), "w"), indent=1)

    # Boltz2 payloads ( Protein_Sequences [VH, VL] ), one file per candidate
    os.makedirs(os.path.join(SUB, "boltz2"), exist_ok=True)
    for scope, cands in selected.items():
        for c in cands:
            fn = os.path.join(SUB, "boltz2", f"boltz2_{c['candidate_id']}.json")
            json.dump({"Protein_Sequences": [c["vh"], c["vl"]]}, open(fn, "w"), indent=1)
    # reference job reused from run_002 doc ids
    ref = json.load(open(os.path.join(R2, "raw", "boltz2_reference_doc.json")))
    print("selected:", {k: [c["candidate_id"] for c in v] for k, v in selected.items()})
    print("reference doc:", ref)
    n = sum(len(v) for v in selected.values())
    print(f"payloads written: {n}; reference reused from run_002")


if __name__ == "__main__":
    main()
