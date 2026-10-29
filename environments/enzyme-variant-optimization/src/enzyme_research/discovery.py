"""Real upstream DiscoveryRSI loop, with enzyme actions and observed feedback.

The upstream critic ranks hypotheses, not molecular candidates or activity.
Only the external executor can supply a scientific observation.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

from .contracts import ResearchError, canonical, digest, safe_data, KINDS

UPSTREAM_REVISION = "7389e0b58ae50486ab35aa3dcbfa2fa15fea1a91"


class HypothesisReviewDeclined(ResearchError):
    """A valid scientific review stopped testing, not an executor malfunction."""
    def __init__(self, review):
        super().__init__("No hypothesis was approved for testing; no scientific job was submitted")
        self.review = review


def upstream_core(source):
    source = Path(source).resolve()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"], text=True)
    if head != UPSTREAM_REVISION or status:
        raise ResearchError("DiscoveryRSI must match the pinned, unchanged upstream revision")
    library = source / "src"
    existing = sys.modules.get("discovery_rsi.core")
    if existing is not None and Path(existing.__file__).resolve() != library / "discovery_rsi" / "core.py":
        raise ResearchError("Another DiscoveryRSI installation is already loaded")
    sys.path.insert(0, str(library))
    try:
        core = importlib.import_module("discovery_rsi.core")
    finally:
        sys.path.remove(str(library))
    return core


class DiscoveryCoordinator:
    def __init__(self, store, upstream_source, context_provider=None):
        self.store = store
        self.core = upstream_core(upstream_source)
        self.context_provider = context_provider

    def advance(self, campaign, propose, critique):
        """Produce one persisted hypothesis/action. This does not submit a job.

        Callbacks may use the native agent's authorized model route or explicit
        offline fixtures. The authoritative task state is supplied identically.
        After execution, decision_observed is required before another round.
        """
        state = self.store.status(campaign)
        if state["arm"] != "specialist":
            raise ResearchError("DiscoveryRSI is exclusive to the specialist arm")
        if state["decisions"] and state["decisions"][-1]["status"] != "observed":
            raise ResearchError("Execute and observe the previous decision before revising")
        number = len(state["decisions"]) + 1
        if number > state["task"]["budget"]["max_rounds"]:
            raise ResearchError("Research round budget exhausted")
        observations = {item["observation_id"]: item for item in state["observations"]}
        parent = state["decisions"][-1]["value"]["selected_id"] if state["decisions"] else None
        context = {"task": state["task"], "candidates": state["candidates"], "round": number,
                   "structures": state["structures"],
                   "structure_assessments": state["structure_assessments"],
                   "previous_decisions": state["decisions"], "observations": list(observations.values()),
                   "parent_hypothesis_id": parent}
        if self.context_provider is not None:
            extra = self.context_provider(state)
            safe_data(extra)
            # Native roles receive the same reconstructable record views as
            # their coordinator, not a second unbounded full-state payload.
            context = {**extra, "round": number, "parent_hypothesis_id": parent}
        actions, criticisms = {}, {}

        def proposer(upstream_number, history):
            proposals = propose(json.loads(canonical(context)))
            if not isinstance(proposals, list) or not 1 <= len(proposals) <= 2:
                raise ResearchError("Each research round needs one or two explicit hypotheses")
            result = []
            for i, value in enumerate(proposals, 1):
                safe_data(value)
                fields = {"claim", "plan", "alternatives", "evidence_refs", "revision_reason", "action"}
                if not isinstance(value, dict) or set(value) != fields:
                    raise ResearchError("Malformed research hypothesis")
                if any(not isinstance(value[k], str) or not value[k].strip() or len(value[k]) > 4000 for k in ("claim", "plan", "revision_reason")):
                    raise ResearchError("Hypothesis claim, plan and revision reason must be bounded text")
                alternatives = value["alternatives"]
                if not isinstance(alternatives, list) or not alternatives or any(not isinstance(v, str) or not v.strip() for v in alternatives):
                    raise ResearchError("Explicit competing explanations are required")
                refs = value["evidence_refs"]
                if not isinstance(refs, list) or any(not isinstance(v, str) for v in refs) or len(refs) != len(set(refs)) or set(refs) - set(observations):
                    raise ResearchError("Hypothesis cites nonexistent or duplicate observations")
                if number > 1 and not refs:
                    raise ResearchError("A revision must reference actual preceding observations")
                action = value["action"]
                if not isinstance(action, dict) or set(action) != {"kind", "job_name", "experiment_data", "candidate_ids"}:
                    raise ResearchError("Hypothesis must propose one explicit scientific action")
                if action["kind"] not in KINDS:
                    raise ResearchError("Scientific action kind is outside the permitted capabilities")
                if action["job_name"] not in state["task"]["allowed_jobs"]:
                    raise ResearchError("Scientific action job_name is outside the permitted task")
                if not isinstance(action["experiment_data"], dict):
                    raise ResearchError("Scientific action experiment_data must be an object")
                ids = action["candidate_ids"]
                known = {c["candidate_id"] for c in state["candidates"]}
                if not isinstance(ids, list) or not ids or any(not isinstance(cid, str) for cid in ids) or len(ids) != len(set(ids)) or set(ids) - known:
                    raise ResearchError("Scientific actions require explicit known candidate IDs")
                hid = f"round-{number}-hypothesis-{i}"
                actions[hid] = {"action": action, "revision_reason": value["revision_reason"]}
                result.append(self.core.Candidate(hid, value["claim"], value["plan"], alternatives, refs, [parent] if parent else []))
            return result

        def critic(candidate):
            # The upstream Candidate has only claim/plan text. Review the exact
            # proposed request as well, rather than hiding its actual tool/data
            # from the supposedly independent feasibility critique.
            reviewed = {**asdict(candidate), "action": json.loads(canonical(actions[candidate.id]["action"]))}
            value = critique(reviewed, json.loads(canonical(context)))
            safe_data(value)
            if not isinstance(value, dict) or set(value) != {"score", "critique", "decision"}:
                raise ResearchError("Malformed hypothesis critique")
            score = value["score"]
            if type(score) not in (int, float) or not 0 <= score <= 10:
                raise ResearchError("Hypothesis-quality score must be finite and between zero and ten")
            if value["decision"] not in {"test", "revise", "stop"} or not isinstance(value["critique"], str) or not value["critique"].strip():
                raise ResearchError("Critic must explicitly recommend test, revise or stop")
            criticisms[candidate.id] = value
            return (float(score) if value["decision"] == "test" else -1.0), value["critique"]

        loop = self.core.DiscoveryLoop(proposer, critic, iterations=1)
        episode = loop.run()[0]
        selected = episode.selected_id
        if selected not in criticisms or criticisms[selected]["decision"] != "test":
            review = {"review_id": "review-" + uuid.uuid4().hex[:16],
                "status": "hypothesis_review_declined", "approved_for_execution": False,
                "upstream": "Gen-Verse/DiscoveryRSI", "upstream_revision": UPSTREAM_REVISION,
                "upstream_components_executed": ["Candidate", "DiscoveryLoop.run", "ReplayBuffer.append"],
                "proposed_round": number, "hypotheses": [asdict(c) for c in episode.candidates],
                "critiques": criticisms, "proposed_actions": actions,
                "observation_ids_available": list(observations), "scientific_jobs_submitted": 0,
                "molecular_improvement_established": False}
            with self.store.transaction() as db:
                self.store.event(db, campaign, "hypothesis_review_declined", review)
            replay = self.core.ReplayBuffer(self.store.root / campaign / "discovery_rsi_episodes.jsonl")
            episode.number = number
            replay.append(episode)
            raise HypothesisReviewDeclined(review)
        value = {"upstream": "Gen-Verse/DiscoveryRSI", "upstream_revision": UPSTREAM_REVISION,
                 "upstream_components_executed": ["Candidate", "DiscoveryLoop.run", "ReplayBuffer.append"],
                 "round": number, "selected_id": selected, "parent_id": parent,
                 "hypotheses": [asdict(c) for c in episode.candidates],
                 "critiques": criticisms, **actions[selected],
                 "observation_ids_available": list(observations),
                 "molecular_improvement_established": False}
        self.store.save_decision(campaign, value)
        replay = self.core.ReplayBuffer(self.store.root / campaign / "discovery_rsi_episodes.jsonl")
        episode.number = number
        replay.append(episode)
        return value
