"""Stage 3: build Boltz2 payloads for reference + top-8 candidates (matched conditions).

Contract: Boltz2, Protein_Sequences = [HER2_construct, VH, VL] (first-versus-rest pairing).
Same HER2 construct (607-aa SEQRES of 1N8Z chain C) and identical settings for the
reference job and every candidate job -> matched conditions.
Writes inputs/boltz2_payloads.json; the actual submissions are made through the
boltzmann_submit tool call-by-call with payload N from this file.
"""
import json

INP = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs"

ref = json.load(open(f"{INP}/reference_sequences.json"))
HER2 = ref["HER2_construct_seqres_607aa"]
cands = json.load(open(f"{INP}/candidates.json"))["candidates"]

payloads = [{"candidate_id": "REFERENCE", "VH": ref["VH"], "VL": ref["VL"]}]
for c in cands[:8]:
    payloads.append({"candidate_id": c["candidate_id"], "VH": c["VH"], "VL": c["VL"], "design_score": c["score"]})

out = []
for p in payloads:
    out.append({
        "candidate_id": p["candidate_id"],
        "job_name": "Boltz2",
        "experiment_data": {"Protein_Sequences": [HER2, p["VH"], p["VL"]], "DNA_Sequences": [], "RNA_Sequences": [], "SMILES": []},
        "VH": p["VH"], "VL": p["VL"],
    })

with open(f"{INP}/boltz2_payloads.json", "w") as f:
    json.dump(out, f, indent=2)
print("payloads written:", len(out))
for p in out:
    print(p["candidate_id"], len(p["experiment_data"]["Protein_Sequences"][0]), len(p["VH"]), len(p["VL"]))
