"""Outcome-independent binding of condition predictions to their chemical inputs."""
import hashlib
import json


def condition_input_digest(spec):
    payload = {key:spec[key] for key in ('study_id','substrate','target','dataset_sha256')}
    payload = {**payload,'candidates':sorted(spec['candidates'],key=lambda row:row['candidate_id'])}
    raw = json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()
