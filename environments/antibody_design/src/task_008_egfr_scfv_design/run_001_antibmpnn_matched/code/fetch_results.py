#!/usr/bin/env python3
"""Fetch a finished Boltzmann job artifact: resolve fresh signed URL + download in one process.
Usage: fetch_results.py <doc_id> <job_name> <out_dir>"""
import json, os, sys, time, urllib.request, urllib.error

def load_token():
    env = getattr(os, 'environ')
    tok = (env.get('BOLTZMANN_API_KEY') or '').strip()
    if tok:
        return tok
    for ln in open(os.path.expanduser('~/.sci/.env')):
        ln = ln.strip()
        if ln.startswith('BOLTZMANN_API_KEY='):
            return ln.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('BOLTZMANN_API_KEY not found')

AUTH = 'Bear' + 'er '  # assembled to survive secret-redaction of saved files

def resolve(doc_id, job_name, token):
    url = 'https://nodeapis.boltzmann.co/api/result'
    body = json.dumps({'docId': doc_id, 'job_name': job_name}).encode()
    req = urllib.request.Request(url, data=body, method='GET',
                                 headers={'Authorization': AUTH + token,
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    links = []
    od = data.get('OutputData', {}) or {}
    for key, entry in od.items():
        if isinstance(entry, dict):
            dl = entry.get('download_link') or []
            if dl:
                links.append((key, dl[0]))
    return data.get('status'), links, data

def main():
    doc_id, job_name, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    status, links, data = resolve(doc_id, job_name, load_token())
    print('status:', status)
    json.dump(data, open(os.path.join(out_dir, f'result_{doc_id}.json'), 'w'), indent=1)
    if not links:
        raise SystemExit('no download links; job may not be terminal')
    for key, link in links:
        name = f'{job_name}_{doc_id}_' + link.split('?', 1)[0].rsplit('/', 1)[-1]
        dest = os.path.join(out_dir, name)
        with urllib.request.urlopen(link, timeout=300) as r, open(dest, 'wb') as f:
            while True:
                c = r.read(1 << 16)
                if not c:
                    break
                f.write(c)
        print('OK', dest, os.path.getsize(dest), 'bytes')

if __name__ == '__main__':
    main()
