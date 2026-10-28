"""Versioned local API with tenant isolation and bounded, authenticated inputs.

The service supports local experiments without claiming chemical validation.
Episode state is process-local: run one worker until durable storage is provided.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
import secrets
from threading import RLock
import time
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import Field, model_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import __version__
from .environment import SynthesisRouteEnv
from .handoff import SmallMoleculeHandoff, build_handoff_task, build_handoff_manifest, build_handoff_feedback
from .schemas import Budget, Constraints, Identifier, InventoryItem, Record, RouteCandidate, Smiles, Task
from .validation import assess_route


def _envelope(data=None, error=None):
    return {"success": error is None, "data": data, "error": error, "meta": {"schema_version": "1.0"}}


class AssessmentRequest(Record):
    task: Task
    route: RouteCandidate


class EpisodeRequest(Record):
    task: Task
    seed: Annotated[int, Field(ge=0, le=2**32 - 1)] = 0


class ActionRequest(Record):
    action: Literal["inspect", "expand", "propose_route", "validate", "predict_conditions", "rank_routes", "review_routes", "submit", "capabilities", "retrieve_sources", "forward_check", "observe_condition", "predict_impurities", "compare_process", "retrieve_biocatalysis", "score_cn_conditions", "predict_reaction_yield", "application_report", "condition_options", "observe_route_condition", "predict_route_impurities", "retrieve_application_sources"]
    arguments: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def finite_json(self):
        json.dumps(self.arguments, allow_nan=False)
        return self


class ConditionCandidate(Record):
    candidate_id: Identifier
    aryl_halide: Smiles = Field(alias="aryl halide")
    ligand: Smiles
    additive: Smiles
    base: Smiles


class ConditionRankingRequest(Record):
    candidates: Annotated[tuple[ConditionCandidate, ...], Field(min_length=1, max_length=1000)]

    @model_validator(mode="after")
    def unique_candidates(self):
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(set(ids)) != len(ids):
            raise ValueError("Condition candidate IDs must be unique")
        return self


@dataclass(frozen=True)
class _Episode:
    owner: str
    environment: SynthesisRouteEnv
    created_at: float
    handoff: dict | None = None
    handoff_manifest: dict | None = None


class _BoundaryMiddleware:
    def __init__(self, app, *, api_keys, max_body_bytes, requests_per_minute, clock):
        self.app = app
        self.keys = tuple(api_keys.items())
        self.max_body_bytes, self.limit, self.clock = max_body_bytes, requests_per_minute, clock
        self._requests, self._lock = {}, RLock()

    def _owner(self, headers):
        value = headers.get(b"authorization", b"").decode("latin-1")
        scheme, _, token = value.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        owner = None
        for expected, identity in self.keys:
            if secrets.compare_digest(token.encode(), expected.encode()):
                owner = identity
        return owner

    def _admit(self, owner):
        now = self.clock()
        with self._lock:
            recent = tuple(t for t in self._requests.get(owner, ()) if now - t < 60)
            if len(recent) >= self.limit:
                return max(1, math.ceil(60 - (now - recent[0])))
            self._requests = {**self._requests, owner: recent + (now,)}
        return None

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", ()))
        owner = self._owner(headers)
        if owner is None:
            response = JSONResponse(_envelope(error="Authentication required"), 401,
                                    headers={"WWW-Authenticate": "Bearer"})
            return await response(scope, receive, send)
        retry = self._admit(owner)
        if retry:
            response = JSONResponse(_envelope(error="Request rate limit exceeded"), 429,
                                    headers={"Retry-After": str(retry)})
            return await response(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_body_bytes:
                response = JSONResponse(_envelope(error="Request body exceeds service limit"), 413)
                return await response(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        scope = {**scope, "state": {**scope.get("state", {}), "owner": owner}}
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        async def secure_send(message):
            if message["type"] == "http.response.start":
                extra = [(b"cache-control", b"no-store"), (b"x-content-type-options", b"nosniff")]
                message = {**message, "headers": list(message.get("headers", ())) + extra}
            await send(message)

        return await self.app(scope, replay, secure_send)


def create_app(api_keys: dict[str, str], expand=None, *, condition_ranker=None, max_body_bytes=1_048_576,
               requests_per_minute=120, max_episodes_per_owner=10,
               episode_ttl_seconds=7200, clock=time.monotonic, scientific_tools=None,
               scientific_limits=None, evidence_corpus=None, condition_study=None, impurity=None,
               biocatalytic_records=None, source_access_mode=None, process_basis=None, forward=None,
               backend_versions=None, cn_condition_model=None, reaction_yield_predictor=None, application_config=None,
               allow_unbudgeted=False):
    """Create a local app from caller-supplied secret token→owner bindings.

    No token appears in OpenAPI or result artifacts. Scientific adapters are
    operator-supplied callables; requests cannot select filesystem paths/models.
    """
    if not isinstance(api_keys, dict) or not api_keys or any(
        not isinstance(v, str) or not v.strip() for pair in api_keys.items() for v in pair
    ):
        raise ValueError("At least one nonempty API token and owner must be configured")
    for value in (max_body_bytes, requests_per_minute, max_episodes_per_owner, episode_ttl_seconds):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError("Service limits must be positive integers")
    if type(allow_unbudgeted) is not bool:
        raise ValueError('allow_unbudgeted must be boolean')
    app = FastAPI(title="Retrosynthesis", version=__version__, docs_url=None,
                  redoc_url=None, openapi_url=None)
    app.add_middleware(_BoundaryMiddleware, api_keys=dict(api_keys), max_body_bytes=max_body_bytes,
                       requests_per_minute=requests_per_minute, clock=clock)
    episodes, lock = {}, RLock()

    def authenticated_openapi():
        if app.openapi_schema is None:
            schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
            components = {**schema.get("components", {}), "securitySchemes": {
                "BearerAuth": {"type": "http", "scheme": "bearer"}}}
            app.openapi_schema = {**schema, "components": components,
                                  "security": [{"BearerAuth": []}]}
        return app.openapi_schema

    app.openapi = authenticated_openapi

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        errors = [{"location": list(item["loc"]), "type": item["type"]} for item in exc.errors()]
        return JSONResponse(_envelope(error={"message": "Invalid request", "fields": errors}), 422)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse(_envelope(error=exc.detail), exc.status_code, headers=exc.headers)

    @app.exception_handler(Exception)
    async def internal_error(request, exc):
        return JSONResponse(_envelope(error="Service operation failed"), 500)

    def check_budget(task):
        if task.budget.regime == 'unbudgeted':
            if not allow_unbudgeted:
                raise HTTPException(422, 'Unbudgeted episodes require host opt-in')
            return
        limits = {"max_actions": 2000, "max_expansions": 1000,
                  "max_wall_seconds": 1800, "max_llm_tokens": 100000}
        if any(getattr(task.budget, key) > value for key, value in limits.items()):
            raise HTTPException(422, "Requested budget exceeds service limits")

    def prune():
        nonlocal episodes
        now = clock()
        episodes = {key: value for key, value in episodes.items()
                    if value.environment.task.budget.regime == 'unbudgeted' or now - value.created_at < episode_ttl_seconds}

    def get_episode(episode_id, owner):
        with lock:
            prune()
            entry = episodes.get(episode_id)
            if entry is None or entry.owner != owner:
                raise HTTPException(404, "Episode not found")
            return entry

    def add_episode(task, seed, owner, handoff=None, handoff_manifest=None):
        nonlocal episodes
        check_budget(task)
        with lock:
            prune()
            if sum(entry.owner == owner for entry in episodes.values()) >= max_episodes_per_owner:
                raise HTTPException(429, "Episode capacity reached; delete completed episodes")
            episode_id = uuid4().hex
            from .host_policy import science_regime
            science = science_regime({'scientific_limits':scientific_limits,'condition_study':condition_study},task.budget.regime)
            env = SynthesisRouteEnv(task, seed=seed, expand=expand, condition_ranker=condition_ranker, clock=clock,
                scientific_tools=scientific_tools, scientific_limits=science['scientific_limits'], evidence_corpus=evidence_corpus,
                condition_study=science['condition_study'], impurity=impurity, biocatalytic_records=biocatalytic_records,
                source_access_mode=source_access_mode, process_basis=process_basis, forward=forward,
                backend_versions=backend_versions,cn_condition_model=cn_condition_model,
                reaction_yield_predictor=reaction_yield_predictor,application_config=application_config)
            episodes = {**episodes, episode_id: _Episode(owner, env, clock(), handoff, handoff_manifest)}
        return {"episode_id": episode_id, "observation": env.inspect(), "handoff": handoff}

    @app.get("/v1/health")
    def health():
        return _envelope({"version": __version__, "storage": "process_local",
                          "execution_scope": "local"})

    @app.get("/v1/openapi.json", include_in_schema=False)
    def openapi():
        return app.openapi()

    @app.post("/v1/routes/assess")
    def assess(payload: AssessmentRequest):
        check_budget(payload.task)
        return _envelope(assess_route(payload.task, payload.route).model_dump(mode="json"))

    @app.post("/v1/conditions/rank")
    def rank_conditions(payload: ConditionRankingRequest):
        if condition_ranker is None:
            raise HTTPException(503, "No condition model has been configured by the operator")
        query = Task(task_id='condition-ranking', target=payload.candidates[0].aryl_halide, inventory=(),
                     budget=Budget(max_actions=1, max_wall_seconds=60))
        tool = SynthesisRouteEnv(query, condition_ranker=condition_ranker)
        inputs = [{'id':row.candidate_id, **row.model_dump(by_alias=True, exclude={'candidate_id'})}
                  for row in payload.candidates]
        response = tool.dispatch('predict_conditions', {'candidates':inputs})
        if response['status'] != 'ok':
            raise HTTPException(503, 'Condition model unavailable or returned an invalid contract')
        result = response['result']['tool_result']
        records = [{**{k:v for k,v in row.items() if k != 'id'}, 'candidate_id':row['id']}
                   for row in result['data']['predictions']]
        records = sorted(records, key=lambda row: (-row['predicted_yield_percent'], row['candidate_id']))
        return _envelope({'ranked_candidates': records, 'tool_result':result,
                          'scope': 'Dreher-Doyle condition yield prediction; no general route feasibility claim'})

    @app.post("/v1/episodes", status_code=201)
    def create_episode(payload: EpisodeRequest, request: Request):
        return _envelope(add_episode(payload.task, payload.seed, request.state.owner))

    @app.get("/v1/episodes/{episode_id}")
    def read_episode(episode_id: Identifier, request: Request):
        entry = get_episode(episode_id, request.state.owner)
        return _envelope({"episode_id": episode_id, "episode": entry.environment.export(), "handoff": entry.handoff})

    @app.post("/v1/episodes/{episode_id}/actions")
    def action(episode_id: Identifier, payload: ActionRequest, request: Request):
        entry = get_episode(episode_id, request.state.owner)
        result = entry.environment.dispatch(payload.action, payload.arguments)
        code = {"closed": 409, "budget_exhausted": 429, "error": 400, "unavailable": 503}.get(result["status"], 200)
        return JSONResponse(_envelope(result, None if code == 200 else result["status"]), code)

    @app.delete("/v1/episodes/{episode_id}")
    def delete_episode(episode_id: Identifier, request: Request):
        nonlocal episodes
        with lock:
            get_episode(episode_id, request.state.owner)
            episodes = {key: value for key, value in episodes.items() if key != episode_id}
        return _envelope({"episode_id": episode_id, "deleted": True})

    @app.get("/v1/episodes/{episode_id}/feedback")
    def feedback(episode_id: Identifier, request: Request):
        with lock:
            entry = get_episode(episode_id, request.state.owner)
            if entry.handoff_manifest is None:
                raise HTTPException(409, "Episode has no small-molecule handoff")
            return _envelope(build_handoff_feedback(entry.handoff_manifest, entry.environment.export(),
                                                   episode_id=episode_id))

    @app.post("/v1/handoffs/small-molecule", status_code=201)
    def handoff(payload: SmallMoleculeHandoff, request: Request):
        task = build_handoff_task(payload)
        manifest = build_handoff_manifest(payload)
        provenance = payload.model_dump(mode="json", include={"candidate_id", "source_job_id", "source_tool"})
        return _envelope(add_episode(task, payload.seed, request.state.owner, provenance, manifest))

    return app


def app_from_environment():
    """Local Uvicorn factory; credentials are supplied through the environment."""
    token = os.environ.get("SYNTHESIS_ROUTE_GYM_API_TOKEN", "")
    owner = os.environ.get("SYNTHESIS_ROUTE_GYM_API_OWNER", "")
    return create_app({token: owner})
