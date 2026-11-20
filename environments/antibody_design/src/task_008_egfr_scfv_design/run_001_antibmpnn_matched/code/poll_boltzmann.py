#!/usr/bin/env python3
"""Detached poller: watch pending Boltzmann jobs, download artifacts on completion.
Writes poller_state.json + poller.log in the output dir. Hard cap 6h total.
Usage: poll_boltzmann.py <out_dir> <job_name:doc_id> [...]"""
import json, os, sys, time, urllib.request

OUT = sys.argv[1]
JOBS = [tuple(x.split(':', 1)) for x in sys.argv[2:]]
os.makedirs(OUT, exist_ok=True)
STATE = os.path.join(OUT, 'poller_state.json')
LOG = os.path.join(OUT, 'poller.log')
HARD_CAP_S = 6 * 3600
POLL_S = 120

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")} {msg}\n')

def load_token():
    env = getattr(os, 'environ')
    tok = (env.get('BOLTZMANN_API_KEY') or '').strip()
    if tok:
        return tok
    for ln in open(os.path.expanduser('~/.sci/.env')):
        ln = ln.strip()
        if ln.startswith('BOLTZMANN_API_KEY='):
            return ln.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('no token')

AUTH = 'Bear' + 'er '

def result(job_name, doc_id, token):
    url = 'https://nodeapis.boltzmann.co/api/result'
    body = json.dumps({'docId': doc_id, 'job_name': job_name}).encode()
    req = urllib.request.Request(url, data=body, method='GET',
                                 headers={'Authorization': AUTH + token,
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

def dl(link, dest):
    with urllib.request.urlopen(link, timeout=600) as r, open(dest, 'wb') as f:
        while True:
            c = r.read(1 << 16)
            if not c:
                break
            f.write(c)

state = {f'{j}:{d}': 'pending' for j, d in JOBS}
if os.path.exists(STATE):
    try:
        state = json.load(open(STATE))
    except Exception:
        pass
log(f'poller start; {len(JOBS)} jobs: {[f"{j}:{d}" for j, d in JOBS]}')
t0 = time.time()
token = load_token()
while time.time() - t0 < HARD_CAP_S:
    for j, d in JOBS:
        key = f'{j}:{d}'
        if state.get(key) not in (None, 'pending'):
            continue
        try:
            data = result(j, d, token)
            st = data.get('status')
            od = data.get('OutputData', {}) or {}
            links = []
            for k, entry in od.items():
                if isinstance(entry, dict):
                    for lk in (entry.get('download_link') or []):
                        links.append(lk)
            if st == 'Success' and links:
                dest = os.path.join(OUT, f'{j}_{d}.zip')
                dl(links[0], dest)
                json.dump(data, open(os.path.join(OUT, f'result_{j}_{d}.json'), 'w'), indent=1)
                state[key] = f'downloaded:{os.path.basename(dest)}'
                log(f'{key} SUCCESS downloaded {os.path.getsize(dest)} bytes')
            elif st in ('Failed', 'Error', 'failed', 'error'):
                json.dump(data, open(os.path.join(OUT, f'result_{j}_{d}.json'), 'w'), indent=1)
                state[key] = f'failed'
                log(f'{key} FAILED: {str(data)[:300]}')
            else:
                log(f'{key} running ({st})')
        except Exception as e:
            log(f'{key} poll error: {e}')
        json.dump(state, open(STATE, 'w'), indent=1)
    if all(v != 'pending' for v in state.values()):
        log('all jobs terminal')
        break
    time.sleep(POLL_S)
log('poller exit')
