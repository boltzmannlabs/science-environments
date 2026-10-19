"""One explicitly approved, host-only Codex connection check. No tool proxy."""
from __future__ import annotations

import dataclasses
import hashlib
import http.server
import json
from pathlib import Path
import re
import socketserver
import threading
import time

from enzyme_environment.policy import digest, strict_json

MODEL = "gpt-6.1-sol"
BASE = "https://chatgpt.com/backend-api/codex"
ENDPOINT = BASE + "/responses"
SENTINEL = "ENZYME_CONNECTION_OK"
SMOKE_BODY = {"model": MODEL, "instructions": "This is a connection check only. Follow the short output instruction. Do not use tools.",
              "input": [{"role": "user", "content": "Reply exactly ENZYME_CONNECTION_OK and nothing else."}],
              "tools": [], "tool_choice": "none", "parallel_tool_calls": False,
              "store": False, "stream": True, "max_output_tokens": 256, "reasoning": {"effort": "low"}}


class AuthorizationUnavailable(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


@dataclasses.dataclass(repr=False)
class HostCredential:
    token: str = dataclasses.field(repr=False)
    headers: dict = dataclasses.field(repr=False)
    source: str = "existing-agent-authorization"


def authorize_read_only(profile):
    """Use the existing agent helper; no login, token adoption or refresh."""
    import sci_yaml as yaml
    from sci_cli.auth_codex import resolve_codex_runtime_credentials, _codex_access_token_is_expiring
    from agent.codex_headers import codex_cloudflare_headers
    cfg = yaml.safe_load((Path(profile) / "config.yaml").read_text()) or {}
    model = cfg.get("model") or {}
    if model.get("provider") != "openai-codex" or model.get("default") != MODEL:
        raise AuthorizationUnavailable("configured_model_or_provider_differs")
    try:
        creds = resolve_codex_runtime_credentials(read_only=True, refresh_if_expiring=False)
    except Exception as exc:
        code = getattr(exc, "code", "authorization_unavailable")
        if not isinstance(code, str) or len(code) > 100 or not all(c.isalnum() or c == "_" for c in code):
            code = "authorization_unavailable"
        raise AuthorizationUnavailable(code) from None
    base = str(creds.get("base_url", "")).rstrip("/")
    if base != BASE:
        raise AuthorizationUnavailable("non_official_route_not_approved")
    token = creds.get("api_key")
    if not isinstance(token, str) or not token.strip():
        raise AuthorizationUnavailable("authorization_missing")
    if _codex_access_token_is_expiring(token, 0):
        raise AuthorizationUnavailable("authorization_expired")
    return HostCredential(token, codex_cloudflare_headers(token, base_url=BASE), str(creds.get("source", "existing")))


def validate_probe_request(body):
    if not isinstance(body, dict) or digest(body) != digest(SMOKE_BODY):
        raise ValueError("Only the exact non-scientific connection-check request is permitted")
    if len(json.dumps(body).encode()) > 2048:
        raise ValueError("Connection request too large")


def redact_error(value, credential):
    text = str(value)
    for secret in [credential.token, *credential.headers.values()]:
        if isinstance(secret, str) and secret:
            text = text.replace(secret, "[redacted]")
    text = re.sub(r"Bearer\s+\S+", "Bearer [redacted]", text, flags=re.I)
    text = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[redacted-jwt]", text)
    return text[:500]


def prefix_diagnostic(raw, credential, status_code, content_type):
    """Classify a bounded prefix without saving model text or private reasoning."""
    raw = raw[:2048]
    info = {"status_code": status_code,
            "content_type": redact_error(content_type, credential),
            "body_prefix_sha256": hashlib.sha256(raw).hexdigest(), "body_prefix_bytes": len(raw)}
    lines = raw.decode("utf-8", errors="replace").splitlines()
    info["has_sse_data_prefix"] = any(line.startswith("data:") for line in lines)
    info["sse_event_names_in_prefix"] = [line[6:].strip() for line in lines
        if line.startswith("event:") and re.fullmatch(r"(?:response\.[a-zA-Z0-9_.]+|error)", line[6:].strip())][:10]
    try:
        value = strict_json(raw)
        if isinstance(value, dict):
            info["body_type"] = "json_object"
            for key in ("error", "detail", "message"):
                if key in value:
                    item = value[key]
                    if isinstance(item, dict):
                        item = {k: item[k] for k in ("message", "type", "code", "param")
                                if k in item and isinstance(item[k], (str, int, float, bool, type(None)))}
                    elif not isinstance(item, (str, int, float, bool, type(None))):
                        item = "non-scalar provider detail omitted"
                    info["provider_" + key] = redact_error(json.dumps(item), credential)
            info["contains_completed_response"] = value.get("object") == "response" and value.get("status") == "completed"
    except (ValueError, UnicodeError):
        info["body_type"] = "not_json"
        title = re.search(r"<title[^>]*>([^<]{0,200})</title>", raw.decode(errors="replace"), re.I)
        if title:
            info["page_title"] = redact_error(title.group(1), credential)
    return info


def response_diagnostic(response, credential):
    """Bounded redacted errors only; never headers/cookies or full model output."""
    raw = b""
    for chunk in response.iter_bytes():
        raw += chunk[:2048 - len(raw)]
        if len(raw) >= 2048:
            break
    return prefix_diagnostic(raw, credential, response.status_code, response.headers.get("content-type", ""))


def inspect_stream(raw, allowed_tools=()):
    events, terminal, texts = 0, None, []
    # Parse complete SSE frames, including multi-line data fields. Do not accept
    # arbitrary HTML/JSON just because a line somewhere contains a data marker.
    payloads, data, event_name = [], [], None
    for line in [*raw.decode("utf-8-sig").splitlines(), ""]:
        if not line:
            if data:
                payloads.append((event_name, "\n".join(data)))
            data, event_name = [], None
        elif line.startswith(":"):
            continue
        else:
            field, separator, value = line.partition(":")
            if not separator or field not in ("data", "event", "id", "retry"):
                raise ValueError("Invalid event-stream framing")
            value = value[1:] if value.startswith(" ") else value
            if field == "data":
                data.append(value)
            elif field == "event":
                event_name = value
    for event_name, payload in payloads:
        payload = payload.strip()
        if payload == "[DONE]":
            continue
        event = strict_json(payload)
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ValueError("Invalid model event")
        if event_name and event_name != event["type"]:
            raise ValueError("Event name and payload type disagree")
        events += 1
        if event.get("type") in ("response.output_item.added", "response.output_item.done"):
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "function_call":
                if not isinstance(item.get("name"), str) or item["name"] not in allowed_tools:
                    raise ValueError("Unapproved streamed tool call")
        if event.get("type") == "response.completed":
            if terminal is not None:
                raise ValueError("Duplicate completed response")
            terminal = event.get("response", {})
        elif event.get("type") in ("response.failed", "response.incomplete", "error"):
            raise ValueError("Provider returned a failed or incomplete stream")
    if not isinstance(terminal, dict) or terminal.get("status") != "completed":
        raise ValueError("No completed model response in the stream")
    output = terminal.get("output")
    if not isinstance(output, list):
        raise ValueError("Invalid completed response output")
    calls, call_ids = [], set()
    for item in output:
        if not isinstance(item, dict) or item.get("type") not in ("message", "reasoning", "function_call"):
            raise ValueError("Unexpected tool call in connection-only response")
        if item.get("type") == "function_call":
            name, call_id, arguments = item.get("name"), item.get("call_id"), item.get("arguments")
            if (not isinstance(name, str) or name not in allowed_tools
                    or not isinstance(call_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", call_id)
                    or call_id in call_ids or not isinstance(arguments, str) or len(arguments) > 32768):
                raise ValueError("Unapproved or malformed function tool call")
            if not isinstance(strict_json(arguments), dict):
                raise ValueError("Function arguments must be a JSON object")
            call_ids.add(call_id)
            calls.append({"name": name, "call_id": call_id, "arguments_sha256": hashlib.sha256(arguments.encode()).hexdigest()})
        if item.get("type") == "message":
            content = item.get("content")
            if not isinstance(content, list):
                raise ValueError("Invalid message content")
            for part in content:
                if not isinstance(part, dict):
                    raise ValueError("Invalid message part")
                if part.get("type") == "output_text":
                    if not isinstance(part.get("text"), str):
                        raise ValueError("Invalid output text")
                    texts.append(part["text"])
    text = "".join(texts).strip()
    usage = terminal.get("usage") or {}
    if not isinstance(usage, dict):
        raise ValueError("Invalid usage metadata")
    result = {"events": events, "response_id": terminal.get("id"), "model_returned": terminal.get("model"),
            "text": text, "sentinel_matches": text == SENTINEL,
            "usage": {k: usage.get(k) for k in ("input_tokens", "output_tokens", "total_tokens")}}
    if allowed_tools:
        result["function_calls"] = calls
    return result


class LiveRoute:
    def __init__(self, credential, audit, client_factory=None):
        self.credential, self.audit = credential, audit
        self.client_factory = client_factory
        self.lock = threading.Lock()
        self.attempted = False
        self.result = None
        self.error = None

    def forward_once(self, body):
        validate_probe_request(body)
        with self.lock:
            if self.attempted:
                raise ValueError("One-request approval already consumed; automatic retry is prohibited")
            self.attempted = True
        self.audit.record("live_request_reserved", endpoint=ENDPOINT, request_hash=digest(body),
                          max_requests=1, max_output_tokens=256, retries=0, store=False)
        import httpx
        factory = self.client_factory or (lambda: httpx.Client(
            timeout=httpx.Timeout(45, connect=10), transport=httpx.HTTPTransport(retries=0),
            trust_env=False, follow_redirects=False))
        started, chunks, size = time.monotonic(), [], 0
        try:
            with factory() as client:
                headers = {**self.credential.headers, "Authorization": "Bearer " + self.credential.token,
                           "Content-Type": "application/json", "Accept": "text/event-stream"}
                with client.stream("POST", ENDPOINT, headers=headers, json=body) as response:
                    if response.status_code != 200:
                        # Errors contain only this fixed synthetic prompt; redact credentials
                        # defensively before saving any bounded error details.
                        self.error = response_diagnostic(response, self.credential)
                        raise ValueError("Provider HTTP " + str(response.status_code))
                    content_type = response.headers.get("content-type", "").strip()
                    media_type = content_type.split(";", 1)[0].strip().lower()
                    if media_type and media_type != "text/event-stream":
                        self.error = {"message": "Unexpected provider content type", **response_diagnostic(response, self.credential)}
                        raise ValueError("Unexpected provider content type")
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > 262144 or time.monotonic() - started > 55:
                            raise ValueError("Response size/time limit reached; no retry")
                        chunks.append(chunk)
            raw = b"".join(chunks)
            try:
                self.result = inspect_stream(raw)
            except (ValueError, UnicodeError) as exc:
                self.error = {"message": "Invalid semantic event stream: " + str(exc),
                              **prefix_diagnostic(raw, self.credential, 200, content_type)}
                raise ValueError("Invalid semantic event stream") from None
            self.result["content_type_header_missing"] = not bool(content_type)
            self.result["semantic_stream_validated"] = True
            self.audit.record("live_response", response_hash=hashlib.sha256(raw).hexdigest(),
                              elapsed_seconds=time.monotonic() - started, **self.result)
            return raw
        except Exception as exc:
            if self.error is None:
                self.error = {"error_type": type(exc).__name__, "message": redact_error(str(exc), self.credential)}
            self.audit.record("live_failed_no_retry", **self.error,
                              acceptance_or_quota_unknown=True, elapsed_seconds=time.monotonic() - started)
            raise ValueError("Live check did not complete; no retry was attempted") from None


class LiveBroker(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    def __init__(self, path, route):
        self.route = route
        super().__init__(str(path), LiveHandler)


class LiveHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, code, data, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.respond(403, b'{"error":{"message":"Endpoint not permitted"}}')

    def do_POST(self):
        self.connection.settimeout(5)
        try:
            if self.path != "/v1/responses":
                self.server.route.audit.record("live_broker_denied", endpoint=self.path[:100])
                return self.respond(403, b'{"error":{"message":"Endpoint not permitted"}}')
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2048 or self.headers.get("Transfer-Encoding"):
                raise ValueError("Invalid request size/framing")
            raw = self.server.route.forward_once(strict_json(self.rfile.read(size)))
            self.respond(200, raw, "text/event-stream")
        except (ValueError, OSError, TypeError) as exc:
            self.server.route.audit.record("live_broker_denied", endpoint=self.path[:100], reason=str(exc)[:200])
            self.respond(400, json.dumps({"error": {"message": str(exc), "type": "benchmark_policy"}}).encode())
