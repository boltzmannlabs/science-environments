"""Synthetic contract cases; source fixture separately documents public identity."""
import copy
import json
import pytest
from pydantic import ValidationError

from synthesis_route_gym.portfolio_biocatalysis import (
    BioSourceRecord, bio_record_digest, build_biocatalysis_report,
)


def task(**updates):
    return {'task_id':'bio-test','target':'CCO','inventory':[
        {'smiles':'CCOC(C)=O'},{'smiles':'O'}],**updates}


def step(**updates):
    return {'step_id':'s1','product':'CCO','reactants':[
        {'smiles':'CCOC(C)=O'},{'smiles':'O'}],
        'source_tool':'test','source_version':'1',**updates}


def record(**updates):
    return {'record_id':'RHEA:58148','reactants':['CCOC(C)=O','O'],
        'products':['CCO','CC(=O)[O-]','[H+]'],'enzyme_name':'ethyl acetate hydrolase',
        'enzyme_class':'3.1.1.113','source_url':'https://www.rhea-db.org/rhea/58148',
        'source_locator':'reaction participants','evidence_kind':'curated_database',**updates}


def candidate(query=None,source=None,**kwargs):
    return build_biocatalysis_report(task(),query or step(),records=[source or record()],**kwargs)['candidates'][0]


def test_projected_product_is_not_complete_exact_reaction():
    c=candidate()
    assert c['match_kind']=='exact_substrates_product_projection'
    assert c['reactant_multiset_match'] and not c['complete_product_multiset_match']
    assert not c['supports_complete_query_reaction']
    assert c['unrepresented_source_products']==['CC(=O)[O-]','[H+]']
    assert c['experimental_yield'] is None and c['claims_activity'] is False
    assert c['conditions_status']=='unknown' and c['enzyme_availability']=='unknown'


def test_full_products_and_reactants_allow_exact_identity_only():
    c=candidate(step(product='CCO.CC(=O)[O-].[H+]'))
    assert c['match_kind']=='exact_reaction'
    assert c['supports_complete_query_reaction']
    assert c['claims_experimental_validation'] is False
    assert c['evidence_kind']=='curated_database'


def test_product_only_match_does_not_infer_substrate_activity():
    c=candidate(step(reactants=[{'smiles':'COC(C)=O'},{'smiles':'O'}]))
    assert c['match_kind']=='product_only'
    assert not c['reactant_multiset_match'] and not c['supports_complete_query_reaction']
    assert c['claims_activity'] is False


def test_product_analogue_never_supports_query_reaction():
    c=candidate(step(product='CCCO'),analogue_threshold=0)
    assert c['match_kind']=='product_similarity_analogue'
    assert not c['supports_complete_query_reaction'] and c['experimental_yield'] is None


def test_dissimilar_candidate_is_excluded_at_high_threshold():
    assert build_biocatalysis_report(task(),step(product='c1ccccc1'),records=[record()],analogue_threshold=1)['candidates']==[]


def test_reactant_multiplicity_not_collapsed():
    c=candidate(step(reactants=[{'smiles':'CCOC(C)=O'},{'smiles':'O'},{'smiles':'O'}]))
    assert c['match_kind']=='product_only'


def test_product_multiplicity_not_collapsed():
    c=candidate(step(product='CCO.CC(=O)[O-].[H+].[H+]'))
    assert not c['complete_product_multiset_match']
    assert c['match_kind']=='product_only'


def test_direction_not_reversed_implicitly():
    s=step(product='CCOC(C)=O',reactants=[{'smiles':'CCO'},{'smiles':'CC(=O)[O-]'},{'smiles':'[H+]'}])
    assert build_biocatalysis_report(task(),s,records=[record()],analogue_threshold=1)['candidates']==[]


@pytest.mark.parametrize('query,source',[('[13CH3]O','CO'),('F[C@H](Cl)Br','F[C@@H](Cl)Br')])
def test_isotopes_and_stereochemistry_stay_distinct(query,source):
    c=candidate(step(product=query),record(products=[source]),analogue_threshold=0)
    assert c['match_kind']=='product_similarity_analogue'
    assert not c['complete_product_multiset_match']


def test_atom_maps_do_not_change_identity():
    c=candidate(step(product='[CH3:1][CH2:2][OH:3]'))
    assert c['match_kind']=='exact_substrates_product_projection'


def test_cofactors_and_zero_stock_are_reported_separately():
    r=record(cofactors=['N'])
    t=task(inventory=[{'smiles':'CCOC(C)=O'},{'smiles':'O','available_mmol':0},{'smiles':'N','available_mmol':0}])
    c=build_biocatalysis_report(t,step(),records=[r])['candidates'][0]
    assert c['missing_reactants']==['O'] and c['missing_cofactors']==['N']
    assert not c['inventory_complete']
    assert c['cofactors_declared_in_query'] is False


def test_declared_cofactor_remains_unverified_operating_suitability():
    r=record(cofactors=['N'])
    c=candidate(step(reagents=[{'smiles':'N'}]),r)
    assert c['cofactors_declared_in_query']
    assert c['claims_activity'] is False


