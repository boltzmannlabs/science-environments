"""Allowlisted, dependency-injected tool contracts; no guessed remote endpoints."""
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, TimeoutError as ToolTimeout
from environment.observations import Observation, now


@dataclass(frozen=True)
class Contract:
    name: str
    version: str
    capability: str
    invoke: object
    validate_request: object
    validate_response: object
    timeout_seconds: float = 10
    retries: int = 0

    def __post_init__(self):
        if not all(callable(x) for x in (self.invoke, self.validate_request, self.validate_response)) or not self.name or not self.version or self.timeout_seconds <= 0 or not 0 <= self.retries <= 3:
            raise ValueError('incomplete documented tool contract')


class Registry:
    """Only register an independently documented, approved implementation."""
    def __init__(self):
        self.contracts: dict[str, Contract] = {}
        self.history: list[dict] = []

    def register(self, contract: Contract, *, approved: bool = False):
        if not approved:
            raise PermissionError('explicit tool approval required')
        if contract.capability in self.contracts:
            raise ValueError('duplicate capability')
        self.contracts[contract.capability] = contract

    def call(self, capability: str, payload: dict, *, task_id: str) -> Observation:
        contract = self.contracts.get(capability)
        if contract is None:
            return Observation(task_id, 'tool_unavailable', missing_data=[f'configure approved {capability} API contract'])
        import uuid
        request_id = str(uuid.uuid4())
        record = {'tool': contract.name, 'version': contract.version, 'request_id': request_id, 'timestamp': now(), 'status': 'failure', 'errors': []}
        self.history.append(record)
        try:
            if contract.validate_request(payload) is not True:
                raise ValueError('request schema rejected')
            for attempt in range(contract.retries + 1):
                pool = ThreadPoolExecutor(max_workers=1)
                try:
                    result = pool.submit(contract.invoke, dict(payload), request_id).result(timeout=contract.timeout_seconds)
                    if contract.validate_response(result) is not True or not isinstance(result, Observation):
                        raise ValueError('malformed response')
                    if result.task_id != task_id or result.result_type != 'predicted' or result.status != 'success':
                        raise ValueError('invalid result identity/evidence/status')
                    result.provenance = {'tool': contract.name, 'version': contract.version, 'request_id': request_id, 'timestamp': record['timestamp'], 'source_ids': result.provenance.get('source_ids', [])}
                    record['status'] = 'success'
                    return result
                except ToolTimeout:
                    record['errors'].append('timeout')
                except PermissionError:
                    record['errors'].append('authentication_failed')
                    break
                except (ConnectionError, OSError) as exc:
                    record['errors'].append(type(exc).__name__)
                finally:
                    pool.shutdown(wait=False, cancel_futures=True)
                if attempt == contract.retries:
                    break
        except PermissionError:
            record['errors'].append('authentication_failed')
        except (ValueError, TypeError) as exc:
            record['errors'].append(str(exc))
        return Observation(task_id, 'failure', warnings=record['errors'], provenance={'tool': contract.name, 'version': contract.version, 'request_id': request_id, 'timestamp': record['timestamp'], 'source_ids': []})
