"""Prepare or verify an allowlisted source release; never invoke Git or network IO."""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

SCHEMA = 'srg-base-release-v1'
MANIFEST = 'release-manifest.json'
MAX_FILE_BYTES = 2 * 1024 * 1024
TOP_FILES = frozenset({'README.md', 'pyproject.toml', '.gitignore', 'Dockerfile',
                       'THIRD_PARTY_NOTICES.md', 'LICENSE', 'ENVIRONMENT_SPEC.md', 'STATUS.md'})
TREES = frozenset({'src', 'tests', 'scripts', 'docs', 'skills', 'integrations'})
CONTRACT_TREES = frozenset({'config', 'tasks', 'results'})
CONTRACT_EXTENSIONS = frozenset({'.md', '.json', '.yaml', '.yml'})
EXTENSIONS = frozenset({'.py', '.md', '.toml', '.yaml', '.yml', '.patch'})
SKIP_DIRS = frozenset({'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
                       '.git', '.venv', '.venv-aizynth', 'build', 'dist', 'node_modules',
                       'artifacts', 'private', 'profiles', '.sci', '.ssh', '.aws'})
SPECIAL_JSON = frozenset({'integrations/platform/manifest.json',
                          'integrations/platform/openapi.v1.json'})
EXAMPLES = frozenset({'examples/aspirin_task.json', 'examples/base_demo.py',
                      'examples/base_session.json'})
APPLICATIONS = frozenset({'inventory', 'process', 'biocatalysis', 'impurities'})
SENSITIVE_CONFIG_NAMES = frozenset({'config', 'settings', 'auth', 'authentication',
                                    'credentials', 'credential', 'secrets', 'secret',
                                    'tokens', 'token'})
SECRET_PATTERNS = (
    re.compile(r'gh[pousr]_[A-Za-z0-9]{20,255}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,255}'),
    re.compile(r'sk-proj-[A-Za-z0-9_-]{20,255}'),
    re.compile(r'-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----'),
    re.compile(r'https?://[^\s/]+@github\.com', re.IGNORECASE),
)


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _path(value):
    path = Path(value).expanduser().absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('Release paths cannot contain symlinks')
    return path


def _allowed(name):
    parts = PurePosixPath(name).parts
    if not parts or any(part in SKIP_DIRS for part in parts):
        return False
    if name != '.gitignore' and any(part.startswith('.') for part in parts):
        return False
    path = PurePosixPath(name)
    if path.suffix in {'.yaml', '.yml', '.toml', '.json', '.ini', '.cfg'} and path.stem.lower() in SENSITIVE_CONFIG_NAMES:
        return False
    if name in TOP_FILES or name in SPECIAL_JSON or name in EXAMPLES:
        return True
    if parts[0] in CONTRACT_TREES and len(parts) == 2:
        return path.suffix in CONTRACT_EXTENSIONS
    if parts[0] in TREES and len(parts) > 1:
        return PurePosixPath(name).suffix in EXTENSIONS
    return (len(parts) == 4 and parts[:2] == ('examples', 'applications') and
            parts[2] in APPLICATIONS and PurePosixPath(name).suffix == '.json')


def _read_safe(path):
    path = _path(path)
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Release source is not a bounded regular file')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES or b'\x00' in data:
        raise ValueError('Release source is too large or binary')
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError('Release source must be UTF-8 text') from exc
    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        raise ValueError('Release source contains a possible credential; content withheld')
    return data


def _candidate_files(source):
    # Never recurse through the research workspace: inspect only named trees.
    for name in sorted(TOP_FILES | SPECIAL_JSON | EXAMPLES):
        path = source / name
        if path.is_symlink() or path.exists():
            yield path
    roots = [source / tree for tree in sorted(TREES | CONTRACT_TREES)]
    roots += [source / 'examples/applications' / application for application in sorted(APPLICATIONS)]
    for root in roots:
        _path(root)
        if not root.exists():
            continue
        for folder, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(name for name in dirs
                             if name not in SKIP_DIRS and not name.startswith('.'))
            for name in dirs:
                _path(Path(folder) / name)
            for name in sorted(files):
                path = Path(folder) / name
                if _allowed(path.relative_to(source).as_posix()):
                    yield path


