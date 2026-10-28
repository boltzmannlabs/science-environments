"""Exercise a real local Uvicorn process; no cloud or scientific jobs are run."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


def main():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_urlsafe(32)
    env = {**os.environ, "SYNTHESIS_ROUTE_GYM_API_TOKEN": token,
           "SYNTHESIS_ROUTE_GYM_API_OWNER": "local-http-verifier"}
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "synthesis_route_gym.api:app_from_environment",
        "--factory", "--host", "127.0.0.1", "--port", str(port), "--workers", "1",
        "--no-access-log"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def request(path, payload=None, authenticated=True):
        headers = {"Authorization": f"Bearer {token}"} if authenticated else {}
        data = None if payload is None else json.dumps(payload).encode()
        if data is not None:
            headers = {**headers, "Content-Type": "application/json"}
        with urlopen(Request(f"http://127.0.0.1:{port}{path}", data=data, headers=headers), timeout=5) as response:
            return json.load(response)

    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("Local server exited during startup")
            try:
                health = request("/v1/health")
                break
            except URLError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Local server did not become ready")
        try:
            request("/v1/health", authenticated=False)
            raise AssertionError("Unauthenticated health request was accepted")
        except HTTPError as error:
            assert error.code == 401
        value = {"task_id": "local-http-smoke", "target": "CCO", "inventory": [{"smiles": "CCO"}]}
        created = request("/v1/episodes", {"task": value})
        episode_id = created["data"]["episode_id"]
        submitted = request(f"/v1/episodes/{episode_id}/actions", {"action": "submit", "arguments": {"route_ids": []}})
        exported = request(f"/v1/episodes/{episode_id}")
        assert submitted["data"]["terminated"]
        assert exported["data"]["episode"]["task"]["task_id"] == value["task_id"]
        assert len(exported["data"]["episode"]["events"]) == 1
        openapi = request("/v1/openapi.json")
        target = Path(__file__).parent
        (target / "openapi.v1.json").write_text(json.dumps(openapi, indent=2, sort_keys=True) + "\n")
        receipt = {"scope": "real_local_http_only", "checked_at": datetime.now(timezone.utc).isoformat(),
                   "version": health["data"]["version"], "status": "passed",
                   "checks": ["unauthenticated_rejection", "episode_creation", "shortlist_submission", "episode_export", "authenticated_openapi"],
                   "execution_scope": health["data"]["execution_scope"]}
        (target / "local_http_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
