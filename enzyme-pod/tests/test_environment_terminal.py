"""Accepted selection ends an episode without fabricating a model completion."""
import json
import pytest
from enzyme_environment.terminal import AcceptedSelection,dispatch


def test_only_host_accepted_ten_candidate_submission_terminates():
    seen=[]
    def rpc(name,args):seen.append((name,args));return {"accepted":True,"count":10}
    with pytest.raises(AcceptedSelection):dispatch("benchmark_submit",'{"candidate_ids":["X"]}',allowed={"benchmark_submit"},rpc=rpc)
    assert len(seen)==1
    assert not issubclass(AcceptedSelection,Exception)


@pytest.mark.parametrize("result",[{"accepted":False,"count":10},{"accepted":True,"count":0},{"accepted":True,"count":"10"},{}])
def test_rejected_or_malformed_ack_is_not_terminal(result):
    assert json.loads(dispatch("benchmark_submit",{},allowed={"benchmark_submit"},rpc=lambda n,a:result))==result


def test_normal_action_and_rpc_errors_do_not_fake_success():
    assert json.loads(dispatch("benchmark_score",{},allowed={"benchmark_score"},rpc=lambda n,a:{"rows":[]}))=={"rows":[]}
    with pytest.raises(ValueError):dispatch("terminal",{},allowed={"benchmark_score"},rpc=lambda n,a:{})
    def failed(n,a):raise OSError("synthetic storage failure")
    with pytest.raises(OSError):dispatch("benchmark_submit",{},allowed={"benchmark_submit"},rpc=failed)
