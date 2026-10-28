"""Condition advice uses bounded, currently observed host evidence only."""
import copy
import json
import subprocess
import sys
import pytest
from synthesis_route_gym.condition_scientist import (
    ConditionPlan, MAX_BYTES, build_context, context_fingerprint, hydrate_plan,
    initial_state, observe, parse_plan,
)

RESOURCES = {'remaining_model_calls': 5, 'remaining_tool_calls': 10,
             'remaining_tokens': 30000, 'remaining_seconds': 120.0}


def view(**changes):
    return {'schema_version': 'srg-condition-view-v1', 'study_id': 'study-1',
        'revision': 5, 'substrate': 'CCBr', 'target': 'CCN',
        'domain_status': 'registered_measured_study',
        'measurement': {'name': 'yield', 'unit': 'percent', 'evidence_kind': 'measured_dataset_replay'},
        'candidates': [{'candidate_id': key, 'conditions': {'base': value}}
                       for key, value in [('a', 'N'), ('b', 'O'), ('c', 'C'), ('d', 'CC')]],
        'observations': [{'candidate_id': key, 'value': number, 'source_record_id': 'record-' + key,
                          'evidence_kind': 'measured_dataset_replay'} for key, number in [('a', 12.0), ('b', 24.0)]],
        'predictions': [{'candidate_id': 'c', 'prediction_id': 'prediction-c', 'status': 'scored',
                         'value': 60.0, 'unit': 'percent', 'domain': 'transfer_not_established',
                         'uncertainty': 'not_calibrated', 'model_version': 'public-model-v1'}],
        'resources': {'initial_observations': 0, 'new_observations_used': 2,
                      'remaining_observations': 2, 'remaining_actions': 20, 'remaining_seconds': 150.0},
        'submission': {'status': 'not_submitted', 'candidate_id': None},
        'unavailable_candidate_ids': [],
        'terminated': False, 'truncated': False,
        'usage': {'actions': 5, 'observation_calls': 2, 'wall_seconds': 20.0}, **changes}


def envelope(data, **changes):
    return {'status': 'ok', 'result': data, 'terminated': False, 'truncated': False, 'usage': {}, **changes}


def state(current=None):
    return observe(initial_state(), 'inspect', {}, envelope(current or view()))


def context(current=None):
    return build_context(state(current), RESOURCES)


def plan(current, **changes):
    return {'schema_version': 'srg-condition-plan-v1', 'context_sha256': context_fingerprint(current),
            'decision': 'observe', 'next_candidate_id': 'c', 'cited_observation_ids': ['record-b'],
            'cited_prediction_ids': ['prediction-c'], 'rationale': 'Compare the next unobserved recipe.',
            'evidence_status': 'agent_proposal', **changes}


def test_context_plan_and_hydration_round_trip():
    current = context()
    assert current['trigger'] == 'feedback_after_two_queries'
    parsed = parse_plan(json.dumps(plan(current)), current)
    assert parse_plan(json.dumps(parsed), current) == parsed
    hydrated = hydrate_plan(parsed, current)
    assert hydrated['selected_conditions'] == {'base': 'C'}
    assert hydrated['supporting_observations'][0]['value'] == 24
    assert hydrated['cited_predictions'][0]['uncertainty'] == 'not_calibrated'
    assert hydrated['evidence_status'] == 'agent_proposal'


def test_all_outputs_are_detached_and_arguments_do_not_supply_evidence():
    raw, original = view(), initial_state()
    baseline = copy.deepcopy((raw, original))
    saved = observe(original, 'inspect', {'secret_yield': 99}, envelope(raw))
    current = build_context(saved, RESOURCES)
    parsed = parse_plan(json.dumps(plan(current)), current)
    hydrated = hydrate_plan(parsed, current)
    hydrated['selected_conditions']['base'] = 'changed'
    current['view']['candidates'][0]['conditions']['base'] = 'changed'
    assert (raw, original) == baseline
    assert saved['view']['candidates'][0]['conditions']['base'] == 'N'
    assert 'secret_yield' not in json.dumps(saved)
    assert parsed == plan(context())


