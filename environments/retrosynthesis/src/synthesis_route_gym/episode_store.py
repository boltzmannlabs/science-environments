"""Local immutable revisions with atomic HEAD and stale-writer rejection.

Inspired by SynthChem's campaign revision pattern; no SynthChem runtime dependency.
Checksums detect accidental corruption, not a hostile owner rewriting the store.
Retain an external HEAD anchor when rollback detection is required.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile


class StoreConflict(RuntimeError):
    """Another writer advanced the episode; reload before admitting more work."""


def _encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _hash(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Missing or symlinked episode artifact')
    try:
        return json.loads(path.read_bytes())
    except (ValueError, UnicodeError) as exc:
        raise ValueError('Invalid episode JSON') from exc


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_write(path, value):
    fd, temp = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(_encoded(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        _sync_directory(path.parent)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class EpisodeStore:
    """A host-configured directory, never a model-supplied filesystem capability."""

    def __init__(self, path):
        self.path = Path(path).expanduser().absolute()
        if any(p.is_symlink() for p in (self.path, *self.path.parents)):
            raise ValueError('Episode store path cannot contain symlinks')

    @contextmanager
    def _locked(self):
        if self.path.is_symlink() or not self.path.is_dir():
            raise ValueError('Invalid episode store directory')
        fd = os.open(self.path / '.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def initialize(self, state):
        _encoded(state)  # Fail before creating a directory for invalid values.
        self.path.mkdir(parents=True, exist_ok=False, mode=0o700)
        (self.path / 'revisions').mkdir(mode=0o700)
        with self._locked():
            return self._commit(state, None)

    def _load(self):
        head = _read(self.path / 'HEAD.json')
        revision = head.get('revision')
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise ValueError('Invalid episode revision')
        revisions = self.path / 'revisions'
        if revisions.is_symlink() or not revisions.is_dir():
            raise ValueError('Invalid episode revisions directory')
        expected = {f'{n:08d}.json' for n in range(1, revision + 1)}
        if {p.name for p in revisions.iterdir()} != expected:
            raise ValueError('Uncommitted episode revision; manual recovery required')
        previous, last = None, None
        for seq in range(1, revision + 1):
            row = _read(revisions / f'{seq:08d}.json')
            if (row.get('revision') != seq or row.get('previous_sha256') != previous
                    or row.get('sha256') != _hash({k: v for k, v in row.items() if k != 'sha256'})):
                raise ValueError('Episode revision hash chain mismatch')
            previous, last = row['sha256'], row
        if previous != head.get('sha256'):
            raise ValueError('Episode HEAD hash mismatch')
        return last['state'], head

    def load(self):
        with self._locked():
            state, head = self._load()
            return state, head['revision']

    def commit(self, state, *, expected_revision):
        _encoded(state)
        with self._locked():
            _, head = self._load()
            if expected_revision != head['revision']:
                raise StoreConflict('Episode changed; stale writer cannot admit work')
            return self._commit(state, head)

    def _commit(self, state, head):
        revision = head['revision'] + 1 if head else 1
        row = {'revision': revision, 'previous_sha256': head['sha256'] if head else None,
               'state': state}
        row = {**row, 'sha256': _hash(row)}
        path = self.path / 'revisions' / f'{revision:08d}.json'
        if path.exists():
            raise StoreConflict('Episode revision already exists')
        _atomic_write(path, row)
        _atomic_write(self.path / 'HEAD.json', {'revision': revision, 'sha256': row['sha256']})
        return revision
