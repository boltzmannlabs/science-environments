"""Synthetic metadata only; no patent text, structures, or benchmark answers."""
import importlib.util
import json
from pathlib import Path
import sys
from urllib.error import HTTPError

import pytest

SPEC = importlib.util.spec_from_file_location('audit_patent_families', Path(__file__).parents[1] / 'scripts/audit_patent_families.py')
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def page(families=('123456',), document='US:1234567:A1'):
    return ('<html><meta name="citation_patent_publication_number" content="' + document + '">' +
            ''.join('<section itemprop="family"><h1>Family</h1><h2>ID=' + value + '</h2></section>' for value in families) + '</html>')


def test_verified_family_scoped_to_own_section_and_identity():
    html = page() + '<section itemprop="forwardReferencesFamily"><h2>ID=999999</h2></section>'
    row = module.extract_family_metadata(html, 'US1234567A1')
    assert row['status'] == 'verified'
    assert row['family_id'] == '123456'
    assert row['family_key'] == 'google_patents_family:123456'
    assert row['family_definition'] == 'google_patents_displayed_family'


@pytest.mark.parametrize('html,diagnostic', [
    (page(('1','2')), 'ambiguous_family_metadata'),
    ('<h2>ID=1234</h2>', 'missing_publication_metadata'),
    (page((), 'US:1234567:A1'), 'missing_family_metadata'),
    (page(('123',), 'US:7654321:A1'), 'publication_mismatch'),
    (page(('abc',)), 'missing_family_metadata'),
    (page().replace('itemprop="family"','itemprop="forwardReferencesFamily"'), 'missing_family_metadata'),
    (page() + '<meta name="citation_patent_publication_number" content="US:7654321:A1">', 'ambiguous_publication_metadata'),
])
def test_missing_mismatched_or_ambiguous_is_not_invented(html, diagnostic):
    row = module.extract_family_metadata(html, 'US1234567A1')
    assert row['status'] == 'unknown'
    assert row['family_id'] is None
    assert row['diagnostic'] == diagnostic


def test_legacy_document_normalization_and_kind_constraints():
    assert module.document_url('US04118563') == 'https://patents.google.com/patent/US4118563/en'
    assert module.extract_family_metadata(page(document='US:4118563:A'), 'US04118563')['status'] == 'verified'
    assert module.extract_family_metadata(page(document='US:4118563:B1'), 'US4118563A')['status'] == 'unknown'
    assert module.document_url('USRE045108E1').endswith('/USRE45108E1/en')


@pytest.mark.parametrize('document', ['', '../secret', 'https://evil', 'US123A1\n', None])
def test_reject_invalid_document(document):
    with pytest.raises(ValueError):module.document_url(document)


def test_selection_uses_all_documents_and_only_selected_route_records():
    prepared={'task_groups':[{'record_id':'r1'},{'record_id':'r1'},{'record_id':'r2'},{'record_id':'condition-1'}]}
    records=[{'record_id':'r1','source_documents':['US123456A1','US654321A1']},
             {'record_id':'r2','source_documents':[]},
             {'record_id':'unused','source_documents':['US999999A1']}]
    result=module.selected_documents(prepared,records)
    assert result['document_ids']==['US123456A1','US654321A1']
    assert result['selected_record_count']==2
    assert result['records_missing_documents']==['r2']


class Response:
    status=200
    def __init__(self, raw, url): self.raw,self.url=raw,url
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.raw[:n]
    def geturl(self):return self.url


class Opener:
    def __init__(self, raw=None, error=None, url=None):self.raw,self.error,self.url=raw,error,url
    def open(self, request, timeout):
        assert timeout<=15
        if self.error:raise self.error
        return Response(self.raw,self.url or request.full_url)


def test_fetch_saves_private_raw_hash_and_reusable_receipt(tmp_path):
    row=module.fetch_document('US1234567A1',tmp_path,opener=Opener(page().encode()))
    assert row['status']=='verified'
    assert len(row['raw_html_sha256'])==64
    assert Path(row['raw_html_path']).stat().st_mode & 0o777 == 0o600
    assert module.cached_document('US1234567A1',tmp_path)['family_id']=='123456'
    Path(row['raw_html_path']).write_text('corrupted')
    assert module.cached_document('US1234567A1',tmp_path) is None


@pytest.mark.parametrize('error', [TimeoutError(),HTTPError('https://example',403,'blocked',{},None)])
def test_fetch_records_unknown_without_exception_text(tmp_path,error):
    row=module.fetch_document('US1234567A1',tmp_path,opener=Opener(error=error))
    assert row['status']=='unknown' and row['family_id'] is None
    assert 'https://example' not in json.dumps(row)


def test_reject_external_redirect_and_large_response(tmp_path):
    row=module.fetch_document('US1234567A1',tmp_path,opener=Opener(page().encode(),url='https://evil.example/'))
    assert row['diagnostic']=='unexpected_response_url'
    row=module.fetch_document('US1234567A1',tmp_path,opener=Opener(b'x'*101),max_bytes=100)
    assert row['diagnostic']=='response_too_large'


