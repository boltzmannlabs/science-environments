#!/usr/bin/env python3
"""Poll a Boltzmann job via NodeAPI; download outputs.zip in the same process.
Usage: poll_and_fetch.py <doc_id> <job_name> <out_dir>"""
import json
import os
import sys
import urllib.request

KEY = None
for cand in ['/home/boltzmann10/.sci/profiles/monoclonal_antibody_design_tools/.env',
             '/home/boltzmann10/.sci/profiles/antibody_design_monoclonal/.env']:
    if os.path.exists(cand):
        txt = open(cand).read()
        import re
        m = re.search(r'[A-Za-z0-9_-]{64}', txt)
        if m:
            KEY = m.group(0)
            break
assert KEY, 'no API key found'

doc_id, job_name, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
req = urllib.request.Request(
    'https://nodeapis.boltzmann.co/api/result',
    data=json.dumps({'docId': doc_id, 'job_name': job_name}).encode(),
    headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
    method='GET')
import urllib.error
try:
    r = json.load(urllib.request.urlopen(req, timeout=60))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read()[:200]); sys.exit(1)
status = r.get('status')
print('status:', status)
od = r.get('OutputData')
os.makedirs(out_dir, exist_ok=True)
json.dump(r, open(f'{out_dir}/result.json', 'w'), indent=1)
if isinstance(od, dict):
    print('OutputData keys:', list(od.keys()))
    zp = od.get('zip_path') or od.get('outputs') or od.get('output_zip')
    if isinstance(zp, dict):
        link = zp.get('download_link')
        if isinstance(link, list):
            link = link[0] if link else None
        if link:
            req2 = urllib.request.Request(link)
            with urllib.request.urlopen(req2, timeout=300) as resp, \
                    open(f'{out_dir}/outputs.zip', 'wb') as out:
                out.write(resp.read())
            print('downloaded', os.path.getsize(f'{out_dir}/outputs.zip'), 'bytes ->',
                  f'{out_dir}/outputs.zip')
    else:
        for k, v in od.items():
            print(' ', k, ':', str(v)[:120])
else:
    print('OutputData:', str(od)[:300])
