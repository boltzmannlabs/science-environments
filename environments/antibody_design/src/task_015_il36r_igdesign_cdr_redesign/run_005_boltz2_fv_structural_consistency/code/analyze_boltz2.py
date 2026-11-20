#!/usr/bin/env python3
"""Analyze Boltz2 Fv predictions for task_015 run_005.

For each of the 13 panel members:
  1. Verify the modelled sequences equal the submitted VH/VL (exact, both chains).
  2. Per-residue confidence = PDB B-factor (Boltz2 writes pLDDT*100 there).
  3. scRMSD vs the 6u6u crystal reference Fv:
       - superpose on Fv framework backbone (N, CA, C, O) excluding all CDRs
         (VH HCDR1/2/3 masks 26-33, 51-58, 97-108; VL CDR masks 24-34, 50-56,
         89-97 in VL numbering per Chothia-lite used for embedding),
       - report RMSD over HCDR1, HCDR2, HCDR3, HCDR123 and whole-Fv backbone
         in the reference (superposed) frame.
Outputs results JSON to the run results dir.
"""
import json
import os
import numpy as np

SRC = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
RUN = f"{SRC}/src/task_015_il36r_igdesign_cdr_redesign/run_005_boltz2_fv_structural_consistency"
OUT = f"{SRC}/results/task_015_il36r_igdesign_cdr_redesign/run_005_boltz2_fv_structural_consistency"
WORK = "/home/boltzmann10/.sci/workspace/outputs/task015_boltz2"
REF_PDB = f"{RUN}/inputs/6u6u.pdb"

T2O = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 'GLU': 'E',
       'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F',
       'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}
BB = ["N", "CA", "C", "O"]

# 1-based inclusive masks on the 119-aa VH / 108-aa VL used across task_015
VH_CDR = {"hcdr1": (26, 33), "hcdr2": (51, 58), "hcdr3": (97, 108)}
VL_CDR = {"lcdr1": (24, 34), "lcdr2": (50, 56), "lcdr3": (89, 97)}


def parse(path):
    """Return {chain: {resnum: {'aa': str, 'atoms': {name: (x,y,z)}, 'b": float})}}."""
    chains = {}
    for line in open(path):
        if line.startswith("ATOM"):
            rn = line[22:27]                      # keeps icode
            key = int(line[22:26]) * 100 + (ord(line[26].strip() or " ") )
            name = line[12:16].strip()
            resn = line[17:20].strip()
            if resn not in T2O:
                continue
            c = chains.setdefault(line[21], {})
            r = c.setdefault(key, {"aa": T2O[resn], "atoms": {}, "b": []})
            r["atoms"].setdefault(name, (float(line[30:38]), float(line[38:46]), float(line[46:54])))
            if name == "CA":
                r["b"] = float(line[60:66])
    return chains


def seq_of(chain):
    return "".join(chain[k]["aa"] for k in sorted(chain))


def coords(chain, keys, atoms=BB):
    """Stacked backbone coords for residues keys (in key order)."""
    out = []
    for k in keys:
        for a in atoms:
            out.append(chain[k]["atoms"][a])
    return np.asarray(out, dtype=float)


def kabsch_rmsd(P, Q):
    """RMSD of P onto Q after optimal superposition; returns rmsd, P_superposed."""
    PC, QC = P.mean(0), Q.mean(0)
    P0, Q0 = P - PC, Q - QC
    V, S, Wt = np.linalg.svd(P0.T @ Q0)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1, 1, d])
    R = V @ D @ Wt
    Ps = P0 @ R + QC
    return float(np.sqrt(((Ps - Q) ** 2).sum(1).mean())), Ps