def _publish(temp, output):
    """Linux atomic rename with no replacement, including concurrent exporters."""
    try:
        rename = ctypes.CDLL(None, use_errno=True).renameat2
    except AttributeError as exc:
        raise RuntimeError('Atomic release preparation requires Linux renameat2') from exc
    rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(temp), -100, os.fsencode(output), 1) != 0:
        error = ctypes.get_errno()
        if error == errno.EEXIST:
            raise FileExistsError('Release output appeared during preparation')
        raise OSError(error, 'Atomic release publication failed')


def prepare(source, output):
    """Preflight all sources, then atomically publish a new local directory."""
    source, output = _path(source), _path(output)
    if not source.is_dir() or source == output or source in output.parents or output in source.parents:
        raise ValueError('Release output must be outside the source workspace')
    if output.exists():
        raise FileExistsError('Release output already exists')
    contents = {path.relative_to(source).as_posix():_read_safe(path)
                for path in _candidate_files(source)}
    if not contents or not {'README.md', 'pyproject.toml'} <= contents.keys():
        raise ValueError('Release requires README.md and pyproject.toml')
    files = {name:_digest(data) for name, data in sorted(contents.items())}
    report = {'schema_version':SCHEMA, 'files':files,
              'scope':'base software release; full scientific benchmarking deferred',
              'exclusions':['research artifacts', 'credentials/profiles', 'model weights',
                            'virtual environments', 'measured condition datasets'],
              'git_operations_performed':False, 'deployment_performed':False}
    output.parent.mkdir(parents=True, exist_ok=True)
    _path(output.parent)
    temp = Path(tempfile.mkdtemp(prefix='.srg-release-', dir=output.parent))
    try:
        for name, data in contents.items():
            # Reject a source changing between preflight and publication.
            if _read_safe(source / name) != data:
                raise ValueError('Source integrity changed during release preparation')
            dest = temp / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream:
                stream.write(data)
            if _digest(dest.read_bytes()) != files[name]:
                raise ValueError('Copied file integrity mismatch')
        payload = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode()
        (temp / MANIFEST).write_bytes(payload)
        verify(temp, expected_manifest_sha256=_digest(payload))
        _publish(temp, output)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return report


def _manifest(output, expected_manifest_sha256):
    data = _read_safe(output / MANIFEST)
    if expected_manifest_sha256 is not None:
        if not re.fullmatch(r'[a-f0-9]{64}', expected_manifest_sha256) or _digest(data) != expected_manifest_sha256:
            raise ValueError('Release manifest integrity mismatch')
    try:
        report = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise ValueError('Invalid release manifest') from exc
    if not isinstance(report, dict) or report.get('schema_version') != SCHEMA:
        raise ValueError('Unsupported release manifest')
    files = report.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Invalid release file index')
    for name, value in files.items():
        parts = PurePosixPath(name).parts
        if (not isinstance(name, str) or name != PurePosixPath(name).as_posix() or
                not parts or PurePosixPath(name).is_absolute() or
                any(part in {'', '.', '..'} for part in parts) or '\\' in name or
                not _allowed(name) or not isinstance(value, str) or
                not re.fullmatch(r'[a-f0-9]{64}', value)):
            raise ValueError('Unsafe release manifest path or hash')
    return files, data


def verify(output, expected_manifest_sha256=None):
    """Verify hashes, file allowlist and absence of additional release payloads.

    Hashes detect corruption. Supply the externally retained manifest hash to
    detect a manifest being rewritten alongside its payload.
    """
    output = _path(output)
    if not output.is_dir():
        raise ValueError('Release directory is missing')
    files, data = _manifest(output, expected_manifest_sha256)
    observed = set()
    for folder, dirs, names in os.walk(output, followlinks=False):
        for name in dirs:
            _path(Path(folder) / name)
        for name in names:
            path = Path(folder) / name
            _path(path)
            logical = path.relative_to(output).as_posix()
            if logical != MANIFEST:
                observed.add(logical)
    if observed - files.keys():
        raise ValueError('Unexpected files in release output')
    if observed != files.keys():
        raise ValueError('Release file integrity mismatch: missing files')
    for name, expected in files.items():
        if _digest(_read_safe(output / name)) != expected:
            raise ValueError('Release file integrity mismatch')
    return {'verified':True, 'files':len(files), 'manifest_sha256':_digest(data)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--expected-manifest-sha256')
    args = parser.parse_args(argv)
    report = (verify(args.output, args.expected_manifest_sha256) if args.verify else
              prepare(args.source, args.output))
    print(json.dumps({'verified':True, 'files':len(report['files'])}
                     if isinstance(report.get('files'), dict) else report, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
