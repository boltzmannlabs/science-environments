"""Existing Agent-Scientist engine with exactly three external benchmark tools."""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import sys

sys.path[:0] = ["/runtime/site-packages", "/agent", "/runner"]

from enzyme_environment.probes import probe, broker_probe, rpc
from enzyme_environment.policy import SCORE_TOOL, TOOLS
from enzyme_environment.terminal import AcceptedSelection,dispatch as dispatch_terminal


def run():
    probe()
    broker_probe()
    import httpx
    from openai import OpenAI
    from run_agent import AIAgent
    from tools.registry import registry
    import model_tools

    config = json.loads(Path("/inputs/run.json").read_text())
    tools = (*TOOLS, SCORE_TOOL)
    names = frozenset(tool["name"] for tool in tools)
    for tool in tools:
        registry.register(name=tool["name"], toolset="enzyme_benchmark",
            schema={key: value for key, value in tool.items() if key != "type"},
            handler=lambda args, **kw: "Denied: use the benchmark dispatcher", description=tool["description"])

    def dispatch(name, arguments, *args, **kwargs):
        return dispatch_terminal(name,arguments,allowed=names,rpc=rpc)
    model_tools.handle_function_call = dispatch

    class IsolatedAgent(AIAgent):
        def _create_openai_client(self, client_kwargs, **kwargs):
            return OpenAI(api_key="sandbox-no-credential", base_url="http://broker/v1", max_retries=0,
                http_client=httpx.Client(transport=httpx.HTTPTransport(uds="/run/benchmark.sock"),
                                         timeout=70, trust_env=False))

    agent = IsolatedAgent(model="gpt-6.1-sol", provider="openai", api_mode="codex_responses",
        base_url="http://broker/v1", api_key="sandbox-no-credential", max_iterations=config["max_model_requests"],
        max_tokens=config["max_output_tokens"], reasoning_config={"effort": "low"},
        request_overrides={"parallel_tool_calls": False}, enabled_toolsets=["enzyme_benchmark"], quiet_mode=True,
        skip_context_files=True, skip_memory=True, skip_background_review=True,
        load_soul_identity=False, save_trajectories=False, session_db=None,
        run_budget_seconds=config["agent_wall_seconds"], cwd="/work")
    if agent.valid_tool_names != names:
        raise RuntimeError("Unexpected agent-facing tools")
    accepted_terminal=False
    try:
        result = agent.run_conversation(config["prompt"], system_message=config["system_message"])
    except AcceptedSelection:
        accepted_terminal=True
        result=None
    usage = resource.getrusage(resource.RUSAGE_SELF)
    safe = {"agent_class": "run_agent.AIAgent (external transport subclass)", "tool_names": sorted(names),
            "completed": accepted_terminal or bool(isinstance(result, dict) and result.get("completed")),
            "failed": not accepted_terminal and bool(not isinstance(result, dict) or result.get("failed")),
            "native_conversation_completed":bool(isinstance(result,dict) and result.get("completed")),
            "completion_reason":"accepted_selection" if accepted_terminal else "native_conversation_ended",
            "termination_policy":"accepted_selection/v1",
            "backend": config["backend"], "stage": "development_only",
            "scientific_superiority_established": False,
            "resources": {"cpu_user_seconds": usage.ru_utime, "cpu_system_seconds": usage.ru_stime,
                          "peak_process_ram_mib": usage.ru_maxrss / 1024,
                          "cpu_affinity_slots": len(os.sched_getaffinity(0)),
                          "measurement_scope": "Guest agent process, not aggregate container/host usage"}}
    Path("/work/benchmark_result.json").write_text(json.dumps(safe, indent=2))
    if not safe["completed"] or safe["failed"]:
        raise RuntimeError("Agent conversation did not complete")


if __name__ == "__main__":
    run()
