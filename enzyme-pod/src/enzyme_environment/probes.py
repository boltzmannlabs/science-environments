"""Runs inside namespaces with no host secrets, network or hidden answers."""
import json
import errno
import os
from pathlib import Path
import socket
import sys
import resource

sys.path[:0] = ["/runtime/site-packages", "/agent", "/runner"]


def probe():
    checks = {}
    hidden = json.loads(os.environ["ENZYME_HOST_PROBES"])
    checks["host_paths_hidden"] = all(not Path(p).exists() for p in hidden)
    checks["private_pid_namespace"] = not Path("/proc/" + os.environ["BENCHMARK_HOST_PID"] + "/cmdline").exists()
    checks["clean_environment"] = not any(k in os.environ for k in ("OPENAI_API_KEY", "SCI_API_KEY", "HF_TOKEN", "AWS_SECRET_ACCESS_KEY"))
    for name, target in (("internet_blocked", ("1.1.1.1", 443)), ("lan_blocked", ("192.168.1.17", 2049))):
        with socket.socket() as conn:
            conn.settimeout(0.5)
            checks[name] = conn.connect_ex(target) != 0
    try:
        socket.getaddrinfo("nodeapis.boltzmann.co", 443)
        checks["dns_blocked"] = False
    except OSError:
        checks["dns_blocked"] = True
    for name, path in (("input_readonly", "/inputs/task.json"), ("source_readonly", "/agent/run_agent.py"),
                       ("runner_readonly", "/runner/enzyme_environment/probes.py")):
        try:
            fd = os.open(path, os.O_WRONLY)
            os.close(fd)
            checks[name] = False
        except OSError as exc:
            checks[name] = exc.errno == errno.EROFS
    checks["host_mount_roots_absent"] = not any(Path(p).exists() for p in ("/home", "/data", "/run/user"))
    checks["cpu_affinity_limited"] = len(os.sched_getaffinity(0)) <= 2
    checks["memory_limit_set"] = resource.getrlimit(resource.RLIMIT_AS) == (2 * 1024 ** 3, 2 * 1024 ** 3)
    checks["cpu_time_limit_set"] = resource.getrlimit(resource.RLIMIT_CPU) == (100, 105)
    checks["no_gpu_device_nodes"] = not list(Path("/dev").glob("nvidia*"))
    Path("/work/probe.json").write_text(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise RuntimeError("Isolation probe failed: " + str(checks))
    return checks


def rpc(name, arguments):
    import httpx
    with httpx.Client(transport=httpx.HTTPTransport(uds="/run/benchmark.sock"), timeout=10, trust_env=False) as client:
        r = client.post("http://broker/tools", json={"name": name, "arguments": arguments})
        r.raise_for_status()
        return r.json()


def broker_probe():
    """Try forbidden actions from inside the actual isolated worker."""
    import httpx
    checks = {}
    with httpx.Client(transport=httpx.HTTPTransport(uds="/run/benchmark.sock"), timeout=10, trust_env=False) as client:
        denied = {
            "paid_submission_route_denied": ("/api/submit-job", {}),
            "paid_submission_tool_denied": ("/tools", {"name": "boltzmann_submit", "arguments": {}}),
            "arbitrary_file_read_denied": ("/tools", {"name": "benchmark_read", "arguments": {"dataset": "/etc/passwd"}}),
            "test_labels_denied": ("/tools", {"name": "benchmark_read", "arguments": {"dataset": "labels"}}),
            "arbitrary_command_denied": ("/tools", {"name": "terminal", "arguments": {"command": "id"}}),
        }
        for name, (endpoint, data) in denied.items():
            checks[name] = client.post("http://broker" + endpoint, json=data).status_code in (400, 403)
    Path("/work/broker_probe.json").write_text(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise RuntimeError("Host broker permission probe failed")
    return checks
