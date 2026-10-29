"""Public naming and monorepo artifacts remain portable across release export."""
import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_public_name_and_legacy_entrypoint_are_available():
    metadata = (ROOT / 'pyproject.toml').read_text()
    assert 'name = "retrosynthesis"' in metadata
    assert 'retrosynthesis = "synthesis_route_gym.cli:main"' in metadata
    assert 'synthesis-route-gym = "synthesis_route_gym.cli:main"' in metadata
    manifest = yaml.safe_load((ROOT / 'integrations/agent_scientist/plugin.yaml').read_text())
    assert manifest['name'] == 'retrosynthesis'
    assert manifest['provides_tools'] == ['srg_action']
    assert (ROOT / 'skills/retrosynthesis/SKILL.md').is_file()


def test_monorepo_artifacts_survive_safe_export(tmp_path):
    spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/prepare_base_release.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = ['README.md', 'pyproject.toml', 'ENVIRONMENT_SPEC.md', 'STATUS.md',
                'config/README.md', 'config/local.yaml', 'tasks/README.md',
                'tasks/example.json', 'results/validation-summary.json']
    excluded = ['config/auth.json', 'config/.env', 'tasks/private/answers.json',
                'results/raw.csv', 'results/credentials.yaml']
    source = tmp_path / 'source'
    for name in expected + excluded:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{}\n')
    report = module.prepare(source, tmp_path / 'export')
    assert set(report['files']) == set(expected)
    assert module.verify(tmp_path / 'export')['verified']


def test_container_build_copies_dependency_notices():
    assert 'COPY THIRD_PARTY_NOTICES.md /app/THIRD_PARTY_NOTICES.md' in (ROOT / 'Dockerfile').read_text()


def test_cli_displays_public_name(capsys):
    import pytest
    from synthesis_route_gym.cli import main
    with pytest.raises(SystemExit) as result:
        main(['--help'])
    assert result.value.code == 0
    assert 'usage: retrosynthesis ' in capsys.readouterr().out
