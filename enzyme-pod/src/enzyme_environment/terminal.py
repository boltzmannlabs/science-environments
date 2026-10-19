"""The environment ends at an accepted selection, not an extra chat response."""
import json
from enzyme_environment.policy import strict_json


class AcceptedSelection(BaseException):
    """Expected control signal, deliberately not a recoverable tool exception."""


def dispatch(name,arguments,*,allowed,rpc):
    if name not in allowed:raise ValueError("Tool not permitted")
    if isinstance(arguments,str):arguments=strict_json(arguments)
    result=rpc(name,arguments)
    if (name=="benchmark_submit" and isinstance(result,dict) and result.get("accepted") is True
            and type(result.get("count")) is int and result["count"]==10):
        raise AcceptedSelection()
    return json.dumps(result)
