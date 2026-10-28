"""Bounded public patent-family metadata audit; reference chemistry stays private.

Only the focal page's explicit family section and publication-number metadata
are parsed. Citation-family links, patent prose, and structures are not inputs
to an LLM. Google Patents family IDs are not asserted to be DOCDB/INPADOC IDs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

_DOCUMENT = re.compile(r'([A-Z]{2})(RE|PP|D|H)?(\d{5,})([A-Z]\d?)?')
MAX_BYTES = 8 * 1024 * 1024


def _identity(value):
    if not isinstance(value, str):
        raise ValueError('Invalid document identifier')
    match = _DOCUMENT.fullmatch(value.replace(':', ''))
    if match is None:
        raise ValueError('Invalid document identifier')
    country, special, number, kind = match.groups()
    return country + (special or '') + str(int(number)), kind or ''


def document_url(document):
    base, kind = _identity(document)
    return f'https://patents.google.com/patent/{base}{kind}/en'


class _Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section_depth = 0
        self.family_depths = ()
        self.header_depth = None
        self.header_text = ''
        self.families = ()
        self.publications = ()
        self.publication_text = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'meta' and attrs.get('name') in {'citation_patent_publication_number', 'citation_patent_number'}:
            self.publications = (*self.publications, attrs.get('content', ''))
        if tag == 'dd' and attrs.get('itemprop') == 'publicationNumber':
            self.publication_text = ''
        if tag == 'section':
            self.section_depth += 1
            if attrs.get('itemprop') == 'family':
                self.family_depths = (*self.family_depths, self.section_depth)
        if tag == 'h2' and self.family_depths:
            self.header_depth = self.section_depth
            self.header_text = ''

    def handle_data(self, data):
        if self.publication_text is not None:
            self.publication_text += data
        if self.header_depth is not None:
            self.header_text += data

    def handle_endtag(self, tag):
        if tag == 'dd' and self.publication_text is not None:
            self.publications = (*self.publications, self.publication_text.strip())
            self.publication_text = None
        if tag == 'h2' and self.header_depth is not None:
            match = re.fullmatch(r'\s*ID\s*=\s*(\d{1,20})\s*', self.header_text)
            if match:
                self.families = (*self.families, match.group(1))
            self.header_depth = None
        if tag == 'section':
            self.family_depths = tuple(depth for depth in self.family_depths if depth != self.section_depth)
            self.section_depth = max(0, self.section_depth - 1)


def _unknown(diagnostic):
    return {'status': 'unknown', 'family_id': None, 'family_key': None,
            'family_definition': 'google_patents_displayed_family', 'diagnostic': diagnostic}


def extract_family_metadata(html, document_id):
    expected_base, expected_kind = _identity(document_id)
    parser = _Metadata()
    parser.feed(html)
    publications = set(parser.publications)
    if not publications:
        return _unknown('missing_publication_metadata')
    try:
        identities = {_identity(value) for value in publications}
    except ValueError:
        return _unknown('invalid_publication_metadata')
    bases = {base for base, _ in identities}
    kinds = {kind for _, kind in identities if kind}
    if len(bases) != 1 or len(kinds) > 1:
        return _unknown('ambiguous_publication_metadata')
    base, kind = next(iter(bases)), next(iter(kinds), '')
    if base != expected_base or (expected_kind and expected_kind != kind):
        return _unknown('publication_mismatch')
    families = set(parser.families)
    if len(families) > 1:
        return _unknown('ambiguous_family_metadata')
    if not families:
        return _unknown('missing_family_metadata')
    family_id = next(iter(families))
    return {'status': 'verified', 'family_id': family_id,
            'family_key': 'google_patents_family:' + family_id,
            'family_definition': 'google_patents_displayed_family',
            'diagnostic': 'explicit_family_section_and_matching_publication_metadata'}


def _save_private(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True))
    path.chmod(0o600)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        # Each document gets at most one HTTP request; redirects stay unknown.
        return None


def fetch_document(document_id, cache_dir, timeout=15, opener=None, max_bytes=MAX_BYTES):
    url = document_url(document_id)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.chmod(0o700)
    receipt = {'document_id': document_id, 'url': url,
               'fetched_at': datetime.now(timezone.utc).isoformat(), 'request_count': 1}
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; SynthesisRouteGymResearch/0.1)'})
    try:
        with (opener or build_opener(_NoRedirect())).open(request, timeout=timeout) as response:
            final_url = response.geturl()
            if final_url != url:
                raise ValueError('unexpected_response_url')
            raw = response.read(max_bytes + 1)
            status_code = response.status
        if len(raw) > max_bytes:
            raise ValueError('response_too_large')
        raw_path = cache_dir / (document_id + '.html')
        raw_path.write_bytes(raw)
        raw_path.chmod(0o600)
        receipt = {**receipt, 'status_code': status_code, 'raw_html_path': str(raw_path.resolve()),
                   'raw_html_sha256': hashlib.sha256(raw).hexdigest(),
                   **extract_family_metadata(raw.decode('utf-8', errors='replace'), document_id)}
    except HTTPError as error:
        receipt = {**receipt, **_unknown('http_error'), 'http_status': error.code}
    except (TimeoutError, URLError, OSError):
        receipt = {**receipt, **_unknown('network_error')}
    except ValueError as error:
        receipt = {**receipt, **_unknown(str(error))}
    _save_private(cache_dir / (document_id + '.json'), receipt)
    return receipt


def cached_document(document_id, cache_dir):
    cache_dir = Path(cache_dir)
    path = cache_dir / (document_id + '.json')
    if not path.is_file():
        return None
    try:
        receipt = json.loads(path.read_text())
        if receipt['document_id'] != document_id or receipt['url'] != document_url(document_id):
            return None
        if receipt['status'] == 'unknown' and 'raw_html_sha256' not in receipt:
            return receipt
        raw_path = cache_dir / (document_id + '.html')
        raw = raw_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt['raw_html_sha256']:
            return None
        parsed = extract_family_metadata(raw.decode('utf-8', errors='replace'), document_id)
        return {**receipt, **parsed}
    except (KeyError, ValueError, OSError):
        return None


def selected_documents(prepared, records):
    groups = prepared if isinstance(prepared, list) else prepared['task_groups']
    selected = {value['record_id'] for value in groups
                if 'task_id' not in value or value['task_id'].startswith('route-')}
    selected_rows = [row for row in records if row['record_id'] in selected]
    documents = sorted({document for row in selected_rows for document in row.get('source_documents', [])})
    for document in documents:
        document_url(document)
    return {'document_ids': documents, 'selected_record_count': len(selected_rows),
            'records_missing_documents': sorted(row['record_id'] for row in selected_rows if not row.get('source_documents')),
            'record_documents': {row['record_id']: row.get('source_documents', []) for row in selected_rows}}


def audit_documents(documents, cache_dir, max_requests=100, prior_requests=0, timeout=15, workers=4, fetcher=None):
    if (isinstance(max_requests, bool) or not isinstance(max_requests, int) or not 0 <= max_requests <= 100
            or isinstance(prior_requests, bool) or not isinstance(prior_requests, int) or not 0 <= prior_requests <= max_requests
            or isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 4
            or isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 15):
        raise ValueError('Audit limits require at most 100 requests, 15 seconds and 4 workers')
    documents = sorted(set(documents))
    for document in documents:
        document_url(document)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.chmod(0o700)
    ledger = cache_dir / 'request_ledger.json'
    reserved = max(prior_requests, json.loads(ledger.read_text()).get('reserved_requests', 0) if ledger.exists() else 0)
    cached = {document: cached_document(document, cache_dir) for document in documents}
    missing = [document for document in documents if cached[document] is None]
    fetch = missing[:max(0, max_requests - reserved)]
    skipped = missing[len(fetch):]
    _save_private(ledger, {'reserved_requests': reserved + len(fetch),
                          'note': 'Requests reserved before execution; interrupted attempts still consume the budget.'})
    operation = fetcher or fetch_document
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(lambda document: operation(document, cache_dir, timeout=timeout), fetch))
    results = {**{document: result for document, result in cached.items() if result is not None},
               **dict(zip(fetch, fetched)),
               **{document: {'document_id': document, **_unknown('request_budget_exhausted')} for document in skipped}}
    verified = [value for value in results.values() if value['status'] == 'verified']
    return {'schema_version': 'patent-family-audit.v1', 'documents': results,
            'document_count': len(documents), 'verified_document_count': len(verified),
            'unknown_document_count': len(documents) - len(verified),
            'unique_verified_family_count': len({value['family_id'] for value in verified}),
            'requests_this_run': len(fetch), 'requests_total': reserved + len(fetch),
            'cache_hits': sum(value is not None for value in cached.values()),
            'family_definition': 'google_patents_displayed_family',
            'independent_docdb_or_inpadoc_validation': False,
            'unknown_reasons': dict(Counter(value['diagnostic'] for value in results.values() if value['status'] != 'verified'))}


def family_partition_audit(report, prepared):
    groups = prepared if isinstance(prepared, list) else prepared['task_groups']
    record_documents = report['selection']['record_documents']
    record_families = {
        record: sorted({report['documents'][document]['family_key'] for document in documents
                        if report['documents'][document]['status'] == 'verified'})
        for record, documents in record_documents.items()}
    complete = sum(bool(documents) and all(report['documents'][document]['status'] == 'verified'
                                         for document in documents)
                   for documents in record_documents.values())
    families = {family for values in record_families.values() for family in values}
    partitions = {family: sorted({row['partition'] for row in groups
                                  if 'partition' in row and family in record_families.get(row['record_id'], [])})
                  for family in families}
    return {'records_with_complete_family_metadata': complete,
            'records_with_unknown_family_metadata': len(record_documents) - complete,
            'cross_partition_family_conflict_count': sum(len(values) > 1 for values in partitions.values()),
            'private_family_partitions': partitions, 'private_record_families': record_families}


def public_summary(report):
    allowed = {'schema_version', 'document_count', 'verified_document_count', 'unknown_document_count',
               'unique_verified_family_count', 'requests_this_run', 'requests_total', 'cache_hits',
               'family_definition', 'independent_docdb_or_inpadoc_validation', 'unknown_reasons',
               'candidate_sha256', 'normalized_records_sha256', 'created_at', 'selected_record_count',
               'parser_source_sha256',
               'records_missing_source_documents', 'records_with_complete_family_metadata',
               'records_with_unknown_family_metadata', 'cross_partition_family_conflict_count'}
    return {key: value for key, value in report.items() if key in allowed}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--public-output', type=Path, required=True)
    parser.add_argument('--prior-requests', type=int, default=0)
    args = parser.parse_args(argv)
    candidate_raw, records_raw = args.candidate.read_bytes(), args.records.read_bytes()
    selection = selected_documents(json.loads(candidate_raw), json.loads(records_raw))
    report = audit_documents(selection['document_ids'], args.cache_dir, prior_requests=args.prior_requests)
    report = {**report, 'selection': selection, 'candidate_sha256': hashlib.sha256(candidate_raw).hexdigest(),
              'normalized_records_sha256': hashlib.sha256(records_raw).hexdigest(),
              'parser_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'created_at': datetime.now(timezone.utc).isoformat(),
              'source_paths': {'candidate': str(args.candidate), 'records': str(args.records)},
              'selected_record_count': selection['selected_record_count'],
              'records_missing_source_documents': len(selection['records_missing_documents'])}
    report = {**report, **family_partition_audit(report, json.loads(candidate_raw))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _save_private(args.output, report)
    args.public_output.parent.mkdir(parents=True, exist_ok=True)
    args.public_output.write_text(json.dumps(public_summary(report), indent=2, sort_keys=True))
    print(json.dumps(public_summary(report), sort_keys=True))


if __name__ == '__main__':
    main()
