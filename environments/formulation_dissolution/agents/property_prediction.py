"""Property scientist: an allowlisted tool is the only prediction source."""
from dataclasses import dataclass
from environment.observations import Observation


@dataclass(frozen=True)
class PredictionRequest:
    task_id: str
    candidate_id: str
    features: dict
    capability: str = 'dissolution'

    def __post_init__(self):
        if not self.task_id or not self.candidate_id or not isinstance(self.features, dict):
            raise ValueError('invalid prediction input')


def predict(request: PredictionRequest, registry=None) -> Observation:
    """Abstain when data/model missing; never label prediction measured."""
    if not isinstance(request, PredictionRequest):
        raise TypeError('PredictionRequest required')
    if not request.features:
        return Observation(request.task_id, 'insufficient_data', candidate_id=request.candidate_id, missing_data=['validated model features'])
    if registry is None:
        return Observation(request.task_id, 'tool_unavailable', candidate_id=request.candidate_id, missing_data=['approved property model'])
    return registry.call(request.capability, {'candidate_id': request.candidate_id, 'features': request.features}, task_id=request.task_id)
