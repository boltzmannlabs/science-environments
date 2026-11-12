import json, csv, shutil
RES="/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_001_her2_trastuzumab_interaction_optimization"
HR="/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results"
# designed_sequences.fasta (paired)
shutil.copy(f"{RES}/sequences.fasta", f"{HR}/designed_sequences.fasta")
# shortlist.csv = candidates.csv
shutil.copy(f"{RES}/candidates.csv", f"{HR}/shortlist.csv")
# benchmark_comparison.csv
shutil.copy(f"{RES}/evidence/benchmark_comparison.csv", f"{HR}/benchmark_comparison.csv")
# metrics.json (matched ref/candidate scores, units, hashes, provenance)
cands=json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json"))["shortlist"]
import hashlib
def h(s):return hashlib.sha256(s.encode()).hexdigest()[:16]
metrics={"task":"task_001_her2_trastuzumab_interaction_optimization","units":{"prodigy_dG":"kcal/mol","prodigy_KD":"M","thermal_stab_protbert":"Antibody_Prediction score","thermal_stab_esm":"Antibody_Prediction score","solubility":"Antibody_Prediction score","clash_count":"count (vdw-1.5A, same-chain, non-adjacent)"},"matched_conditions":"fixed 1N8Z pose; candidate = 1N8Z backbone + designed CDR side chains (ideal geometry, CB-oriented)","reference":{"seq_id":"REF_1N8Z","VH_hash":h("EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"),"VL_hash":h("DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"),"prodigy_dG":-9.9,"prodigy_KD":"5.6e-08","prodigy_IC":61,"clash_count":26,"thermal_stab_protbert":49.549126,"thermal_stab_esm":94.066696,"solubility":1},"candidates":{},"benchmark":{"name":"Ab-SELDON REF15 (JCIM 2026)","metric":"REF15 interaction score (Rosetta REU), lower favorable","best_diversity_FINAL_REU":-94.8663,"best_random_FINAL_REU":-92.6947,"comparability":"NON-COMPARABLE — Rosetta unavailable; ProDIGy is a different protocol (kcal/mol)","status":"NOT COMPUTED — did not fabricate"}}
prodigy={"AB_08":(-9.8,"6.3e-08",69,26),"AB_20":(-9.9,"5.9e-08",67,26),"AB_04":(-9.6,"9.6e-08",60,26),"AB_05":(-9.9,"5.7e-08",65,38),"AB_13":(-10.9,"9.4e-09",68,27)}
props={r["seq_id"]:r for r in csv.DictReader(open("/home/boltzmann10/.sci/workspace/outputs/task001_props_parsed.csv"))}
for c in cands:
    pid=c["id"];dg,kd,ic,cl=prodigy[pid];pp=props[pid]
    metrics["candidates"][pid]={"VH_hash":h(c["heavy"]),"VL_hash":h(c["light"]),"cdr_edits_H":c["cdr_edits_H"],"cdr_edits_L":c["cdr_edits_L"],"prodigy_dG":dg,"prodigy_dG_delta_vs_ref":round(dg-(-9.9),2),"prodigy_KD":kd,"prodigy_IC":ic,"clash_count":cl,"thermal_stab_protbert":pp["ts_protbert"],"thermal_stab_esm":pp["Thermal_stab_esm"],"solubility":pp["solubility"],"antibmpnn_score":c["score"]}
json.dump(metrics,open(f"{HR}/metrics.json","w"),indent=1)
# report.md
open(f"{HR}/report.md","w").write("""# Task 001 — HER2: Trastuzumab Interaction Optimization — Report

## Design rationale
AntiBMPNN (structure-conditioned on the 1N8Z trastuzumab/HER2 complex) designed all six CDRs (H1/H2/H3 on VH, L1/L2/L3 on VL) while fixing the framework and disulfides. 20 paired VH/VL variants were generated; all passed framework-integrity and disulfide-preservation checks. A diverse shortlist of 5 was selected (low AntiBMPNN score + CDR-edit spread).

## Matched-conditions evaluation
Reference and candidates were evaluated on the same HER2 construct (1N8Z chain C) and preparation. For each candidate, the 1N8Z backbone was kept fixed and the designed CDR side chains were placed (ideal geometry oriented by the original CA->CB direction). ProDIGy (open-source, contact-based) scored Fab(A,B)-vs-HER2(C) binding; Antibody_Prediction (Boltzmann) scored thermal stability and solubility.

## Supported improvements
- **AB_13** is the best candidate: ProDIGy dG -10.9 kcal/mol (1.0 better than the reference -9.9), KD 9.4e-9 M (~6x lower than the reference 5.6e-8 M), 68 interface contacts, 27 clashes (+1 vs reference), and the highest thermal-stability scores (ProtBert 52.4, ESM 104.8).
- AB_20 and AB_05 maintain reference binding (dG -9.9); AB_08 (-9.8) and AB_04 (-9.6) are slightly weaker.

## Unresolved evidence / limitations
- The published benchmark metric is REF15 (Rosetta REU). Rosetta is not available in this environment, so REF15 was NOT computed and was NOT fabricated. ProDIGy (kcal/mol, contact-based) is a different scoring protocol and is NON-COMPARABLE to REF15; published REF15 values are reported as controls only.
- ProDIGy's empirical RMSE is ~2.6 kcal/mol; a 1.0 kcal/mol difference is within that uncertainty.
- Side-chain reconstruction uses ideal geometry (no full rotamer optimization); it is an approximation for a matched-conditions comparison, not a physical simulation.
- Boltz2 de novo predictions: the VH-VL dimer is reliable (ipTM 0.955) but the VH-HER2 pair is not (ipTM 0.245), so the fixed-pose approach was used for binding. Candidate Boltz2 structure downloads failed (300s signed-URL TTL).
- Computational interaction improvement does not establish experimental affinity or therapeutic activity.

## Artifacts
- designed_sequences.fasta, shortlist.csv, metrics.json, benchmark_comparison.csv, report.md (this file).
- Structures: reconstructed/ (fixed-pose candidate complexes) and 1N8Z_deposited_complex.pdb (reference).
- Full evaluation evidence: results/task_001_her2_trastuzumab_interaction_optimization/evidence/.
""")
print("her2_results bundle done:")
for f in ["designed_sequences.fasta","shortlist.csv","metrics.json","benchmark_comparison.csv","report.md"]:
    print(" ",f)