def main():
    os.makedirs(OUT, exist_ok=True)
    panel = {p["member_id"]: p for p in json.load(open(f"{RUN}/inputs/boltz2_panel.json"))}
    jobs = json.load(open(f"{RUN}/inputs/job_map.json"))["jobs"]

    # ---- reference Fv from 6u6u: map crystal H/L prefixes onto VH/VL numbering
    ref = parse(REF_PDB)
    vh, vl = panel["reference"]["vh"], panel["reference"]["vl"]
    hseq, lseq = seq_of(ref["H"]), seq_of(ref["L"])
    hcut = next((i for i in range(min(len(hseq), len(vh))) if hseq[i] != vh[i]), None)
    lcut = next((i for i in range(min(len(lseq), len(vl))) if lseq[i] != vl[i]), None)
    diag = {"6u6u_H_len": len(hseq), "6u6u_L_len": len(lseq),
            "H_prefix_match_len": hcut, "L_prefix_match_len": lcut,
            "hseq_first60": hseq[:60], "lseq_first60": lseq[:60]}
    print(json.dumps(diag, indent=1))

    hkeys = sorted(ref["H"]); lkeys = sorted(ref["L"])
    # crystal residue i (1-based order index) -> model numbering i (VH 1..119)
    hmap = {i + 1: hkeys[i] for i in range(119)}
    lmap = {i + 1: lkeys[i] for i in range(108)}
    assert "".join(ref["H"][hmap[i]]["aa"] for i in range(1, 120)) == vh, "H mapping mismatch"
    assert "".join(ref["L"][lmap[i]]["aa"] for i in range(1, 109)) == vl, "L mapping mismatch"

    def region_keys(mapping, maskdict):
        fw, cdrs = [], {n: [] for n in maskdict}
        for i in sorted(mapping):
            tag = next((n for n, (a, b) in maskdict.items() if a <= i <= b), None)
            (cdrs[tag] if tag else fw).append(i)
        return fw, cdrs

    vh_fw, vh_cdrs = region_keys(hmap, VH_CDR)
    vl_fw, vl_cdrs = region_keys(lmap, VL_CDR)
    # reference framework coordinate set (VH+VL framework backbone)
    ref_fw = np.vstack([coords(ref["H"], [hmap[i] for i in vh_fw]),
                        coords(ref["L"], [lmap[i] for i in vl_fw])])
    ref_regions = {f"vh_{n}": coords(ref["H"], [hmap[i] for i in ks]) for n, ks in vh_cdrs.items()}
    ref_regions["vh_hcdr123"] = np.vstack([ref_regions[f"vh_{n}"] for n in ("hcdr1", "hcdr2", "hcdr3")])
    ref_regions["fv_all"] = np.vstack([coords(ref["H"], list(hmap.values())),
                                       coords(ref["L"], list(lmap.values()))])

    results = {}
    for mid, meta in jobs.items():
        pdb = f"{WORK}/{mid}/boltz_pdb/1_model_0.pdb"
        m = parse(pdb)
        exp_vh, exp_vl = panel[mid]["vh"], panel[mid]["vl"]
        got_vh = seq_of(m["A"]); got_vl = seq_of(m["B"]) if "B" in m else seq_of(m[list(m)[1]])
        assert got_vh == exp_vh, f"{mid}: VH model mismatch"
        assert got_vl == exp_vl, f"{mid}: VL model mismatch"
        # model chains are numbered 1..119 / 1..108 directly
        mh = {i + 1: k for i, k in enumerate(sorted(m["A"]))}
        ml = {i + 1: k for i, k in enumerate(sorted(m["B"]))}
        plddt_vh = float(np.mean([m["A"][mh[i]]["b"] for i in range(1, 120)]))
        plddt_vl = float(np.mean([m["B"][ml[i]]["b"] for i in range(1, 109)]))
        plddt_cdr = float(np.mean([m["A"][mh[i]]["b"] for n, (a, b) in VH_CDR.items() for i in range(a, b + 1)]))
        mod_fw = np.vstack([coords(m["A"], [mh[i] for i in vh_fw]),
                            coords(m["B"], [ml[i] for i in vl_fw])])
        _, R, t = None, None, None
        # superposition transform from framework fit
        MC, RC = mod_fw.mean(0), ref_fw.mean(0)
        V, S, Wt = np.linalg.svd((mod_fw - MC).T @ (ref_fw - RC))
        d = np.sign(np.linalg.det(V @ Wt))
        R = V @ np.diag([1, 1, d]) @ Wt
        def xform(P):
            return (P - MC) @ R + RC
        scrmsd = {}
        for name, refc in ref_regions.items():
            mapping = mh if name.startswith("vh_") else None
            if name == "fv_all":
                modc = np.vstack([coords(m["A"], list(mh.values())), coords(m["B"], list(ml.values()))])
            else:
                ks = {"vh_hcdr1": vh_cdrs["hcdr1"], "vh_hcdr2": vh_cdrs["hcdr2"],
                      "vh_hcdr3": vh_cdrs["hcdr3"],
                      "vh_hcdr123": vh_cdrs["hcdr1"] + vh_cdrs["hcdr2"] + vh_cdrs["hcdr3"]}[name]
                modc = coords(m["A"], [mh[i] for i in ks])
            P = xform(modc)
            scrmsd[name] = round(float(np.sqrt(((P - refc) ** 2).sum(1).mean())), 4)
        # framework-aligned framework RMSD (fit quality)
        P = xform(mod_fw)
        scrmsd["fv_framework_fit"] = round(float(np.sqrt(((P - ref_fw) ** 2).sum(1).mean())), 4)
        results[mid] = {
            "doc_id": meta["doc_id"], "experiment_name": meta["experiment_name"],
            "sequence_check": {"vh_exact": True, "vl_exact": True,
                               "vh_len": len(got_vh), "vl_len": len(got_vl)},
            "mean_plddt": {"vh": round(plddt_vh, 2), "vl": round(plddt_vl, 2),
                           "vh_cdrs": round(plddt_cdr, 2)},
            "scrmsd_A_frame_aligned_vs_6u6u": scrmsd,
            "vh_mutations_vs_reference": sum(a != b for a, b in zip(exp_vh, vh)),
        }
        print(f"{mid:24s} pLDDT vh={plddt_vh:5.1f} cdr={plddt_cdr:5.1f} | "
              f"H1={scrmsd['vh_hcdr1']:.3f} H2={scrmsd['vh_hcdr2']:.3f} "
              f"H3={scrmsd['vh_hcdr3']:.3f} H123={scrmsd['vh_hcdr123']:.3f} "
              f"Fv={scrmsd['fv_all']:.3f} fwfit={scrmsd['fv_framework_fit']:.3f}")

    payload = {
        "definition": {
            "predictor": "Boltz-2 (boltz-structure-prediction, platform job Boltz2)",
            "reference_structure": "6u6u crystal Fv (chains H/L variable domains), Spesolimab Fab in complex with IL-36R (chain R)",
            "atom_selection": "backbone N, CA, C, O",
            "alignment": "global Fv framework (all non-CDR VH+VL residues), Kabsch superposition",
            "regions_1_based": {"VH": VH_CDR, "VL_masks_for_alignment_exclusion": VL_CDR},
            "scRMSd_units": "angstrom",
            "plddt_source": "PDB B-factor column of Boltz2 output (0-100)"
        },
        "members": results,
    }
    with open(f"{OUT}/boltz2_metrics.json", "w") as f:
        json.dump(payload, f, indent=1)
    print(f"\nwrote {OUT}/boltz2_metrics.json")


if __name__ == "__main__":
    main()
