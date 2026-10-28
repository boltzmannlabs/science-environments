"""Unlimited search contracts using finite synthetic graphs, no scientific models."""
import pytest

from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.fixed_search import run_best_first_workflow
from synthesis_route_gym.planning import run_fixed_workflow
from synthesis_route_gym.schemas import Budget, Constraints, InventoryItem, Task
from synthesis_route_gym.synthchem_search import run_synthchem_workflow


CHOICES = {
    'CCOC(C)=O': [['CCO', 'CC(=O)O']],
    'CCO': [['C=C', 'O']],
    'CC(=O)O': [['CC=O', 'O']],
}


def environment(*, choices=None, top_k=10, budget=None, fail=False, **kwargs):
    choices = CHOICES if choices is None else choices
    task = Task(task_id='unbudgeted-search-fixture', target='CCOC(C)=O',
        inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC=O')),
        budget=budget or Budget.unbudgeted(top_k=top_k), **kwargs)

    def expand(smiles, width):
        if fail:
            raise RuntimeError('synthetic operational failure')
        return {'status': 'ok', 'predictions': [
            {'product': smiles, 'reactants': reactants,
             'source': {'tool': 'finite-fixture', 'version': '1'}}
            for reactants in choices.get(smiles, [])][:width]}

    return SynthesisRouteEnv(task, expand=expand)


@pytest.mark.parametrize('workflow', [run_fixed_workflow, run_best_first_workflow])
def test_unbudgeted_fixed_search_crosses_old_frontier_cap(workflow):
    result = workflow(environment(), max_frontier_states=1)
    assert result['episode']['submitted_route_ids']
    assert result['search_states'] > 1
    assert result['episode']['usage']['expansions'] == 3
    assert result['max_frontier_states'] is None
    assert result['stop_reason'] == 'frontier_exhausted'


@pytest.mark.parametrize('algorithm', ['astar', 'mcts', 'portfolio'])
def test_native_unbudgeted_graph_crosses_old_node_cap_and_exhausts(algorithm):
    result = run_synthchem_workflow(environment(), algorithm=algorithm, max_graph_nodes=1)
    assert len(result['accepted_route_ids']) == 1
    assert result['max_graph_nodes_per_phase'] is None
    assert result['stop_reason'] == 'frontier_exhausted'
    assert all(row['graph_nodes'] > 1 for row in result['searches'])
    assert all(row['termination'] == 'frontier_exhausted' for row in result['searches'])
    assert all(row['allocated_expansion_actions'] is None for row in result['searches'])
    assert result['proposal_pool']['backend_calls'] == 3


@pytest.mark.parametrize('algorithm', ['astar', 'mcts', 'portfolio'])
def test_native_budgeted_and_unbudgeted_return_identical_route_identity(algorithm):
    budget = Budget(max_expansions=20, max_wall_seconds=30)
    finite = run_synthchem_workflow(environment(budget=budget), algorithm=algorithm)
    unlimited = run_synthchem_workflow(environment(), algorithm=algorithm)
    assert unlimited['accepted_route_ids'] == finite['accepted_route_ids']
    assert unlimited['episode']['routes'] == finite['episode']['routes']
    assert unlimited['episode']['assessments'] == finite['episode']['assessments']


@pytest.mark.parametrize('workflow', [run_fixed_workflow, run_best_first_workflow,
                                    run_synthchem_workflow])
def test_operational_failure_is_not_natural_exhaustion(workflow):
    result = workflow(environment(fail=True))
    assert result['stop_reason'] == 'backend_failure'
    assert not result['episode']['submitted_route_ids']


@pytest.mark.parametrize('algorithm', ['astar', 'mcts', 'portfolio'])
def test_native_unbudgeted_stops_on_requested_routes(algorithm):
    result = run_synthchem_workflow(environment(top_k=1), algorithm=algorithm)
    assert len(result['accepted_route_ids']) == 1
    assert result['stop_reason'] == 'route_quota'


@pytest.mark.parametrize('algorithm', ['astar', 'mcts', 'portfolio'])
def test_native_unbudgeted_still_obeys_task_depth(algorithm):
    result = run_synthchem_workflow(environment(constraints=Constraints(max_steps=1)),
                                   algorithm=algorithm)
    assert not result['accepted_route_ids']
    assert result['stop_reason'] == 'frontier_exhausted'


def test_unbudgeted_native_scheduler_is_round_robin_without_phase_quota(monkeypatch):
    import synthesis_route_gym.synthchem_unbounded as native
    visits = []
    original = native.UnboundedNativePhase.advance

    def advance(phase):
        visits.append(phase.name)
        return original(phase)

    monkeypatch.setattr(native.UnboundedNativePhase, 'advance', advance)
    run_synthchem_workflow(environment())
    assert visits[:4] == ['astar', 'mcts', 'astar', 'mcts']


def test_unbudgeted_native_constructor_has_no_hidden_limits():
    from synthesis_route_gym.synthchem_pool import EnvironmentProposalPool
    from synthesis_route_gym.synthchem_unbounded import UnboundedNativePhase
    env = environment()
    pool = EnvironmentProposalPool(env, 10, 1, 0)
    for name in ('astar', 'mcts'):
        phase = UnboundedNativePhase(pool, name, frozenset(), seed=0, depth=3)
        for field in ('limit_iterations', 'limit_reaction_model_calls',
                      'limit_graph_nodes', 'time_limit_s'):
            assert getattr(phase.search, field) is None
        phase.close('fixture_cleanup')


@pytest.mark.parametrize('top_k',[1,10])
@pytest.mark.parametrize('cancel_action',['propose_route','submit'])
def test_cancellation_during_submission_is_not_natural_completion(monkeypatch,top_k,cancel_action):
    env = environment(top_k=top_k)
    dispatch = env.dispatch
    def cancel_proposal(action, arguments, **kwargs):
        if action == cancel_action:
            env.cancel('external interruption during finalization')
        return dispatch(action, arguments, **kwargs)
    monkeypatch.setattr(env, 'dispatch', cancel_proposal)
    result = run_synthchem_workflow(env, algorithm='astar')
    assert result['stop_reason'] == 'episode_closed_before_submission'
    assert result['submission_status'] == ('not_submitted_episode_closed' if cancel_action == 'propose_route' else 'not_submitted_closed')
    assert not result['accepted_route_ids']
    assert result['episode']['truncated']
    assert result['status'] == 'interrupted'
    assert not result['naturally_completed']
