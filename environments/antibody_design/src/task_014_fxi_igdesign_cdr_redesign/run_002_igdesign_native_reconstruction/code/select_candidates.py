#!/usr/bin/env python3
"""S4 preparation: select distinct IgDesign candidates and build Boltz2 payloads.

Selection (predeclared in workflow.md): from each best-of-100 execution, drop
duplicate CDR tuples and exact native reconstructions, rank by summed
independent cross-entropy over designed regions (lower = better), keep top 5
per scope. The unmodified reference is a separate labelled control job.

For every selected candidate the full VH is rebuilt from the native 120-aa
variable domain by substituting only the masked CDR positions, then asserted:
length unchanged, every substitution inside the declared mask, VL identical to
native. Payloads are written to files (built from the data, never retyped).
"""
import csv
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "..")
RES = os.path.abspath(os.path.join(RUN, "..", "..", "..", "results",
                                   "task_014_fxi_igdesign_cdr_redesign",
                                   "run_002_igdesign_native_reconstruction"))

NATIVE_VH = ("EVQLLESGGGLVQPGGSLRLSCAASGFTFSQYGMDWVRQAPGKGLEWVSGIGPSGGSTVYADSVK"
             "GRFTISRDNSKNTLYLQMNSLRAEDTAVYYCTRGGPYYYYGMDVWGQGTTVTVSS")
NATIVE_VL = ("DIQMTQSPSSLSASVGDRVTITCQASQDISNYLNWYQQKPGKAPKLLIYDASNLETGVPSRFSG"
             "SGSGTDFTFTISSLQPEDIATYYCQQANSFPVTFGGGTKVEIK")
NATIVE_CDR = {"hcdr1": "GFTFSQYG", "hcdr2": "IGPSGGST", "hcdr3": "TRGGPYYYYGMDV"}
POS = {"hcdr1": list(range(25, 33)), "hcdr2": list(range(50, 58)),
       "hcdr3": list(range(96, 109))}


def rebuild_vh(cdrs):
    """Substitute sampled CDRs into the native VH at the masked positions."""
    vh = list(NATIVE_VH)
    for r, seq in cdrs.items():
        for i, p in enumerate(POS[r]):
            vh[p] = seq[i]
    return "".join(vh)


def verify_vh(vh, cdrs):
    """Assert: length preserved, all edits inside mask, framework identical."""
    assert len(vh) == len(NATIVE_VH), "VH length changed"
    edits = [i for i, (a, b) in enumerate(zip(vh, NATIVE_VH)) if a != b]
    mask = set()
    for r in cdrs:
        mask |= set(POS[r])
    assert set(edits) <= mask, f"edits outside mask: {sorted(set(edits) - mask)}"
    for r, seq in cdrs.items():
        got = "".join(vh[p] for p in POS[r])
        assert got == seq, f"{r} roundtrip mismatch"
    return edits


def load(exec_id, regions):
    path = os.path.join(RES, "raw", f"{exec_id}_samples.csv")
    with open(path) as f:
        return list(csv.DictReader(f)), regions


def select(exec_id, regions, k=5):
    rows, _ = load(exec_id, regions)
    seen, cands = set(), []
    for i, row in enumerate(rows):
        cdrs = {r: row[r] for r in regions}
        key = tuple(cdrs[r] for r in regions)
        if key in seen:
            continue
        seen.add(key)
        if all(cdrs[r] == NATIVE_CDR[r] for r in regions):
            continue  # exact native reconstruction: control, not a candidate
        ce = sum(float(row[f"ce_loss_independent_{r}"]) for r in regions)
        aar = {r: sum(a == b for a, b in zip(cdrs[r], NATIVE_CDR[r])) / len(NATIVE_CDR[r])
               for r in regions}
        vh = rebuild_vh(cdrs)
        edits = verify_vh(vh, cdrs)
        cands.append({
            "candidate_id": f"t014r002_{exec_id}_{i:03d}",
            "scope": "+".join(regions),
            "execution": exec_id,
            "sample_index": i,
            "cdrs": cdrs,
            "ce_loss_sum": round(ce, 4),
            "per_cdr_aar": {r: round(aar[r], 4) for r in regions},
            "vh": vh,
            "vl": NATIVE_VL,
            "n_substitutions": len(edits),
        })
    cands.sort(key=lambda c: c["ce_loss_sum"])
    return cands[:k], len(rows), len(seen)


def main():
    out = {"reference": {
        "candidate_id": "t014_reference_osocimab",
        "vh": NATIVE_VH, "vl": NATIVE_VL,
        "cdrs": NATIVE_CDR, "ce_loss_sum": None,
        "note": "unmodified Osocimab Fv (positive control)"}}
    stats = {}
    for exec_id, regions in [("hcdr3_best100", ["hcdr3"]),
                             ("hcdr123_best100", ["hcdr1", "hcdr2", "hcdr3"])]:
        top, n_rows, n_uniq = select(exec_id, regions)
        stats[exec_id] = {"samples": n_rows, "unique_cdr_tuples": n_uniq,
                          "selected": len(top)}
        out[exec_id] = top
        for c in top:
            seqhash = hashlib.sha256((c["vh"] + "|" + c["vl"]).encode()).hexdigest()[:16]
            c["sequence_hash"] = seqhash
    sel_path = os.path.join(RES, "selected_candidates.json")
    with open(sel_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(stats, indent=1))

    # Boltz2 payload files: Protein_Sequences [VH, VL] per job
    pdir = os.path.join(RUN, "inputs", "submitted_requests")
    os.makedirs(pdir, exist_ok=True)
    jobs = [("t014_reference_osocimab", NATIVE_VH, NATIVE_VL)]
    for exec_id in ("hcdr3_best100", "hcdr123_best100"):
        for c in out[exec_id]:
            jobs.append((c["candidate_id"], c["vh"], c["vl"]))
    for cid, vh, vl in jobs:
        p = os.path.join(pdir, f"boltz2_{cid}.json")
        with open(p, "w") as f:
            json.dump({"Protein_Sequences": [vh, vl]}, f, indent=1)
        print(f"payload {p} (VH {len(vh)}aa, VL {len(vl)}aa)")
    print(f"WROTE {sel_path}; {len(jobs)} Boltz2 jobs (1 reference + "
          f"{len(jobs)-1} candidates)")


if __name__ == "__main__":
    main()
