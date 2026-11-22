#!/usr/bin/env python3
"""Build task_12 results folder (reference-style) for the ACVR2B IgDesign CDR redesign run."""
import csv, json, os, shutil

WS = "/home/boltzmann4/.sci/profiles/ab_task_10/workspace"
TASK = "task_12_acvr2b_igdesign_cdr_redesign"
RUN = "run_001_igdesign_hcdr_redesign"
OUT = os.path.join(WS, "results", TASK, RUN)
RAW = os.path.join(OUT, "raw")
STR = os.path.join(OUT, "structures")
for d in (OUT, RAW, STR):
    os.makedirs(d, exist_ok=True)

# ---- Native sequences (correct, from 5ngv_sequences.json) ----
NATIVE_VH = "VQLVQSGAEVKKPGASVKVSCKASGYTFTSSYINWVRQAPGQGLEWMGTINPVSGSTSYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARGGWFDYWGQGTLVTVS"
NATIVE_VL = "SALTQPASVSGSPGQSITISCTGTSSDVGSYNYVNWYQQHPGKAPKLMIYGVSKRPSGVSNRFSGSKSGNTASLTISGLQAEDEADYYCGTFAGGSYYGVFGGGTKLTVLW"
ANTIGEN   = "ETRECIYYNANWELERTNQSGLERCEGEQDKRLHCYASWRNSSGTIELVKKGCWLDDFNCYDRQECVATEENPQVYFCCCEGNFCNERFTHLP"
assert len(NATIVE_VH) == 113 and len(NATIVE_VL) == 111 and len(ANTIGEN) == 93
# CDR positions 0-indexed
P1, P2, P3 = (24,32), (49,57), (95,103)
assert NATIVE_VH[24:32] == "GYTFTSSY" and NATIVE_VH[49:57] == "INPVSGST" and NATIVE_VH[95:103] == "ARGGWFDY"

def build_vh(c1, c2, c3):
    s = list(NATIVE_VH)
    s[24:32] = list(c1); s[49:57] = list(c2); s[95:103] = list(c3)
    return "".join(s)

# ---- 20 candidates: (id, scope, HCDR1, HCDR2, HCDR3, ce_loss_sum) ----
C = [
 ("T12-C001","HCDR3-only","GYTFTSSY","INPVSGST","ARGSYFDY",0.5019),
 ("T12-C002","HCDR3-only","GYTFTSSY","INPVSGST","ARGGYFDY",0.5085),
 ("T12-C003","HCDR3-only","GYTFTSSY","INPVSGST","ARGSDFDY",0.5361),
 ("T12-C004","HCDR3-only","GYTFTSSY","INPVSGST","ARGGDFDY",0.5427),
 ("T12-C005","HCDR3-only","GYTFTSSY","INPVSGST","ARGSAFDY",0.5605),
 ("T12-C006","HCDR3-only","GYTFTSSY","INPVSGST","ARGGAFDY",0.5671),
 ("T12-C007","HCDR3-only","GYTFTSSY","INPVSGST","ARGSYMDY",0.6313),
 ("T12-C008","HCDR3-only","GYTFTSSY","INPVSGST","ARGSEFDY",0.6378),
 ("T12-C009","HCDR3-only","GYTFTSSY","INPVSGST","ARGGYMDY",0.6379),
 ("T12-C010","HCDR3-only","GYTFTSSY","INPVSGST","ARGNYFDY",0.6388),
 ("T12-C011","HCDR123","GYTFTSSY","INPVTGNT","ARGSYFDY",0.9748),
 ("T12-C012","HCDR123","GYTFTSTY","INPVTGNT","ARGSYFDY",0.9906),
 ("T12-C013","HCDR123","GYTFTSSY","INPVTGNT","ARGSDFDY",0.9974),
 ("T12-C014","HCDR123","GYTFTSAY","INPVTGNT","ARGSYFDY",1.0038),
 ("T12-C015","HCDR123","GYTFTSSY","INPVTGNT","ARGSAFDY",1.0249),
 ("T12-C016","HCDR123","GYTFTSAY","INPVTGNT","ARGSDFDY",1.0264),
 ("T12-C017","HCDR123","GYTFTSSY","INPITGNT","ARGSYFDY",1.0365),
 ("T12-C018","HCDR123","GYTFTSTY","INPITGNT","ARGSYFDY",1.0523),
 ("T12-C019","HCDR123","GYTFTSTY","INPVTGNT","ARGGDFDY",1.0558),
 ("T12-C020","HCDR123","GYTFTSSY","INPVTGNT","ARGGAFDY",1.0675),
]
# map T12-Cxxx -> raw id for rmsd lookup
RAWID = {f"T12-C{i:03d}": (f"acvr2b_hcdr3_{i:02d}" if i<=10 else f"acvr2b_hcdr123_{i-10:02d}") for i in range(1,21)}

