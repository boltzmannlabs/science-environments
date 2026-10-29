"""Interactive synthesis episodes; failed actions consume the shared episode budget."""
from dataclasses import dataclass, replace
import hashlib
import json
import logging
import time
from threading import RLock, Event, Thread
from contextvars import copy_context
import queue
from uuid import uuid4
from .episode_store import EpisodeStore
from .scientific_execution import SCIENTIFIC_ACTIONS, ACCOUNTED_SCIENTIFIC_ACTIONS, APPLICATION_ACTIONS, ACCOUNTING_ALIASES, ScientificLimits, execute_scientific, science_checkpoint
from .schemas import RouteCandidate, Task
from .validation import assess_route

log = logging.getLogger(__name__)


def _snapshot(value):
    return json.loads(json.dumps(value, allow_nan=False))


@dataclass(frozen=True)
class Usage:
    actions: int = 0
    expansions: int = 0


class SynthesisRouteEnv:
    """Host reset starts episodes; agents cannot replace tasks or reset budgets.

    Expand adapters must enforce cancellation of external jobs separately.
    This environment discards results arriving after the episode deadline.
    """
    def __init__(self, task: Task, seed=0, *, expand=None, condition_ranker=None,
                 clock=time.monotonic, wall_clock=time.time, store=None, scientific_tools=None,
                 scientific_limits=None, evidence_corpus=None, condition_study=None,
                 impurity=None, biocatalytic_records=None, forward=None, backend_versions=None,
                 process_basis=None, source_access_mode=None, cn_condition_model=None,
                 reaction_yield_predictor=None, application_config=None):
        self._expand, self._clock, self._lock = expand, clock, RLock()
        self._wall_clock, self._condition_ranker = wall_clock, condition_ranker
        self._store = store if isinstance(store, EpisodeStore) or store is None else EpisodeStore(store)
        self._supplied_scientific_tools = scientific_tools
        self._scientific_limits = (scientific_limits if isinstance(scientific_limits, ScientificLimits)
                                   else ScientificLimits(**(scientific_limits or {})))
        if (condition_study is not None and condition_study.budget is not None
                and (self._scientific_limits.observation_calls is None or
                     self._scientific_limits.observation_calls > condition_study.budget - len(condition_study.observed_ids))):
            raise ValueError('Observation allowance exceeds remaining study budget')
        self._source_access_mode = source_access_mode or (evidence_corpus.mode if evidence_corpus is not None else 'closed_information')
        if self._source_access_mode not in {'closed_information','evidence_retrieval'}:
            raise ValueError('Invalid source access mode')
        if evidence_corpus is not None and evidence_corpus.mode != self._source_access_mode:
            raise ValueError('Source corpus and access mode differ')
        self._evidence_corpus = evidence_corpus
        self._science_options = {'evidence_corpus': evidence_corpus, 'condition_study': condition_study,
                                 'impurity': impurity, 'biocatalytic_records': biocatalytic_records,
                                 'forward':forward,'backend_versions':backend_versions,
                                 'process_basis':process_basis,'source_access_mode':source_access_mode,
                                 'cn_condition_model':cn_condition_model,
                                 'reaction_yield_predictor':reaction_yield_predictor}
        if scientific_tools is not None and any(v is not None for k,v in self._science_options.items() if k != 'source_access_mode'):
            raise ValueError('Supply a scientific registry or component configuration, not both')
        from .application_actions import configure
        self._application_config, self._application_fingerprint = configure(application_config, condition_study)
        self._revision = None
        self._cancelled = Event()
        self.reset(task, seed=seed)
        if self._store:
            self._revision = self._store.initialize(self._checkpoint())

    def reset(self, task=None, *, seed=0):
        with self._lock:
            if self._revision is not None:
                raise ValueError("Cannot reset a persistent episode; create a new store")
            if task is not None:
                self.task = Task.model_validate(task.model_dump() if isinstance(task, Task) else task)
            self._validate_resource_regime()
            self._task_sha256 = hashlib.sha256(self.task.model_dump_json().encode()).hexdigest()
            self.seed, self._started = seed, self._clock()
            self._started_at, self._elapsed_before = self._wall_clock(), 0.0
            self._usage, self._routes, self._events = Usage(), (), ()
            self._submitted, self._terminated, self._truncated = (), False, False
            self._receipts, self._pending, self._cancel_reason = {}, None, None
            self._cancelled.clear()
            self._scientific_usage, self._retrieved_source_ids = {}, ()
            from .scientific_bindings import build_default_registry
            self._scientific_tools = self._supplied_scientific_tools or build_default_registry(
                self.task, expand=self._expand, condition_ranker=self._condition_ranker,
                route_lookup=self._route, **self._science_options)
            return self.inspect(), {"task_id": self.task.task_id, "seed": seed}

    def _elapsed(self):
        return max(0.0, self._elapsed_before + self._clock() - self._started,
                   self._wall_clock() - self._started_at)

    def _validate_resource_regime(self):
        limits = (self._scientific_limits.retrieval_calls, self._scientific_limits.observation_calls)
        study = self._science_options.get('condition_study')
        if self.task.budget.regime == 'unbudgeted':
            if any(value not in (None, 0) for value in limits) or (study is not None and study.budget is not None):
                raise ValueError('unbudgeted episodes require absent scientific query ceilings or disabled tools')
        elif any(value is None for value in limits) or (study is not None and study.budget is None):
            raise ValueError('budgeted episodes require finite scientific query ceilings')

    def _wall_exhausted(self):
        ceiling = self.task.budget.max_wall_seconds
        return ceiling is not None and self._elapsed() >= ceiling

    def _actions_exhausted(self):
        ceiling = self.task.budget.max_actions
        return ceiling is not None and self._usage.actions >= ceiling

    def _usage_dict(self):
        return {"actions": self._usage.actions, "expansions": self._usage.expansions,
                "wall_seconds": self._elapsed()}

    def inspect(self):
        with self._lock:
            return {"task": self.task.model_dump(mode="json"), "seed": self.seed,
                    "routes": [r.model_dump(mode="json") for r in self._routes],
                    "submitted_route_ids": list(self._submitted), "usage": self._usage_dict(),
                    "terminated": self._terminated, "truncated": self._truncated,
                    "application_fingerprint": self._application_fingerprint,
                    **science_checkpoint(self)}

    def search_status(self):
        """Host search counters without copying the inventory or route collection."""
        with self._lock:
            return {"usage": self._usage_dict(), "terminated": self._terminated,
                    "truncated": self._truncated,
                    "capability_fingerprint": self._scientific_tools.fingerprint}

    def expansion_cache_identity(self, arguments):
        """Bind a canonical expansion request to host tool and snapshot versions."""
        return self._scientific_tools.cache_identity("expand", arguments)

    def _checkpoint(self):
        return {**self.inspect(), "checkpoint_version": 3 if self.task.budget.regime == 'unbudgeted' else 2,
                "retrieved_source_ids": list(self._retrieved_source_ids),
                "task_sha256": self._task_sha256,
                "started_at": self._started_at, "saved_at": self._wall_clock(),
                "deadline_at": None if self.task.budget.max_wall_seconds is None else self._started_at + self.task.budget.max_wall_seconds,
                "events": _snapshot(self._events), "receipts": _snapshot(self._receipts),
                "pending_action": _snapshot(self._pending), "cancel_reason": self._cancel_reason}

    def _persist(self):
        if self._store:
            self._revision = self._store.commit(self._checkpoint(), expected_revision=self._revision)

    @classmethod
    def resume(cls, store, *, expected_task=None, expand=None, condition_ranker=None,
               clock=time.monotonic, wall_clock=time.time, scientific_tools=None, scientific_limits=None,
               evidence_corpus=None, condition_study=None, impurity=None, biocatalytic_records=None,
               forward=None, backend_versions=None, process_basis=None, source_access_mode=None,
               cn_condition_model=None, reaction_yield_predictor=None, application_config=None):
        """Resume host state, counting downtime; uncertain pending work closes the episode."""
        from .episode_restore import validate_checkpoint
        store = store if isinstance(store, EpisodeStore) else EpisodeStore(store)
        state, revision = store.load()
        task = validate_checkpoint(state, expected_task=expected_task, now=wall_clock())
        if state['checkpoint_version'] not in {2, 3}:
            raise ValueError('Legacy checkpoint requires explicit scientific configuration migration')
        env = cls(task, seed=state["seed"], expand=expand, condition_ranker=condition_ranker,
                  clock=clock, wall_clock=wall_clock, scientific_tools=scientific_tools,
                  scientific_limits=scientific_limits, evidence_corpus=evidence_corpus,
                  condition_study=condition_study, impurity=impurity, biocatalytic_records=biocatalytic_records,
                  forward=forward,backend_versions=backend_versions,process_basis=process_basis,
                  source_access_mode=source_access_mode,cn_condition_model=cn_condition_model,
                  reaction_yield_predictor=reaction_yield_predictor,application_config=application_config)
        from .application_actions import configure
        if state.get('application_fingerprint',configure(None,None)[1]) != env._application_fingerprint:
            raise ValueError('Resume application configuration differs from checkpoint')
        if state['checkpoint_version'] in {2, 3}:
            if (state['capability_fingerprint'] != env._scientific_tools.fingerprint
                    or state['scientific_limits'] != science_checkpoint(env)['scientific_limits']
                    or state['source_access_mode'] != env._source_access_mode):
                raise ValueError('Resume scientific configuration differs from checkpoint')
            env._scientific_usage = dict(state['scientific_usage'])
            env._retrieved_source_ids = tuple(state['retrieved_source_ids'])
        env._store, env._revision = store, revision
        env._started_at = state["started_at"]
        env._elapsed_before = state["usage"]["wall_seconds"] + max(0.0, wall_clock() - state["saved_at"])
        env._usage = Usage(state["usage"]["actions"], state["usage"]["expansions"])
        env._routes = tuple(RouteCandidate.model_validate(r) for r in state["routes"])
        env._events, env._receipts = tuple(state["events"]), state["receipts"]
        env._submitted = tuple(state["submitted_route_ids"])
        env._terminated, env._truncated = state["terminated"], state["truncated"]
        env._pending, env._cancel_reason = state["pending_action"], state["cancel_reason"]
        if env._cancel_reason:
            env._cancelled.set()
        if env._pending:
            env._truncated = True
            env._finish("interrupted", {"reason": "Action outcome unknown after interruption; not replayed"})
        return env

    def cancel(self, reason="Host cancelled episode"):
        """Signal before taking the lock so blocked adapters cannot delay fencing."""
        if not isinstance(reason, str) or not 1 <= len(reason) <= 500:
            raise ValueError("Cancellation reason must be 1..500 characters")
        self._cancelled.set()
        with self._lock:
            self._cancel_reason, self._truncated = reason, True
            self._persist()
            return self._response("cancelled", {"reason": reason})

    def dispatch(self, action: str, arguments: dict, *, action_id=None):
        with self._lock:
            if action_id is not None and (not isinstance(action_id, str) or not 1 <= len(action_id) <= 200):
                raise ValueError("action_id must be 1..200 characters")
            try:
                payload = _snapshot({"action": action, "arguments": arguments})
                fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            except (ValueError, TypeError):
                payload = {"action": str(action), "arguments": {"rejected": "Arguments could not be serialized"}}
                fingerprint = None
            if action_id in self._receipts:
                old = self._receipts[action_id]
                if old["payload_sha256"] != fingerprint or fingerprint is None:
                    raise ValueError("Action ID payload conflict")
                return _snapshot(old["response"])
            if self._pending:
                raise RuntimeError("Unresolved action; recover episode before admitting work")
            if self._terminated or self._truncated:
                return self._response("closed", {"reason": "Episode has ended"})
            if self._cancelled.is_set():
                self._truncated = True
                self._persist()
                return self._response("cancelled", {"reason": "Host cancelled episode"})
            if self._actions_exhausted() or self._wall_exhausted():
                self._truncated = True
                self._persist()
                return self._response("budget_exhausted", {"reason": "Episode budget exhausted"})
            try:
                canonical_action = self._scientific_tools.canonical_name(action)
            except (ValueError, KeyError, TypeError):
                canonical_action = action if isinstance(action,str) else "__invalid__"
            charged_action = ACCOUNTING_ALIASES.get(canonical_action,canonical_action)
            if charged_action in ACCOUNTED_SCIENTIFIC_ACTIONS:
                self._scientific_usage = {**self._scientific_usage,
                    charged_action: self._scientific_usage.get(charged_action, 0) + 1}
            expansion_allowed = self.task.budget.max_expansions is None or self._usage.expansions < self.task.budget.max_expansions
            self._usage = replace(self._usage, actions=self._usage.actions + 1,
                expansions=self._usage.expansions + int(canonical_action == "expand" and expansion_allowed))
            self._pending = {**payload, "action_id": action_id or uuid4().hex, "payload_sha256": fingerprint,
                             "scientific_usage": dict(self._scientific_usage)}
            self._persist()  # Reservation precedes external side effects.
            previous_state = (self._routes, self._submitted, self._terminated, self._retrieved_source_ids)
            try:
                if not isinstance(arguments, dict) or fingerprint is None:
                    raise ValueError("Action arguments must be a serializable object")
                if canonical_action == "expand" and not expansion_allowed:
                    status, result = "budget_exhausted", {"reason": "Expansion budget exhausted"}
                else:
                    status, result = self._execute(canonical_action, _snapshot(arguments))
                result = _snapshot(result)
            except (ValueError, TypeError, KeyError):
                status, result = "error", {"reason": "Invalid action or arguments"}
            except _OperationStopped as exc:
                status, result = exc.status, {"reason": str(exc)}
                self._truncated = True
            except Exception:
                log.exception("Environment action failed: %s", action)
                status, result = "error", {"reason": "Scientific tool failed; no prediction available"}
            if status in {"error", "cancelled", "budget_exhausted"}:
                self._routes, self._submitted, self._terminated, self._retrieved_source_ids = previous_state
            if self._cancelled.is_set() or self._wall_exhausted():
                status = "cancelled" if self._cancelled.is_set() else "budget_exhausted"
                result = {"reason": "Result discarded after cancellation or episode deadline"}
                self._truncated = True
                self._routes, self._submitted, self._terminated, self._retrieved_source_ids = previous_state
            if self._actions_exhausted() and not self._terminated:
                self._truncated = True
            return self._finish(status, result)

    def _finish(self, status, result):
        pending = self._pending
        event = {"index": len(self._events), "action": pending["action"],
                 "action_id": pending["action_id"], "arguments": pending["arguments"],
                 "status": status, "result": _snapshot(result), "usage": self._usage_dict(),
                 "scientific_usage": dict(self._scientific_usage)}
        previous = self._events[-1]["sha256"] if self._events else ""
        event = {**event, "previous_sha256": previous,
                 "sha256": hashlib.sha256((previous + json.dumps(event, sort_keys=True)).encode()).hexdigest()}
        self._events = self._events + (event,)
        response = self._response(status, result)
        self._receipts = {**self._receipts, pending["action_id"]:
            {"payload_sha256": pending["payload_sha256"], "response": response}}
        self._pending = None
        self._persist()
        return response

    def _call_bounded(self, callback, *args, timeout_seconds=None):
        """Bound waiting; backend job termination remains the adapter's responsibility."""
        tool_deadline = time.monotonic() + timeout_seconds if timeout_seconds is not None else None
        replies = queue.Queue(maxsize=1)
        def run():
            try:
                replies.put((True, callback(*args)))
            except BaseException as exc:
                replies.put((False, exc))
        Thread(target=copy_context().run, args=(run,), daemon=True).start()
        while True:
            remaining = None if self.task.budget.max_wall_seconds is None else self.task.budget.max_wall_seconds - self._elapsed()
            tool_remaining = None if tool_deadline is None else tool_deadline - time.monotonic()
            if tool_remaining is not None and tool_remaining <= 0:
                raise TimeoutError('Scientific tool timeout')
            if self._cancelled.is_set():
                raise _OperationStopped("cancelled", "Scientific callback cancelled")
            if remaining is not None and remaining <= 0:
                raise _OperationStopped("budget_exhausted", "Scientific callback deadline exceeded")
            try:
                wait = min(value for value in (0.05, remaining, tool_remaining) if value is not None)
                ok, result = replies.get(timeout=wait)
                if not ok:
                    raise result
                return result
            except queue.Empty:
                continue

    def _response(self, status, result):
        return _snapshot({"status": status, "result": result, "usage": self._usage_dict(),
                          "terminated": self._terminated, "truncated": self._truncated})

    def _execute(self, action, args):
        if action in APPLICATION_ACTIONS:
            from .application_actions import execute_application
            return execute_application(self,action,args)
        if action == 'capabilities':
            if args:
                raise ValueError('Capability discovery takes no arguments')
            from .application_contracts import tool_schemas
            return 'ok', {'capabilities': self._scientific_tools.describe(),
                          'application_tools':tool_schemas(),
                          'application_fingerprint':self._application_fingerprint, **science_checkpoint(self)}
        if action in SCIENTIFIC_ACTIONS:
            return execute_scientific(self, action, args)
        if action == "inspect":
            from .observation import compact_observation
            return "ok", compact_observation(self, args)
        if action == "propose_expansion":
            from .agent_expansions import validate_agent_expansions
            return "ok", validate_agent_expansions(self.task, args, self._events)
        if action == "propose_route":
            route = RouteCandidate.model_validate(args["route"])
            ids = {r.route_id for r in self._routes}
            if route.route_id in ids or (route.parent_route_id and route.parent_route_id not in ids):
                raise ValueError("Revision requires a new ID and an existing parent")
            assessment = self._assess(route).model_dump(mode="json")
            self._routes = self._routes + (route,)
            return "ok", {"route_id": route.route_id, "assessment": assessment}
        if action == "graft_route":
            if set(args) != {'parent_route_id', 'donor_route_id', 'intermediate'}:
                raise ValueError('Graft requires parent, donor and intermediate')
            from .route_graft import graft_intermediate
            route = graft_intermediate(self.task, self._route(args['parent_route_id']),
                                       self._route(args['donor_route_id']), args['intermediate'])
            if any(existing.route_id == route.route_id for existing in self._routes):
                raise ValueError('Grafted route already exists')
            assessment = self._assess(route).model_dump(mode='json')
            self._routes = self._routes + (route,)
            return 'ok', {'route_id': route.route_id, 'parent_route_id': route.parent_route_id,
                          'donor_route_id': args['donor_route_id'], 'assessment': assessment}
        if action == "validate":
            return "ok", self._assess(self._route(args["route_id"])).model_dump(mode="json")
        if action == "rank_routes":
            return self._rank_routes(args)
        if action == "review_routes":
            return self._review_routes(args)
        if action == "submit":
            return self._submit(args)
        raise ValueError("Unsupported action; reset is host-only")

    def _review_routes(self, args):
        from .route_review import build_route_review
        ids = args.get('route_ids')
        if (set(args) != {'route_ids'} or not isinstance(ids, list) or not 1 <= len(ids) <= 3
                or any(not isinstance(value, str) for value in ids) or len(set(ids)) != len(ids)):
            raise ValueError('Expected one to three unique stored route IDs')
        routes = [self._route(ident) for ident in ids]
        sources, results = {}, []
        for event in self._events:
            if event['status'] != 'ok':
                continue
            if event['action'] == 'retrieve_sources' and self._source_access_mode == 'evidence_retrieval':
                for row in (event['result'].get('data') or {}).get('records', []):
                    ident = row['record_id']
                    if ident not in self._retrieved_source_ids:
                        continue
                    if ident in sources and sources[ident] != row:
                        raise ValueError('Accessible source identity changed within the episode')
                    sources = {**sources, ident:row}
            if event['action'] in {'forward_check','predict_reaction_yield','predict_conditions','score_cn_conditions'}:
                results = [*results, {'action':event['action'], 'arguments':event['arguments'],
                                     'result':event['result']}]
        return 'ok', build_route_review(self.task, routes, [self._assess(r) for r in routes],
            sources=[sources[key] for key in sorted(sources)], scientific_results=results)

    def _rank_routes(self, args):
        ids = args["route_ids"]
        if (set(args) != {"route_ids"} or not isinstance(ids, list) or len(ids) > 1000
                or any(not isinstance(v, str) for v in ids) or len(set(ids)) != len(ids)):
            raise ValueError("Expected unique route IDs")
        records = []
        for route_id in ids:
            route = self._route(route_id)
            assessment = self._assess(route).model_dump(mode="json")
            record = route.model_dump(mode="json")
            # Agent-authored yield assertions never become host model scores.
            steps = [{**step, "predicted_yield": None} for step in record["steps"]]
            records.append({**record, **assessment, "steps": steps})
        from .scientific_ranking import rank_with_contract
        ranking, calls = rank_with_contract(self, records)
        return "ok", {"ranking": ranking, "scientific_calls": calls,
                      "scope": "Declared heuristic using host predictions; independent review remains required"}

    def _assess(self, route):
        corpus = self._evidence_corpus
        trusted = () if corpus is None else tuple(r for r in corpus.trusted_legacy_records()
            if r.evidence_id in self._retrieved_source_ids)
        records = {r.evidence_id: r for r in self.task.evidence}
        records = {**records, **{r.evidence_id:r for r in trusted}}
        task = self.task.model_copy(update={'evidence':tuple(records.values())}) if trusted else self.task
        return assess_route(task, route, trusted_evidence=trusted)

    def _route(self, route_id):
        route = next((r for r in self._routes if r.route_id == route_id), None)
        if route is None:
            raise ValueError("Unknown route ID")
        return route

    def _submit(self, args):
        ids = args["route_ids"]
        if not isinstance(ids, list) or len(ids) > self.task.budget.top_k or len(set(ids)) != len(ids):
            raise ValueError("Invalid shortlist")
        assessments = [self._assess(self._route(route_id)) for route_id in ids]
        accepted = [a.route_id for a in assessments if a.graph_valid and a.inventory_complete and a.constraint_compliant
                    and a.quantity_status in {"complete", "not_requested"} and not a.acquisition_only]
        self._submitted, self._terminated = tuple(ids), True
        return "ok", {"submitted_route_ids": ids, "accepted_route_ids": accepted,
                      "acceptance_scope": "deterministic_gates_only", "independently_solved": None,
                      "assessments": [a.model_dump(mode="json") for a in assessments]}

    def step(self, action):
        info = self.dispatch(action["action"], action.get("arguments", {}), action_id=action.get("action_id"))
        return self.inspect(), 0.0, self._terminated, self._truncated, info

    def export(self):
        with self._lock:
            task_json = self.task.model_dump_json()
            return {**self.inspect(), "schema_version": "1.0", "task_sha256": hashlib.sha256(task_json.encode()).hexdigest(),
                    "events": _snapshot(self._events),
                    "assessments": [self._assess(r).model_dump(mode="json") for r in self._routes]}


class _OperationStopped(RuntimeError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