def test_source_conditions_match_is_not_assay_validation():
    c=candidate(step(conditions=['fixture condition'],conditions_complete=True),record(conditions=['fixture condition']))
    assert c['conditions_status']=='same_declared_conditions'
    assert c['claims_experimental_validation'] is False


@pytest.mark.parametrize('conditions,expected',[([],'query_conditions_unknown'),(['other'],'different_declared_conditions')])
def test_conditions_uncertainty(conditions,expected):
    assert candidate(step(conditions=conditions),record(conditions=['fixture']))['conditions_status']==expected


def test_available_enzyme_requires_sourced_host_declaration():
    with pytest.raises(ValueError): BioSourceRecord.model_validate(record(enzyme_availability='available'))
    r=record(enzyme_availability='available',enzyme_availability_source='https://example.org/catalog',enzyme_availability_locator='synthetic stock fixture')
    c=candidate(source=r)
    assert c['enzyme_availability']=='available'
    assert c['enzyme_availability_scope']=='host_supplied_sourced_declaration_not_verified_stock'


@pytest.mark.parametrize('updates',[
    {'record_id':''},{'enzyme_name':' '},{'enzyme_class':'invalid'},{'source_url':'file:///private'},
    {'source_url':'https://user:password@example.org/x'},{'source_locator':' '},
    {'reactants':[]},{'products':[]},{'cofactors':['not-smiles']},{'conditions':[' ']},
    {'evidence_kind':'predicted'},{'experimental_yield':0.99},{'activity':10},{'conditions':['x']*51},
    {'enzyme_availability':'unknown','enzyme_availability_source':'https://example.org/stock'},
])
def test_invalid_or_forged_source_fields_rejected(updates):
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records=[record(**updates)])


@pytest.mark.parametrize('threshold',[True,-0.1,1.1,float('nan'),'0.5'])
def test_invalid_threshold_rejected(threshold):
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records=[],analogue_threshold=threshold)


def test_duplicate_and_oversized_records_rejected():
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records=[record(),record()])
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records=[record(record_id=f'r{i}') for i in range(101)])


def test_unknown_record_and_invalid_containers_rejected():
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records={'bad':'value'})
    with pytest.raises(ValueError): build_biocatalysis_report(task(),step(),records=[{'bad':'value'}])


def test_empty_catalog_and_identity_digests():
    report=build_biocatalysis_report(task(),step())
    assert report['schema_version']=='srg-biocatalysis-report-v1'
    assert report['candidates']==[] and report['scientific_validation']=='unvalidated'
    assert len(report['step_sha256'])==len(report['catalog_sha256'])==64


def test_record_frozen_and_report_detached():
    source=record();t=task();s=step();before=copy.deepcopy((t,s,source))
    model=BioSourceRecord.model_validate(source)
    with pytest.raises(ValidationError): model.enzyme_name='changed'
    report=build_biocatalysis_report(t,s,records=[model]);report['candidates'][0]['reactants'].append('N')
    assert (t,s,source)==before
    assert len(model.reactants)==2


def test_canonical_digest_and_sorted_candidates():
    a=record(record_id='z');b=record(record_id='a',products=['CCCO'])
    c=record(record_id='m',reactants=['COC(C)=O','O'])
    report=build_biocatalysis_report(task(),step(),records=[b,c,a],analogue_threshold=0)
    assert [r['record_id']for r in report['candidates']]==['z','m','a']
    assert bio_record_digest(a)==bio_record_digest(BioSourceRecord.model_validate(a))
    assert bio_record_digest(a)==bio_record_digest({**a,'reactants':['O','CCOC(C)=O']})


def test_report_can_serialize_without_nonfinite_values():
    report=build_biocatalysis_report(task(),step(),records=[record()])
    assert json.loads(json.dumps(report,allow_nan=False))==report


def test_nonserializable_record_is_rejected_at_boundary():
    with pytest.raises(ValueError):
        build_biocatalysis_report(task(),step(),records=[{'unexpected':object()}])


def test_catalog_serialized_size_bound():
    rows=[record(record_id=f'r{i}',reactants=['C'*1000]*100) for i in range(11)]
    with pytest.raises(ValueError,match='bounded'):
        build_biocatalysis_report(task(),step(),records=rows)


def test_unreported_cofactor_requirements_remain_explicit():
    assert candidate()['cofactor_requirements_status']=='not_reported'
    assert candidate(source=record(cofactors=['N']))['cofactor_requirements_status']=='source_recorded'


def test_full_identity_with_missing_cofactor_does_not_support_query():
    c=candidate(step(product='CCO.CC(=O)[O-].[H+]'),record(cofactors=['N']))
    assert c['match_kind']=='exact_reaction' and not c['supports_complete_query_reaction']


def test_bounded_source_text_is_enforced():
    with pytest.raises(ValueError):
        candidate(source=record(notes='x'*4001))
