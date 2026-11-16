"""Verify the packaged gym matches its SHA-256 manifest and source episode hashes."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/'results/package_manifest.json').read_text())
gym = root/'scripts/formulation-optimization-gym'
assert manifest['status']=='verified_file_copy_not_scientific_validation'
assert manifest['source_files_verified']==len(manifest['files'])
for item in manifest['files']:
    target=gym/item['path']
    assert target.is_file(), item['path']
    assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'], item['path']
source=json.loads((gym/'data/processed/D-0092-2024.dailymed.episode.json').read_text())
for sid, name in {
    'FDA-RES-D-0092-2024':'fda-res-D-0092-2024.json',
    'FDA-SPL-0cf58732-c242-49b0-8e3f-248778b4458d':'fda-spl-glenmark.json',
    'FDA-DAILYMED-0cf58732-c242-49b0-8e3f-248778b4458d':'dailymed-glenmark.xml',
}.items():
    raw=gym/'data/raw'/name
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==source['sources'][sid]['sha256'], sid
print('Verified packaged file copies:',len(manifest['files']),'and Glenmark raw source hashes: 3')
