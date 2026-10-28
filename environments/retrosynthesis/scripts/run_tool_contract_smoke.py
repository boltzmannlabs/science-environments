#!/usr/bin/env python3
"""Offline Step 4 contract smoke; every chemical/data value is a synthetic fixture."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.evidence_contracts import SourceRecord, HostAttestation, record_digest, reaction_digest
from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy
from synthesis_route_gym.schemas import InventoryItem, MaterialUse, ReactionStep, RouteCandidate, Task
from synthesis_route_gym.scientific_execution import ScientificLimits, SCIENTIFIC_ACTIONS

NOW = datetime(2026,10,27,12,tzinfo=timezone.utc)
SENTINEL = 'SYNTHETIC_PRIVATE_FIELD_MUST_NOT_APPEAR'


def _write(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')


def _forbid_external(*args,**kwargs):
    raise RuntimeError('Offline contract smoke forbids network and subprocess work')


def _fixtures():
    stock = tuple(InventoryItem(smiles=s,available_mmol=2,price_per_mmol=price,currency='USD',
        source='synthetic-test-quote',quoted_at='2026-10-01') for s,price in [('CCO',1),('CC(=O)O',2)])
    task = Task(task_id='synthetic-contract-fixture',target='CCOC(C)=O',inventory=stock,target_amount_mmol=1)
    route = RouteCandidate(route_id='fixture-route',target=task.target,steps=(ReactionStep(
        step_id='fixture-step',product=task.target,product_amount_mmol=1,
        reactants=tuple(MaterialUse(smiles=item.smiles,amount_mmol=1) for item in stock),
        source_tool='synthetic-test-fixture',source_version='1'),))
    source = SourceRecord(record_id='fixture-source',document_id='synthetic-document',
        source_url='https://example.invalid/synthetic-fixture',locator='synthetic fixture row only',
        reactants=['CCO','CC(=O)O'],product=task.target,claim_kind='literature_analogue',
        retrieved_at=NOW-timedelta(days=1),source_content_sha256='a'*64)
    study = FiniteConditionStudy((ConditionRecord('fixture-observation',(('condition','synthetic-A'),),12),
        ConditionRecord('hidden-fixture-observation',(('condition','synthetic-B'),),94)),(),1,
        'https://example.invalid/synthetic-fixture','synthetic condition rows','b'*64,'CCO')
    bio = [{'record_id':'fixture-bio','enzyme_name':'synthetic-test-enzyme-label',
        'source_url':'https://example.invalid/synthetic-fixture','source_locator':'synthetic biocatalytic row',
        'evidence_kind':'curated_database','reactants':['CCO','CC(=O)O'],'products':[task.target],
        'cofactors':['O'],'experimental_yield':94,'private':SENTINEL}]
    return task,route,source,study,bio


class FixturePredictor:
    metadata = {'model_version':'synthetic-double-v1'}
    def predict(self,rows):
        return [{'predicted_yield_percent':12,'evidence_status':'measured','private':SENTINEL} for _ in rows]


class FixtureImpurity:
    def predict(self,reactants,product,top_k):
        return {'status':'ok','predicted_smiles':['CCO',product],
                'measured_impurities':['CCO'],'private':SENTINEL}


def _expansion(smiles,top_k):
    return {'status':'ok','predictions':[{'product':smiles,'reactants':['CCO','CC(=O)O'],'score':.25}],
            'reference_answer':SENTINEL}


def _forward(args):
    return {'predictions':[{'product':args['product'],'score':.5}],
            'experimental_validation':True,'private':SENTINEL}


def _options(source,study,bio):
    return {'expand':_expansion,'condition_ranker':FixturePredictor(),
        'forward':_forward,'impurity':FixtureImpurity(),
        'evidence_corpus':FrozenEvidenceCorpus([source],mode='evidence_retrieval',now=NOW),
        'condition_study':study,'biocatalytic_records':bio,
        'scientific_limits':ScientificLimits(retrieval_calls=2,observation_calls=1),
        'process_basis':{'purity_basis':'synthetic_pure_target_mmol','exclusions':['workup','energy']}}


def _configured(output,task,route,source,study,bio):
    options = _options(source,study,bio)
    env = SynthesisRouteEnv(task,store=output/'episode',**options)
    descriptors = env.dispatch('capabilities',{})['result']['capabilities']
    assert {row['name'] for row in descriptors} == SCIENTIFIC_ACTIONS
    _write(output/'tool-contract.v1.json',{'schema_version':'srg-scientific-tool-v1',
        'scope':'injected_synthetic_fixture_configuration','capabilities':descriptors})
    assert env.dispatch('propose_route',{'route':route.model_dump(mode='json')})['status']=='ok'
    requests = {
        'expand':{'smiles':task.target},
        'predict_conditions':{'candidates':[{'id':'fixture-prediction','aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}]},
        'forward_check':{'reactants':['CCO','CC(=O)O'],'product':task.target},
        'predict_impurities':{'reactants':['CCO','CC(=O)O'],'product':task.target},
        'retrieve_sources':{'product':task.target},
        'observe_condition':{'candidate_id':'fixture-observation'},
        'compare_process':{'route_ids':[route.route_id]},
        'retrieve_biocatalysis':{'target_smiles':task.target},
    }
    results = {name:env.dispatch(name,args,action_id='smoke-'+name) for name,args in requests.items()}
    assert all(result['status']=='ok' for result in results.values()), results
    public_text = json.dumps(results)
    assert SENTINEL not in public_text and 'hidden-fixture-observation' not in public_text
    assert 'dataset_optimum' not in public_text
    assert results['expand']['result']['predictions'][0]['evidence_status']=='predicted'
    assert results['predict_impurities']['result']['data']['measured_impurities'] is None
    assert results['forward_check']['result']['data']['atom_balance_status']=='unknown_coproducts_not_provided'
    assert results['retrieve_sources']['result']['data']['records'][0]['verification_status']=='not_attested'
    assert results['retrieve_biocatalysis']['result']['data']['candidates'][0]['experimental_yield'] is None
    assert results['compare_process']['result']['data']['claims_manufacturing_savings'] is False
    _write(output/'configured-results.json',results)
    before = env.export()['scientific_usage']
    resumed = SynthesisRouteEnv.resume(output/'episode',expected_task=task,**options)
    assert resumed.export()['scientific_usage']==before
    assert resumed.dispatch('observe_condition',requests['observe_condition'],action_id='smoke-observe_condition')==results['observe_condition']
    assert resumed.export()['scientific_usage']==before
    denied = resumed.dispatch('source_retrieval',{'product':task.target})
    assert denied['status']=='error' and denied['result']['error']['code']=='access_budget_exhausted'
    assert resumed.export()['scientific_usage']['retrieve_sources']==before['retrieve_sources']+1
    malformed = resumed.dispatch('retrieve_sources',{'records_path':'/synthetic-private/evaluator.json'})
    assert malformed['status']=='error' and '/synthetic-private/' not in json.dumps(malformed)
    _write(output/'resumed-episode.json',resumed.export())
    return {'usage_preserved':True,'duplicate_observation_not_charged':True,
            'alias_retrieval_quota_enforced':True,'usage_before_resume':before,
            'usage_after_checks':resumed.export()['scientific_usage']}


def _access_checks(task,source,bio):
    empty = SynthesisRouteEnv(task)
    unavailable = {
        'expand':{'smiles':task.target},
        'forward_check':{'reactants':['CCO'],'product':task.target},
        'predict_impurities':{'reactants':['CCO'],'product':task.target},
        'observe_condition':{'candidate_id':'fixture-observation'},
        'retrieve_biocatalysis':{'target_smiles':task.target},
    }
    for name,args in unavailable.items():
        result = empty.dispatch(name,args)
        assert result['status']=='unavailable' and result['result'].get('data') is None
    closed = SynthesisRouteEnv(task,evidence_corpus=FrozenEvidenceCorpus([source],now=NOW),
        biocatalytic_records=bio,scientific_limits=ScientificLimits(retrieval_calls=2))
    source_result = closed.dispatch('retrieve_sources',{'product':task.target})
    bio_result = closed.dispatch('retrieve_biocatalysis',{'target_smiles':task.target})
    assert source_result['status']==bio_result['status']=='unavailable'
    attestation = HostAttestation(attestation_id='synthetic-attestation',record_id=source.record_id,
        record_sha256=record_digest(source),reaction_sha256=reaction_digest(source.reactants,source.product),
        source_content_sha256=source.source_content_sha256,checked_at=NOW,expires_at=NOW+timedelta(days=30),
        reviewer='synthetic-fixture-reviewer',decision='supported')
    changed = source.model_copy(update={'source_content_sha256':'c'*64})
    corpus = FrozenEvidenceCorpus([changed],mode='evidence_retrieval',attestations=[attestation],now=NOW)
    checked = corpus.verify(source.record_id,reactants=source.reactants,product=source.product,now=NOW)
    assert not checked['supported'] and checked['verification_status']=='stale'
    return {'closed_information_sources_withheld':True,'closed_information_biocatalysis_withheld':True,
        'stale_attestation_remains_unresolved':True,'missing_backend_capabilities_tested':len(unavailable),
        'source_review_scope':'synthetic_contract_check_not_real_source_authentication'}


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    socket.socket.connect = _forbid_external
    socket.socket.connect_ex = _forbid_external
    socket.create_connection = _forbid_external
    subprocess.Popen = _forbid_external
    started = time.monotonic()
    task,route,source,study,bio = _fixtures()
    resume = _configured(output,task,route,source,study,bio)
    evidence = _access_checks(task,source,bio)
    files = sorted((ROOT/'src/synthesis_route_gym').rglob('*.py'))+[Path(__file__).resolve()]
    receipt = {'schema_version':'srg04-tool-contract-smoke-v1','status':'passed',
        'scope':'offline_contract_behavior_only','configured_capabilities_tested':8,
        'synthetic_fixtures_not_experimental_measurements':True,
        'backend':'deterministic_python_doubles','live_llm_calls':0,'scientific_model_inferences':0,
        'hidden_evaluator_data_accessed':False,'network_and_subprocess_calls_blocked':True,
        'real_profile_modified':False,'scientific_improvement_claimed':False,
        'resume':resume,'evidence':evidence,
        'projections':{'raw_private_fields_omitted':True,'unqueried_outcomes_omitted':True,
            'predictions_not_promoted_to_measurements':True,'unavailable_not_fabricated':True,
            'model_supplied_paths_rejected':True},
        'elapsed_seconds':time.monotonic()-started,
        'source_hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        'contract_sha256':hashlib.sha256((output/'tool-contract.v1.json').read_bytes()).hexdigest()}
    _write(output/'receipt.json',receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output directory already exists; choose a fresh path')
    receipt = run(args.output)
    print(json.dumps({'status':receipt['status'],'configured_capabilities_tested':8,
        'live_llm_calls':0,'scientific_model_inferences':0,'output':str(args.output.resolve())}))


if __name__=='__main__':
    main()
