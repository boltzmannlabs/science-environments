"""External native-engine episode reusing the audited host model transport.

The existing host transport exposes permitted research operations through a
bounded policy and keeps each native step attached to its campaign record.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from .contracts import ResearchError
from .native_policy import NativeResearchPolicy


def command(runtime, run, socket, research_package, environment_package, benchmark_package):
    args = [str(runtime.bubblewrap), "--unshare-all", "--die-with-parent", "--new-session", "--cap-drop", "ALL", "--clearenv"]
    for root in ("/usr", "/lib", "/lib64"):
        if Path(root).is_dir(): args += ["--ro-bind", root, root]
    args += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--dir", "/run", "--dir", "/etc",
        "--ro-bind", str(runtime.python_root), "/runtime/python", "--ro-bind", str(runtime.site_packages), "/runtime/site-packages",
        "--ro-bind", str(run / "source"), "/agent", "--ro-bind", str(research_package), "/runner/enzyme_research",
        "--ro-bind", str(environment_package), "/runner/enzyme_environment", "--ro-bind", str(benchmark_package), "/runner/enzyme_benchmark",
        "--ro-bind", str(run / "inputs"), "/inputs", "--bind", str(run / "guest"), "/work",
        "--ro-bind", str(socket), "/run/research.sock", "--chdir", "/work"]
    env = {"HOME": "/work/home", "SCI_HOME": "/work/profile", "PATH": "/runtime/python/bin:/usr/bin", "LANG": "C.UTF-8",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1", "SCI_DISABLE_LAZY_INSTALLS": "1",
           "CUDA_VISIBLE_DEVICES": "", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
           "RESEARCH_HOST_PID": str(os.getpid()),
           "ENZYME_HOST_PROBES": json.dumps([str(runtime.agent_source), str(run), str(runtime.profile)])}
    for key, value in env.items(): args += ["--setenv", key, value]
    args += ["/runtime/python/bin/python3", "-I", "-B", "/runner/enzyme_research/native_worker.py"]
    return [str(runtime.limit_python), "-I", "-B", str(environment_package / "limits.py"), *args]


def run_native_step(service, campaign, runtime, output, *, backend="offline", provider_factory=None, instruction="Choose the next appropriate research action", budget=None, allowed_actions=None):
    import enzyme_benchmark
    import enzyme_environment
    from enzyme_environment.connection import HostCredential, authorize_read_only
    from enzyme_environment.policy import Audit, verify_audit
    from enzyme_environment.transport import Budget, BenchmarkBroker, BenchmarkRoute
    if backend not in {"offline", "live"}:
        raise ResearchError("Unknown native research backend")
    if backend == "offline" and provider_factory is None:
        raise ResearchError("Offline native execution requires an explicit scripted provider")
    runtime.check()
    run = Path(output).absolute()
    run.mkdir(parents=True, exist_ok=False, mode=0o700)
    for name in ("inputs", "guest/home", "guest/profile", "host_only"):
        (run / name).mkdir(parents=True, exist_ok=True)
    (run / "guest/profile/config.yaml").write_text("plugins:\n  entries: {}\ntools:\n  tool_search:\n    enabled: off\n")
    before = runtime.source_snapshot()
    runtime.export_source(run / "source", before)
    audit = Audit(run / "host_only/audit.jsonl")
    policy = NativeResearchPolicy(service, campaign, audit, allowed_actions=allowed_actions)
    budget = budget or Budget(max_requests=6, max_output_tokens_per_request=2048, max_total_observed_tokens=48000,
                              max_request_bytes=262144, max_total_request_bytes=1048576, max_wall_seconds=180)
    started = time.monotonic()
    code = None
    route = roles = None
    failure = None
    stage = "context_preparation"
    previous_roles = getattr(service, "model_roles", None)
    try:
        public = {"backend": backend, "max_model_requests": budget.max_requests, "max_output_tokens": budget.max_output_tokens_per_request,
            "agent_wall_seconds": budget.max_wall_seconds - 5,
            "system_message": "You are Agent-Scientist investigating an enzyme through the supplied research operations. Use real observations, preserve candidate IDs and catalytic constraints, and choose tools from the authoritative task catalogue. Predictions are not experimental answers. Complete one valid next research action; the host records it and ends this step. No arbitrary commands, file reads or hidden labels are available.",
            "prompt": instruction + "\nCurrent permitted research context:\n" + json.dumps(policy.context(), sort_keys=True)}
        (run / "inputs/run.json").write_text(json.dumps(public))
        stage = "model_authorization"
        credential = authorize_read_only(runtime.profile) if backend == "live" else HostCredential("offline-fixture", {})
        route = BenchmarkRoute(credential, policy, budget, client_factory=provider_factory)
        from .model_roles import LiveDiscoveryRoles
        roles = LiveDiscoveryRoles(route)
        service.model_roles = roles
        stage = "native_execution"
        with tempfile.TemporaryDirectory(prefix="enzyme-research-broker-") as directory:
            broker = BenchmarkBroker(Path(directory) / "research.sock", route)
            thread = threading.Thread(target=broker.serve_forever, daemon=True)
            thread.start()
            try:
                import enzyme_research
                cmd = command(runtime, run, broker.server_address, Path(enzyme_research.__file__).parent,
                              Path(enzyme_environment.__file__).parent, Path(enzyme_benchmark.__file__).parent)
                with (run / "host_only/stdout.txt").open("w") as out, (run / "host_only/stderr.txt").open("w") as err:
                    proc = subprocess.Popen(cmd, stdout=out, stderr=err, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
                    try: code = proc.wait(timeout=budget.max_wall_seconds + 5)
                    except subprocess.TimeoutExpired:
                        proc.kill(); proc.wait(); code = -9
            finally:
                broker.shutdown(); broker.server_close(); thread.join(timeout=3)
    except Exception as exc:
        # Provider/authorization exceptions can include account material. The
        # durable report needs a failure category, never the exception text.
        failure = {"stage": stage, "error_type": type(exc).__name__,
                   "message": "Research step failed; no successful action is confirmed. Inspect tracked calls before retrying."}
        audit.record("native_step_failed", stage=stage, error_type=type(exc).__name__)
    finally:
        if previous_roles is not None:
            service.model_roles = previous_roles
        elif hasattr(service, "model_roles"):
            del service.model_roles
        audit.close()
    worker_path = run / "guest/native_result.json"
    worker = json.loads(worker_path.read_bytes()) if worker_path.is_file() else {}
    probe_path = run / "guest/isolation.json"
    probes = json.loads(probe_path.read_bytes()) if probe_path.is_file() else {}
    source_unchanged = runtime.source_snapshot() == before
    result = {"success": bool(failure is None and route is not None and code == 0 and policy.accepted_action and worker.get("accepted_research_action") and probes and all(probes.values()) and source_unchanged and not route.failed),
        "backend": backend, "native_agent_executed": worker.get("native_agent_executed", False),
        "model_requests": route.requests if route is not None else 0,
        "real_model_requests": route.requests if backend == "live" and route is not None else 0,
        "usage": route.usage if route is not None else {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "role_requests": dict(roles.calls) if roles is not None else {"proposer": 0, "critic": 0},
        "synthetic_model_responses": backend == "offline", "accepted_action": policy.accepted_action,
        "native_agent": worker, "isolation": probes, "source_unchanged": source_unchanged,
        "audit_events": len(verify_audit(audit.path)), "exit_code": code,
        "model_error": route.error if route is not None else None, "execution_failure": failure,
        "elapsed_seconds": time.monotonic() - started, "local_gpu_used": False,
        "scientific_comparison_complete": False}
    (run / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    with service.store.transaction() as db:
        service.store.event(db, campaign, "native_step_finished", {"backend": backend, "success": result["success"],
            "model_requests": result["model_requests"], "model_usage": result["usage"], "report_path": str(run / "report.json")})
    return result
