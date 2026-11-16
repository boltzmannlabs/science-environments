"""Stage 7: build monoclonal.md-compliant result artifacts for run_001.

Outputs (results/<task>/run_001_antibmpnn_matched/):
  candidates.csv, shortlist.csv, sequences.fasta, metrics.csv,
  benchmark_comparison.csv, report.md (rename results.md -> report.md)
"""
import csv
import json
import math
import os

BASE = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
RUN = BASE + "/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched"
INP = RUN + "/inputs"
RES = BASE + "/results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched"
RAW = RES + "/raw"

R = 0.0019872041
T = 298.15

cands = json.load(open(INP + "/candidates.json"))
conf = json.load(open(RAW + "/boltz2_confidence.json"))
ev = {r["candidate"]: r for r in json.load(open(RAW + "/evaluation.json"))}
clash = json.load(open(RAW + "/clash_counts.json"))
jm = json.load(open(INP + "/job_map.json"))
ref = json.load(open(INP + "/reference_sequences.json"))

REF_VH, REF_VL = ref["VH"], ref["VL"]

# ---------- candidates.csv (all 38 unique, evaluated or not) ----------
with open(RES + "/candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["candidate_id", "VH", "VL", "n_mutations", "mut_H", "mut_L",
                "design_score", "evaluated", "liabilities_inherited_or_new"])
    for c in cands["candidates"]:
        w.writerow([c["candidate_id"], c["VH"], c["VL"], c["n_mutations"],
                    ";".join(c["mut_H"]), ";".join(c["mut_L"]), c.get("score"),
                    "yes" if c["candidate_id"] in ev else "no",
                    ";".join(c.get("liabilities", []))])
print("candidates.csv:", len(cands["candidates"]))

# ---------- shortlist.csv (8 evaluated, ranked) ----------
def rank_key(cid):
    r = ev[cid]
    # primary: mean Prodigy dG (more negative better), secondary ipTM rec2, tertiary fewer muts
    return (-(r["dG_rec1_H"] + r["dG_rec2_L"]) / 2, -r["iptm_rec2"], r["n_mutations"])

short = sorted([cid for cid in ev if cid != "REFERENCE"], key=rank_key)
with open(RES + "/shortlist.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "candidate_id", "n_mutations", "mut_H", "mut_L",
                "prodigy_dG_VH_record", "prodigy_dG_VL_record", "Kd_uM_VL_record",
                "iptm_VL_record", "iptm_VH_record", "cdr_plddt_VH", "cdr_plddt_VL",
                "epitope_recovery", "interface_clashes"])
    for i, cid in enumerate(short, 1):
        r = ev[cid]
        w.writerow([i, cid, r["n_mutations"], r["mut_H"], r["mut_L"],
                    r["dG_rec1_H"], r["dG_rec2_L"], r["Kd_uM_rec2"],
                    r["iptm_rec2"], r["iptm_rec1"], r["cdr_plddt_VH"], r["cdr_plddt_VL"],
                    r["epitope_recovery_rec2"], clash[cid]["1_model_0.pdb"] + clash[cid]["2_model_0.pdb"]])
print("shortlist.csv:", len(short), "top:", short[0])

# ---------- sequences.fasta (reference + all candidates; evaluated flagged) ----------
with open(RES + "/sequences.fasta", "w") as f:
    f.write(">REFERENCE_VH|task_001|run_001|trastuzumab|source=PDB_1N8Z\n%s\n" % REF_VH)
    f.write(">REFERENCE_VL|task_001|run_001|trastuzumab|source=PDB_1N8Z\n%s\n" % REF_VL)
    for c in cands["candidates"]:
        tag = "evaluated" if c["candidate_id"] in ev else "unevaluated"
        f.write(">%s_VH|task_001|run_001|antiBMPNN_CDR|status=%s\n%s\n" % (c["candidate_id"], tag, c["VH"]))
        f.write(">%s_VL|task_001|run_001|antiBMPNN_CDR|status=%s\n%s\n" % (c["candidate_id"], tag, c["VL"]))
print("sequences.fasta:", 2 + 2 * len(cands["candidates"]))

