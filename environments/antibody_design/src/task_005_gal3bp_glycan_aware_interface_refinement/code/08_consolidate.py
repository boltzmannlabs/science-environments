#!/usr/bin/env python3
"""Consolidate task_005 metrics and write deliverables."""
import json, os, csv

BASE = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy"
ENV = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design"

# Load metrics
with open(os.path.join(BASE,"evidence/task005_interface_metrics.json")) as f: im = json.load(f)
with open(os.path.join(BASE,"evidence/prodigy_validation.json")) as f: pr = json.load(f)
with open(os.path.join(BASE,"evidence/glycan_aware_analysis.json")) as f: gl = json.load(f)

im_by = {r["tag"]:r for r in im["results"]}
pr_by = pr["results"]

# Consolidated table
rows = []
for tag, name in [("ref_bdbv43","BDBV-43 (reference)"),("cand11","task005_cand11"),("cand7","task005_cand7"),("cand17","task005_cand17")]:
    i = im_by[tag]; p = pr_by[name]
    rows.append({
        "candidate_id": tag, "name": name,
        "ipTM": i["ipTM"], "pLDDT": i["pLDDT"], "pDE": i["pDE"],
        "interface_residue_pairs": i["interface_residue_pairs"],
        "vdw_atom_pairs": i["vdw_atom_pairs"], "hbond_atom_pairs": i["hbond_atom_pairs"],
        "hbond_share": round(i["hbond_share_of_contacts"],4),
        "antigen_residues": i["antigen_residues_in_interface"],
        "prodigy_dG_kcal_mol": p["dg_kcal_mol"], "prodigy_Kd_M": p["kd_M"],
        "prodigy_IC": p["n_intermolecular_contacts"],
    })

# Ranking: cand17 (best Prodigy + 2nd ipTM), cand11 (best ipTM), cand7
rank = {"ref_bdbv43":0,"cand17":1,"cand11":2,"cand7":3}
reasons = {
 "cand17":"Best open-source Prodigy binding estimate (dG -14.5 kcal/mol, Kd 2.3e-11 M, 102 ICs) AND 2nd-highest Boltz2 ipTM (0.485); most vdW pairs (499) and H-bonds (18).",
 "cand11":"Highest Boltz2 ipTM (0.554) and largest interface extent (59 residue pairs, 21 antigen residues); Prodigy dG near reference (-11.1).",
 "cand7":"Intermediate ipTM (0.306) and Prodigy dG (-10.8); retained as a lower-confidence comparison.",
 "ref_bdbv43":"Published-design reference scaffold (BDBV-43, CDR-H3=ARDEIIGADS); not an established Gal-3BP binder.",
}

# Write candidates.csv
cpath = os.path.join(BASE,"candidates.csv")
with open(cpath,"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["candidate_id","name","rank","selection_status","selection_reason","ipTM","pLDDT","pDE","interface_residue_pairs","vdw_atom_pairs","hbond_atom_pairs","hbond_share","antigen_residues","prodigy_dG_kcal_mol","prodigy_Kd_M","prodigy_IC","structure_file"])
    w.writeheader()
    for r in sorted(rows, key=lambda x: rank[x["candidate_id"]]):
        if r["candidate_id"]=="ref_bdbv43":
            r2 = dict(r); r2["structure_file"]="evidence/reference/task005_ref_bdbv43.pdb"
        else:
            r2 = dict(r); r2["structure_file"]=f"structures/{r['candidate_id']}_complex.pdb"
        r2["rank"] = rank[r["candidate_id"]]
        r2["selection_status"] = "shortlisted" if rank[r["candidate_id"]]>=1 else "reference_control"
        r2["selection_reason"] = reasons[r["candidate_id"]]
        w.writerow(r2)
print(f"Wrote {cpath}")

# Write consolidated metrics.json
mpath = os.path.join(BASE,"evidence/metrics.json")
with open(mpath,"w") as f:
    json.dump({
        "task":"task_005_gal3bp_glycan_aware_interface_refinement",
        "conditions":"Matched-conditions: Boltz2-predicted BDBV-43 Fab + full-length LGALS3BP (585 aa), unglycosylated protein; CDR-H3-only redesign.",
        "contact_definitions":im["definitions"],
        "glycan_aware":gl,
        "metrics":rows,
        "prodigy":pr,
        "ranking":{"1st":"task005_cand17","2nd":"task005_cand11","3rd":"task005_cand7"},
        "benchmark_note":"Published 161/165/67%/5A/2.9A2 require the study's mature construct, glycan model, E1 mapping and heated-MD replicas (paper inaccessible). Matched-conditions comparison only.",
    }, f, indent=2)
print(f"Wrote {mpath}")

# Write benchmark_comparison.csv
bpath = os.path.join(BASE,"evidence/benchmark_comparison.csv")
with open(bpath,"w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["published_metric","published_value","new_matched_condition_value","comparable","explanation"])
    w.writerow(["Unique reference-complex interactions","161","32 (Boltz2 C-alpha<8A residue pairs)","NO","Different construct (full-length unglycosylated) + contact definition; not like-for-like."])
    w.writerow(["Unique Mut1-complex interactions","165","n/a (Mut1 sequence unavailable)","NO","Mut1 is a paper-only point-mutation variant; not reproduced."])
    w.writerow(["H-bond share of contacts","~67%","1.3-5.0% (N/O<3.5A proxy)","NO","Different contact-counting definition + glycan context."])
    w.writerow(["Interface RMSD selection boundary","5 A","n/a (no heated-MD replicas run)","NO","Requires 3 heated MD replicas per system (MDS contract blocked)."])
    w.writerow(["Mut1 interface-stability outcome","No replica exceeded 5 A","n/a","NO","Same reason."])
    w.writerow(["E1 glycan-associated dSASA","2.9 A2","34.2 A2 (BACK-domain, single glycan at 362)","PARTIAL","Our E1 proxy is the whole BACK domain (101 res) with a single simplified glycan; paper's E1 is a smaller subset with a multi-glycan model. Not directly comparable."])
    w.writerow(["E2 glycan-associated dSASA","7.0 A2","n/a","NO","E2 not in scope (E1 task)."])
    w.writerow(["Global glycan-associated SASA reduction","~1299 A2","n/a","NO","Requires the study's full glycan model."])
    w.writerow(["Boltz2 ipTM (reference)","n/a (paper uses AF2)","0.323","NEW","Our matched-conditions Boltz2 confidence."])
    w.writerow(["Boltz2 ipTM (best candidate)","n/a","0.554 (cand11) / 0.485 (cand17)","NEW","Improved interface confidence over reference."])
    w.writerow(["Prodigy dG (reference)","n/a","-11.2 kcal/mol","NEW","Open-source PPI affinity estimate."])
    w.writerow(["Prodigy dG (best candidate)","n/a","-14.5 kcal/mol (cand17)","NEW","cand17 strongest open-source binding estimate."])
print(f"Wrote {bpath}")
print("Done.")
