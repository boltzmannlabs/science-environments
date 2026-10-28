# Local API compatibility contract

This directory retains its existing path and contains local API schemas, tests
and receipts. Ownership belongs to the Synthesis and Retrosynthesis pod. The
tool version is `0.1.0`, the API version is `v1`, and the request/result schema
version is `1.0`. `manifest.json` records the executable boundaries.

## Local use

Install the package with its `api` extra. Set
`SYNTHESIS_ROUTE_GYM_API_TOKEN` and `SYNTHESIS_ROUTE_GYM_API_OWNER` in the local
process environment, then run:

```sh
uvicorn synthesis_route_gym.api:app_from_environment --factory --host 127.0.0.1 --port 8080 --workers 1
```

The factory fails if either value is missing. Tests can construct
`create_app(api_keys={token: owner, ...})` directly. Every endpoint, including
health and OpenAPI, requires `Authorization: Bearer ...`; identity comes from
the token binding. Health reports `execution_scope: local`.

Bind existing local scientific tools using `create_app(..., expand=adapter.expand,
condition_ranker=loaded_ranker)`. The standalone factory has neither configured
and returns explicit unavailable results for operations requiring them. Request
payloads cannot select filesystem paths, model files, credentials or another
LLM. The API does not select or train an LLM.

## Request/result flow

1. `POST /v1/episodes` with `{ "task": <Task>, "seed": 0 }` creates an episode.
2. `POST /v1/episodes/{id}/actions` accepts `action` and `arguments`. Actions are
   `inspect`, `expand`, `propose_route`, `validate`, `predict_conditions`,
   `rank_routes` and `submit`. Agent-requested resets are rejected.
3. Submit a shortlist with action `submit` and `arguments.route_ids`.
4. `GET /v1/episodes/{id}` exports routes, assessments, usage and the hash-linked
   event trace. `DELETE /v1/episodes/{id}` removes the episode.

`predict_conditions` takes `arguments.candidates`: each has `id`, `aryl halide`,
`ligand`, `additive` and `base`, with chemical roles represented as SMILES.
`rank_routes` takes `arguments.route_ids` referring to previously proposed routes.
Both actions use the same caller-configured model as `/v1/conditions/rank`,
consume an episode action, and appear in the event trace. Route ranking ignores
agent-authored predicted yields and uses the configured model when applicable.

`POST /v1/routes/assess` accepts `{ "task": <Task>, "route": <RouteCandidate> }`.
`POST /v1/conditions/rank` accepts `candidates` with unique `candidate_id` and
the same four chemical roles. `GET /v1/openapi.json` gives precise schemas.
Responses contain `success`, `data`, `error` and schema-version metadata. Errors
omit credentials, raw input values and exception traces. HTTP status codes
distinguish invalid input (400/422), authentication (401), absent/foreign episode
(404), closed episode (409), size (413), budget/rate/capacity (429), and
unavailable scientific tool (503).

## Candidate and artifact compatibility

`POST /v1/handoffs/small-molecule` requires `candidate_id`, `smiles`,
`source_job_id`, `source_tool` and `inventory`; constraints, budget and seed are
optional. It canonicalizes identity while preserving stereochemistry and retains
the supplied upstream provenance beside the local episode.

The pure Python `synthesis_route_gym.rebolt_bridge.enrich_rebolt_paths` interface
adds annotations to existing saved REBOLT trees. Actual-artifact fixtures,
negative findings and receipts are in `examples/rebolt/`. Legacy scores and
citations remain unverified metadata; this interface changes no existing worker.

## Limits and scientific interpretation

- Requests default to 1 MiB and 120 requests per minute per owner. At most ten
  episodes per owner are retained; they expire after two hours.
- Episode state is process-local and lost on restart. Use one local worker
  and export results before deletion or restart.
- Task caps are 2,000 actions, 1,000 expansions, 1,800 seconds and 100,000 declared
  LLM tokens. Actual LLM accounting belongs to the Agent Scientist runner.
- Scientific callbacks must enforce their own deadlines. A local API thread is
  not a sandbox for arbitrary callback code.
- The condition model concerns the measured Dreher–Doyle screening domain, not
  general multistep feasibility. Yields remain predictions. Deterministic checks
  do not verify publications, mechanisms or experimental success. Unknown amounts
  and costs remain unknown; independent chemical review is separate.

## Local acceptance checks

```sh
.venv/bin/python -m pytest tests/test_api.py tests/test_rebolt_bridge.py -q
.venv/bin/python integrations/platform/verify_local_http.py
```

The first command checks authentication, owner isolation, validation, resource
limits, candidate provenance and configured-model episode actions. The second
uses a temporary loopback HTTP process and writes `local_http_receipt.json`
and `openapi.v1.json`; it does not invoke external scientific services.
