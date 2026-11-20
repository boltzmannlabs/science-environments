"""Cross-check public FDA SPL identifiers against documented DailyMed v2 XML.

Never interpret the currently served label as the recalled lot's formula/SOP.
"""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from environment.actions import Action, execute
from environment.state import Episode

NS = '{urn:hl7-org:v3}'


def crosscheck(state_path: Path, xml_path: Path, output_path: Path) -> Episode:
    """Verify exact SPL set ID, recalled-package NDC, and ranolazine label identity."""
    state = Episode.load(state_path)
    number = state.task.get('case_id')
    if not number or 'FDA-RES-' + number not in state.sources:
        raise ValueError('FDA recall episode required')
    source = state.sources['FDA-RES-' + number]
    if source.get('source_type') != 'FDA enforcement report':
        raise ValueError('recall provenance missing')
    claims = [c['text'] for c in state.evidence if c.get('source_id') == 'FDA-RES-' + number and c.get('field') == 'product_description' and c.get('text', '').startswith('Product: ')]
    if len(claims) != 1:
        raise ValueError('unique recalled product description required')
    ndc = re.search(r'\b\d{5}-\d{3}-\d{2}\b',claims[0])
    if not ndc:
        raise ValueError('recalled package NDC missing')
    raw = xml_path.read_bytes()
    root = ET.fromstring(raw)
    if root.tag != NS+'document':
        raise ValueError('not an SPL document')
    set_id = root.find(NS+'setId')
    spl_id = root.find(NS+'id')
    effective = root.find(NS+'effectiveTime')
    if set_id is None or spl_id is None or effective is None:
        raise ValueError('missing SPL identity or version')
    sid = set_id.get('root')
    label_id = 'FDA-SPL-' + sid
    if label_id not in state.sources or state.sources[label_id].get('document_id') != sid or state.sources[label_id].get('effective_time') != effective.get('value'):
        raise ValueError('SPL label ID or version does not match FDA episode')
    package_codes = {e.get('code') for e in root.iter(NS+'code')}
    if ndc.group() not in package_codes or 'ranolazine' not in ' '.join(root.itertext()).lower():
        raise ValueError('recalled NDC or ingredient does not match SPL')
    evidence_id = 'FDA-DAILYMED-' + sid
    if evidence_id in state.sources:
        raise ValueError('already cross-checked')
    source_entry = {'source_id':evidence_id, 'citation':'https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/'+sid+'.xml', 'document_id':sid, 'verified_by':'DailyMed v2 SPL XML ID, version and recalled NDC check', 'source_type':'FDA DailyMed SPL public label', 'sha256':hashlib.sha256(raw).hexdigest(), 'spl_version':spl_id.get('root'), 'effective_time':effective.get('value'), 'authorized_measurement':False, 'verified_fields':['public_label_identity_crosscheck']}
    result = execute(state, Action('verify_source',source_entry))
    if result.status != 'success':
        raise ValueError(result.warnings)
    state.evidence.append({'text':'DailyMed currently served SPL ID and package NDC corroborate public label identity; no recalled-lot formula or QC method established', 'label':'literature_reported','source_id':evidence_id,'field':'setId+code'})
    state.save(output_path)
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--xml',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    state = crosscheck(args.state,args.xml,args.out)
    print(json.dumps({'case_id':state.task['case_id'],'crosscheck':'success','sources':list(state.sources),'out':str(args.out)}))


if __name__ == '__main__':
    main()
