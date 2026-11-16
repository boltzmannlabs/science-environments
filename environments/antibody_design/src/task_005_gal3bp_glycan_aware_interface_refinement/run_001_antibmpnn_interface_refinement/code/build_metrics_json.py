#!/usr/bin/env python3
"""Build metrics.json (task-required bundle file) + extend benchmark_comparison.csv."""
import json, csv, glob, hashlib

R = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement"
RSLT = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

chem = {c: json.load(open(f"{R}/gal3bp_w3_candidate_eval/outputs/interface_chem_{c}.json")) for c in ("G3BPD-14", "G3BPD-04", "G3BPD-17")}
gly = {c: json.load(open(f"{R}/gal3bp_w3_candidate_eval/outputs/glycan_dsasa_{c}.json")) for c in ("G3BPD-14", "G3BPD-04", "G3BPD-17")}
pers = json.load(open(f"{R}/gal3bp_w3_candidate_eval/outputs/candidate_per_sample_persistence.json"))
agre = json.load(open(f"{R}/gal3bp_w3_candidate_eval/outputs/candidate_model_agreement.json"))
ref_chem = json.load(open(f"{R}/gal3bp_w1_ref_complex/outputs/interface_chem_ref.json"))
ref_gly = json.load(open(f"{R}/gal3bp_w1_ref_complex/outputs/glycan_dsasa_ref_E1approx.json"))
germ = json.load(open(f"{R}/gal3bp_w3_candidate_eval/outputs/anarci_candidates_summary.json"))
designs = json.load(open(f"{R}/gal3bp_w2_cdr_design/outputs/candidate_designs.json"))

iptm = {}
for C in ("G3BPD-14", "G3BPD-04", "G3BPD-17"):
    per = {}
    for f in glob.glob(f"{R}/gal3bp_w3_candidate_eval/outputs_{C}/extracted/**/*scores_rank_0*.json", recursive=True):
        d = json.load(open(f))
        per[f.split("scores_rank_")[1][:3]] = d.get("iptm", 0)
    iptm[C] = per

prod = {"G3BPD-14": (63, -8.7, "4.5e-07"), "G3BPD-04": (63, -8.7, "4.1e-07"), "G3BPD-17": (63, -8.6, "5.2e-07")}

mapping = {"BDBV43_reference": "ref_complex_afm_rank1.pdb", "G3BPD-14": "G3BPD-14_afm_rank1.pdb",
           "G3BPD-04": "G3BPD-04_afm_rank1.pdb", "G3BPD-17": "G3BPD-17_afm_rank1.pdb"}
docs = {"BDBV43_reference": "6af879cf9de6b44b075d7f4c", "G3BPD-14": "6af89d409850a93adf67dbf3",
        "G3BPD-04": "6af89d539030bff41644864d", "G3BPD-17": "6af8a897445ae94313c3cfa6"}
prov = {k: {"file": f"structures/{f}", "sha256": sha(f"{RSLT}/structures/{f}"), "afm_doc_id": docs[k],
            "rank": "001 of 5", "engine": "colabfold_multimer (AF2-Multimer v3)"} for k, f in mapping.items()}

metrics = {
    "run": "run_001_antibmpnn_interface_refinement",
    "target": {
        "antigen": "Gal-3BP (LGALS3BP) UniProt Q08380 mature 19-585",
        "antigen_construct": "predicted (AlphaFold-derived coordinates through AFM), NOT experimental",
        "reference_antibody": "BDBV-43 Fv from PDB 7KEW (VH 122aa, VL 106aa)",
    },
    "definitions": {
        "interface_residue_pair": "antibody-antigen residue pair with CA-CA < 6 A",
        "heavy_contact": "any non-H atom pair <= 5 A",
        "hbond": "donor(N/S/O)-acceptor(N/O/S) <= 3.5 A, geometry proxy (no H)",
        "salt_bridge": "Asp/Glu carboxyl O to Lys/Arg/His N <= 4 A",
        "interface_rmsd": "align on antigen CA; RMSD on antibody interface (paratope) atoms",
        "glycan_model": ("simplified N-glycan (12 six-C rings, 5.5 A spacing, ring radius 1.5 A) at mature N344 CA; "
                          "dSASA = SASA(unglyc) - SASA(glyc), positive = occlusion; E1 approximated by BACK-domain "
                          "window C276-C350 (study E1 residues NEEDS_INPUT)"),
    },
    "reference_measurements": {
        "BDBV43_reference": {
            "iptm_per_rank": [0.32, 0.27, 0.27, 0.27, 0.26],
            "interface_residue_pairs": ref_chem["n_interface_residue_pairs_CA_independent"],
            "heavy_contacts_5A": ref_chem["n_heavy_atom_contacts_5A"],
            "hbonds": ref_chem["n_hbonds"],
            "hbond_share_pct": ref_chem["hbond_share_of_contacts_pct"],
            "salt_bridges": ref_chem["n_salt_bridges"],
            "cc_contacts": ref_chem["n_carbon_carbon_contacts_5A"],
            "paratope_residues": ref_chem["paratope_residues"],
            "epitope_residues": ref_chem["epitope_residues"],
            "prodigy_dG_kcal_mol": -9.2,
            "prodigy_Kd_M": "1.7e-07",
            "prodigy_contacts": 72,
            "glycan_dsasa_A2": ref_gly["glycan_dsasa_A2"],
            "glycan_clashes": ref_gly["glycan_antibody_clashes_n2p5A"],
            "cross_model_persistence": "0/130 pairs in >=3 of 5 AFM models; pairwise interface RMSD 18-28 A",
            "protenix_independent": "3 seeds x 5 samples iptm 0.146-0.166; no pair shared by >1 sample",
            "boltz2_pair_aux": "VH:ag iptm 0.317 (doc 6af844cd9de6b44b075d7a93)",
        }
    },
    "candidates": {},
    "structure_provenance": prov,
    "data_provenance": {
        "candidate_designs": "gal3bp_w2_cdr_design/outputs/candidate_designs.json (AntiBMPNN doc 6af89b4ed29658acc304eef4)",
        "afm_outputs": "gal3bp_w3_candidate_eval/outputs_<CAND>/output.zip per candidate",
        "chemistry": "gal3bp_w3_candidate_eval/outputs/interface_chem_*.json",
        "prodigy": "gal3bp_w3_candidate_eval/outputs/prodigy_*.txt",
        "glycan": "gal3bp_w3_candidate_eval/outputs/glycan_dsasa_*.json",
        "persistence": "gal3bp_w3_candidate_eval/outputs/candidate_per_sample_persistence.json",
        "anarci": "gal3bp_w3_candidate_eval/outputs/anarci_candidates_summary.json",
        "job_registry": "gal3bp_w3_candidate_eval/outputs/w3_job_registry.json",
    },
    "controls": {
        "Mut1_published_comparator": {
            "status": "NOT_REPRODUCED",
            "reason": "study full text unobtainable; Mut1 sequences/metrics NEEDS_INPUT; retained as published comparison control only, not re-generated",
        },
        "self_consistency": "reference-vs-itself interface metrics recomputed twice (identical); candidate model sequences verified byte-exact vs designs post-download",
    },
    "limitations": [
        "engine confidence (iptm) is not affinity",
        "study metrics (161/165 interactions, ~67% H-bond share, 5 A heated-MD RMSD, 2.9 A2 E1 dSASA) not comparable: definitions and protocol unavailable",
        "predictor sampling substitutes for the study's GaMD/heated-MD replicas (protocol-incomparable)",
        "glycan model is simplified; N344-window E1 approximation only",
    ],
}

