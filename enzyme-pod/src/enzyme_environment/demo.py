"""Dependency-free synthetic environment demo, with no native SDK/model use."""
import hashlib
import json
from pathlib import Path

from enzyme_benchmark.cli import demo as benchmark_demo
from enzyme_benchmark.contracts import TaskContract
from enzyme_benchmark.core import read_csv
from enzyme_benchmark.predictor import FrozenPredictor
from enzyme_environment.policy import Audit,Policy,verify_audit
from enzyme_environment.research_loop import ResearchLoop


def demo(output):
    output=Path(output).absolute()
    output.mkdir(parents=True,exist_ok=False)
    data=output/"synthetic_inputs"
    benchmark_demo(data)
    task=TaskContract.from_dict(json.loads((data/"task.json").read_bytes()))
    rows=read_csv(data/"candidates.csv")
    raw=(data/"frozen_models.synthetic.json").read_bytes()
    model=FrozenPredictor.from_bytes(raw,hashlib.sha256(raw).hexdigest(),"substitution_pair_one_hot",rows)
    audit=Audit(output/"audit.jsonl")
    policy=Policy({"task":[task.to_dict()],"candidates":rows,"train":[],"development":[]},output/"result",audit,
                  predictor=model,max_unique_scores=20,compact_candidates=True)
    research=ResearchLoop(policy)
    ids=[r["candidate_id"] for r in rows]
    def propose(context):
        return {"question":"Check a synthetic ranking action","claim":"This is a scripted protocol fixture, not scientific reasoning",
            "comparator":"Same synthetic frozen predictor","alternative_explanation":"Prediction need not match real experiments",
            "stop_condition":"Two rounds then final selection","revision_reason":"Use previous critique and actual observations",
            "parent_id":context["parent_id"],"evidence_refs":[r["observation"]["observation_id"] for r in context["history"] if r["observation"]],
            "action":{"tool":"benchmark_score","arguments":{"candidate_ids":ids[(context["round"]-1)*10:context["round"]*10]}}}
    def critique(proposal,context):
        return {"decision":"test","reason":"Allowed bounded synthetic action","objections":["No experimental evidence"],
                "requested_revision":"Inspect returned observations and retain IDs"}
    try:
        records=research.run(propose,critique,question=task.objective)
        policy.tool("benchmark_submit",{"candidate_ids":sorted(ids,key=lambda cid:(-policy.prediction_cache[cid],cid))[:10],
            "rationale":"Synthetic scripted environment demo only; no biological claim."})
        (output/"research_records.json").write_bytes(research.export_bytes())
    finally:audit.close()
    report={"success":policy.submitted and len(records)==2,"synthetic_only":True,"native_agent_executed":False,
        "model_requests":0,"network_requests":0,"local_gpu_used":False,"research_rounds":len(records),
        "unique_candidates_scored":len(policy.prediction_cache),"selected_candidates":10,"audit_events":len(verify_audit(audit.path)),
        "scientific_superiority_established":False}
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