def test_request_budget_and_unknown_are_explicit(tmp_path):
    called=[]
    def fetch(document,cache_dir,timeout):
        called.append(document)
        return {'document_id':document,'status':'unknown','family_id':None,'diagnostic':'blocked'}
    report=module.audit_documents(['US123456A1','US234567A1','US345678A1'],tmp_path,
                                 max_requests=3,prior_requests=2,workers=1,fetcher=fetch)
    assert len(called)==1
    assert report['requests_this_run']==1 and report['requests_total']==3
    assert report['unknown_document_count']==3
    assert sum(x['diagnostic']=='request_budget_exhausted' for x in report['documents'].values())==2


@pytest.mark.parametrize('kwargs',[{'max_requests':101},{'workers':5},{'timeout':16},{'prior_requests':101},{'workers':0}])
def test_invalid_resource_limits(tmp_path,kwargs):
    with pytest.raises(ValueError):module.audit_documents([],tmp_path,**kwargs)


def test_cache_avoids_requests_and_aggregate_contains_no_document_ids(tmp_path):
    module.fetch_document('US1234567A1',tmp_path,opener=Opener(page().encode()))
    report=module.audit_documents(['US1234567A1'],tmp_path,max_requests=0,workers=1)
    assert report['verified_document_count']==1 and report['requests_this_run']==0
    assert 'US1234567A1' not in json.dumps(module.public_summary(report))


def test_final_assignment_list_filters_condition_rows():
    rows=[{'record_id':'r1','task_id':'route-one'},{'record_id':'r2','task_id':'condition-one'}]
    records=[{'record_id':'r1','source_documents':['US123456A1']},{'record_id':'r2','source_documents':['US654321A1']}]
    assert module.selected_documents(rows,records)['document_ids']==['US123456A1']


def test_cli_synthetic_end_to_end_writes_only_aggregates_publicly(tmp_path,monkeypatch,capsys):
    candidate=tmp_path/'assignments.json';candidate.write_text(json.dumps([{'record_id':'r1','task_id':'route-one'}]))
    records=tmp_path/'records.json';records.write_text(json.dumps([{'record_id':'r1','source_documents':['US1234567A1']}]))
    cache=tmp_path/'cache'
    module.fetch_document('US1234567A1',cache,opener=Opener(page().encode()))
    private=tmp_path/'private.json';public=tmp_path/'public.json'
    module.main(['--candidate',str(candidate),'--records',str(records),'--cache-dir',str(cache),
                 '--output',str(private),'--public-output',str(public)])
    assert json.loads(private.read_text())['documents']['US1234567A1']['family_id']=='123456'
    assert json.loads(public.read_text())['verified_document_count']==1
    assert 'US1234567A1' not in public.read_text()+capsys.readouterr().out


def test_request_reservation_persists_across_invocations(tmp_path):
    def fetch(document,cache_dir,timeout):return {'status':'unknown','family_id':None,'diagnostic':'blocked'}
    first=module.audit_documents(['US123456A1'],tmp_path,max_requests=1,fetcher=fetch)
    second=module.audit_documents(['US654321A1'],tmp_path,max_requests=1,fetcher=fetch)
    assert first['requests_this_run']==1
    assert second['requests_this_run']==0 and second['requests_total']==1


def test_invalid_publication_metadata_is_unknown():
    assert module.extract_family_metadata(page(document='not-publication'), 'US1234567A1')['diagnostic']=='invalid_publication_metadata'


def test_redirect_handler_refuses_followup_request():
    assert module._NoRedirect().redirect_request(None,None,302,'redirect',{},'https://example') is None


def test_family_overlap_audit_counts_conflicts_without_rewriting_assignment():
    prepared=[{'record_id':'r1','task_id':'route-one','partition':'train'},
              {'record_id':'r2','task_id':'route-two','partition':'final'},
              {'record_id':'r2','task_id':'route-two-restricted','partition':'final'},
              {'record_id':'r3','task_id':'route-three','partition':'validation'}]
    report={'selection':{'record_documents':{'r1':['D1'],'r2':['D2'],'r3':['D3']}},
            'documents':{'D1':{'status':'verified','family_key':'google_patents_family:1'},
                         'D2':{'status':'verified','family_key':'google_patents_family:1'},
                         'D3':{'status':'unknown','family_key':None}}}
    result=module.family_partition_audit(report,prepared)
    assert result['records_with_complete_family_metadata']==2
    assert result['records_with_unknown_family_metadata']==1
    assert result['cross_partition_family_conflict_count']==1
    assert result['private_family_partitions']=={'google_patents_family:1':['final','train']}
    assert 'google_patents_family:1' not in json.dumps(module.public_summary(result))


def test_granted_patent_primary_identity_metadata_and_kind():
    html=page(document='US:1234567').replace('citation_patent_publication_number','citation_patent_number')
    assert module.extract_family_metadata(html,'US01234567')['status']=='verified'
    assert module.extract_family_metadata(html,'US1234567B2')['status']=='unknown'
    html += '<dd itemprop="publicationNumber">US1234567B2</dd>'
    assert module.extract_family_metadata(html,'US1234567B2')['status']=='verified'
    html += '<dd itemprop="publicationNumber">US1234567B1</dd>'
    assert module.extract_family_metadata(html,'US1234567B2')['status']=='unknown'