# ---------- metrics.csv (long format: candidate x metric) ----------
with open(RES + "/metrics.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["candidate_id", "metric", "value", "units", "source", "protocol"])
    for cid in ["REFERENCE"] + sorted(c for c in ev if c != "REFERENCE"):
        r = ev[cid]
        rows = [
            ("prodigy_dG", "dG_rec1_H", r["dG_rec1_H"], "kcal/mol", "Prodigy (Boltzmann)", "HER2+VH pairwise record"),
            ("prodigy_dG", "dG_rec2_L", r["dG_rec2_L"], "kcal/mol", "Prodigy (Boltzmann)", "HER2+VL pairwise record"),
            ("Kd_predicted", "Kd_uM_rec2", r["Kd_uM_rec2"], "uM", "derived: exp(dG/RT)", "HER2+VL record"),
            ("iptm", "iptm_rec1", r["iptm_rec1"], "dimensionless", "Boltz2", "HER2+VH"),
            ("iptm", "iptm_rec2", r["iptm_rec2"], "dimensionless", "Boltz2", "HER2+VL"),
            ("cdr_plddt", "cdr_plddt_VH", r["cdr_plddt_VH"], "dimensionless", "Boltz2 plddt npz", "VH CDRs (Kabat H31-35,50-65,95-102)"),
            ("cdr_plddt", "cdr_plddt_VL", r["cdr_plddt_VL"], "dimensionless", "Boltz2 plddt npz", "VL CDRs (Kabat L24-34,50-56,89-97)"),
            ("epitope_recovery", "epitope_recovery_rec2", r["epitope_recovery_rec2"], "fraction", "local: prodigy interface vs 1N8Z contacts", "strict residue-number overlap"),
            ("interface_clashes", "clashes_total", clash[cid]["1_model_0.pdb"] + clash[cid]["2_model_0.pdb"], "count", "local: heavy-atom <2.2A", "both records"),
        ]
        for m, name, val, unit, src, proto in rows:
            w.writerow([cid, name, val, unit, src, proto])
print("metrics.csv rows:", 9 * len(ev))

# ---------- benchmark_comparison.csv ----------
# Published benchmark = Ab-SELDON REF15 (REU) endpoints; our metrics = Prodigy dG / Boltz2 ipTM.
# Different scoring protocols -> not_comparable per benchmark doc rules.
with open(RES + "/benchmark_comparison.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_type", "record_id", "metric", "value", "scope", "source"])
    w.writerow(["published_reference", "trastuzumab_initial_REF15_div6", "REF15", -49.6996,
                "Ab-SELDON diversity run 6 initial (per-run log)", "JCIM 2026 10.1021/acs.jcim.5c01924 + Zenodo 15803983"])
    w.writerow(["published_reference", "trastuzumab_final_REF15_div6", "REF15", -94.8663,
                "Ab-SELDON diversity run 6 final (best)", "JCIM 2026 10.1021/acs.jcim.5c01924 + Zenodo 15803983"])
    w.writerow(["published_reference", "trastuzumab_final_REF15_ran4", "REF15", -92.6947,
                "Ab-SELDON random run 4 final (best)", "JCIM 2026 10.1021/acs.jcim.5c01924 + Zenodo 15803983"])
    w.writerow(["published_reference", "published_candidate_level_iptm_plddt_pae_pdockq", "iptm/plddt/pae/pDockQ", "",
                "not verified from released evidence (benchmark md line 33) -> report unavailable", "not_retrieved"])
    w.writerow(["individual_new_candidate", "REFERENCE", "prodigy_dG_VL_record", ev["REFERENCE"]["dG_rec2_L"],
                "our Boltz2+Prodigy matched protocol", "run_001"])
    for cid in short:
        w.writerow(["individual_new_candidate", cid, "prodigy_dG_VL_record", ev[cid]["dG_rec2_L"],
                    "our Boltz2+Prodigy matched protocol", "run_001"])
        w.writerow(["individual_new_candidate", cid, "iptm_VL_record", ev[cid]["iptm_rec2"],
                    "our Boltz2 prediction", "run_001"])
    w.writerow(["comparison_verdict", "REF15_vs_prodigy", "protocol_compatibility", "not_comparable",
                "REF15 (Rosetta REU, design-protocol internal) vs Prodigy dG (empirical interfacial-contact model on predicted structure): different scores, structures and conditions", "benchmark md evaluation-criteria rule"])
