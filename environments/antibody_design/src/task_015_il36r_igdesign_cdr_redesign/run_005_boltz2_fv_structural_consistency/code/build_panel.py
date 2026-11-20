#!/usr/bin/env python3
"""Build the Boltz-2 Fv evaluation panel for task_015 run_005.

Panel: unmodified reference Fv (Spesolimab VH/VL, PDB 6u6u variable domains)
+ top-3 candidates from each generation run:
  - run_001 IgDesign HCDR3 (rank by ce_loss_independent_hcdr3, lower better)
  - run_002 IgDesign HCDR123 (rank by sum of per-CDR ce losses, lower better)
  - run_003 AntiBMPNN HCDR3 (rank by generation-metrics score, higher better)
  - run_004 AntiBMPNN HCDR123 (rank by generation-metrics score, higher better)
Candidates are embedded into the native VH context (framework identical by
construction/mask). All members pair with the native VL. Writes
inputs/boltz2_panel.json with full sequences, sources and selection records.
"""
import json
import os

ENV = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
T = "task_015_il36r_igdesign_cdr_redesign"
HERE = os.path.dirname(os.path.abspath(__file__))

import pandas as pd

NAT_VH = ("QVQLVQSGAEVKKPGASVKVSCKASGYSFTSSWIHWVKQAPGQGLEWMGEINPGNVRTNYNENFRN"
          "KVTMTVDTSISTAYMELSRLRSDDTAVYYCTVVFYGEPYFPYWGQGTLVTVSS")
NAT_VL = ("QIVLTQSPGTLSLSPGERATMTCTASSSVSSSYFHWYQQKPGQAPRLWIYRTSRLASGVPDRFSG"
          "SGSGTDFTLTISRLEPEDAATYYCHQFHRSPLTFGAGTKLEIK")
CDR_SLICES = {"hcdr1": (25, 33), "hcdr2": (50, 58), "hcdr3": (96, 108)}


def embed(cdrs):
    vh = NAT_VH
    for name, (a, b) in CDR_SLICES.items():
        if name in cdrs and cdrs[name]:
            assert len(cdrs[name]) == b - a, (name, cdrs[name])
            vh = vh[:a] + cdrs[name] + vh[b:]
    return vh


def main():
    panel = [{
        "member_id": "reference",
        "source_run": None,
        "vh": NAT_VH, "vl": NAT_VL,
        "selection": "unmodified Spesolimab reference (rank-0 control)",
    }]

    # IgDesign runs: lowest independent CE loss
    for run, rid, col in [
            ("run_001_igdesign_hcdr3_native_reconstruction", "igdesign_hcdr3",
             "ce_loss_independent_hcdr3"),
            ("run_002_igdesign_hcdr123_native_reconstruction", "igdesign_hcdr123",
             None)]:
        df = pd.read_csv(f"{ENV}/results/{T}/{run}/raw/{'hcdr3' if 'hcdr3' in rid else 'hcdr123'}_100.csv")
        if col is None:
            df["ce_sum"] = sum(df[f"ce_loss_independent_{c}"] for c in ["hcdr1", "hcdr2", "hcdr3"])
            col = "ce_sum"
        df = df.drop_duplicates(subset=[c for c in ["hcdr1", "hcdr2", "hcdr3"] if c in df.columns])
        df = df.sort_values(col).head(3).reset_index(drop=True)
        for i, row in df.iterrows():
            cdrtxt = {c: row[c] for c in ["hcdr1", "hcdr2", "hcdr3"] if c in row.index}
            panel.append({
                "member_id": f"{rid}_top{i+1}",
                "source_run": run,
                "vh": embed(cdrtxt), "vl": NAT_VL,
                "selection": f"rank {i+1} by {col}={row[col]:.4f} (lower better)",
                "cdrs": cdrtxt,
            })

    # AntiBMPNN runs: highest generation score
    for run, rid, rawcsv in [
            ("run_003_antibmpnn_hcdr3_redesign", "antibmpnn_hcdr3", "hcdr3_scope"),
            ("run_004_antibmpnn_hcdr123_redesign", "antibmpnn_hcdr123", "hcdr123_scope")]:
        res = pd.read_csv(f"{ENV}/results/{T}/{run}/raw/antibmpnn_results.csv")
        met = pd.read_csv(f"{ENV}/results/{T}/{run}/raw/antibmpnn_generation_metrics.csv")
        res["sample"] = res.index + 1
        m = res.merge(met[["sample", "score"]], on="sample").sort_values("score", ascending=False).head(3).reset_index(drop=True)
        for i, row in m.iterrows():
            vh = row.heavy_chain
            assert len(vh) == 119 and vh != NAT_VH
            panel.append({
                "member_id": f"{rid}_top{i+1}",
                "source_run": run,
                "vh": vh, "vl": row.light_chain,
                "selection": f"rank {i+1} by antibmpnn score={row.score:.4f} (higher better)",
                "native_sample_index": int(row["sample"]),
            })

    # sanity: every VH 119aa, VL native, framework preserved, unique
    seen = set()
    for p in panel:
        assert len(p["vh"]) == 119 and p["vl"] == NAT_VL
        fw = p["vh"][:25] + p["vh"][33:50] + p["vh"][58:96] + p["vh"][108:]
        nat_fw = NAT_VH[:25] + NAT_VH[33:50] + NAT_VH[58:96] + NAT_VH[108:]
        assert fw == nat_fw, p["member_id"]
        assert p["vh"] not in seen or p["member_id"] == "reference", p["member_id"]
        seen.add(p["vh"])
    out = os.path.join(HERE, "..", "inputs", "boltz2_panel.json")
    with open(out, "w") as f:
        json.dump(panel, f, indent=1)
    print(f"panel size: {len(panel)} (1 reference + {len(panel)-1} candidates)")
    for p in panel:
        d = sum(a != b for a, b in zip(p["vh"], NAT_VH))
        print(f"  {p['member_id']:24s} VH mutations vs reference: {d:2d}  [{p['selection'][:60]}]")


if __name__ == "__main__":
    main()
