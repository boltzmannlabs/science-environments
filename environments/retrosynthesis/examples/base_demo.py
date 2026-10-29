"""Offline software demo using a synthetic route fixture, not a scientific result.

Run ``python examples/base_demo.py`` after installing synthesis-route-gym.
No predictor, provider, measured dataset, network request or credentials needed.
"""
import json

from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.route_import import import_routes
from synthesis_route_gym.schemas import Task


def main():
    task = Task(task_id='synthetic-offline-demo', target='CCO',
                inventory=[{'smiles':'CC=O'}, {'smiles':'[H][H]'}])
    payload = [{'route_id':'synthetic-fixture', 'target':'CCO', 'steps':[{
        'step_id':'fixture-step', 'product':'CCO',
        'reactants':[{'smiles':'CC=O'}, {'smiles':'[H][H]'}],
        'source_tool':'synthetic-software-fixture', 'source_version':'v1'}]}]
    imported = import_routes(payload, target=task.target, format='srg-route-candidates-v1')
    env = SynthesisRouteEnv(task)
    for route in imported['routes']:
        response = env.dispatch('propose_route', {'route':route})
        if response.get('status') != 'ok':
            raise RuntimeError('Synthetic fixture proposal failed')
    checks = env.dispatch('validate', {'route_id':'synthetic-fixture'})
    ranked = env.dispatch('rank_routes', {'route_ids':['synthetic-fixture']})
    submitted = env.dispatch('submit', {'route_ids':['synthetic-fixture']})
    for response in (checks, ranked, submitted):
        if response.get('status') != 'ok':
            raise RuntimeError('Synthetic demo action failed')
    print(json.dumps({'example_kind':'synthetic_software_demo',
        'claims_experimental_validation':False, 'import':imported,
        'validation':checks, 'ranking':ranked, 'submission':submitted}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