print("benchmark_comparison.csv written")

# ---------- report.md (rename results.md, extend) ----------
rep = open(RES + "/results.md").read()
header = "# run_001_antibmpnn_matched report — AntiBMPNN fixed-backbone CDR redesign (executed)\n\n"
rep = rep.replace("# task_001_her2_trastuzumab_interaction_optimization — Results (run_001_antibmpnn_matched)\n", header)
extra = """
## 7. Benchmark comparison (benchmark/monoclonal_antibody_design/task_001...md)
- Published metric is REF15 (Rosetta REU) from Ab-SELDON per-run logs (JCIM 2026; Zenodo 15803983). Our metrics are Prodigy dG and Boltz2 ipTM on Boltz2-predicted structures. These are different scoring functions on different structures under different conditions -> labelled not_comparable per the benchmark doc's evaluation criteria; no REU-equivalent value is claimed for our candidates.
- Published best endpoints: diversity run 6 final REF15 -94.8663 (initial -49.6996), random run 4 final -92.6947 (initial -48.9576). Candidate-level pLDDT/ipTM/PAE/pDockQ for those endpoints are unavailable in the released evidence inspected and are reported as such, not inferred.
- Released per-sequence archive (4.1 GB) not retrievable in-session -> no direct sequence-level comparison to published endpoints (NEEDS_INPUT recorded in config).
- Within OUR matched protocol, candidate-vs-reference deltas are valid: all 8 evaluated candidates improve ipTM(VL record) over reference (0.34 -> 0.57-0.81); 6/8 improve Prodigy dG(VL record) (-8.7 -> -9.5..-10.1).

## 8. Deliverables index (monoclonal.md section 6)
- candidates.csv: 38 unique AntiBMPNN candidates (2 duplicate pairs removed from 40), all mutations verified inside CDR mask, framework byte-identical.
- shortlist.csv: 8 evaluated candidates ranked by mean Prodigy dG then ipTM(VL); top = %(top)s.
- sequences.fasta: reference VH/VL + 76 chains (38 candidates), evaluated/unevaluated flagged.
- metrics.csv: long-format metric table (Prodigy dG, derived Kd, ipTM, CDR pLDDT, epitope recovery, clashes) for REFERENCE + 8 candidates.
- benchmark_comparison.csv: published REF15 endpoints (reference rows) + our metrics (candidate rows) with explicit not_comparable verdict for cross-protocol comparison.
- structures/: 18 PDBs (REFERENCE + 8 candidates x 2 pairwise records).
- raw/: boltz2_confidence.{json,csv}, evaluation.{json,csv}, clash_counts.json + native platform outputs under inputs/.

## 9. Counts reconciliation (monoclonal.md section 2)
- Designed workflows: 3 (run_001 selected+executed; run_002 not_selected - matched-conditions rationale in its workflow.md; run_003 not_run - no distinct scientific strategy under this task's constraints).
- Submitted jobs: 25 ledger entries (job_map.json): 5 AntiBMPNN design attempts (4 input-format failures + 1 success) + 1 control, 9 Boltz2, 10 Prodigy (9 failed nested-zip + ... corrected flat resubmissions counted in state files).
- Completed: AntiBMPNN 1/5; Boltz2 9/9; Prodigy 9/9 (after one corrected resubmission each).
- Candidates: 40 generated -> 38 unique -> 8 evaluated (budget: one Boltz2+Prodigy batch) -> 30 unevaluated preserved in candidates.csv/sequences.fasta.
- Blockers: Zenodo 4.1 GB archive (NEEDS_INPUT); no REF15 scorer available (open-source Rosetta build not available in-session; not attempted on predicted structures since protocol non-comparability stands regardless).
""" % {"top": short[0]}
rep = rep + extra
open(RES + "/report.md", "w").write(rep)
os.remove(RES + "/results.md")
print("report.md written (results.md renamed+extended)")
print("DONE")
