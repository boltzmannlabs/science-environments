"""Fetch published patent record to an immutable SHA-named local snapshot.

Only checks accessible source text; does not claim table cells match unless
explicit machine parsing has proved it.
"""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):
        if data.strip():self.parts.append(data.strip())

def fetch(url,out):
    with urlopen(url,timeout=18) as r: raw=r.read()
    digest=hashlib.sha256(raw).hexdigest()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    target=out/('US6525057B2-'+digest+'.html')
    if target.exists() and target.read_bytes()!=raw: raise ValueError('snapshot collision')
    if not target.exists(): target.write_bytes(raw)
    parser=Text();parser.feed(raw.decode(errors='replace'))
    text=' '.join(parser.parts)
    expected=(
        'TABLE 4 Percentage of Formulation Dissolved Time Formulation (hours) IR A B C '
        '0.25 88.1 0.5 100.5 13.9 17.6 17.5 1 101.7 19.9 26.0 25.7 '
        '2 27.8 47.5 35.9 4 39.0 69.2 48.4 8 52.4 90.1 64.7 '
        '12 61.6 99.6 74.2 24 80.8 105.6 95.4'
    )
    table_match=expected in text
    snippets=[]
    for term in ('Table 4','105.6','88.1','80.8'):
        m=re.search(re.escape(term),text,re.I)
        snippets.append({'term':term,'found':bool(m),'context':text[max(0,m.start()-90):m.end()+130] if m else None})
    report={'source_locator':url,'snapshot':str(target),'sha256':digest,'snippets':snippets,
            'table_4_expected_sequence_matches_primary_html':table_match,
            'status':'table_4_transcription_sequence_verified' if table_match else 'table_4_transcription_not_verified'}
    (out/'US6525057B2_source_check.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    print(json.dumps(fetch('https://patents.google.com/patent/US6525057B2/en','data/raw'),indent=2))