@pytest.mark.parametrize('count,remaining', [(0, 3), (1, 2), (2, 0)])
def test_insufficient_feedback_or_allowance_suppresses(count, remaining):
    raw = view()
    raw['observations'] = raw['observations'][:count]
    raw['resources'] = {**raw['resources'], 'new_observations_used': count, 'remaining_observations': remaining}
    raw['usage']['observation_calls'] = count
    assert context(raw) is None


def test_initial_observations_are_not_new_queries():
    raw = view()
    raw['resources'] = {**raw['resources'], 'initial_observations': 2, 'new_observations_used': 0}
    raw['usage']['observation_calls'] = 0
    assert context(raw) is None


def test_unknown_domain_closed_or_missing_view_suppresses():
    assert context(view(domain_status='unrelated_chemistry')) is None
    assert build_context(initial_state(), RESOURCES) is None
    for flag in ('terminated', 'truncated'):
        assert build_context(observe(state(), 'inspect', {}, envelope(view(), **{flag: True})), RESOURCES) is None
    assert context(view(submission={'status': 'selected', 'candidate_id': 'a'}, terminated=True)) is None


def test_no_unobserved_candidates_suppresses():
    raw = view()
    raw['candidates'], raw['predictions'] = raw['candidates'][:2], []
    assert context(raw) is None


def test_actions_update_only_from_host_view():
    updated = view(revision=6)
    for action in ('observe_condition', 'predict_reaction_yield'):
        saved = observe(state(), action, {'view': view(study_id='forged')}, envelope({'view': updated}))
        assert saved['view'] == updated
    assert observe(state(), 'irrelevant', {}, envelope({'view': updated})) == state()
    assert observe(state(), 'inspect', {}, envelope(updated, status='error')) == state()


@pytest.mark.parametrize('field,value', [('study_id', 'other'), ('substrate', 'N'), ('target', 'O'),
    ('candidates', [{'candidate_id': 'invented', 'conditions': {'base': 'O'}}]), ('predictions', []),
    ('measurement', {'name': 'CAD', 'unit': 'percent', 'evidence_kind': 'measured_dataset_replay'})])
def test_study_identity_and_frozen_inputs_cannot_change(field, value):
    with pytest.raises(ValueError):
        observe(state(), 'inspect', {}, envelope(view(**{field: value, 'revision': 6})))


def test_stale_revision_or_changed_observation_rejected():
    with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(view(revision=4)))
    changed = view(revision=6)
    changed['observations'][0]['value'] = 99
    with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(changed))
    changed['observations'] = changed['observations'][1:]
    with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(changed))


@pytest.mark.parametrize('mutate', [
    lambda v: v.update(optimum=100),
    lambda v: v['candidates'][0].update(yield_percent=100),
    lambda v: v['candidates'][0]['conditions'].update(yield_percent='100'),
    lambda v: v['observations'][0].update(value=float('nan')),
    lambda v: v['observations'][0].update(value=True),
    lambda v: v['observations'][0].update(evidence_kind='predicted'),
    lambda v: v['observations'].append(copy.deepcopy(v['observations'][0])),
    lambda v: v['predictions'][0].update(value=float('inf')),
    lambda v: v['predictions'][0].update(status='abstained'),
    lambda v: v['predictions'][0].update(candidate_id='unknown'),
    lambda v: v['candidates'].append(copy.deepcopy(v['candidates'][0])),
    lambda v: v['resources'].update(new_observations_used=True),
])
def test_bad_host_views_rejected(mutate):
    raw = view(); mutate(raw)
    with pytest.raises(ValueError): state(raw)


