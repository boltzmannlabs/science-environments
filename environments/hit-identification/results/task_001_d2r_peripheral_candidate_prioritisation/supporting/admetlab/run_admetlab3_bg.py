import pandas as pd
import urllib.request, json, time, os

BASE = 'environments/hit-identification/results/run_rsi'
PLAT = f'{BASE}/platform'
OUT = f'{PLAT}/admetlab3_bbb_results.jsonl'
LOG = f'{PLAT}/admetlab3_bbb_log.txt'
URL = 'https://admetlab3.scbdd.com/api/single/admet'

df = pd.read_csv(f'{PLAT}/integrated_raw.csv')
mols = list(zip(df['compound_id'].astype(int), df['canonical_smiles']))

# Resume: load already-done
done = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        for line in f:
            try:
                rec = json.loads(line)
                done[rec['compound_id']] = rec
            except: pass

out_f = open(OUT, 'a')
log_f = open(LOG, 'a')
def log(msg):
    log_f.write(f'{time.strftime("%H:%M:%S")} {msg}\n'); log_f.flush()

def call(smi, max_attempts=10):
    h = {'User-Agent':'Mozilla/5.0', 'Content-Type':'application/json'}
    for a in range(max_attempts):
        try:
            req = urllib.request.Request(URL, data=json.dumps({'SMILES':smi}).encode(), headers=h, method='POST')
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < max_attempts-1:
                time.sleep(12*(a+1)); continue
            return {'http_error': e.code}
        except Exception as e:
            if a < max_attempts-1: time.sleep(8); continue
            return {'error': str(e)}
    return {'error':'max_attempts'}

n_done = len(done)
log(f'start: {len(mols)} total, {n_done} already done')
for i,(cid, smi) in enumerate(mols):
    if cid in done: continue
    resp = call(smi)
    rec = {'compound_id': int(cid), 'smiles': smi, 'response': resp}
    out_f.write(json.dumps(rec)+'\n'); out_f.flush()
    done[cid] = rec
    ok = resp.get('status')=='success'
    log(f'[{i+1}/{len(mols)}] cid={cid} {"OK" if ok else "FAIL:"+str(resp.get("error",resp.get("http_error")))}')
    # small base delay
    time.sleep(6)

log(f'complete: {len(done)} done')
out_f.close(); log_f.close()
