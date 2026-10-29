"""Independent-context review using only the configured Agent Scientist main model."""
import json
from pathlib import Path
import hashlib
import os
from synthesis_route_gym.agent_bridge import run_agent_scientist_bridge
from synthesis_route_gym.agent_runner import AgentBudget
from synthesis_route_gym.benchmark import route_fingerprint, _reviewable_route, evaluate_episode
from synthesis_route_gym.cli import write_json

root=Path(__file__).resolve().parents[1]
runs=json.loads((root/'artifacts/aspirin_comparison/runs.json').read_text())
for name in ('local_main_aspirin_v2.json','local_specialists_aspirin_v2.json'):
 path=root/'artifacts'/name
 if path.exists():
  additional=json.loads(path.read_text())
  runs=[*runs,{**additional,'method':additional['method']+'_v2'}]
all_records={route_fingerprint(r):_reviewable_route(r) for run in runs for r in run['episode']['routes']}
existing_path=root/'artifacts/aspirin_comparison/reviews.json'
existing_reviews=json.loads(existing_path.read_text()) if existing_path.exists() else []
existing_by_id={r['route_fingerprint']:r for r in existing_reviews if r['route_fingerprint'] in all_records}
records={k:v for k,v in all_records.items() if k not in existing_by_id}
if not records:
 for record in existing_by_id.values():
  write_json(root/'artifacts/aspirin_comparison/reviews_by_fingerprint'/f"{record['route_fingerprint']}.json",record)
 metrics=[{'method':run['method'],**evaluate_episode(run['episode'],list(existing_by_id.values()))} for run in runs]
 write_json(root/'artifacts/aspirin_comparison/metrics.json',metrics)
 print(json.dumps({'newly_reviewed_routes':0,'total_reviewed_routes':len(existing_by_id),'metrics':metrics}))
 raise SystemExit(0)
sources=[{
 'source_id':'NJIT-aspirin','url':'https://web.njit.edu/~mitra/green_chemistry/EXP_5.htm',
 'locator':'Synthesis of Aspirin; Materials Required; Experimental Procedure; Results and Discussion',
 'source_type':'university experimental teaching report',
 'inspected_by':'Codex source retrieval, 2026-10-27',
 'summary':'The report describes preparation of aspirin from salicylic acid and acetic anhydride with phosphoric acid catalysis, followed by aqueous workup and isolation. It reports results for specified heating methods. Those measured yields cannot be assigned to a proposal with unspecified quantities and conditions. The source does not document direct preparation using acetic acid in place of acetic anhydride.',
 'limitations':'Teaching report, not a peer-reviewed process validation; webpage has a naming typo in explanatory prose. The target, precursor list and procedure identify aspirin.'
}]
payload={'routes':[{'route_fingerprint':k,'route':v} for k,v in sorted(records.items())], 'independently_retrieved_sources':sources}
write_json(root/'artifacts/aspirin_comparison'/('review_input_'+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:12]+'.json'),payload)
write_json(root/'artifacts/aspirin_comparison/review_input.json',payload)
schema={'name':'inspect','description':'Read blinded route structures and independently retrieved evidence excerpts.',
        'parameters':{'type':'object','properties':{},'required':[],'additionalProperties':False}}
prompt='''You are reviewing each proposed route individually in an isolated evaluation session. You did not generate these routes. All tool calls and model selection are controlled by the host. Call inspect once. Return ONLY a JSON array, one entry per route_fingerprint, with these keys: route_fingerprint, verdict (accepted/rejected/unresolved), reviewer_kind (automated_source_audit), reviewer (configured main-profile model), independent (true), source_locators (list of URL plus section), evidence_relation (exact_transformation/analogue/no_support), conditions_support (complete/partial/absent), lab_ready (false), rationale (short), unresolved_requirements (list). Judge transformation plausibility under the listed molecular inputs. Accepted means source-supported plausible transformation only, NOT demonstrated yield, exact full conditions or lab readiness. Unspecified catalysts or process details must be explicitly flagged; do not presume an analogous or unsupported reaction is successful or impossible. Evaluate every structure, the phenolic O-acetylation versus other reactions, all atom-contributing precursors, catalyst availability, and missing operational information. Use only the supplied source record for evidence claims. Do not copy a source yield onto a proposed route. No knowledge of generating method or scores is available. This is an automated evidence audit, not human review.'''
captured=[]
def executor(name,args):
 if name=='inspect':
  return payload
 submitted=args['reviews']
 if {r['route_fingerprint'] for r in submitted} != set(records):
  raise ValueError('Every route must be reviewed exactly once')
 captured.extend(submitted)
 return {'recorded':len(submitted)}
