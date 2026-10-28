"""Host-owned local science configuration never becomes an agent reader API."""
import json
import pytest
from synthesis_route_gym.science_config import load_science_config


def base(**updates):
    return {'schema_version':'srg-science-config-v1', **updates}


def study(**updates):
    return {'data_role':'development', 'rows':[
        {'candidate_id':'c1','conditions':{'solvent':'O'},'yield_percent':12},
        {'candidate_id':'c2','conditions':{'solvent':'CCO'},'yield_percent':87}],
        'budget':2,'substrate':'OCC','source_url':'https://example.org/study',
        'source_locator':'Table 2','dataset_sha256':'a'*64,**updates}


def write(tmp_path, value):
    path=tmp_path/'science.json'
    path.write_text(json.dumps(value))
    return path


def test_minimal_config_defaults_to_closed_source_and_zero_observations(tmp_path):
    result=load_science_config(write(tmp_path,base()))
    assert result['source_access_mode']=='closed_information'
    assert result['scientific_limits'].observation_calls==0
    assert result['scientific_limits'].retrieval_calls==0
    assert result['condition_study'] is None
    assert result['evidence_corpus'].retrieve()['status']=='unavailable'
    assert set(result)=={'evidence_corpus','scientific_limits','condition_study',
                        'biocatalytic_records','source_access_mode','process_basis','application_config'}
    assert result['application_config'] is None


def test_inline_replay_creates_immutable_study_without_exposing_unqueried_yields(tmp_path):
    config=base(condition_replay=study(),scientific_limits={'observation_calls':2})
    result=load_science_config(write(tmp_path,config))
    replay=result['condition_study']
    assert replay.substrate=='CCO'
    assert replay.observed_ids==()
    view=replay.view()
    assert [row['candidate_id'] for row in view['candidates']]==['c1','c2']
    assert all('yield_percent' not in row for row in view['candidates'])
    assert replay.observe('c1').view()['observations'][0]['yield_percent']==12
    assert 'evaluation' not in view
    assert replay._records[0].conditions==( ('solvent','O'), )


@pytest.mark.parametrize('changes',[
    {'data_role':'sealed_final'},{'data_role':'final'},{'dataset_path':'/tmp/judge.csv'},
    {'budget':True},{'budget':0},{'source_url':'file:///tmp/judge.csv'},
    {'source_locator':' '},{'dataset_sha256':'x'},{'substrate':'invalid smiles'},
    {'rows':[{'candidate_id':'c1','conditions':{'solvent':'O'},'yield_percent':True}]},
    {'rows':[{'candidate_id':'c1','conditions':{'solvent':'O'},'yield_percent':101}]},
    {'rows':[{'candidate_id':'c1','conditions':{'yield_percent':'99'},'yield_percent':10}]},
    {'rows':[{'candidate_id':'c1','conditions':{'solvent':'O'},'yield_percent':10,'best':True}]},
    {'rows':[]},
])
def test_invalid_or_final_replay_is_rejected(tmp_path,changes):
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=study(**changes))))


def test_observation_budget_cannot_exceed_study_or_exist_without_study(tmp_path):
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(scientific_limits={'observation_calls':1})))
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=study(),scientific_limits={'observation_calls':3})))
    dup=study();dup['rows'][1]['candidate_id']='c1'
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=dup)))


def bio(**updates):
    return {'record_id':'bio1','enzyme_name':'fixture oxidoreductase','source_url':'https://example.org/bio',
        'source_locator':'Figure 1','reactants':['OCC'],'products':['O=CC'],'cofactors':['O'],
        'evidence_kind':'curated_database',**updates}


def test_biocatalytic_records_preserve_stoichiometry_and_source_mode(tmp_path):
    result=load_science_config(write(tmp_path,base(source_access_mode='evidence_retrieval',
        biocatalytic_records=[bio(reactants=['OCC','OCC'])])))
    row=result['biocatalytic_records'][0]
    assert row['reactants']==['CCO','CCO']
    assert row['products']==['CC=O']
    assert row['cofactors']==['O']
    assert result['source_access_mode']=='evidence_retrieval'


