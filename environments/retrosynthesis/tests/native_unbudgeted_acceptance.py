"""Executed by the actual Sci interpreter with no network/provider access."""
import json
import os
from pathlib import Path
import site
import sys
import tempfile
from unittest.mock import patch

source = Path(sys.argv[1])
sys.path.insert(0, str(source))
from pm.environments import committed_venv, site_packages
site.addsitedir(str(site_packages(committed_venv(source))))


def main():
    with tempfile.TemporaryDirectory() as temp, patch('socket.socket.connect', side_effect=AssertionError('network forbidden')):
        os.environ['SCI_HOME'] = temp
        os.environ['SCI_RUNTIME_DIR'] = str(Path(temp)/'runtime')
        (Path(temp)/'config.yaml').write_text('agent:\n  run_budget_seconds: 0.001\n  budget_warning_ratio: 0.5\n')
        from run_agent import AIAgent
        from agent.turn_iteration_prep import _maybe_inject_iteration_budget_warning
        from agent.turn_context import _reset_per_turn_agent_state
        from agent.transports.codex import ResponsesApiTransport
        from openai.types.chat import ChatCompletion

        response = ChatCompletion(id='offline', object='chat.completion', created=1,
            model='fixture-model', choices=[{'index':0,'finish_reason':'stop',
                'message':{'role':'assistant','content':'offline native completed'}}],
            usage={'prompt_tokens':5,'completion_tokens':2,'total_tokens':7})
        calls = []
        class OfflineAgent(AIAgent):
            def _interruptible_api_call(self, *args, **kwargs):
                calls.append('api')
                return response
            def _interruptible_streaming_api_call(self, *args, **kwargs):
                calls.append('stream')
                return response

        from agent.iteration_budget import IterationBudget
        for limits in ({'max_iterations':1},
                       {'max_iterations':None,'iteration_budget':IterationBudget(1)}):
            try:
                mixed = OfflineAgent(model='fixture-model',provider='openai-compat',
                    api_key='offline',base_url='http://127.0.0.1:1/v1',
                    unbudgeted_run=True,max_tokens=None,enabled_toolsets=[],quiet_mode=True,
                    skip_memory=True,skip_context_files=True,skip_background_review=True,
                    fallback_model=[],**limits)
            except ValueError:
                pass
            else:
                mixed.close()
                raise AssertionError('Unbudgeted native construction accepted a finite iteration ceiling')

        agent = OfflineAgent(model='fixture-model', provider='openai-compat',
            api_key='offline', base_url='http://127.0.0.1:1/v1',
            max_iterations=None, run_budget_seconds=None, unbudgeted_run=True,
            max_tokens=None, enabled_toolsets=[], quiet_mode=True, skip_memory=True,
            skip_context_files=True, skip_background_review=True, fallback_model=[])
        try:
            assert agent.max_iterations is None
            assert agent.iteration_budget.max_total is None
            assert agent.run_budget_seconds is None, 'profile wall budget leaked'
            assert agent.max_tokens is None
            agent.iteration_budget._used = sys.maxsize * 2
            assert agent.iteration_budget.consume()
            assert agent.iteration_budget.remaining is None
            assert not _maybe_inject_iteration_budget_warning(agent, [{'role':'tool','content':'ok'}])
            _reset_per_turn_agent_state(agent)
            assert agent.iteration_budget.max_total is None
            result = agent.run_conversation('Return the offline response.', task_id='offline-srg12')
            assert result['completed'], result.get('error', result.get('turn_exit_reason'))
            assert result['final_response'] == 'offline native completed'
            assert len(calls) == 1, calls
            kwargs = ResponsesApiTransport().build_kwargs(model='fixture-model', messages=[{'role':'user','content':'x'}],
                tools=None, max_tokens=None, provider='openai-codex', base_url='https://chatgpt.com/backend-api/codex')
            assert 'max_output_tokens' not in kwargs
        finally:
            agent.close()
            from sci_logging import flush_log_queue, release_profile_log_handlers
            flush_log_queue()
            release_profile_log_handlers(temp)
        print(json.dumps({'completed':True,'provider_calls':0,'offline_native_calls':len(calls),
                          'max_iterations':None,'max_output_tokens':None,'run_budget_seconds':None}))


if __name__ == '__main__':
    main()
