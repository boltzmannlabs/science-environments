"""Bounded model forwarding for enzyme selection, separate from smoke checks.

The host owns credentials, endpoint, budget and scientific tool policy. Failed,
ambiguous, incomplete or unaccounted responses latch the route closed. No retry
is made, and no generic network proxy is provided to the isolated agent.
"""
from __future__ import annotations

from dataclasses import dataclass
import asyncio
import hashlib
import http.server
import json
import socketserver
import threading
import time

from enzyme_environment.connection import ENDPOINT, MODEL, inspect_stream, redact_error
from enzyme_environment.policy import digest, strict_json, validate_model_request


@dataclass(frozen=True)
class Budget:
    max_requests: int = 8
    max_output_tokens_per_request: int = 1024
    max_total_observed_tokens: int = 48000
    max_request_bytes: int = 131072
    max_total_request_bytes: int = 524288
    max_response_bytes: int = 524288
    max_wall_seconds: int = 180

    def __post_init__(self):
        caps = {"max_requests": 12, "max_output_tokens_per_request": 2048,
                "max_total_observed_tokens": 96000, "max_request_bytes": 262144,
                "max_total_request_bytes": 1048576, "max_response_bytes": 1048576,
                "max_wall_seconds": 300}
        for key, cap in caps.items():
            if type(getattr(self, key)) is not int or not 1 <= getattr(self, key) <= cap:
                raise ValueError("Invalid benchmark budget: " + key)


class BenchmarkRoute:
    def __init__(self, credential, policy, budget=None, client_factory=None):
        self.credential, self.policy = credential, policy
        self.audit = policy.audit
        self.budget = budget or Budget()
        self.client_factory = client_factory
        self.lock = threading.Lock()
        self.requests = self.request_bytes = self.observed_tokens = 0
        self.usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        self.responses = []
        self.failed = False
        self.error = None
        self.started = time.monotonic()

    async def _fetch(self, body):
        import httpx
        factory = self.client_factory or (lambda: httpx.AsyncClient(
            timeout=httpx.Timeout(50, connect=10), transport=httpx.AsyncHTTPTransport(retries=0),
            trust_env=False, follow_redirects=False))
        remaining = self.budget.max_wall_seconds - (time.monotonic() - self.started)
        async with asyncio.timeout(min(55, max(0.001, remaining))):
            async with factory() as client:
                headers = {**self.credential.headers, "Authorization": "Bearer " + self.credential.token,
                           "Content-Type": "application/json", "Accept": "text/event-stream"}
                async with client.stream("POST", ENDPOINT, headers=headers, json=body) as response:
                    if response.status_code != 200:
                        raise ValueError("Provider HTTP " + str(response.status_code))
                    media_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                    if media_type and media_type != "text/event-stream":
                        raise ValueError("Unsupported provider content type")
                    chunks, size = [], 0
                    async for chunk in response.aiter_bytes():
                        size += len(chunk)
                        if size > self.budget.max_response_bytes:
                            raise ValueError("Response size limit reached")
                        chunks.append(chunk)
                    return b"".join(chunks), media_type

    def validate(self, body):
        validate_model_request(body, self.policy.tools)
        maximum = body.get("max_output_tokens")
        if type(maximum) is not int or not 1 <= maximum <= self.budget.max_output_tokens_per_request:
            raise ValueError("Explicit model output bound required")
        # This isolated task has no reason to request remote context or background
        # execution; the underlying policy also rejects unrecognized request keys.
        if body.get("parallel_tool_calls", False) is not False:
            raise ValueError("Parallel model tool calls are disabled for this pilot")
        raw = json.dumps(body, allow_nan=False, separators=(",", ":")).encode()
        if len(raw) > self.budget.max_request_bytes:
            raise ValueError("Model request byte limit exceeded")
        return raw

    def forward(self, body):
        raw_request = self.validate(body)
        # Serialize whole forwards: simultaneous guest requests cannot race the
        # token ledger or reserve many unseen completions before usage is known.
        with self.lock:
            if self.failed:
                raise ValueError("Model route closed after a failed or ambiguous request; no retry")
            if self.requests >= self.budget.max_requests:
                raise ValueError("Model request budget exhausted")
            if self.request_bytes + len(raw_request) > self.budget.max_total_request_bytes:
                raise ValueError("Aggregate model request byte budget exhausted")
            if self.observed_tokens >= self.budget.max_total_observed_tokens:
                raise ValueError("Observed model token budget exhausted")
            if time.monotonic() - self.started >= self.budget.max_wall_seconds:
                raise ValueError("Model run wall-time budget exhausted")
            self.requests += 1
            self.request_bytes += len(raw_request)
            self.audit.record("benchmark_model_reserved", request_number=self.requests,
                request_sha256=hashlib.sha256(raw_request).hexdigest(), request_bytes=len(raw_request),
                maximum_output_tokens=body["max_output_tokens"], endpoint=ENDPOINT, retries=0)
            started = time.monotonic()
            reported_usage=None
            try:
                raw, media_type = asyncio.run(self._fetch(body))
                metadata = inspect_stream(raw, allowed_tools=self.policy.names)
                if metadata["model_returned"] != MODEL:
                    raise ValueError("Returned model differs from configured model")
                usage = metadata["usage"]
                if (any(type(usage.get(key)) is not int or usage[key] < 0 for key in self.usage)
                        or usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]):
                    raise ValueError("Missing or inconsistent model usage; quota outcome uncertain")
                reported_usage=dict(usage)
                for key in self.usage:
                    self.usage[key] += usage[key]
                self.observed_tokens = self.usage["total_tokens"]
                self.audit.record("benchmark_model_usage_observed",request_number=self.requests,
                    usage=reported_usage,aggregate_usage=dict(self.usage))
                if usage["output_tokens"] > body["max_output_tokens"]:
                    raise ValueError("Provider exceeded the declared output-token bound")
                if self.observed_tokens > self.budget.max_total_observed_tokens:
                    raise ValueError("Observed aggregate token cap exceeded; route closed")
                safe = {key: value for key, value in metadata.items() if key not in {"text", "sentinel_matches"}}
                safe.update(response_sha256=hashlib.sha256(raw).hexdigest(),
                            text_sha256=hashlib.sha256(metadata["text"].encode()).hexdigest(),
                            elapsed_seconds=time.monotonic() - started, content_type_header_missing=not bool(media_type))
                self.responses.append(safe)
                self.audit.record("benchmark_model_completed", request_number=self.requests, **safe)
                return raw
            except Exception as exc:
                self.failed = True
                # Even exception text can contain an echoed request/header. Keep
                # only known local validation messages or the exception class.
                message = str(exc) if type(exc) is ValueError else type(exc).__name__
                self.error = {"error_type": type(exc).__name__, "message": redact_error(message, self.credential)}
                self.audit.record("benchmark_model_failed_closed", request_number=self.requests,
                                  quota_or_acceptance_may_be_unknown=True,observed_usage_this_attempt=reported_usage,
                                  aggregate_observed_usage=dict(self.usage), **self.error)
                raise ValueError("Model route failed and is closed; no automatic retry") from None


