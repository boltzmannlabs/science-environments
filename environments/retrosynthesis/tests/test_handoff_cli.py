"""Local handoff CLI uses the same explicit host configuration as agent episodes."""
import json
import pytest
from synthesis_route_gym.cli import _parser, execute


def test_handoff_command_forwards_typed_input_and_persistent_paths(tmp_path, monkeypatch):
    import synthesis_route_gym.handoff_runner as runner
    source = tmp_path / 'candidate.json'
    source.write_text(json.dumps({'candidate_id': 'c', 'smiles': 'CCO', 'source_job_id': 'j',
                                 'source_tool': 'upstream', 'inventory': []}))
    calls = []
    def run(args, handoff, output_dir, **kwargs):
        calls.append((args, handoff, output_dir, kwargs))
        return {'schema_version': 'test-receipt'}
    monkeypatch.setattr(runner, 'run_handoff', run)
    args = _parser().parse_args(['handoff', '--input', str(source), '--output', str(tmp_path / 'out.json'),
        '--output-dir', str(tmp_path / 'episode'), '--scientist-python', '/python',
        '--scientist-source', '/sci', '--method', 'main_adaptive', '--resume'])
    assert execute(args) == {'schema_version': 'test-receipt'}
    assert calls[0][1].candidate_id == 'c'
    assert calls[0][3]['resume'] is True
    assert calls[0][2] == str(tmp_path / 'episode')
    assert callable(calls[0][3]['environment_options']['expand'])


def test_handoff_cli_default_remains_main():
    args = _parser().parse_args(['handoff', '--input', 'i', '--output', 'o', '--output-dir', 'd',
        '--scientist-python', '/python', '--scientist-source', '/sci'])
    assert args.method == 'main' and args.orchestration_policy is None


def test_handoff_cli_rejects_oversize_file_before_decoding(tmp_path):
    source = tmp_path / 'oversize.json'
    with source.open('wb') as stream:
        stream.truncate(20_000_001)
    args = _parser().parse_args(['handoff', '--input', str(source), '--output', 'o', '--output-dir', 'd',
        '--scientist-python', '/python', '--scientist-source', '/sci'])
    with pytest.raises(ValueError, match='20 MB'):
        execute(args)