@pytest.mark.parametrize('changes', [
    {'context_sha256': '0' * 64}, {'next_candidate_id': 'a'}, {'next_candidate_id': 'unknown'},
    {'next_candidate_id': None}, {'decision': 'abstain'}, {'cited_observation_ids': ['record-c']},
    {'cited_prediction_ids': ['invented']}, {'cited_observation_ids': ['record-b', 'record-b']},
    {'cited_prediction_ids': ['prediction-c', 'prediction-c']}, {'rationale': ' '},
    {'rationale': 'x' * 1201}, {'predicted_yield': 100}, {'evidence_status': 'measured'}, {'decision': 'execute'},
])
def test_invalid_or_fabricated_plan_rejected(changes):
    current = context()
    with pytest.raises(ValueError): parse_plan(json.dumps(plan(current, **changes)), current)


def test_abstention_and_unscored_predictions_explicit():
    raw = view()
    raw['predictions'][0] = {**raw['predictions'][0], 'status': 'abstained', 'value': None}
    current = context(raw)
    parsed = parse_plan(json.dumps(plan(current, decision='abstain', next_candidate_id=None)), current)
    hydrated = hydrate_plan(parsed, current)
    assert hydrated['selected_conditions'] is None
    assert hydrated['cited_predictions'][0]['value'] is None


@pytest.mark.parametrize('raw', ['[]', 'NaN', '{} extra', '```json\n{}\n```',
    '{"decision":"observe","decision":"abstain"}', 'x' * 100001])
def test_only_bounded_unique_key_json_object_allowed(raw):
    with pytest.raises(ValueError): parse_plan(raw, context())


@pytest.mark.parametrize('bad', [True, -1, float('nan'), float('inf'), '3'])
def test_bad_resources_rejected(bad):
    with pytest.raises(ValueError): build_context(state(), {**RESOURCES, 'remaining_seconds': bad})


def test_fingerprint_canonical_and_resource_bound():
    current = context()
    assert context_fingerprint(current) == context_fingerprint(dict(reversed(list(current.items()))))
    assert context_fingerprint(current) != context_fingerprint({**current, 'resources': {
        **current['resources'], 'remaining_model_calls': 4}})


def test_input_size_limit_and_no_rdkit_import():
    raw = view()
    raw['candidates'] = [{'candidate_id': str(i), 'conditions': {'base': 'C' * 1500}} for i in range(100)]
    with pytest.raises(ValueError): state(raw)
    assert len(json.dumps(context()).encode()) < MAX_BYTES
    code = 'import sys; sys.modules["rdkit"]=None; import synthesis_route_gym.condition_scientist; print("ok")'
    run = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def test_plan_frozen_and_hydration_revalidates():
    current = context()
    typed = ConditionPlan.model_validate(plan(current))
    with pytest.raises(ValueError): typed.decision = 'abstain'
    with pytest.raises(ValueError): hydrate_plan(plan(current, next_candidate_id='unknown'), current)


def test_reserved_but_unreturned_queries_do_not_trigger_feedback_advice():
    raw = view()
    raw['observations'] = []
    assert context(raw) is None


@pytest.mark.parametrize('bad_state', [None, {}, {'schema_version': 'wrong'},
    {**initial_state(), 'identity_sha256': 'a' * 64},
    {**initial_state(), 'closed': 'yes'}])
def test_observer_snapshot_validation(bad_state):
    with pytest.raises(ValueError): observe(bad_state, 'inspect', {}, envelope(view()))


def test_corrupt_saved_identity_and_budget_reset_rejected():
    saved = state()
    saved['identity_sha256'] = '0' * 64
    with pytest.raises(ValueError): build_context(saved, RESOURCES)
    for resource, value in [('initial_observations', 1), ('remaining_actions', 99),
                            ('remaining_observations', 99)]:
        changed = view(revision=6)
        changed['resources'][resource] = value
        with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(changed))


def test_malformed_envelopes_contexts_and_zero_runtime_resources():
    for arguments, response in [(None, envelope(view())), ({}, None),
                                ({}, envelope(view(), terminated=1)), ({}, envelope(None))]:
        with pytest.raises(ValueError): observe(state(), 'inspect', arguments, response)
    for key in RESOURCES:
        assert build_context(state(), {**RESOURCES, key: 0}) is None
    for wrong in [{}, {**context(), 'extra': 1}, {**context(), 'trigger': 'manual'},
                  {**context(), 'view': view(domain_status='unknown')}]:
        with pytest.raises(ValueError): context_fingerprint(wrong)


