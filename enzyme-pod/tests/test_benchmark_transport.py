"""Fake provider tests for scientific forwarding; no auth store or quota use."""
import copy
import asyncio
import json
import socket
import threading
import time

import httpx
import pytest

from enzyme_environment.transport import BenchmarkBroker, BenchmarkRoute, Budget
from enzyme_environment.connection import ENDPOINT, HostCredential, inspect_stream
from enzyme_environment.policy import Audit, Policy, verify_audit


def request(policy):
    return {"model": "gpt-6.1-sol", "stream": True, "store": False,
            "tools": copy.deepcopy(list(policy.tools)), "input": [], "max_output_tokens": 1024,
            "parallel_tool_calls": False}


def event_stream(*, tool=None, usage=None, model="gpt-6.1-sol"):
    output = [{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Synthetic reply"}]}]
    if tool:
        output = [{"type": "function_call", "name": tool, "call_id": "call_unit_1", "arguments": '{"dataset":"candidates"}'}]
    response = {"id": "resp_unit", "model": model, "status": "completed", "output": output,
                "usage": {"input_tokens": 5, "output_tokens": 4, "total_tokens": 9} if usage is None else usage}
    return ("event: response.completed\ndata: " + json.dumps({"type": "response.completed", "response": response}) + "\n\n").encode()


@pytest.fixture
def policy(tmp_path):
    audit = Audit(tmp_path / "audit.jsonl")
    p = Policy({"candidates": [{"candidate_id": f"S{i}"} for i in range(20)], "task": [], "train": [], "development": []},
               tmp_path / "result", audit)
    yield p
    audit.close()


def make_route(policy, raw=None, status=200, budget=None, content_type="text/event-stream", fail=False):
    attempts = []
    def handle(req):
        assert str(req.url) == ENDPOINT
        attempts.append(1)
        if fail: raise httpx.ConnectError("unit-provider-error")
        return httpx.Response(status, headers={"Content-Type": content_type}, content=raw or event_stream())
    route = BenchmarkRoute(HostCredential("unit-token-not-real", {}), policy, budget,
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handle), trust_env=False, follow_redirects=False))
    return route, attempts


def test_function_calls_opt_in_and_hashes_only(policy):
    raw = event_stream(tool="benchmark_read")
    with pytest.raises(ValueError): inspect_stream(raw)
    result = inspect_stream(raw, policy.names)
    assert result["function_calls"][0]["name"] == "benchmark_read"
    assert "arguments" not in result["function_calls"][0]
    route, attempts = make_route(policy, raw)
    assert route.forward(request(policy)) == raw
    assert len(attempts) == 1 and route.usage["total_tokens"] == 9
    log = policy.audit.path.read_text()
    assert "unit-token-not-real" not in log and "Synthetic reply" not in log


def test_successful_requests_count_usage_and_stop_at_request_cap(policy):
    route, attempts = make_route(policy, budget=Budget(max_requests=2))
    route.forward(request(policy))
    route.forward(request(policy))
    with pytest.raises(ValueError, match="budget exhausted"): route.forward(request(policy))
    assert len(attempts) == 2
    assert route.usage == {"input_tokens": 10, "output_tokens": 8, "total_tokens": 18}


@pytest.mark.parametrize("status", [302, 400, 401, 403, 429, 500])
def test_failed_response_latches_closed(status, policy):
    route, attempts = make_route(policy, status=status)
    with pytest.raises(ValueError, match="closed"): route.forward(request(policy))
    with pytest.raises(ValueError, match="closed"): route.forward(request(policy))
    assert len(attempts) == 1
    assert verify_audit(policy.audit.path)[-1]["quota_or_acceptance_may_be_unknown"]


def test_network_error_does_not_expose_or_retry_provider_message(policy):
    route, attempts = make_route(policy, fail=True)
    with pytest.raises(ValueError): route.forward(request(policy))
    with pytest.raises(ValueError): route.forward(request(policy))
    assert len(attempts) == 1
    assert "unit-provider-error" not in str(route.error)


@pytest.mark.parametrize("raw", [event_stream(tool="terminal"), event_stream(usage={}),
    event_stream(usage={"input_tokens": 5, "output_tokens": 4, "total_tokens": 10}),
    event_stream(usage={"input_tokens": True, "output_tokens": 4, "total_tokens": 5}),
    event_stream(model="different-model"), b"data: not json\n\n"])