class BenchmarkBroker(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, path, route):
        self.route = route
        self.policy = route.policy
        super().__init__(str(path), BenchmarkHandler)


class BenchmarkHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *args):
        pass

    def reply(self, data, status=200, media="application/json"):
        if not isinstance(data, bytes): data = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", media)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply({"error": {"message": "Endpoint not permitted"}}, 403)

    def do_POST(self):
        self.connection.settimeout(5)
        try:
            if self.path not in ("/v1/responses", "/tools"):
                self.server.policy.audit.record("benchmark_route_denied", endpoint=self.path[:100])
                return self.reply({"error": {"message": "Endpoint not permitted"}}, 403)
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 262144 or self.headers.get("Transfer-Encoding"):
                raise ValueError("Invalid request size or framing")
            raw = self.rfile.read(size)
            if len(raw) != size: raise ValueError("Truncated request")
            body = strict_json(raw)
            if self.path == "/tools":
                if not isinstance(body, dict) or set(body) != {"name", "arguments"}:
                    raise ValueError("Invalid tool envelope")
                return self.reply(self.server.policy.tool(body["name"], body["arguments"]))
            response = self.server.route.forward(body)
            self.reply(response, media="text/event-stream")
        except (ValueError, TypeError, KeyError, OSError) as exc:
            self.server.policy.audit.record("benchmark_broker_denied", error_type=type(exc).__name__)
            self.reply({"error": {"message": str(exc), "type": "benchmark_policy"}}, 400)
