"""Import FDA openFDA public enforcement/label snapshots as separate episodes.

Only source-linked recall/label facts are imported; API results are not lab data.
CLI requires explicit local snapshots captured from documented FDA endpoints.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from environment.actions import Action, execute
from environment.state import Episode
from run import TASK_ID

API = 'https://api.fda.gov/drug/'


def load_one(path: Path) -> tuple[dict, dict, str]:
    """Accept exactly one response result with FDA metadata; keep source hash."""
    raw = path.read_bytes()
    blob = json.loads(raw)
    if not isinstance(blob, dict) or not isinstance(blob.get('meta'), dict) or len(blob.get('results', [])) != 1 or not blob['meta'].get('last_updated'):
        raise ValueError('expected exactly one FDA result with update metadata')
    return blob['results'][0], blob['meta'], hashlib.sha256(raw).hexdigest()


def import_case(recall_path: Path, label_path: Path, out: Path) -> Episode:
    """Cross-check drug/strength/NDC/SPL link; never infer batch formula or QC limits."""
    r, rm, rh = load_one(recall_path)
    label, lm, lh = load_one(label_path)
    number = r.get('recall_number', '')
    description = r.get('product_description', '')
    reason = r.get('reason_for_recall', '')
    spl = r.get('openfda', {}).get('spl_set_id', [])
    ndc_match = re.search(r'\b\d{5}-\d{3}-\d{2}\b', description)
    strength = re.search(r'\b(500|1000)\s*mg\b', description, flags=re.I)
    if not re.fullmatch(r'D-\d{4}-\d{4}', number) or not ndc_match or not strength or 'ranolazine' not in description.lower() or 'dissolution' not in reason.lower():
        raise ValueError('recall identity/reason unverified or inconsistent')
    if not spl or spl[0] not in label.get('openfda', {}).get('spl_set_id', []) or ndc_match.group() not in label.get('openfda', {}).get('package_ndc', []):
        raise ValueError('label SPL or package NDC does not match recall')
    if not label.get('description') or 'ranolazine' not in label['description'][0].lower():
        raise ValueError('label description missing or wrong active ingredient')
    for key in ('report_date', 'recall_initiation_date'):
        dt = datetime.strptime(r[key], '%Y%m%d').replace(tzinfo=timezone.utc)
        if dt > datetime.now(timezone.utc):
            raise ValueError('future recall event date')
    rid = 'FDA-RES-' + number
    lid = 'FDA-SPL-' + spl[0]
    recall_url = API + 'enforcement.json?' + urlencode({'search':f'recall_number:"{number}"'})
    label_url = API + 'label.json?' + urlencode({'search':f'openfda.spl_set_id:"{spl[0]}"'})
    state = Episode({'task_id': TASK_ID, 'case_id': number, 'api': 'ranolazine', 'dosage_form': 'extended_release_tablet', 'reported_issue':'dissolution_specification_failure', 'recall_status':'FDA-openFDA-RES-reported'})
    for data in [
        {'source_id':rid, 'citation':recall_url, 'document_id':number, 'verified_by':'openFDA FDA-origin exact-query and identifier check', 'sha256':rh, 'api_last_updated':rm['last_updated'], 'source_type':'FDA enforcement report', 'authorized_measurement':False, 'verified_fields':['primary_recall_record','manufacturer_and_product_identity','jurisdiction_lots']},
        {'source_id':lid, 'citation':label_url, 'document_id':spl[0], 'verified_by':'FDA-origin SPL set ID and package NDC cross-check', 'sha256':lh, 'api_last_updated':lm['last_updated'], 'effective_time':label.get('effective_time'), 'source_type':'FDA labeling', 'authorized_measurement':False, 'verified_fields':['public_label_ingredient_identities']}
    ]:
        obs = execute(state, Action('verify_source',data))
        if obs.status != 'success':
            raise ValueError(obs.warnings)
    state.evidence.extend([
        {'text':'FDA enforcement reason: '+reason, 'label':'literature_reported', 'source_id':rid, 'field':'reason_for_recall'},
        {'text':'Recalling firm: '+r['recalling_firm'], 'label':'literature_reported', 'source_id':rid, 'field':'recalling_firm'},
        {'text':'Product: '+description, 'label':'literature_reported', 'source_id':rid, 'field':'product_description'},
        {'text':'Lot/code as reported: '+r['code_info'], 'label':'literature_reported', 'source_id':rid, 'field':'code_info'},
        {'text':'FDA report date: '+r['report_date'], 'label':'literature_reported', 'source_id':rid, 'field':'report_date'},
        {'text':'Labeled inactive ingredients (qualitative only): '+label['description'][0].split('the following inactive ingredients:')[-1].split('structure')[0].strip() if 'the following inactive ingredients:' in label['description'][0] else 'FDA label description available; quantities unknown', 'label':'literature_reported','source_id':lid,'field':'description'},
        {'text':'Labeled strength', 'value':int(strength.group(1)), 'unit':'mg','label':'literature_reported','source_id':rid,'field':'product_description'},
    ])
    state.log('import_public_fda_sources','success',{'recall_number':number,'source_ids':[rid,lid]})
    state.save(out)
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--recall', type=Path, required=True)
    parser.add_argument('--label', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    state = import_case(args.recall,args.label,args.out)
    print(json.dumps({'case_id':state.task['case_id'],'sources':list(state.sources),'out':str(args.out),'status':'FDA-sourced-recall-verified; QC and lot-level measurements unavailable'}))


if __name__ == '__main__':
    main()
