#!/usr/bin/env python3
"""Submit exact frozen variants through the documented public DDGun form, once.
No Boltzmann API or credential access. Never retries a POST.
"""
import datetime, hashlib, html.parser, json, pathlib, sys, time, urllib.request, urllib.error

W = pathlib.Path(__file__).resolve().parents[1]
class Meta(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.refresh = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.refresh.append(a.get('content', ''))

def main():
    key = sys.argv[1]
    if key not in ['RML_WT', 'LEH_WT']: raise ValueError(key)
    ip = W/'inputs'/f'ddgun_{key}.json'
    inp = json.loads(ip.read_text())
    seq = inp['payload']['seqs']
    if hashlib.sha256(seq.encode()).hexdigest() != inp['parent_sha256']: raise ValueError('parent hash')
    for v in inp['variants']:
        s = list(seq)
        for m in v['mutation'].split(','):
            p = int(m[1:-1])
            if s[p-1] != m[0]: raise ValueError(m)
            s[p-1] = m[-1]
        if ''.join(s) != v['sequence']: raise ValueError(v['id'])
        if hashlib.sha256(''.join(s).encode()).hexdigest() != v['sequence_sha256']: raise ValueError('variant hash')
    out = W/'jobs'/f'ddgun_{key}_001'
    out.mkdir(parents=True, exist_ok=False)
    boundary = 'SCI-DDGun-isolated-postselection-20261112'
    body = b''
    for k,v in inp['payload'].items():
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n').encode()
    body += f'--{boundary}--\r\n'.encode()
    (out/'request_body.bin').write_bytes(body)
    receipt = {'provider':'DDGun_public_documented_webform', 'attempt_id':out.name,
               'input_path':str(ip), 'input_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),
               'body_sha256':hashlib.sha256(body).hexdigest(), 'endpoint':inp['endpoint'],
               'submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'method':'DDGun_SEQ', 'variant_count':len(inp['variants']),
               'status':'intent_reserved_no_response', 'docID':None, 'collection':None,
               'credit_cost':None, 'email_requested':False, 'post_attempts':1}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    st = time.monotonic()
    req = urllib.request.Request(inp['endpoint'], data=body, headers={
        'Content-Type':f'multipart/form-data; boundary={boundary}',
        'User-Agent':'SCI-isolated-retrospective/1.0'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read(); receipt['http_status']=r.status; receipt['response_url']=r.url
        (out/'response.html').write_bytes(data)
        receipt['response_sha256']=hashlib.sha256(data).hexdigest()
        p=Meta();p.feed(data.decode('utf-8','replace'))
        receipt['refresh_targets']=p.refresh
        receipt['status']='accepted_job_link' if any('find-ddgun-job' in s for s in p.refresh) else 'response_requires_review_do_not_retry'
    except urllib.error.HTTPError as e:
        data=e.read();(out/'http_error_body.bin').write_bytes(data)
        receipt.update(status='http_error_acceptance_unknown_do_not_retry',http_status=e.code,error=repr(e))
    except Exception as e:
        receipt.update(status='acceptance_unknown_do_not_retry',error=repr(e))
    receipt['elapsed_seconds']=time.monotonic()-st
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': main()