submit={'name':'submit','description':'Submit completed independent evidence reviews.', 'parameters':{'type':'object','properties':{'reviews':{'type':'array','items':{'type':'object','properties':{'route_fingerprint':{'type':'string'},'verdict':{'type':'string','enum':['accepted','rejected','unresolved']},'reviewer_kind':{'type':'string','enum':['automated_source_audit']},'reviewer':{'type':'string'},'independent':{'type':'boolean'},'source_locators':{'type':'array','items':{'type':'string'}},'evidence_relation':{'type':'string'},'conditions_support':{'type':'string'},'lab_ready':{'type':'boolean'},'rationale':{'type':'string'},'unresolved_requirements':{'type':'array','items':{'type':'string'}}},'required':['route_fingerprint','verdict','reviewer_kind','reviewer','independent','source_locators','evidence_relation','conditions_support','lab_ready','rationale','unresolved_requirements'],'additionalProperties':False}}},'required':['reviews'],'additionalProperties':False}}
# All object properties are required for strict provider schema compatibility.
prompt=prompt.replace('Return ONLY a JSON array, one entry per route_fingerprint,', 'Call submit with reviews as a JSON array, one entry per route_fingerprint,').replace('Call inspect once.', 'Call inspect once, then submit your reviews, then say DONE.')
previous=root/'artifacts/aspirin_comparison/review_run.json'
previous_archive=None
if previous.exists():
 digest=hashlib.sha256(previous.read_bytes()).hexdigest()[:12]
 archive=previous.with_name(f'review_run.previous-{digest}.json')
 previous_archive=archive.name
 if not archive.exists():
  archive.write_bytes(previous.read_bytes())
# The source-runtime log confirms 12-second SSE-idle cancellations. This
# invocation-only transport allowance leaves model/provider and total caps intact.
previous_idle=os.environ.get('SCI_CODEX_EVENT_STALE_TIMEOUT_SECONDS')
os.environ['SCI_CODEX_EVENT_STALE_TIMEOUT_SECONDS']='60'
try:
 result=run_agent_scientist_bridge(prompt,executor,tool_schemas=[schema,submit],
  scientist_python='/home/boltzmann6/.sci/tools/python-3.14.7+20260901-linux-x64/bin/python3',
  scientist_source='/home/boltzmann6/Agent-Scientist',budget=AgentBudget(max_model_calls=8,max_tool_calls=4,
  max_output_tokens_per_call=4096,max_total_tokens=150000,wall_seconds=180))
finally:
 if previous_idle is None:
  os.environ.pop('SCI_CODEX_EVENT_STALE_TIMEOUT_SECONDS',None)
 else:
  os.environ['SCI_CODEX_EVENT_STALE_TIMEOUT_SECONDS']=previous_idle
result={**result,'transport_configuration':{'codex_stream_idle_timeout_seconds':60,
 'scope':'review child process only','main_profile_configuration_changed':False}}
write_json(root/'artifacts/aspirin_comparison/review_run.json',result)
result_digest=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()[:12]
result_receipt=f'review_run.completed-{result_digest}.json'
if result['completed']:
 write_json(root/'artifacts/aspirin_comparison'/result_receipt,result)
if not captured:
 raise RuntimeError('Review submission missing; failure and provider diagnostics retained in review_run.json')
text=result['final_response'].strip()
if text.startswith('```'):
 text='\n'.join(text.splitlines()[1:-1])
reviews=captured if captured else json.loads(text)
if {r['route_fingerprint'] for r in reviews} != set(records) or len(reviews)!=len(records):
 raise ValueError('Review did not cover each unique proposal exactly once')
new_reviews=[{**r,'reviewer':result['model'],'review_scope':'transformation_plausibility_only','lab_ready':False,'review_run_file':result_receipt} for r in reviews]
existing_by_id={key:{**value,'review_run_file':value.get('review_run_file',previous_archive)} for key,value in existing_by_id.items()}
merged={**existing_by_id,**{r['route_fingerprint']:r for r in new_reviews}}
reviews=[merged[key] for key in sorted(merged)]
for record in reviews:
 write_json(root/'artifacts/aspirin_comparison/reviews_by_fingerprint'/f"{record['route_fingerprint']}.json",record)
write_json(root/'artifacts/aspirin_comparison/reviews.json',reviews)
metrics=[{'method':run['method'],**evaluate_episode(run['episode'],reviews)} for run in runs]
write_json(root/'artifacts/aspirin_comparison/metrics.json',metrics)
print(json.dumps({'newly_reviewed_routes':len(new_reviews),'total_reviewed_routes':len(reviews),'model':result['model'],'metrics':metrics}))
