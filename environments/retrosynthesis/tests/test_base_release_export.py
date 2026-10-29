"""A source release must not inherit the research workspace's data or secrets."""
import importlib.util
import json
from pathlib import Path

import pytest


def exporter():
    path = Path(__file__).parents[1] / 'scripts/prepare_base_release.py'
    spec = importlib.util.spec_from_file_location('base_release_export', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(root):
    for name in ('pyproject.toml', 'README.md', '.gitignore',
                 'src/synthesis_route_gym/__init__.py', 'tests/test_example.py',
                 'docs/BASE_RELEASE.md', 'integrations/agent_scientist/plugin.yaml'):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# source fixture\n')
    for name in ('artifacts/private/answers.json', '.env', '.venv-aizynth/bin/python',
                 'build/private.txt', 'examples/portfolio/doyle_measured_subset.csv',
                 'examples/applications/conditions/science-config.json',
                 'src/synthesis_route_gym/__pycache__/hidden.pyc'):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('excluded bytes')
    return root


def test_export_is_allowlisted_hashed_and_does_not_change_source(tmp_path):
    module = exporter()
    source = fixture(tmp_path / 'source')
    output = tmp_path / 'release'
    report = module.prepare(source, output)
    names = set(report['files'])
    assert 'src/synthesis_route_gym/__init__.py' in names
    assert not any('artifacts/' in name or '.venv' in name or 'conditions/science' in name for name in names)
    assert not (output / '.env').exists()
    assert (source / '.env').read_text() == 'excluded bytes'
    assert module.verify(output)['verified'] is True
    assert json.loads((output / 'release-manifest.json').read_text()) == report
    with pytest.raises(FileExistsError):
        module.prepare(source, output)


def test_changed_export_and_extra_files_fail_verification(tmp_path):
    module = exporter()
    output = tmp_path / 'release'
    module.prepare(fixture(tmp_path / 'source'), output)
    (output / 'README.md').write_text('tampered')
    with pytest.raises(ValueError, match='integrity'):
        module.verify(output)
    (output / 'README.md').write_text('# source fixture\n')
    (output / '.env').write_text('unexpected')
    with pytest.raises(ValueError, match='Unexpected'):
        module.verify(output)


@pytest.mark.parametrize('kind', ['secret', 'symlink', 'large'])
def test_unsafe_included_sources_fail_before_output_creation(tmp_path, kind):
    module = exporter()
    source = fixture(tmp_path / 'source')
    path = source / 'src/synthesis_route_gym/unsafe.py'
    if kind == 'secret':
        path.write_text('token = "ghp_' + 'A' * 36 + '"')
    elif kind == 'symlink':
        path.symlink_to(source / '.env')
    else:
        path.write_bytes(b'x' * (2 * 1024 * 1024 + 1))
    with pytest.raises(ValueError):
        module.prepare(source, tmp_path / 'release')
    assert not (tmp_path / 'release').exists()


def test_output_inside_source_is_rejected(tmp_path):
    module = exporter()
    source = fixture(tmp_path / 'source')
    with pytest.raises(ValueError):
        module.prepare(source, source / 'release')


def test_manifest_anchor_missing_files_and_unsafe_names_fail_closed(tmp_path):
    module=exporter();output=tmp_path/'release'
    module.prepare(fixture(tmp_path/'source'),output)
    result=module.verify(output)
    assert module.verify(output,result['manifest_sha256'])==result
    with pytest.raises(ValueError,match='integrity'):module.verify(output,'0'*64)
    path=output/'release-manifest.json';manifest=json.loads(path.read_text())
    for name in ('../escape.py','/absolute.py','src/../escape.py','src\\escape.py','private/file.py'):
        path.write_text(json.dumps({**manifest,'files':{name:'0'*64}}))
        with pytest.raises(ValueError):module.verify(output)
    path.write_text(json.dumps(manifest))
    (output/'README.md').unlink()
    with pytest.raises(ValueError,match='missing'):module.verify(output)


@pytest.mark.parametrize('kind',['binary','unicode','root_symlink','ancestor_symlink','directory_symlink'])
def test_preflight_rejects_binary_or_symlinked_inputs(tmp_path,kind):
    module=exporter();source=fixture(tmp_path/'source');output=tmp_path/'release'
    if kind in ('binary','unicode'):
        (source/'src/data.py').write_bytes(b'bad\x00bytes' if kind=='binary' else b'\xff')
    elif kind=='root_symlink':
        alias=tmp_path/'alias';alias.symlink_to(source,target_is_directory=True);source=alias
    elif kind=='ancestor_symlink':
        alias=tmp_path/'alias';alias.symlink_to(tmp_path,target_is_directory=True);source=alias/'source'
    else:
        (source/'src/link').symlink_to(source/'docs',target_is_directory=True)
    with pytest.raises(ValueError):module.prepare(source,output)
    assert not output.exists()


def test_positive_allowlist_preserves_only_explicit_examples_and_contracts(tmp_path):
    module=exporter();source=fixture(tmp_path/'source')
    included=('examples/base_demo.py','examples/base_session.json',
              'examples/applications/inventory/task.json',
              'integrations/platform/manifest.json','integrations/platform/openapi.v1.json',
              'integrations/agent_scientist/native.patch')
    excluded=('examples/applications/conditions/README.md','examples/other.json',
              'integrations/agent_scientist/auth.json','docs/profiles/config.yaml')
    for name in (*included,*excluded):
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
    result=module.prepare(source,tmp_path/'release')
    assert set(included)<=result['files'].keys()
    assert not set(excluded)&result['files'].keys()


@pytest.mark.parametrize('kind',['extra_symlink','root_symlink','invalid_json','bad_schema','empty_index','bad_hash'])
def test_verification_rejects_corrupted_manifests_and_symlinks(tmp_path,kind):
    module=exporter();output=tmp_path/'release';module.prepare(fixture(tmp_path/'source'),output)
    path=output/'release-manifest.json';original=json.loads(path.read_text())
    if kind=='extra_symlink':(output/'unexpected').symlink_to(tmp_path/'source/.env')
    elif kind=='root_symlink':
        alias=tmp_path/'alias';alias.symlink_to(output,target_is_directory=True);output=alias
    elif kind=='invalid_json':path.write_text('not json')
    elif kind=='bad_schema':path.write_text(json.dumps({**original,'schema_version':'unknown'}))
    elif kind=='empty_index':path.write_text(json.dumps({**original,'files':{}}))
    else:path.write_text(json.dumps({**original,'files':{'README.md':'invalid'}}))
    with pytest.raises(ValueError):module.verify(output)


def test_cli_prepare_and_verify_are_local_only(tmp_path,capsys):
    module=exporter();source=fixture(tmp_path/'source');output=tmp_path/'release'
    assert module.main(['--source',str(source),'--output',str(output)])==0
    assert json.loads(capsys.readouterr().out)['files']>0
    assert module.main(['--output',str(output),'--verify'])==0
    assert json.loads(capsys.readouterr().out)['verified'] is True


def test_changed_source_during_copy_is_not_published(tmp_path,monkeypatch):
    module=exporter();source=fixture(tmp_path/'source');output=tmp_path/'release'
    original=module._read_safe;seen={}
    def changing(path):
        key=str(path);seen[key]=seen.get(key,0)+1
        data=original(path)
        return data+b'changed' if seen[key]>1 and path.name=='README.md' else data
    monkeypatch.setattr(module,'_read_safe',changing)
    with pytest.raises(ValueError,match='changed'):module.prepare(source,output)
    assert not output.exists()
    assert not list(tmp_path.glob('.srg-release-*'))


def test_hidden_and_sensitive_configs_are_excluded_without_reading(tmp_path,monkeypatch):
    module=exporter();source=fixture(tmp_path/'source');output=tmp_path/'release'
    excluded=('src/.env.yaml','src/.hidden/config.py','src/.venv-other/unsafe.py',
              'src/credentials.json','src/credentials.yaml','docs/auth.toml',
              'integrations/config.yaml')
    for name in excluded:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('token="ghp_'+'A'*36+'"')
    (source/'src/test_auth_validation.py').write_text('# ordinary source file\n')
    original=module._read_safe
    def guarded(path):
        assert path.relative_to(source).as_posix() not in excluded
        return original(path)
    def only_source_guard(path):
        return guarded(path) if source in path.parents else original(path)
    monkeypatch.setattr(module,'_read_safe',only_source_guard)
    result=module.prepare(source,output)
    assert not set(excluded)&result['files'].keys()
    assert 'src/test_auth_validation.py' in result['files']


def test_concurrent_creation_of_output_never_overwrites_it(tmp_path,monkeypatch):
    module=exporter();source=fixture(tmp_path/'source');output=tmp_path/'release'
    original=module.verify
    def concurrent(target,*args,**kwargs):
        result=original(target,*args,**kwargs)
        output.mkdir();(output/'keep.txt').write_text('other exporter')
        return result
    monkeypatch.setattr(module,'verify',concurrent)
    with pytest.raises(FileExistsError):module.prepare(source,output)
    assert (output/'keep.txt').read_text()=='other exporter'
    assert not list(tmp_path.glob('.srg-release-*'))
