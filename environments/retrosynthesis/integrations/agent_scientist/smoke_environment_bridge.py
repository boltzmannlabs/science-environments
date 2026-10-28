"""Live integration check: trivial in-stock target, not synthesis validation."""
import argparse
import json
from pathlib import Path
from synthesis_route_gym.agent_runner import AgentBudget
from synthesis_route_gym.agent_bridge import run_agent_scientist_bridge
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task
from synthesis_route_gym.planning import environment_tool_schemas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scientist-python', type=Path, required=True)
    parser.add_argument('--scientist-source', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    task = Task(task_id='bridge-smoke-in-stock', target='CCO', inventory=[{'smiles': 'CCO'}],
                budget={'max_actions': 8, 'max_expansions': 1, 'max_wall_seconds': 120,
                        'max_llm_tokens': 100000, 'top_k': 1})
    env = SynthesisRouteEnv(task)
    result = run_agent_scientist_bridge(
        'Integration check. The target CCO is already in inventory. Call inspect, propose_route with '
        '{"route":{"route_id":"in-stock","target":"CCO","steps":[]}}, then submit '
        '{"route_ids":["in-stock"]}. Return OK. This is a trivial in-stock case, not evidence of synthesis skill.',
        env.dispatch, tool_schemas=environment_tool_schemas(),
        scientist_python=args.scientist_python, scientist_source=args.scientist_source,
        budget=AgentBudget(max_model_calls=5, max_tool_calls=5, wall_seconds=120,
                           max_output_tokens_per_call=256, max_total_tokens=task.budget.max_llm_tokens))
    receipt = {key: result[key] for key in ['backend','model','provider','completed','usage','ledger']}
    receipt['test_kind'] = 'trivial_in_stock_integration_only'
    receipt['episode'] = env.export()
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'episode'}))


if __name__ == '__main__':
    main()
