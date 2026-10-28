"""Per-request wire guard: host compatibility retries cannot bypass admission."""
from threading import Lock


class WireGate:
    def __init__(self):
        self._lock, self._used, self._closed = Lock(), False, False

    def claim(self):
        with self._lock:
            if self._closed or self._used:
                raise RuntimeError('Unmetered or stale wire retry blocked; retry through outer admission')
            self._used = True

    def close(self):
        with self._lock:
            self._closed = True


class GuardedClient:
    """Transparent endpoint facade; request-owned close/abort unwrap the SDK object."""
    def __init__(self, client, gate, *, root=True):
        if root and getattr(client, 'max_retries', None) != 0:
            raise RuntimeError('Provider SDK retries must be explicitly disabled')
        self._raw, self._gate = client, gate

    def __getattr__(self, name):
        value = getattr(self._raw, name)
        if name in {'responses', 'chat', 'completions', 'messages', 'with_raw_response', 'with_streaming_response', 'beta'}:
            return GuardedClient(value, self._gate, root=False)
        if name in {'create', 'stream'} and callable(value):
            def call(*args, **kwargs):
                self._gate.claim()
                return value(*args, **kwargs)
            return call
        if name in {'with_options', 'copy'} and callable(value):
            return lambda *args, **kwargs: GuardedClient(value(*args, **kwargs), self._gate)
        return value


def unwrap_client(client):
    return client._raw if isinstance(client, GuardedClient) else client
