"""Scripted model responses for exercising the actual native engine offline."""
import json
import time


def scripted_research_provider(campaign, *, report_review=False):
    import httpx
    calls = []
    def handler(request):
        calls.append(json.loads(request.content))
        number = len(calls)
        if number == 1:
            name, args = "enzyme_research_status", {"campaign_id": campaign}
        elif number == 2:
            name = "enzyme_research_next"
            args = ({"campaign_id": campaign, "action": "inspect_report",
                     "values": {"record_id": "parent", "pointer": "/missing_evidence"}} if report_review else
                    {"campaign_id": campaign, "action": "add_candidates", "values": {"candidates": [
                        {"candidate_id": "native_fixture_candidate", "parent_id": "parent", "sequence": "AGCAAAAAAA"}]}})
        elif number == 3 and report_review:
            name, args = "enzyme_research_report", {"campaign_id": campaign}
        else:
            raise RuntimeError("Offline fixture unexpectedly requested another response")
        item = {"id": "fc_" + str(number), "type": "function_call", "name": name,
                "call_id": "call_" + str(number), "arguments": json.dumps(args), "status": "completed"}
        response = {"id": "resp_" + str(number), "object": "response", "created_at": int(time.time()),
            "status": "completed", "model": "gpt-6.1-sol", "output": [item], "tools": [], "error": None,
            "incomplete_details": None, "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}
        events = [{"type": "response.output_item.added", "output_index": 0, "item": item},
                  {"type": "response.output_item.done", "output_index": 0, "item": item},
                  {"type": "response.completed", "response": response}]
        raw = "".join("event: " + e["type"] + "\ndata: " + json.dumps({**e, "sequence_number": i}) + "\n\n" for i, e in enumerate(events))
        return httpx.Response(200, headers={"Content-Type": "text/event-stream"}, content=raw.encode())
    return lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False), calls


def scripted_specialist_provider(campaign, *, context_lookup=False):
    import httpx
    calls = []
    lookup_requested = False
    def handler(request):
        nonlocal lookup_requested
        body = json.loads(request.content)
        calls.append(body)
        number = len(calls)
        instructions = body.get("instructions", "")
        if "ROLE: ENZYME_PROPOSER" in instructions:
            if context_lookup and not lookup_requested:
                lookup_requested = True
                value = {"read_context": {"view": "task", "record_id": "task", "pointer": "/parent/sequence"}}
            else:
                if context_lookup:
                    context = json.loads(body["input"][0]["content"])
                    assert context["context_reads"][0]["result"]["items"][0]["value"] == "AGAAAAAAAA"
                value = {"hypotheses": [{"claim": "Test one synthetic activity prediction", "plan": "Use the permitted fixture predictor",
                "alternatives": ["A predicted improvement need not reflect actual catalysis"], "evidence_refs": [],
                "revision_reason": "Initial bounded hypothesis", "action": {"kind": "activity", "job_name": "FixtureActivity",
                    "experiment_data": {"synthetic_only": True}, "candidate_ids": ["parent"]}}]}
        elif "ROLE: ENZYME_CRITIC" in instructions:
            value = {"score": 7, "critique": "Explicit test with an alternative; synthetic evidence only", "decision": "test"}
        else:
            value = None
        if value is None:
            item = {"id": "fc_" + str(number), "type": "function_call", "name": "enzyme_research_next",
                    "call_id": "call_" + str(number), "arguments": json.dumps({"campaign_id": campaign, "action": "investigate", "values": {}}), "status": "completed"}
        else:
            item = {"id": "msg_" + str(number), "type": "message", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": json.dumps(value), "annotations": []}]}
        response = {"id": "resp_" + str(number), "object": "response", "created_at": int(time.time()), "status": "completed",
            "model": "gpt-6.1-sol", "output": [item], "tools": [], "error": None, "incomplete_details": None,
            "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}
        events = [{"type": "response.output_item.added", "output_index": 0, "item": item},
                  {"type": "response.output_item.done", "output_index": 0, "item": item}, {"type": "response.completed", "response": response}]
        raw = "".join("event: " + e["type"] + "\ndata: " + json.dumps({**e, "sequence_number": i}) + "\n\n" for i, e in enumerate(events))
        return httpx.Response(200, headers={"Content-Type": "text/event-stream"}, content=raw.encode())
    return lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False), calls