for C in ("G3BPD-14", "G3BPD-04", "G3BPD-17"):
    d = next(x for x in designs if x["candidate"] == C)
    c = chem[C]
    metrics["candidates"][C] = {
        "vh_mutations": [f"{a}{p}{b}" for p, a, b in d["vh_mutations"]],
        "vl_mutations": [f"{a}{p}{b}" for p, a, b in d["vl_mutations"]],
        "antibmpnn_score": d["score"],
        "seq_recovery": d["seq_recovery"],
        "iptm_per_rank": [round(iptm[C][k], 2) for k in sorted(iptm[C])],
        "interface_residue_pairs": c["n_interface_residue_pairs_CA_independent"],
        "heavy_contacts_5A": c["n_heavy_atom_contacts_5A"],
        "hbonds": c["n_hbonds"],
        "hbond_share_pct": c["hbond_share_of_contacts_pct"],
        "salt_bridges": c["n_salt_bridges"],
        "cc_contacts": c["n_carbon_carbon_contacts_5A"],
        "paratope_residues": c["paratope_residues"],
        "epitope_residues": c["epitope_residues"],
        "prodigy_dG_kcal_mol": prod[C][1],
        "prodigy_Kd_M": prod[C][2],
        "prodigy_contacts": prod[C][0],
        "glycan_dsasa_A2": gly[C]["glycan_dsasa_A2"],
        "glycan_clashes": gly[C]["glycan_antibody_clashes_n2p5A"],
        "per_sample_interface_pairs": pers[C]["per_sample_pair_counts"],
        "persistence_pairs_in_ge3_of_5": pers[C]["n_pairs_in_ge3_of_5"],
        "interface_ca_rmsd_to_rank001_A": pers[C]["interface_ca_rmsd_to_rank001_A"],
        "top2_epitope_jaccard": agre.get(C, {}).get("jaccard_epitope"),
        "germline_VH": germ[f"{C}_VH"]["germline"]["v"],
        "germline_VL": germ[f"{C}_VL"]["germline"]["v"],
        "developability_liabilities": "parental framework NS motif at VH 85 (inherited, not introduced)",
        "sequence_verified_vs_design": True,
    }

json.dump(metrics, open(f"{RSLT}/metrics.json", "w"), indent=2)
print("metrics.json written")

with open(f"{RSLT}/benchmark_comparison.csv", "a", newline="") as f:
    w = csv.writer(f)
    w.writerow(["glycan occlusion dSASA (candidates; simplified model, N344, C276-350)", "2.9 A2 (E1, study definition)",
                "222.2 / 217.2 / 217.5 A2 (G3BPD-14/-04/-17)", "G3BPD-14/-04/-17", "not_comparable",
                "same conventions as reference; study E1 residues NEEDS_INPUT"])
    w.writerow(["interface persistence (candidates)", "study: Mut1 stable across 3 heated-MD replicas (per task md)",
                "0/6, 0/7, 0/2 rank-1 pairs persist >=3/5 AFM models; inter-model RMSD 6.1-45.3 A", "G3BPD-14/-04/-17",
                "not_comparable", "predictor sampling != heated-MD replicas; no candidate shows a reproducible pose"])
    w.writerow(["Mut1 published comparator", "165 interactions (study)", "not re-generated; Mut1 sequence/metrics NEEDS_INPUT",
                "-", "not_comparable", "retained as published control only per task constraint"])
print("benchmark_comparison.csv extended")
