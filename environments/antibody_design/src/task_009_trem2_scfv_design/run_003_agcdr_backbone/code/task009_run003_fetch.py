#!/usr/bin/env python
"""Fetch + echo-verify task009 run_003 Boltz2 top-4 (local-AntiBMPNN candidates)."""
import json, os, time, urllib.request, zipfile

KEY = None
for line in open("/home/boltzmann10/.sci/.env"):
    if line.startswith("BOLTZMANN_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
assert KEY

DOCS = {"cand027": "6afb49567fc9c7f56da82a7c", "cand032": "6afb4961ef7b50fcff15c07f",
        "cand036": "6afb496c7426d09ad749d7c5", "cand006": "6afb497775ff2e0d02e6ee18"}
g = json.load(open("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw/native_generation/outputs/gate_report.json"))
INTENDED = {f"cand{t['idx']:03d}": t["scfv245"] for t in g["top4"]}
RAW = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw"
three2one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

def api(doc):
    req = urllib.request.Request("https://nodeapis.boltzmann.co/api/result",
        data=json.dumps({"docId": doc, "job_name": "Boltz2"}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def get(url, dst):
    with urllib.request.urlopen(url, timeout=180) as r, open(dst, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)

pending = dict(DOCS); metrics = {}
for attempt in range(40):
    for cand, doc in list(pending.items()):
        try:
            res = api(doc)
        except Exception as e:
            print(cand, "api error", e); continue
        st = res.get("status")
        if st == "Success":
            od = res.get("OutputData") or {}
            json.dump(res, open(f"{RAW}/{cand}_boltz2_result.json", "w"), indent=1)
            for field, name in (("zip_path", f"{cand}_outputs.zip"), ("pdb_zip", f"{cand}_pdbs.zip")):
                link = od.get(field, {}).get("download_link")
                if isinstance(link, list): link = link[0] if link else None
                if link:
                    try: get(link, f"{RAW}/{name}"); print(cand, name, "ok")
                    except Exception as e: print(cand, name, "dl fail", e)
            m = {}
            try:
                z = zipfile.ZipFile(f"{RAW}/{cand}_outputs.zip")
                conf = [n for n in z.namelist() if "confidence" in n and n.endswith(".json")]
                d = json.loads(z.read(conf[0]))
                m = {"iptm": d.get("iptm"), "ptm": d.get("ptm")}
                pl = d.get("plddt")
                if isinstance(pl, list): m["mean_plddt"] = sum(pl)/len(pl)
            except Exception as e:
                m["metrics_error"] = str(e)[:120]
            try:
                z = zipfile.ZipFile(f"{RAW}/{cand}_pdbs.zip")
                pl2 = [n for n in z.namelist() if n.endswith(".pdb")][0]
                lines = z.read(pl2).decode().splitlines()
                seqs = {}
                for ln in lines:
                    if ln.startswith("ATOM") and ln[12:16].strip() == "CA":
                        seqs.setdefault(ln[21], "")
                        seqs[ln[21]] += three2one.get(ln[17:20].strip(), "X")
                scfv = max(seqs.values(), key=len)
                m["echo_exact_match"] = scfv == INTENDED[cand]
                if m["echo_exact_match"]:
                    os.makedirs(f"{RAW}/../structures/{cand}", exist_ok=True)
                    open(f"{RAW}/../structures/{cand}/{cand}_scFv_TREM2_boltz2.pdb", "w").write("\n".join(lines) + "\n")
            except Exception as e:
                m["echo_error"] = str(e)[:120]
            metrics[cand] = {"doc_id": doc, **m}
            print(cand, metrics[cand])
            del pending[cand]
        elif st in ("Failed", "Error"):
            metrics[cand] = {"doc_id": doc, "status": st, "raw": str(res)[:300]}
            json.dump(res, open(f"{RAW}/{cand}_boltz2_result.json", "w"), indent=1)
            print(cand, "TERMINAL", st); del pending[cand]
        else:
            print(cand, "status", st)
    if not pending: break
    time.sleep(60)
json.dump(metrics, open(f"{RAW}/boltz2_metrics_and_echo.json", "w"), indent=1)
print("DONE pending:", list(pending) or "none")