# ---- scRMSD (precise, from candidate_rmsd.json) ----
rmsd = json.load(open(os.path.join(WS, "scrmsd_preds/candidate_rmsd.json")))
# keys in that file: hcdr3_01..10, hcdr123_01..10 (no hcdr123_03)
def get_rmsd(tid):
    rid = RAWID[tid]
    base = rid.split("_",1)[1]  # hcdr3_01 or hcdr123_01
    return rmsd.get(base)

# reference executed
REF_RMSD = {"HCDR1":0.2347,"HCDR2":0.6304,"HCDR3":0.3705,"HCDR123":0.4434,"Fv_whole":1.2140}

# AAR
AAR = {
 "HCDR3-only":{"HCDR3":{"native":"ARGGWFDY","one_shot":0.875,"best_of_100":0.875,"mean":0.750}},
 "HCDR123":{"HCDR1":{"native":"GYTFTSSY","one_shot":0.750,"best_of_100":1.000,"mean":0.897},
            "HCDR2":{"native":"INPVSGST","one_shot":0.750,"best_of_100":0.875,"mean":0.703},
            "HCDR3":{"native":"ARGGWFDY","one_shot":0.750,"best_of_100":1.000,"mean":0.757}}
}

# published benchmark (native reference, from Bimagrumab-ACVR2B.csv positive control)
PUB = {
 "ABB2":{"HCDR1":0.3593,"HCDR2":0.3204,"HCDR3":0.2988,"HCDR123":0.3271,"Fv":0.4350},
 "ABB3":{"HCDR1":0.3690,"HCDR2":0.6996,"HCDR3":0.8772,"HCDR123":0.6819,"Fv":0.7242},
 "ABB3-LM":{"HCDR1":0.4611,"HCDR2":0.6991,"HCDR3":0.6228,"HCDR123":0.6026,"Fv":0.9211},
 "ESMFold":{"HCDR1":0.4362,"HCDR2":0.7643,"HCDR3":0.5768,"HCDR123":0.6075,"Fv":1.1243},
}

def n_mut(c1,c2,c3):
    n=0
    if c1!="GYTFTSSY": n+=8
    if c2!="INPVSGST": n+=8
    if c3!="ARGGWFDY": n+=8
    return n
def mut_h(c1,c2,c3):
    m=[]
    if c1!="GYTFTSSY": m.append(f"HCDR1 GYTFTSSY->{c1}")
    if c2!="INPVSGST": m.append(f"HCDR2 INPVSGST->{c2}")
    if c3!="ARGGWFDY": m.append(f"HCDR3 ARGGWFDY->{c3}")
    return "; ".join(m)

