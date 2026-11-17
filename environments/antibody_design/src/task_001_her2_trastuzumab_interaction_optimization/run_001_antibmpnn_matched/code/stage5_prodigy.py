"""Stage 5: Prodigy binding-affinity on Boltz2 structures (reference + 8 candidates).

Input per job: the job's pdbs_outputs.zip (2 complex PDBs: HER2+VH, HER2+VL).
chain_list=[] -> automatic pairwise analysis of uppercase chains (A/B per record).
State file inputs/prodigy_state.json tracks upload path, doc_id, status per candidate
so the script is resumable without duplicate submissions.
"""
import json
import os
import time
import urllib.request
import urllib.error

KEY = [l.split("=", 1)[1].strip() for l in open("/home/boltzmann10/.sci/profiles/monoclonal_antibody_design_tools/.env") if l.startswith("BOLTZMANN_API_KEY")][0]
INP = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs"
STATE_F = INP + "/prodigy_state.json"
BASE = "https://nodeapis.boltzmann.co"

def api(path, body=None, method=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
                                 method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()) if r.length else {}
    except urllib.error.HTTPError as e:
        try:
            return {"http_error": e.code, "body": e.read().decode()[:300]}
        except Exception:
            return {"http_error": e.code}

state = json.load(open(STATE_F)) if os.path.exists(STATE_F) else {}

jobs = {"REFERENCE": INP + "/boltz2_reference/pdbs_outputs.zip"}
for cid in sorted(os.listdir(INP + "/boltz2_candidates")):
    p = INP + "/boltz2_candidates/" + cid + "/pdbs_outputs.zip"
    if os.path.exists(p):
        jobs[cid] = p

# 1) upload + submit missing
for cid, zpath in jobs.items():
    st = state.setdefault(cid, {})
    if not st.get("folder"):
        boundary = "----sciboundary7MA4YWxkTrZu0gW"
        fn = os.path.basename(zpath)
        with open(zpath, "rb") as f:
            payload = f.read()
        body = (("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: application/zip\r\n\r\n" % (boundary, fn)).encode() + payload + ("\r\n--%s--\r\n" % boundary).encode())
        req = urllib.request.Request(BASE + "/api/fileUpload", data=body,
                                     headers={"Authorization": "Bearer " + KEY, "Content-Type": "multipart/form-data; boundary=" + boundary})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            st["folder"] = d["fileDetails"]["folderPath"]
            print(cid, "uploaded ->", st["folder"])
        except urllib.error.HTTPError as e:
            print(cid, "UPLOAD FAIL", e.code, e.read().decode()[:200]); continue
        json.dump(state, open(STATE_F, "w"), indent=2)
    if not st.get("doc") and st.get("folder"):
        d = api("/api/submit-job", {"experimentData": {"input_path": st["folder"] + "/" + os.path.basename(jobs[cid]), "chain_list": []},
                                    "job_name": "Prodigy", "experimentName": "Prodigy task001 %s" % cid})
        if d.get("http_error"):
            print(cid, "SUBMIT FAIL", d); continue
        st["doc"] = d.get("docId") or d.get("doc_id")
        st["submit_raw"] = {k: v for k, v in d.items() if k in ("status", "message")}
        print(cid, "submitted ->", st["doc"])
        json.dump(state, open(STATE_F, "w"), indent=2)

# 2) poll all
def all_terminal():
    return all(state[c].get("final") for c in state)

for round in range(80):
    if all_terminal():
        break
    for cid, st in state.items():
        if st.get("final") or not st.get("doc"):
            continue
        d = api("/api/result", {"docId": st["doc"], "job_name": "Prodigy"}, method="GET")
        if d.get("status") == "Success":
            st["final"] = "Success"
            dest = os.path.join(INP, "prodigy", cid)
            os.makedirs(dest, exist_ok=True)
            od = d.get("OutputData", {})
            for art_name, art in (od.items() if isinstance(od, dict) else []):
                if isinstance(art, dict) and art.get("download_link"):
                    fn = os.path.join(dest, os.path.basename(art["path"]))
                    urllib.request.urlretrieve(art["download_link"][0], fn)
                    print("saved", cid, os.path.basename(fn), os.path.getsize(fn))
            st["time_taken"] = d.get("time_taken")
            print(round, cid, "Success")
        elif d.get("http_error") and str(d.get("body", "")).find("running") < 0 and d.get("http_error") != 404:
            print(round, cid, "ERR", str(d)[:200]); st["final"] = "error:" + str(d.get("http_error"))
        elif d.get("status") not in (None, "running") and d.get("status") != "Success":
            print(round, cid, "status", d.get("status")); st["final"] = d.get("status")
    json.dump(state, open(STATE_F, "w"), indent=2)
    if not all_terminal():
        time.sleep(45)

print("terminal states:", {c: s.get("final") for c, s in state.items()})
