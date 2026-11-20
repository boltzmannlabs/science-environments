#!/usr/bin/env python
"""Submit Boltz2 for task009 run_003 local-AntiBMPNN top-4 — programmatic payloads."""
import json, time, urllib.request

KEY = None
for line in open("/home/boltzmann10/.sci/.env"):
    if line.startswith("BOLTZMANN_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
assert KEY

TREM2 = "TGHNTTVFQGVAGQSLQVSCPYDSMKHWGRRKAWCRQLGEKGPCQRVVSTHNLWLLSFLRRWNGSTAITDDTLGGTLTITLRNLQPHDAGLYQCQSLHGSEADTLRKVLVEVLADPLGTKHHHHHH"
assert len(TREM2) == 126

g = json.load(open("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw/native_generation/outputs/gate_report.json"))
RECS = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw/boltz2_submission_records.json"

def submit(experiment_name, seqs):
    body = json.dumps({"experimentData": {"experiment_name": experiment_name, "Protein_Sequences": seqs},
                       "job_name": "Boltz2", "experiment_name": experiment_name}).encode()
    req = urllib.request.Request("https://nodeapis.boltzmann.co/api/submit-job", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

records = []
for t in g["top4"]:
    cand = f"cand{t['idx']:03d}"
    scfv = t["scfv245"]
    assert len(scfv) == 245 and scfv.startswith("SM")
    name = f"task009_trem2_agcdr_antibmpnn_{cand}_boltz2"
    res = submit(name, [TREM2, scfv])
    records.append({"cand": cand, "experiment": name, "doc_id": res.get("docId"),
                    "status": (res.get("apiResponse") or {}).get("status"), "full": res})
    print(cand, "->", res.get("docId"), (res.get("apiResponse") or {}).get("status"))
    time.sleep(5)
json.dump(records, open(RECS, "w"), indent=1)
print("records ->", RECS)