# ============ candidates.csv ============
with open(os.path.join(OUT,"candidates.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["candidate_id","scope","VH","VL","n_mutations","mut_H","mut_L","design_score","evaluated","structure_predicted"])
    for tid,scope,c1,c2,c3,ce in C:
        vh=build_vh(c1,c2,c3); r=get_rmsd(tid)
        w.writerow([tid,scope,vh,NATIVE_VL,n_mut(c1,c2,c3),mut_h(c1,c2,c3),"",f"{ce:.4f}","yes",("yes" if r else "no")])

# ============ shortlist.csv (ranked by HCDR123 scRMSD) ============
rows=[]
for tid,scope,c1,c2,c3,ce in C:
    r=get_rmsd(tid)
    if r: rows.append((tid,scope,c1,c2,c3,ce,r))
rows.sort(key=lambda x:x[6]["HCDR123"])
with open(os.path.join(OUT,"shortlist.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["rank","candidate_id","scope","n_mutations","mut_H","HCDR1_scRMSD_A","HCDR2_scRMSD_A","HCDR3_scRMSD_A","HCDR123_scRMSD_A","Fv_scRMSD_A","delta_HCDR123_vs_ref_A","ce_loss_sum"])
    for i,(tid,scope,c1,c2,c3,ce,r) in enumerate(rows,1):
        w.writerow([i,tid,scope,n_mut(c1,c2,c3),mut_h(c1,c2,c3),
            f"{r['HCDR1']:.4f}",f"{r['HCDR2']:.4f}",f"{r['HCDR3']:.4f}",f"{r['HCDR123']:.4f}",f"{r['Fv_whole']:.4f}",
            f"{r['HCDR123']-REF_RMSD['HCDR123']:+.4f}",f"{ce:.4f}"])

# ============ metrics.csv (long format) ============
with open(os.path.join(OUT,"metrics.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["candidate_id","metric","value","units","source","protocol"])
    def add(cid,metric,value,units,source,protocol): w.writerow([cid,metric,value,units,source,protocol])
    # reference scRMSD
    for k in ["HCDR1","HCDR2","HCDR3","HCDR123","Fv_whole"]:
        add("REFERENCE",f"scRMSD_{k}",f"{REF_RMSD[k]:.4f}","A","AlphaFold2-Multimer v3 (Boltzmann)","C-alpha, whole-Fv Kabsch onto 5NGV")
    # AAR (native recovery)
    add("REFERENCE","AAR_HCDR3_only_one_shot","0.875","fraction","IgDesign ACVR2B-holdout","per-position identity vs native, 1 sample")
    add("REFERENCE","AAR_HCDR3_only_best_of_100","0.875","fraction","IgDesign ACVR2B-holdout","max over 100 samples")
    for cdr in ["HCDR1","HCDR2","HCDR3"]:
        a=AAR["HCDR123"][cdr]
        add("REFERENCE",f"AAR_{cdr}_one_shot",f"{a['one_shot']:.3f}","fraction","IgDesign ACVR2B-holdout","per-position identity vs native, 1 sample")
        add("REFERENCE",f"AAR_{cdr}_best_of_100",f"{a['best_of_100']:.3f}","fraction","IgDesign ACVR2B-holdout","max over 100 samples")
    # candidates
    for tid,scope,c1,c2,c3,ce in C:
        r=get_rmsd(tid)
        if r:
            for k in ["HCDR1","HCDR2","HCDR3","HCDR123","Fv_whole"]:
                add(tid,f"scRMSD_{k}",f"{r[k]:.4f}","A","AlphaFold2-Multimer v3 (Boltzmann)","C-alpha, whole-Fv Kabsch onto 5NGV")
        add(tid,"ce_loss_sum",f"{ce:.4f}","nats/token","IgDesign ACVR2B-holdout","summed independent CDR cross-entropy")

# ============ benchmark_comparison.csv ============
with open(os.path.join(OUT,"benchmark_comparison.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["record_type","record_id","metric","value","scope","source"])
    for pred,vals in PUB.items():
        for k in ["HCDR1","HCDR2","HCDR3","HCDR123","Fv"]:
            w.writerow(["published_reference",pred,f"scRMSD_{k}",f"{vals[k]:.4f}","native Bimagrumab reference",f"IgDesign released benchmark CSV ({pred})"])
    for k in ["HCDR1","HCDR2","HCDR3","HCDR123","Fv_whole"]:
        w.writerow(["executed","REFERENCE",f"scRMSD_{k}",f"{REF_RMSD[k]:.4f}","native Bimagrumab reference","AlphaFold2-Multimer v3 (this run)"])
    for tid,scope,c1,c2,c3,ce in C:
        r=get_rmsd(tid)
        if r:
            for k in ["HCDR1","HCDR2","HCDR3","HCDR123","Fv_whole"]:
                w.writerow(["executed",tid,f"scRMSD_{k}",f"{r[k]:.4f}","designed candidate","AlphaFold2-Multimer v3 (this run)"])
    w.writerow(["comparison_verdict","published_vs_executed","protocol_compatibility","not_comparable","different structure predictors (ABB2/ABB3/ABB3-LM/ESMFold vs AF2-Multimer v3)","side-by-side only; like-for-like is candidate vs native within executed predictor"])

# ============ sequences.fasta ============
with open(os.path.join(OUT,"sequences.fasta"),"w") as f:
    f.write(f">REFERENCE_VH|{TASK}|{RUN}|bimagrumab|source=PDB_5NGV\n{NATIVE_VH}\n")
    f.write(f">REFERENCE_VL|{TASK}|{RUN}|bimagrumab|source=PDB_5NGV\n{NATIVE_VL}\n")
    for tid,scope,c1,c2,c3,ce in C:
        vh=build_vh(c1,c2,c3); r=get_rmsd(tid)
        st="evaluated" if r else "no_structure"
        f.write(f">{tid}_VH|{TASK}|{RUN}|igdesign_{scope}|status={st}\n{vh}\n")
        f.write(f">{tid}_VL|{TASK}|{RUN}|bimagrumab|status=native_preserved\n{NATIVE_VL}\n")

# ============ run.json ============
run={
 "schema_version":"compact-run-config-v2",
 "task_id":TASK,"run_id":RUN,"workflow_id":"wf_igdesign_backbone_conditioned_cdr","status":"complete",
 "paths":{"src":f"src/{TASK}/{RUN}","results":f"results/{TASK}/{RUN}"},
 "preparation":{"objective":"Reference-backbone-conditioned heavy-chain CDR redesign of Bimagrumab Fv against human ACVR2B","inputs":"@src/inputs","inventory":"@src/inputs/execution_records/run_files.csv"},
 "stages":[
  {"stage_id":"S0_prep","purpose":"verify 5NGV VH/VL/ACVR2B sequences, CDR numbering, antigen identity","status":"complete",
   "tools":[{"tool":"stage0_fetch_verify.py","source":"open_source","records":["C01"],
     "inputs":{"pdb":"inputs/5ngv.pdb (chains A=antigen, H=VH, L=VL)"},
     "outputs":{"outputs":["inputs/reference_sequences.json","inputs/cdr_positions.json"]},
     "states":{"complete":1}}]},
  {"stage_id":"S1_design","purpose":"IgDesign reference-backbone-conditioned CDR design, two scopes","status":"complete","dependencies":["S0_prep"],
   "tools":[{"tool":"IgDesign","source":"open_source","records":["C02","C03"],
     "inputs":{"by_record":{"C02":{"scope":"HCDR3-only","condition":"VH backbone + VL + ACVR2B"},"C03":{"scope":"HCDR123","condition":"VH backbone + VL + ACVR2B"}}},
     "parameters":{"by_record":{"C02":{"samples":100,"temperature":0.5,"seed":0},"C03":{"samples":100,"temperature":0.5,"seed":0}}},
     "outputs":{"recorded_outputs":{"by_record":{"C02":{"outputs":["raw/igdesign/acvr2b_hcdr3_results.csv (100 samples, 44 unique)"]},"C03":{"outputs":["raw/igdesign/acvr2b_hcdr123_results.csv (100 samples, 89 unique)"]}}},"saved_artifacts":["@results/raw/igdesign"]},
     "states":{"complete":2}}]},
  {"stage_id":"S2_verify","purpose":"edit-mask verification, dedupe, native-recovery AAR","status":"complete","dependencies":["S1_design"],
   "tools":[{"tool":"stage2_verify_mask.py","source":"open_source","records":["C04"],
     "inputs":{"input":"raw/igdesign/*.csv"},
     "outputs":{"outputs":["raw/igdesign/aar.json"]},
     "states":{"complete":1}}]},
  {"stage_id":"S3_structure","purpose":"matched AF2-Multimer v3 prediction: reference + 20 candidates","status":"complete","dependencies":["S2_verify"],
   "tools":[{"tool":"Multimer_Structure_Prediction","source":"boltzmann","records":["C05"],
     "inputs":{"Protein_Sequences":"VH+VL multimer per candidate"},
     "parameters":{"model":"AlphaFold2-Multimer v3 / ColabFold","rank":"rank_001"},
     "outputs":{"recorded_outputs":{"by_record":{"C05":{"outputs":["structures/ (19 of 20 candidates + reference)"]}}},"saved_artifacts":["@results/structures"]},
     "states":{"complete":19,"unknown_state":1}}]},
  {"stage_id":"S4_evaluation","purpose":"C-alpha scRMSD vs 5NGV (whole-Fv Kabsch)","status":"complete","dependencies":["S3_structure"],
   "tools":[{"tool":"stage4_compute_rmsd.py","source":"open_source","records":["C06"],
     "inputs":{"inputs":"structures/ + 5ngv.pdb"},
     "parameters":{"atoms":"C-alpha","alignment":"whole-Fv (224 CA) Kabsch onto 5NGV","regions":"HCDR1/2/3/123 (VH), Fv_whole (VH+VL)"},
     "outputs":{"outputs":["raw/evaluation/candidate_rmsd.json"]},
     "states":{"complete":1}}]},
  {"stage_id":"S5_evaluation","purpose":"consolidated metrics + artifacts","status":"complete","dependencies":["S4_evaluation"],
   "tools":[{"tool":"stage5_artifacts.py","source":"open_source","records":["C07"],
     "inputs":{"inputs":"candidate_rmsd.json + aar.json + igdesign CSVs"},
     "parameters":{"rank_key":"executed HCDR123 scRMSD (lower=better)"},
     "outputs":{"outputs":["candidates.csv (20)","shortlist.csv (19 ranked)","sequences.fasta (42)","metrics.csv","benchmark_comparison.csv","report.md"]},
     "states":{"complete":1}}]}
 ],
 "outcome":{"workflows_designed":1,"selected":1,"executed":1,"generated":200,"unique_candidates":133,"shortlist":20,"evaluated":19,"unevaluated":114,"top_shortlist":"T12-C008 (HCDR3-only, HCDR123 scRMSD 0.3803 A)","integrative_lead":"T12-C011 (HCDR123, HCDR123 scRMSD 0.3879 A)"},
 "evidence":{"tool_details":"@src/inputs/execution_records/tool_details.json","activity_log":"@src/logs/agent_scientist_log.md","original_config_sha256":"5775fdfa2b23802aa4a295e7b98d3bbd52f4bd83440e33a3c9a0fca723dfcae9"},
 "artifact_links":{"report_md":"@results/report.md","candidates_csv":"@results/candidates.csv","shortlist_csv":"@results/shortlist.csv","metrics_csv":"@results/metrics.csv","benchmark_comparison_csv":"@results/benchmark_comparison.csv","sequences_fasta":"@results/sequences.fasta","structures":"@results/structures","raw":"@results/raw","run_json":"@results/run.json"},
 "lineage":{"parent":None,"derived_from":"PDB 5NGV (Bimagrumab Fv + ACVR2B fragment)","historical_components":[]}
}
with open(os.path.join(OUT,"run.json"),"w") as f: json.dump(run,f,indent=2)

# ============ raw/ ============
shutil.copy(os.path.join(WS,"igdesign_repo/output/acvr2b_hcdr3_results.csv"), os.path.join(RAW,"acvr2b_hcdr3_results.csv"))
shutil.copy(os.path.join(WS,"igdesign_repo/output/acvr2b_hcdr123_results.csv"), os.path.join(RAW,"acvr2b_hcdr123_results.csv"))
shutil.copy(os.path.join(WS,"scrmsd_preds/candidate_rmsd.json"), os.path.join(RAW,"candidate_rmsd.json"))
shutil.copy(os.path.join(WS,"scrmsd_preds/job_ledger.json"), os.path.join(RAW,"job_ledger.json"))
shutil.copy(os.path.join(WS,"acvr2b_results/metrics.json"), os.path.join(RAW,"metrics_source.json"))

# ============ structures/ ============
pdbs = os.path.join(WS,"scrmsd_preds/pdbs")
if os.path.isdir(pdbs):
    for fn in os.listdir(pdbs):
        if fn.endswith(".pdb"): shutil.copy(os.path.join(pdbs,fn), os.path.join(STR,fn))

print("DONE. Files in", OUT)
for root,dirs,files in os.walk(OUT):
    for fn in sorted(files):
        p=os.path.join(root,fn); print(" ", os.path.relpath(p,OUT), os.path.getsize(p))
