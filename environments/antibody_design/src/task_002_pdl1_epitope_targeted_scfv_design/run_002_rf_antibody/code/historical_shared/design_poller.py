#!/usr/bin/env python3
"""Long poller for the task002 epitope_abgen design job.
Downloads the results archive when output appears.
Output contract per plugin contract docs: OutputData.datainfo.output_path
(fallbacks: zip_path.download_link or any list of signed URLs)."""
import re, json, time, os, sys, urllib.request, urllib.error
key = re.search(r'[A-Za-z0-9_-]{64}', open('/home/boltzmann10/.sci/profiles/antibody_design_monoclonal/.env').read()).group(0)
DOC, JOB = '6af8443c9850a93adf67ca50', 'epitope_abgen'
OUT = '/home/boltzmann10/.sci/cache/scratch/task002/epitope_abgen_raw'

def fetch():
    req = urllib.request.Request('https://nodeapis.boltzmann.co/api/result',
        data=json.dumps({'docId': DOC, 'job_name': JOB}).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='GET')
    try:
        return json.load(urllib.request.urlopen(req, timeout=45))
    except urllib.error.HTTPError as e:
        return {'err': e.code}

def find_links(od):
    """Yield (label, url) for any download links in OutputData."""
    if not isinstance(od, dict):
        return
    di = od.get('datainfo')
    if isinstance(di, dict):
        op = di.get('output_path')
        if isinstance(op, str) and op.startswith('http'):
            yield ('datainfo.output_path', op)
        elif isinstance(op, dict):
            l = op.get('download_link', op.get('link'))
            for x in (l if isinstance(l, list) else [l]):
                if isinstance(x, str) and x.startswith('http'):
                    yield ('datainfo.output_path', x)
    zp = od.get('zip_path')
    if isinstance(zp, dict):
        l = zp.get('download_link', zp.get('link'))
        for x in (l if isinstance(l, list) else [l]):
            if isinstance(x, str) and x.startswith('http'):
                yield ('zip_path', x)
    for k, v in od.items():
        if isinstance(v, str) and v.startswith('http') and ('storage' in v or 'zip' in v or 'download' in v):
            yield (k, v)

deadline = time.time() + 6*3600
n = 0
while time.time() < deadline:
    n += 1
    r = fetch()
    if isinstance(r, dict) and 'err' not in r:
        print(f'DESIGN OUTPUT READY after {n} polls', flush=True)
        os.makedirs(OUT, exist_ok=True)
        json.dump(r, open(f'{OUT}/result.json', 'w'), indent=1)
        od = r.get('OutputData') or {}
        links = list(find_links(od))
        print('OutputData keys:', list(od.keys()) if isinstance(od, dict) else str(od)[:300], flush=True)
        ok = False
        for label, url in links:
            try:
                req2 = urllib.request.Request(url)
                with urllib.request.urlopen(req2, timeout=600) as resp:
                    data = resp.read()
                fn = f'{OUT}/{label.replace(".", "_")}_{len(os.listdir(OUT))}.bin'
                open(fn, 'wb').write(data)
                # sniff content
                head = data[:4]
                ext = '.zip' if head[:2] == b'PK' else ('.csv' if b',' in data[:2000] else '.bin')
                final = fn.rsplit('.', 1)[0] + ext
                os.rename(fn, final)
                print(f'downloaded {label}: {len(data)} bytes -> {final}', flush=True)
                ok = True
            except Exception as e:
                print(f'download {label} failed: {e}', flush=True)
        if not ok:
            json.dump(od, open(f'{OUT}/outputdata_shape.json', 'w'), indent=1)
            print('no direct links; full OutputData saved to outputdata_shape.json', flush=True)
        sys.exit(0)
    if n % 6 == 0:
        print(f'{n} polls ({(n*300)//60} min), still no output ({r.get("err")})', flush=True)
    time.sleep(300)
print('TIMEOUT: no output after 6 h', flush=True)
sys.exit(2)