@pytest.mark.parametrize('changes',[{'measured_activity':12},{'experimental_yield':90},{'records_path':'/tmp/file'},
    {'source_url':'file:///tmp/hidden'},{'enzyme_name':' '},{'cofactors':['invalid smiles']}])
def test_bio_outcomes_paths_and_malformed_records_reject(tmp_path,changes):
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(biocatalytic_records=[bio(**changes)])))


@pytest.mark.parametrize('changes',[{'model':'alternate-llm'},{'provider':'other'},{'tools_path':'/tmp/code.py'},
    {'scientific_limits':{'retrieval_calls':True}}, {'scientific_limits':{'unknown':2}},
    {'source_access_mode':'web'}, {'process_basis':{'cost':100}}, {'process_basis':{'purity_basis':' '}}])
def test_unknown_config_and_unsafe_configuration_fields_reject(tmp_path,changes):
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(**changes)))


def test_duplicate_json_nonfinite_oversize_and_nonobject_are_rejected(tmp_path):
    path=tmp_path/'config.json'
    for raw in ['{"schema_version":"srg-science-config-v1","schema_version":"srg-science-config-v1"}',
                '{"schema_version":"srg-science-config-v1","number":NaN}', '[]', '{broken']:
        path.write_text(raw)
        with pytest.raises(ValueError): load_science_config(path)
    path.write_bytes(b' '*20_000_001)
    with pytest.raises(ValueError): load_science_config(path)


def test_source_records_and_process_basis_are_supported(tmp_path):
    source={'record_id':'s1','document_id':'d1','source_url':'https://example.org/paper','locator':'Table 1',
            'reactants':['CCO'],'product':'CC=O','claim_kind':'literature_exact',
            'retrieved_at':'2026-01-01T00:00:00Z','source_content_sha256':'b'*64}
    result=load_science_config(write(tmp_path,base(source_access_mode='evidence_retrieval',source_records=[source],
        process_basis={'purity_basis':'supplier-declared','exclusions':['workup cost']})))
    assert result['evidence_corpus'].retrieve()['records'][0]['record_id']=='s1'
    assert result['process_basis']=={'purity_basis':'supplier-declared','exclusions':['workup cost']}


def test_repeated_settings_inconsistent_factors_and_duplicate_bio_ids_reject(tmp_path):
    repeated=study(); repeated['rows'][1]['conditions']={'solvent':'O'}
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=repeated)))
    changed=study(); changed['rows'][1]['conditions']={'temperature':'20'}
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=changed)))
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(biocatalytic_records=[bio(),bio()])))
    blank=study(); blank['rows'][0]['conditions']={'solvent':' '}
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=blank)))
    empty=study(); empty['rows'][0]['conditions']={}
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(condition_replay=empty)))
    with pytest.raises(ValueError): load_science_config(write(tmp_path,base(process_basis={'exclusions':[' ']})))


def test_loaded_host_attestation_remains_separate_from_retrieval_projection(tmp_path):
    from datetime import datetime, timedelta, timezone
    from synthesis_route_gym.evidence_contracts import HostAttestation, SourceRecord, record_digest, reaction_digest
    now=datetime.now(timezone.utc)
    source=SourceRecord(record_id='s1',document_id='d1',source_url='https://example.org/paper',locator='Table 1',
        reactants=['CCO'],product='CC=O',claim_kind='literature_exact',retrieved_at=now-timedelta(days=1),source_content_sha256='b'*64)
    review=HostAttestation(attestation_id='a1',record_id='s1',record_sha256=record_digest(source),
        reaction_sha256=reaction_digest(source.reactants,source.product),source_content_sha256=source.source_content_sha256,
        checked_at=now,expires_at=now+timedelta(days=1),reviewer='host-review',decision='supported')
    result=load_science_config(write(tmp_path,base(source_access_mode='evidence_retrieval',
        source_records=[source.model_dump(mode='json')],host_attestations=[review.model_dump(mode='json')])))
    corpus=result['evidence_corpus']
    assert corpus.retrieve()['records'][0]['verification_status']=='not_attested'
    assert corpus.verify('s1',reactants=['CCO'],product='CC=O')['supported']
