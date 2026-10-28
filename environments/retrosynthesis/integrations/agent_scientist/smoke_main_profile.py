"""Explicitly invoked, bounded live smoke using only the configured main model."""
import argparse
import json
import os
from pathlib import Path
import site
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scientist-source', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    source = args.scientist_source.resolve()
    os.environ['SCI_HOME'] = str(Path.home() / '.sci')
    sys.path.insert(0, str(source))
    from pm.environments import committed_venv, site_packages
    runtime = committed_venv(source)
    if runtime is None:
        raise RuntimeError('No committed Agent Scientist runtime')
    site.addsitedir(str(site_packages(runtime)))
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
    from synthesis_route_gym.agent_runner import AgentBudget, run_agent_scientist
    schema = {'name': 'inspect', 'description': 'Read the test environment status.',
              'parameters': {'type': 'object', 'properties': {}, 'additionalProperties': False}}
    result = run_agent_scientist(
        'This is an integration smoke test. Call inspect exactly once, then say OK. No chemistry planning is needed.',
        lambda name, arguments: {'status': 'ok'}, tool_schemas=[schema],
        budget=AgentBudget(max_model_calls=2, max_tool_calls=1, wall_seconds=120,
                           max_output_tokens_per_call=128, max_total_tokens=100000),
    )
    receipt = {key: result[key] for key in ['backend', 'model', 'provider', 'completed', 'usage', 'ledger']}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