def test_bad_or_unaccounted_response_closes_route(policy, raw):
    route, attempts = make_route(policy, raw)
    with pytest.raises(ValueError): route.forward(request(policy))
    assert route.failed
    with pytest.raises(ValueError): route.forward(request(policy))
    assert len(attempts) == 1


@pytest.mark.parametrize("key,value", [("max_output_tokens", 1025), ("max_output_tokens", None),
    ("parallel_tool_calls", True), ("base_url", "https://evil.example"), ("model", "other")])
def test_bad_request_does_not_spend_attempt(policy, key, value):
    route, attempts = make_route(policy)
    body = request(policy)
    body[key] = value
    with pytest.raises(ValueError): route.forward(body)
    assert not attempts and route.requests == 0


def test_headerless_semantic_stream_is_accepted(policy):
    route, attempts = make_route(policy, content_type="")
    route.forward(request(policy))
    assert route.responses[0]["content_type_header_missing"]


def test_budgets_and_byte_limits(policy):
    with pytest.raises(ValueError): Budget(max_requests=True)
    with pytest.raises(ValueError): Budget(max_requests=13)
    route, attempts = make_route(policy, budget=Budget(max_request_bytes=10))
    with pytest.raises(ValueError, match="byte limit"): route.forward(request(policy))
    assert not attempts
    route, attempts = make_route(policy, budget=Budget(max_total_observed_tokens=8))
    with pytest.raises(ValueError): route.forward(request(policy))
    assert route.failed and route.usage["total_tokens"] == 9 and len(attempts) == 1
    failed=[row for row in verify_audit(policy.audit.path) if row["kind"]=="benchmark_model_failed_closed"][-1]
    assert failed["observed_usage_this_attempt"]["total_tokens"]==9
    assert failed["aggregate_observed_usage"]["total_tokens"]==9
    observed=[row for row in verify_audit(policy.audit.path) if row["kind"]=="benchmark_model_usage_observed"]
    assert observed[-1]["usage"]["total_tokens"]==9


def test_aggregate_bytes_reserved_before_forward(policy):
    size = len(json.dumps(request(policy), separators=(",", ":")).encode())
    route, attempts = make_route(policy, budget=Budget(max_total_request_bytes=size + 1))
    route.forward(request(policy))
    with pytest.raises(ValueError, match="byte budget"): route.forward(request(policy))
    assert len(attempts) == 1


def test_slow_provider_is_cancelled_at_total_deadline(policy):
    attempts = []
    async def slow(request):
        attempts.append(1)
        await asyncio.sleep(2)
        return httpx.Response(200, content=event_stream())
    route = BenchmarkRoute(HostCredential("unit-token-not-real", {}), policy, Budget(max_wall_seconds=1),
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(slow)))
    route.started = time.monotonic() - 0.9
    started = time.monotonic()
    with pytest.raises(ValueError): route.forward(request(policy))
    assert time.monotonic() - started < 1
    assert route.failed and len(attempts) == 1 and route.error["error_type"] == "TimeoutError"


def test_streamed_tool_cannot_hide_behind_benign_terminal(policy):
    item = {"type": "response.output_item.done", "item": {"type": "function_call", "name": "terminal"}}
    raw = ("data: " + json.dumps(item) + "\n\n").encode() + event_stream()
    route, attempts = make_route(policy, raw)
    with pytest.raises(ValueError): route.forward(request(policy))
    assert route.failed and len(attempts) == 1


def test_only_local_benchmark_routes(policy, tmp_path):
    route, _ = make_route(policy)
    broker = BenchmarkBroker(tmp_path / "broker.sock", route)
    thread = threading.Thread(target=broker.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(transport=httpx.HTTPTransport(uds=broker.server_address), trust_env=False) as client:
            assert client.post("http://broker/api/submit-job", json={}).status_code == 403
            assert client.get("http://broker/v1/models").status_code == 403
            assert client.post("http://broker/tools", json={"name": "terminal", "arguments": {}}).status_code == 400
            assert client.post("http://broker/tools", json={"name": "benchmark_read", "arguments": {"dataset": "task"}}).status_code == 200
            result = client.post("http://broker/v1/responses", json=request(policy))
            assert result.status_code == 200 and "text/event-stream" in result.headers["content-type"]
    finally:
        broker.shutdown()
        broker.server_close()
        thread.join(timeout=3)
