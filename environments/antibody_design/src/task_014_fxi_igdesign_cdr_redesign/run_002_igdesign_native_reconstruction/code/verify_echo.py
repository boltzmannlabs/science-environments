#!/usr/bin/env python3
"""S4 check: sequence-echo verification of all Boltz2 predictions.

For every downloaded prediction, re-extract per-chain sequences from the PDB
and assert they are byte-identical to the submitted payload sequences
(read back from inputs/submitted_requests/*.json). A mismatch invalidates the
run (payload fault, not model fault).
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "..")
RES = os.path.abspath(os.path.join(RUN, "..", "..", "..", "results",
                                   "task_014_fxi_igdesign_cdr_redesign",
                                   "run_002_igdesign_native_reconstruction"))
THREE = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q',
         'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
         'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
         'TYR': 'Y', 'VAL': 'V'}

LABELS = {"reference": "t014_reference_osocimab",
          "hcdr3_c012": "t014r002_hcdr3_best100_012",
          "hcdr3_c022": "t014r002_hcdr3_best100_022",
          "hcdr3_c027": "t014r002_hcdr3_best100_027",
          "hcdr3_c065": "t014r002_hcdr3_best100_065",
          "hcdr3_c082": "t014r002_hcdr3_best100_082",
          "hcdr123_c034": "t014r002_hcdr123_best100_034",
          "hcdr123_c035": "t014r002_hcdr123_best100_035",
          "hcdr123_c067": "t014r002_hcdr123_best100_067",
          "hcdr123_c070": "t014r002_hcdr123_best100_070",
          "hcdr123_c082": "t014r002_hcdr123_best100_082"}


def pdb_chains(pdb):
    chains = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[17:20].strip() in THREE:
            ch = line[21]
            chains.setdefault(ch, {})
            chains[ch][line[22:27]] = THREE[line[17:20].strip()]
    out = {}
    for ch, d in chains.items():
        keys = sorted(d, key=lambda k: int(k[:4]) if k[:4].strip().isdigit() else 0)
        out[ch] = "".join(d[k] for k in keys)
    return out


def main():
    pdir = os.path.join(RUN, "inputs", "submitted_requests")
    report = {}
    ok = 0
    for label, cid in LABELS.items():
        pdb = os.path.join(RES, "raw", "boltz2", label, "boltz_pdb", "1_model_0.pdb")
        payload = json.load(open(os.path.join(pdir, f"boltz2_{cid}.json")))
        want = payload["Protein_Sequences"]
        got = pdb_chains(pdb)
        got_list = [got[c] for c in sorted(got)]
        match = got_list == want
        report[label] = {"candidate_id": cid,
                         "chains": {c: len(s) for c, s in got.items()},
                         "echo_match": match}
        print(f"{label:14s} chains={sorted((c, len(s)) for c, s in got.items())} "
              f"echo_match={match}")
        if not match:
            for i, (g, w) in enumerate(zip(got_list, want)):
                if g != w:
                    bad = [j for j, (a, b) in enumerate(zip(g, w)) if a != b]
                    print(f"  !! chain {i} mismatch at {bad[:5]}")
        ok += int(match)
    assert ok == len(LABELS), f"{len(LABELS) - ok} echo mismatches — invalid runs"
    out = os.path.join(RES, "raw", "boltz2", "sequence_echo_report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=1)
    print(f"ALL {ok}/{len(LABELS)} sequence echoes verified — wrote {out}")


if __name__ == "__main__":
    main()
