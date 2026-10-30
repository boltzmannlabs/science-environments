"""Descriptive uncertainty and holdout calibration; no assumed confidence interval."""
from math import sqrt


def calibration(predicted: list[float], observed: list[float], *, minimum: int = 10) -> dict:
    if len(predicted) != len(observed) or not predicted or any(not isinstance(x,(float,int)) for x in predicted+observed):
        raise ValueError('matched numeric holdout pairs required')
    if len(observed) < minimum:
        return {'status':'not_established','reason':'insufficient independent holdout pairs'}
    errors = [p-y for p,y in zip(predicted, observed)]
    return {'status':'evaluated','n':len(errors),'mae':sum(abs(e) for e in errors)/len(errors),'rmse':sqrt(sum(e*e for e in errors)/len(errors)),'note':'point error metrics; interval coverage not established'}
