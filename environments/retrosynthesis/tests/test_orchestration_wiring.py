"""New orchestration modes retain one main conversation and bound policy on resume."""
import copy
import pytest
from synthesis_route_gym.agent_runner import run_agent_scientist
from synthesis_route_gym.cli import _parser


SCHEMAS = [{'name': n, 'parameters': {'type': 'object'}} for n in ('inspect', 'submit')]


class Backend:
    def __init__(self, failure=False):
        self.calls = []
        self.failure = failure

    def run(self, **kw):
        self.calls.append(kw)
        request = kw['ledger'].claim_model_call(estimated_input_tokens=20, reserved_output_tokens=10)
        if self.failure:
            raise OSError('provider-private-detail')
        kw['executor']('inspect', {})
        kw['executor']('submit', {'route_ids': []})
        kw['ledger'].settle_request(request, 12)
        return {'completed': True, 'final_response': 'submitted', 'messages': [],
                'model': kw['profile'].model, 'provider': kw['profile'].provider,
                'usage': {'total_tokens': 12}, 'token_confirmations': {request: 12}}


@pytest.fixture
def home(tmp_path):
    (tmp_path / 'config.yaml').write_text('model:\n  default: configured-main\n  provider: configured-provider\n')
    return tmp_path


def execute(name, args):
    return {'status': 'ok', 'result': {}, 'terminated': name == 'submit', 'truncated': False}


def run(home, backend, mode, **kwargs):
    return run_agent_scientist('same task', execute, tool_schemas=SCHEMAS, profile_home=home,
                               mode=mode, backend=backend, **kwargs)


@pytest.mark.parametrize('mode', ['main_role_prompt', 'main_adaptive', 'main_all_advisors'])
def test_ineligible_modes_have_no_extra_requests(home, mode):
    backend = Backend(); result = run(home, backend, mode)
    assert result['completed'] and result['submission_status'] == 'submitted'
    assert [kw['role'] for kw in backend.calls] == ['main']
    assert result['ledger']['model_calls'] == 1
    assert result['ledger']['tool_calls'] == 2
    assert result['orchestration_runs'] == []
    assert result['orchestration']['schema_version'] == 'srg-orchestration-result-v1'


def test_role_prompt_control_adds_instructions_without_other_conversations(home):
    backend = Backend(); run(home, backend, 'main_role_prompt')
    prompt = backend.calls[0]['prompt'].lower()
    assert 'strategist' in prompt and 'condition' in prompt and 'critic' in prompt


def test_completed_resume_does_not_repeat_or_reset_ledger(home):
    saved = []; first = run(home, Backend(), 'main_adaptive', checkpoint=lambda state: saved.append(copy.deepcopy(state)))
    backend = Backend(); again = run(home, backend, 'main_adaptive', resume_state=saved[-1])
    assert not backend.calls and again['ledger']['model_calls'] == first['ledger']['model_calls']
    assert again['orchestration_runs'] == []
    assert saved[-1]['schema_version'] == 'srg-agent-runtime-orchestrated-v1'


def test_policy_is_host_only_and_rejects_unknown_fields_before_requests(home):
    backend = Backend()
    with pytest.raises(ValueError):
        run(home, backend, 'main_adaptive', orchestration_policy={'promotion_claim': 'trust me'})
    assert not backend.calls


def test_failure_has_final_orchestration_report_and_retains_reservation(home):
    result = run(home, Backend(failure=True), 'main_adaptive')
    assert not result['completed'] and result['submission_status'] == 'not_submitted'
    assert result['ledger']['model_calls'] == 1 and result['ledger']['reserved_tokens'] == 30
    assert result['orchestration']['schema_version'] == 'srg-orchestration-result-v1'
    assert 'provider-private-detail' not in str(result)


@pytest.mark.parametrize('mode', ['main_role_prompt', 'main_adaptive', 'main_all_advisors'])
def test_cli_exposes_modes_and_host_policy(mode):
    args = _parser().parse_args(['agent', '--task', 't.json', '--output', 'r.json',
        '--scientist-python', '/python', '--scientist-source', '/sci', '--method', mode,
        '--orchestration-policy', 'host-policy.json'])
    assert args.method == mode and args.orchestration_policy == 'host-policy.json'
