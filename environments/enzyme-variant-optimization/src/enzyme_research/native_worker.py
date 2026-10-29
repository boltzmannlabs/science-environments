"""Native AIAgent in a namespace; research actions are dispatched by the host."""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import sys

sys.path[:0] = ["/runtime/site-packages", "/agent", "/runner"]


class ResearchStepAccepted(BaseException):
    pass


def rpc(name, arguments):
    import httpx
    with httpx.Client(transport=httpx.HTTPTransport(uds="/run/research.sock"), timeout=650, trust_env=False) as client:
        response = client.post("http://broker/tools", json={"name": name, "arguments": arguments})
        if response.status_code == 400:
            payload = response.json()
            error = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(error, dict) and error.get("type") == "benchmark_policy" and isinstance(error.get("message"), str):
                # A host rejection is feedback, not permission to retry a send.
                # Return its exact field/path diagnostic to the coordinator.
                return {"error": error, "research_step_finished": False}
        response.raise_for_status()
        return response.json()


def probes():
    import errno
    import socket
    hidden = json.loads(os.environ["ENZYME_HOST_PROBES"])
    checks = {"host_paths_hidden": all(not Path(p).exists() for p in hidden),
              "host_pid_hidden": not Path("/proc/" + os.environ["RESEARCH_HOST_PID"] + "/cmdline").exists(),
              "credentials_absent": not any(k in os.environ for k in ("OPENAI_API_KEY", "BOLTZMANN_API_KEY", "HF_TOKEN")),
              "no_gpu": not list(Path("/dev").glob("nvidia*")),
              "cpu_affinity_limited": len(os.sched_getaffinity(0)) <= 2}
    with socket.socket() as connection:
        connection.settimeout(0.5)
        checks["general_network_blocked"] = connection.connect_ex(("1.1.1.1", 443)) != 0
    for label, path in (("source_readonly", "/agent/run_agent.py"), ("inputs_readonly", "/inputs/run.json"),
                         ("runner_readonly", "/runner/enzyme_research/native_worker.py")):
        try:
            fd = os.open(path, os.O_WRONLY)
            os.close(fd)
            checks[label] = False
        except OSError as exc:
            checks[label] = exc.errno == errno.EROFS
    if not all(checks.values()):
        raise RuntimeError("Native research isolation failed")
    Path("/work/isolation.json").write_text(json.dumps(checks, indent=2))


def main():
    probes()
    import httpx
    from openai import OpenAI
    from run_agent import AIAgent
    from tools.registry import registry
    import model_tools
    from enzyme_research.context import native_tool_schemas
    SCHEMAS = native_tool_schemas()
    config = json.loads(Path("/inputs/run.json").read_bytes())
    names = frozenset(s["name"] for s in SCHEMAS)
    for schema in SCHEMAS:
        registry.register(name=schema["name"], toolset="enzyme_research", schema=schema,
            handler=lambda args, **kw: "Denied: use the research host dispatcher", description=schema["description"])

    def dispatch(name, arguments, *args, **kwargs):
        if name not in names:
            raise RuntimeError("Unapproved native research operation")
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        result = rpc(name, arguments)
        if result.get("research_step_finished") is True:
            raise ResearchStepAccepted()
        return json.dumps(result)
    model_tools.handle_function_call = dispatch

    class ResearchAgent(AIAgent):
        def _create_openai_client(self, client_kwargs, **kwargs):
            return OpenAI(api_key="guest-no-credential", base_url="http://broker/v1", max_retries=0,
                http_client=httpx.Client(transport=httpx.HTTPTransport(uds="/run/research.sock"), timeout=70, trust_env=False))

    agent = ResearchAgent(model="gpt-6.1-sol", provider="openai", api_mode="codex_responses", base_url="http://broker/v1",
        api_key="guest-no-credential", max_iterations=config["max_model_requests"], max_tokens=config["max_output_tokens"],
        reasoning_config={"effort": "low"}, request_overrides={"parallel_tool_calls": False},
        enabled_toolsets=["enzyme_research"], quiet_mode=True, skip_context_files=True, skip_memory=True,
        skip_background_review=True, load_soul_identity=False, save_trajectories=False, session_db=None,
        run_budget_seconds=config["agent_wall_seconds"], cwd="/work")
    if agent.valid_tool_names != names:
        raise RuntimeError("Native tool discovery differs from the research contract")
    accepted = False
    try:
        result = agent.run_conversation(config["prompt"], system_message=config["system_message"])
    except ResearchStepAccepted:
        accepted, result = True, None
    usage = resource.getrusage(resource.RUSAGE_SELF)
    completed = bool(isinstance(result, dict) and result.get("completed"))
    outcome = ("action_accepted" if accepted else "conversation_completed_without_action" if completed
               else "conversation_incomplete_without_action")
    report = {"native_agent_executed": True, "accepted_research_action": accepted,
              "native_conversation_completed": completed, "control_flow_outcome": outcome,
              "tool_names": sorted(names), "backend": config["backend"],
              "peak_guest_ram_mib": usage.ru_maxrss / 1024, "guest_cpu_seconds": usage.ru_utime + usage.ru_stime,
              "experimental_improvement_established": False}
    Path("/work/native_result.json").write_text(json.dumps(report, indent=2))
    if not accepted and not completed:
        raise RuntimeError("Native conversation ended incomplete without an accepted research action")


if __name__ == "__main__": main()
