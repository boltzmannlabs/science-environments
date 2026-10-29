"""Bounded live check of the learned condition tool through the Sci bridge.

Candidates use known component identities from model metadata. No measured
outcomes, dataset rows, hidden evaluator or model filesystem tools reach the LLM.
This is an integration check, never a held-out model-quality benchmark.
"""
import argparse
import hashlib
import json
from pathlib import Path

from synthesis_route_gym.agent_bridge import run_agent_scientist_bridge
from synthesis_route_gym.agent_runner import AgentBudget
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.planning import environment_tool_schemas
from synthesis_route_gym.ranking import COMPONENTS, ConditionRanker
from synthesis_route_gym.schemas import Task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scientist-python', type=Path, required=True)
    parser.add_argument('--scientist-source', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    model = ConditionRanker.load(args.model)
    known = model.metadata['training_component_smiles']
    candidate = {'id': 'metadata-combination', **{role: known[role][0] for role in COMPONENTS}}
    task = Task(task_id='condition-tool-smoke', target='CCO', inventory=[],
                budget={'max_actions': 3, 'max_expansions': 1, 'max_wall_seconds': 120,
                        'max_llm_tokens': 100000, 'top_k': 1})
    environment = SynthesisRouteEnv(task, condition_ranker=model)
    schemas = [s for s in environment_tool_schemas() if s['name'] == 'predict_conditions']
    if len(schemas) != 1:
        raise RuntimeError('Core predict_conditions schema is unavailable; no model call made')
    result = run_agent_scientist_bridge(
        'Integration test only. Call predict_conditions exactly once with the following candidates. '
        'Then report only the predicted yield and say it is a prediction, not measured evidence. '
        'Do not propose or submit synthesis routes. Candidate combination: ' + json.dumps([candidate]),
        environment.dispatch, tool_schemas=schemas,
        scientist_python=args.scientist_python, scientist_source=args.scientist_source,
        budget=AgentBudget(max_model_calls=2, max_tool_calls=1, wall_seconds=120,
                           max_output_tokens_per_call=512, max_total_tokens=task.budget.max_llm_tokens))
    episode = environment.export()
    invoked = any(event['action'] == 'predict_conditions' and event['status'] == 'ok'
                  for event in episode['events'])
    receipt = {key: result[key] for key in ['backend', 'model', 'provider', 'completed', 'usage', 'ledger']}
    receipt.update(test_kind='learned_condition_tool_integration_only',
                   scientific_model_version=model.metadata['model_version'],
                   scientific_model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),
                   candidate_source='training_component_identities_only_no_measured_outcomes',
                   final_response=result['final_response'], scientific_tool_invoked=invoked, episode=episode)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in {'episode', 'final_response'}}))
    if not invoked:
        raise SystemExit('Condition tool was not successfully invoked; receipt retained')


if __name__ == '__main__':
    main()
