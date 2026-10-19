"""Deterministic provider fixture; never a live scientific/model result."""
import json
import math
import time

from enzyme_environment.connection import MODEL


def scripted_provider(policy):
    import httpx
    ids=[row["candidate_id"] for row in policy.datasets["candidates"]]
    main_turn=0
    calls=[]
    def handle(request):
        nonlocal main_turn
        body=json.loads(request.content)
        calls.append(1)
        role=body.get("text",{}).get("format",{}).get("name")
        name,args,value=None,None,None
        if role in ("enzyme_proposal","enzyme_critique"):
            context=json.loads(body["input"][0]["content"])["research_context"]
            if role=="enzyme_proposal":
                width=min(50,math.ceil(len(ids)/context["maximum_rounds"]))
                value={"question":"Exercise permitted development scoring","claim":"Offline fixture: predictions are not measured activity",
                    "comparator":"The identical conventional frozen predictor","alternative_explanation":"Scores may not match assay outcomes",
                    "stop_condition":"Complete the fixed round budget","revision_reason":"Use actual preceding feedback and a new subset",
                    "parent_id":context["parent_id"],"evidence_refs":[r["observation"]["observation_id"] for r in context["history"] if r["observation"]],
                    "action":{"tool":"benchmark_score","arguments":{"candidate_ids":ids[(context["round"]-1)*width:context["round"]*width]}}}
            else:
                value={"decision":"test","reason":"Allowed bounded fixture test","objections":["This is not live reasoning or activity evidence"],
                    "requested_revision":"Use actual observations without accessing final labels"}
        else:
            main_turn+=1
            batches=math.ceil(len(ids)/50)
            if main_turn==1: name,args="benchmark_read",{"dataset":"candidates","limit":50}
            elif 2<=main_turn<=batches+1:
                name,args="benchmark_score",{"candidate_ids":ids[(main_turn-2)*50:(main_turn-1)*50]}
            elif main_turn==batches+2:
                if set(policy.prediction_cache)!=set(ids): raise RuntimeError("Scripted provider did not receive the expected actual score actions")
                selected=sorted(ids,key=lambda cid:(-policy.prediction_cache[cid],cid))[:10]
                name,args="benchmark_submit",{"candidate_ids":selected,"rationale":"OFFLINE SCRIPTED FIXTURE: conventional frozen ranking, not a live scientific decision."}
        if name:
            output=[{"id":f"fc_{len(calls)}","type":"function_call","name":name,"call_id":f"call_{len(calls)}",
                     "arguments":json.dumps(args),"status":"completed"}]
        else:
            output=[{"id":f"msg_{len(calls)}","type":"message","role":"assistant","status":"completed",
                "content":[{"type":"output_text","text":json.dumps(value) if value is not None else "Offline fixture completed; no scientific improvement claim.","annotations":[]}]}]
        response={"id":f"resp_{len(calls)}","object":"response","created_at":int(time.time()),"status":"completed","model":MODEL,
            "output":output,"tools":[],"error":None,"incomplete_details":None,"usage":{"input_tokens":1,"output_tokens":1,"total_tokens":2}}
        events=[]
        for index,item in enumerate(output):
            events.extend([{"type":"response.output_item.added","output_index":index,"item":item},
                           {"type":"response.output_item.done","output_index":index,"item":item}])
        events.append({"type":"response.completed","response":response})
        stream="".join("event: "+e["type"]+"\ndata: "+json.dumps({**e,"sequence_number":i})+"\n\n" for i,e in enumerate(events)).encode()
        return httpx.Response(200,headers={"Content-Type":"text/event-stream"},content=stream)
    return lambda:httpx.AsyncClient(transport=httpx.MockTransport(handle),trust_env=False),calls
