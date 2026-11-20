#!/usr/bin/env python
"""task_009 run_002_igdesign_local stage 2: gates + full scFv reconstruction.

Gates (mirroring run_001 stage-4 gates where applicable):
  G1 loop lengths fixed by config (8/8/14) - verified by parse
  G2 no new Cys in any designed CDR
  G3 framework byte-identity - by construction (only CDR regions designed)
  G4 sequence uniqueness (full VH)
  G5 aromatic/Tyr content of H3 sanity band (>=2 Y in H3, as reference H3 is Tyr-rich)
Ranking: mean independent CE loss across the three CDRs (lower = model-preferred).
Top-4 unique candidates -> full 245-aa scFv payloads for Boltz2 evaluation.
"""
import csv, json

REF_VH = "EVQLLESGGGLVSPGGSLRLSCAASGFTFSYYYMGWVRQAPGKGLEWVSGISPSSGYTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCARYYYGYYYSHMDYWGQGTLVTVSS"  # 121, SM stripped
REF_VL = "DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQSRSGLHTFGQGTKLEIK"  # 107
LINKER = "GGGGSGGGGSGGGGS"
STUB = "SM"
assert len(REF_VH) == 121 and len(REF_VL) == 107

# 0-based slices within the 121 variable domain (frozen mask)
H1 = (25, 32)   # 8 residues
H2 = (50, 57)   # 8 residues
H3 = (96, 109)  # 14 residues

def ref_cdr(a, b):
    return REF_VH[a:b+1]

REF_CDRS = {"hcdr1": ref_cdr(*H1), "hcdr2": ref_cdr(*H2), "hcdr3": ref_cdr(*H3)}

def build_vh(c1, c2, c3):
    vh = list(REF_VH)
    for a, b, cdr in ((H1[0], H1[1], c1), (H2[0], H2[1], c2), (H3[0], H3[1], c3)):
        assert len(cdr) == b - a + 1, (a, b, len(cdr))
        for i, ch in enumerate(cdr):
            vh[a + i] = ch
    return "".join(vh)

rows = list(csv.DictReader(open("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_002_igdesign_local/raw/igdesign_run002_results.csv")))
out, seen = [], set()
n_pass = 0
for n, r in enumerate(rows):
    c1, c2, c3 = r["hcdr1"], r["hcdr2"], r["hcdr3"]
    losses = [float(r["ce_loss_independent_hcdr1"]), float(r["ce_loss_independent_hcdr2"]), float(r["ce_loss_independent_hcdr3"])]
    gates = {}
    gates["G1_lengths"] = len(c1) == 8 and len(c2) == 8 and len(c3) == 14
    gates["G2_no_new_cys"] = "C" not in c1 + c2 + c3
    gates["G5_h3_tyr"] = c3.count("Y") >= 2
    vh = build_vh(c1, c2, c3) if gates["G1_lengths"] else None
    gates["G4_unique"] = vh is not None and vh not in seen
    passed = all(gates.values())
    if passed:
        n_pass += 1
        seen.add(vh)
    out.append({
        "idx": n, "hcdr1": c1, "hcdr2": c2, "hcdr3": c3,
        "loss_h1": losses[0], "loss_h2": losses[1], "loss_h3": losses[2],
        "loss_mean": round(sum(losses) / 3, 4),
        "n_cdr_mut_vs_ref": sum(1 for k in ("hcdr1", "hcdr2", "hcdr3")
                                 for a, b in zip(REF_CDRS[k], (c1, c2, c3)[("hcdr1", "hcdr2", "hcdr3").index(k)])
                                 if a != b),
        "gates": gates, "pass": passed,
        "vh_full": vh,
        "scfv_full": (STUB + vh + LINKER + REF_VL) if vh else None,
    })

passed = [r for r in out if r["pass"]]
passed.sort(key=lambda r: r["loss_mean"])
top4 = passed[:4]

res = {
    "n_generated": len(rows),
    "n_pass_all_gates": n_pass,
    "n_unique_vh": len(seen),
    "reference_cdrs_121num": {k: REF_CDRS[k] for k in REF_CDRS},
    "top4": [{k: r[k] for k in ("idx", "hcdr1", "hcdr2", "hcdr3", "loss_mean", "n_cdr_mut_vs_ref", "scfv_full")} for r in top4],
}
base = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_002_igdesign_local/raw/native_generation/outputs"
import os
os.makedirs(base, exist_ok=True)
json.dump(res, open(f"{base}/gate_report.json", "w"), indent=1)
with open(f"{base}/candidates_gated.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["idx", "hcdr1", "hcdr2", "hcdr3", "loss_h1", "loss_h2", "loss_h3", "loss_mean", "n_cdr_mut_vs_ref", "pass", "vh_full"])
    w.writeheader()
    for r in out:
        w.writerow({k: r[k] for k in w.fieldnames})
print(json.dumps({k: res[k] for k in ("n_generated", "n_pass_all_gates", "n_unique_vh")}, indent=1))
for r in top4:
    print(f"cand{r['idx']:03d} loss_mean={r['loss_mean']} muts={r['n_cdr_mut_vs_ref']} H1={r['hcdr1']} H2={r['hcdr2']} H3={r['hcdr3']} scFv_len={len(r['scfv_full'])}")
