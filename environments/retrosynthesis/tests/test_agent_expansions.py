"""Agent precursor hypotheses remain bounded, metered and session scoped."""

import sys
from types import SimpleNamespace

import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.interactive_session import InteractiveSessions
from synthesis_route_gym.schemas import Constraints
from test_core import make_task


def _call(host, action, arguments=None, *, sid=None, profile="main"):
    return host.handle({"profile": profile, "action": action,
                        "arguments": arguments or {}, "session_id": sid})


def _session(host, *, profile="main"):
    return _call(host, "reset", {"task": make_task().model_dump(mode="json")},
                 profile=profile)["session_id"]


def _proposal(reactants=None):
    return {"product": "CCOC(C)=O", "candidates": [{"reactants": reactants or ["CCO", "CC(=O)O"],
            "status": "hypothesis", "rationale": "Possible disconnection"}]}


def test_agent_expansion_is_metered_and_has_host_provenance():
    host = InteractiveSessions()
    sid = _session(host)
    before = host.sessions[("main", sid)][0].search_status()["usage"]["actions"]
    observation = _call(host, "propose_expansion", _proposal(), sid=sid)["observation"]
    assert observation["status"] == "ok"
    assert observation["usage"]["actions"] == before + 1
    assert observation["usage"]["expansions"] == 0
    prediction = observation["result"]["predictions"][0]
    assert prediction["source"] == {"tool": "submitted_hypothesis", "version": "host-registered-v1"}
    assert "evidence_ids" not in prediction and "score" not in prediction
    assert host.sessions[("main", sid)][0].export()["events"][-1]["action"] == "propose_expansion"


@pytest.mark.parametrize("candidate", [
    {"reactants": ["CCO", "CC(=O)O"], "status": "literature_exact"},
    {"reactants": ["CCO", "CC(=O)O"], "status": "hypothesis", "source": "paper"},
    {"reactants": ["CCO", "CC(=O)O"], "status": "hypothesis", "evidence_ids": ["e1"]},
    {"reactants": ["CCO", "CC(=O)O"], "status": "hypothesis", "score": 0.9},
    {"reactants": ["CCO", "CC(=O)O"], "status": "hypothesis", "product": "CCO"},
    {"reactants": ["CCOC(C)=O"], "status": "hypothesis"},
    {"reactants": ["not-smiles"], "status": "hypothesis"},
])
def test_invalid_or_authority_claiming_proposals_fail_closed(candidate):
    host = InteractiveSessions()
    sid = _session(host)
    observation = _call(host, "propose_expansion", {"product": "CCOC(C)=O", "candidates": [candidate]}, sid=sid)["observation"]
    assert observation["status"] == "error"
    assert not [event for event in host.sessions[("main", sid)][0].export()["events"]
                if event["action"] == "propose_expansion" and event["status"] == "ok"]


def test_agent_proposals_are_read_only_within_their_session_and_profile(monkeypatch):
    host = InteractiveSessions()
    first = _session(host)
    second = _session(host)
    other_profile = _session(host, profile="other")
    _call(host, "propose_expansion", _proposal(), sid=first)
    captured = []

    def search(view, **kwargs):
        captured.append(view.proposal_bank)
        return {"stop_reason": "fixture"}

    monkeypatch.setitem(sys.modules, "synthesis_route_gym.synthchem_search",
                        SimpleNamespace(run_synthchem_workflow=search))
    for sid, profile in ((first, "main"), (second, "main"), (other_profile, "other")):
        _call(host, "generate_routes", {"search_policy": "synthchem_portfolio"}, sid=sid, profile=profile)
    assert captured[0]["CCOC(C)=O"][0]["source"]["tool"] == "submitted_hypothesis"
    assert captured[1] == {} and captured[2] == {}
    with pytest.raises(ValueError, match="Unknown"):
        _call(host, "generate_routes", {"search_policy": "synthchem_portfolio"}, sid=first, profile="other")


def test_agent_expansion_is_in_checkpoint_event_history(tmp_path):
    from synthesis_route_gym.episode_store import EpisodeStore

    store = EpisodeStore(tmp_path / "episode.json")
    env = SynthesisRouteEnv(make_task(), store=store)
    assert env.dispatch("propose_expansion", _proposal())["status"] == "ok"
    resumed = SynthesisRouteEnv.resume(store)
    event = resumed.export()["events"][-1]
    assert event["action"] == "propose_expansion" and event["status"] == "ok"
    assert resumed.search_status()["usage"]["actions"] == 1


def test_agent_proposal_batch_is_atomic_against_task_constraints():
    task = make_task(constraints=Constraints(forbidden_smiles=("O",)))
    host = InteractiveSessions()
    sid = _call(host, "reset", {"task": task.model_dump(mode="json")})["session_id"]
    batch = {"product": "CCOC(C)=O", "candidates": [
        {"reactants": ["CCO", "CC(=O)O"], "status": "hypothesis"},
        {"reactants": ["CCO", "O"], "status": "hypothesis"}]}
    result = _call(host, "propose_expansion", batch, sid=sid)["observation"]
    assert result["status"] == "error"
    assert result["usage"]["actions"] == 2  # reset inspect and rejected proposal
    assert not [event for event in host.sessions[("main", sid)][0].export()["events"]
                if event["action"] == "propose_expansion" and event["status"] == "ok"]


def test_episode_proposal_allowance_applies_to_later_calls(monkeypatch):
    from synthesis_route_gym import agent_expansions

    monkeypatch.setattr(agent_expansions, "MAX_EPISODE_PROPOSALS", 1)
    host = InteractiveSessions()
    sid = _session(host)
    assert _call(host, "propose_expansion", _proposal(), sid=sid)["observation"]["status"] == "ok"
    second = {"product": "CCOC(C)=O", "candidates": [{
        "reactants": ["CC=O", "CC(=O)O"], "status": "hypothesis"}]}
    assert _call(host, "propose_expansion", second, sid=sid)["observation"]["status"] == "error"


@pytest.mark.parametrize("mode", ["hybrid", "agent_fallback", "agent_only", "model_only"])
def test_synthchem_proposal_mode_passes_to_search_and_reports_gaps(monkeypatch, mode):
    host = InteractiveSessions()
    sid = _session(host)
    seen = []

    def search(view, **kwargs):
        seen.append(kwargs)
        return {"stop_reason": "frontier_exhausted", "proposal_pool": {
            "unresolved_products": ["CCO"]}}

    monkeypatch.setitem(sys.modules, "synthesis_route_gym.synthchem_search",
                        SimpleNamespace(run_synthchem_workflow=search))
    result = _call(host, "generate_routes", {"search_policy": "synthchem_portfolio",
                   "proposal_mode": mode}, sid=sid)
    assert seen[0]["proposal_mode"] == mode
    assert result["proposal_mode"] == mode
    assert result["unresolved_products"] == ["CCO"]


def test_non_synthchem_search_rejects_agent_proposal_mode():
    host = InteractiveSessions()
    sid = _session(host)
    with pytest.raises(ValueError, match="SynthChem"):
        _call(host, "generate_routes", {"search_policy": "breadth_first",
               "proposal_mode": "agent_only"}, sid=sid)


@pytest.mark.parametrize("mode", [[], True, "unknown"])
def test_search_rejects_invalid_agent_proposal_modes(mode):
    host = InteractiveSessions()
    sid = _session(host)
    with pytest.raises(ValueError, match="proposal mode"):
        _call(host, "generate_routes", {"search_policy": "synthchem_portfolio",
               "proposal_mode": mode}, sid=sid)