@pytest.mark.parametrize('mutate', [
    lambda raw: raw.update(submission={'status': 'abstained', 'candidate_id': 'a'}),
    lambda raw: raw.update(submission={'status': 'selected', 'candidate_id': 'd'}),
    lambda raw: raw['resources'].update(initial_observations=3),
    lambda raw: raw['usage'].update(observation_calls=99),
])
def test_inconsistent_host_accounting_or_submission_rejected(mutate):
    raw = view(); mutate(raw)
    with pytest.raises(ValueError): state(raw)


def test_same_revision_cannot_publish_additional_observation():
    raw = view()
    raw['observations'].append({'candidate_id': 'c', 'value': 40.0,
        'source_record_id': 'record-c', 'evidence_kind': 'measured_dataset_replay'})
    raw['resources'] = {**raw['resources'], 'new_observations_used': 3, 'remaining_observations': 1}
    raw['usage']['observation_calls'] = 3
    with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(raw))


def test_query_allowance_total_cannot_change_between_views():
    raw = view(revision=6)
    raw['resources']['new_observations_used'] = 3
    raw['usage']['observation_calls'] = 3
    with pytest.raises(ValueError): observe(state(), 'inspect', {}, envelope(raw))


def test_real_condition_episode_feedback_builds_a_valid_cited_plan():
    from synthesis_route_gym.condition_episode import ConditionEpisode
    from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy
    records = tuple(ConditionRecord(key, (('base', reagent),), number)
                    for key, reagent, number in [('a', 'N', 12.0), ('b', 'O', 24.0),
                                                  ('c', 'C', 36.0), ('d', 'CC', 48.0)])
    study = FiniteConditionStudy(records, (), 4, 'https://example.org/source', 'fixture-study', 'a' * 64, 'CCBr')
    env = ConditionEpisode(study, study_id='study-1', predictions=view()['predictions'], target='CCN')
    observer = observe(initial_state(), 'inspect', {}, env.dispatch('inspect', {}))
    assert build_context(observer, RESOURCES) is None
    for ident in ('a', 'b'):
        args = {'candidate_id': ident}
        observer = observe(observer, 'observe_condition', args, env.dispatch('observe_condition', args))
    current = build_context(observer, RESOURCES)
    observed_id = current['view']['observations'][0]['source_record_id']
    parsed = parse_plan(json.dumps(plan(current, cited_observation_ids=[observed_id])), current)
    assert hydrate_plan(parsed, current)['supporting_observations'][0]['value'] == 12.0
    assert 'dataset_optimum' not in json.dumps(current)
    assert 'yield_percent' not in json.dumps(current)


def test_interrupted_unknown_candidates_cannot_be_recommended():
    raw = view(unavailable_candidate_ids=['c'])
    raw['resources'] = {**raw['resources'], 'new_observations_used': 3, 'remaining_observations': 1}
    raw['usage']['observation_calls'] = 3
    current = context(raw)
    with pytest.raises(ValueError): parse_plan(json.dumps(plan(current)), current)
    assert parse_plan(json.dumps(plan(current, next_candidate_id='d')), current)['next_candidate_id'] == 'd'
    raw['unavailable_candidate_ids'] = ['c', 'd']
    assert context(raw) is None


@pytest.mark.parametrize('ids', [['unknown'], ['a'], ['c', 'c']])
def test_invalid_unavailable_candidates_rejected(ids):
    with pytest.raises(ValueError): state(view(unavailable_candidate_ids=ids))


def test_unavailable_candidate_cannot_silently_become_queryable_again():
    raw = view(unavailable_candidate_ids=['c'])
    before = state(raw)
    with pytest.raises(ValueError):
        observe(before, 'inspect', {}, envelope(view(revision=6, unavailable_candidate_ids=[])))
