"""Bounded proposal/critique/test/revision core with real host observations.

This is the external specialist's execution core, not a model adapter, trained
scientific model or independent evaluator. Role callbacks must share the host's
model budget when wired to a live model. Offline fixtures are not live agents.
"""
from __future__ import annotations

import copy
import json

from enzyme_environment.policy import digest


def text(value, name, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(name + " requires nonempty bounded text")
    return value


class ResearchLoop:
    def __init__(self, policy, *, max_rounds=2):
        if type(max_rounds) is not int or not 1 <= max_rounds <= 3:
            raise ValueError("Research loop permits one to three rounds")
        if policy.submitted:
            raise ValueError("Cannot start research after final submission")
        self.policy, self.max_rounds = policy, max_rounds
        self._records = []
        self.closed = False
        self.status = "not_started"

    @property
    def records(self):
        return copy.deepcopy(self._records)

    def _proposal(self, value, parent, observations):
        fields = {"question", "claim", "comparator", "alternative_explanation", "stop_condition",
                  "revision_reason", "parent_id", "evidence_refs", "action"}
        if not isinstance(value, dict) or set(value) != fields:
            raise ValueError("Proposal has unexpected or missing fields")
        value = copy.deepcopy(value)
        for name in fields - {"parent_id", "evidence_refs", "action"}:
            text(value[name], name)
        if value["parent_id"] != parent:
            raise ValueError("Proposal parent does not match the actual previous round")
        refs = value["evidence_refs"]
        if (not isinstance(refs, list) or len(refs) > 20 or any(not isinstance(ref, str) for ref in refs)
                or len(set(refs)) != len(refs) or not set(refs) <= observations):
            raise ValueError("Evidence references must identify actual prior observations")
        if parent is not None and observations and not refs:
            raise ValueError("A revision must reference at least one available prior observation")
        action = value["action"]
        if (not isinstance(action, dict) or set(action) != {"tool", "arguments"}
                or not isinstance(action["tool"], str)
                or action["tool"] not in {"benchmark_read", "benchmark_score"}
                or not isinstance(action["arguments"], dict)):
            raise ValueError("Only existing permitted scientific read/score actions may be proposed")
        if action["tool"] == "benchmark_score":
            if set(action["arguments"]) != {"candidate_ids"} or self.policy.predictor is None:
                raise ValueError("Proposal needs the existing frozen predictor")
            self.policy.predictor.validate_request(action["arguments"]["candidate_ids"])
        else:
            args = action["arguments"]
            if (set(args) - {"dataset", "offset", "limit"} or not isinstance(args.get("dataset"), str)
                    or args["dataset"] not in self.policy.datasets
                    or type(args.get("offset", 0)) is not int or args.get("offset", 0) < 0
                    or type(args.get("limit", 50)) is not int or not 1 <= args.get("limit", 50) <= 50):
                raise ValueError("Proposal read does not match the permitted paging contract")
        digest(value)  # reject non-JSON/nonfinite nested values before logging
        return value

    @staticmethod
    def _critique(value):
        if not isinstance(value, dict) or set(value) != {"decision", "reason", "objections", "requested_revision"}:
            raise ValueError("Critique has unexpected or missing fields")
        value = copy.deepcopy(value)
        if not isinstance(value["decision"], str) or value["decision"] not in {"test", "revise", "stop"}:
            raise ValueError("Critique decision must be test, revise or stop")
        text(value["reason"], "critique reason")
        text(value["requested_revision"], "requested revision")
        if not isinstance(value["objections"], list) or len(value["objections"]) > 10:
            raise ValueError("Critique objections must be a bounded list")
        for objection in value["objections"]: text(objection, "objection", 1000)
        return value

    def run(self, proposer, critic, *, question):
        text(question, "research question")
        if self.closed:
            raise ValueError("Research loop is already closed; no replay or overwrite")
        self.closed = True  # callbacks failing cannot leave a replayable invocation
        self.status = "running"
        parent, observations = None, set()
        try:
            for round_number in range(1, self.max_rounds + 1):
                context = {"question": question, "round": round_number, "maximum_rounds": self.max_rounds,
                    "parent_id": parent, "history": self.records,
                    "evidence_boundary": "Frozen predictions/practice data only, never final experimental answers",
                    "critic_boundary": "Critique assesses proposal quality, not measured enzyme activity"}
                proposal = self._proposal(proposer(copy.deepcopy(context)), parent, observations)
                critique = self._critique(critic(copy.deepcopy(proposal), copy.deepcopy(context)))
                record = {"round": round_number, "parent_id": parent, "proposal": proposal,
                          "critique": critique, "observation": None, "scientific_improvement_established": False}
                self.policy.audit.record("research_proposal", round=round_number, proposal_sha256=digest(proposal))
                self.policy.audit.record("research_critique", round=round_number, critique_sha256=digest(critique),
                                         independent_activity_evaluation=False)
                if critique["decision"] == "test":
                    action = proposal["action"]
                    # Actual host policy, not prose describing an unexecuted tool.
                    result = self.policy.tool(action["tool"], action["arguments"])
                    observation = {"tool": action["tool"], "arguments": copy.deepcopy(action["arguments"]),
                        "result": copy.deepcopy(result), "result_sha256": digest(result),
                        "evidence_type": "prediction" if action["tool"] == "benchmark_score" else "permitted_dataset_page"}
                    observation["observation_id"] = "obs_" + digest(observation)
                    observations.add(observation["observation_id"])
                    record["observation"] = observation
                record["record_id"] = "research_" + digest(record)
                self._records.append(record)
                self.policy.audit.record("research_round", round=round_number, record_sha256=digest(record),
                                         actual_tool_executed=record["observation"] is not None)
                parent = record["record_id"]
                if critique["decision"] == "stop": break
        except Exception as exc:
            self.status = "failed"
            self.policy.audit.record("research_failed_closed", error_type=type(exc).__name__,
                                     completed_rounds=len(self._records))
            raise
        self.status = "completed"
        return self.records

    def export_bytes(self):
        if not self.closed: raise ValueError("Research loop has not run")
        return (json.dumps({"schema_version": "enzyme-research-loop/0.1", "records": self.records,
            "status": self.status,
            "independent_evaluator": False, "scientific_improvement_established": False},
            sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
