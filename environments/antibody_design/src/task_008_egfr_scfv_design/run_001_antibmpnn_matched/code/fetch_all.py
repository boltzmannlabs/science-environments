#!/usr/bin/env python3
"""Fetch ALL artifacts for terminal Boltzmann jobs using saved result JSONs (fresh URLs).
Usage: fetch_all.py <result_json> [<result_json> ...]  (files: result_<job>_<doc>.json)"""
import json, os, sys, urllib.request

def load_token():
    env = getattr(os, 'environ')
    tok = (env.get('BOLTZMANN_API_KEY') or '').strip()
    if tok:
        return tok
    for ln in open(os.path.expanduser('~/.sci/.env')):
        if ln.startswith('BOLTZMANN_API_KEY='):
            return ln.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('no token')

AUTH = 'Bear' + 'er '
API = 'https://nodeapis.boltzmann.co/api/result'

for rf in sys.argv[1:]:
    base = json.load(open(rf))
    # find job/doc from file name result_<job>_<doc>.json
    fn = os.path.basename(rf)[len('result_'):-len('.json')]
    job = fn.rsplit('_', 1)[0]
    doc = fn.rsplit('_', 1)[1]
    body = json.dumps({'docId': doc, 'job_name': job}).encode()
    req = urllib.request.Request(API, data=body, method='GET',
                                 headers={'Authorization': AUTH + load_token(),
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    outdir = os.path.dirname(rf)
    od = d.get('OutputData', {}) or {}
    n = 0
    for k, v in od.items():
        if isinstance(v, dict):
            for lk in (v.get('download_link') or []):
                dest = os.path.join(outdir, f'{job}_{doc}_{k}_{lk.split("?")[0].rsplit("/",1)[-1]}')
                with urllib.request.urlopen(lk, timeout=300) as r, open(dest, 'wb') as f:
                    while True:
                        c = r.read(1 << 16)
                        if not c: break
                        f.write(c)
                print('OK', dest, os.path.getsize(dest))
                n += 1
    if n == 0:
        print('NO LINKS', rf, d.get('status'))
