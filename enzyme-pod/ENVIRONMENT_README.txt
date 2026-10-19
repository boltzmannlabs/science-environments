ENZYME ENVIRONMENT - PRIVATE DEVELOPMENT CONTRIBUTION

SCOPE
External proposal/critique/test/revision roles and a bounded enzyme-variant
selection environment for the existing, unchanged native Agent-Scientist.
The current task selects ten IDs from ten to two hundred single-substitution
candidates. This is not the completed chemistry-aware enzyme-catalysis-gym,
a trained molecular model, experimental proof or an agent-superiority claim.

INSTALLATION
The separate boltzmann-enzyme-benchmark==0.1.0 provides the ONE canonical task,
candidate, predictor and operator-evaluation implementation. It is not copied
into this environment. Both are development packages, not public index releases.
Given the reviewed local wheels:
  python -m venv .venv
  .venv/bin/python -m pip install --no-index --find-links /path/to/wheels boltzmann-enzyme-benchmark==0.1.0 boltzmann-enzyme-environment==0.1.0
  .venv/bin/enzyme-env demo --output synthetic-demo

Default package runtime uses the Python standard library plus the benchmark
package. The demo needs no native SDK, network, credentials, GPU or checkpoints.
It uses scripted roles and synthetic inputs: this is a protocol example, not
live reasoning. Existing output directories are never overwritten.

REAL NATIVE-ENGINE EPISODES
The Linux namespace runner additionally requires an EXISTING clean, revision-
pinned Agent-Scientist checkout, standalone Python 3.14, its compatible native
SDK dependencies, bubblewrap and a system Python for the resource-limit helper.
The environment never installs, updates, checks out, resets or modifies these.
Windows/macOS native namespace execution is not supported by this version.
The inspected setup uses Python 3.14.7, OpenAI SDK 2.24.0 and HTTPX 0.28.1.
These observed versions are not a replacement for the upstream SDK's full lock.
Provider hardware and aggregate remote/host model memory are not measured here.

Runtime JSON, schema_version: enzyme-native-runtime/1
  agent_source: absolute clean Agent-Scientist Git checkout directory
  agent_revision: exact 40-character revision; no branch-name substitution
  python_root: standalone Python directory containing bin/python3
  site_packages: compatible native SDK site-packages directory
  profile: optional existing authorized profile directory; required for live use
  bubblewrap: optional executable path; default /usr/bin/bwrap
  limit_python: optional executable path; default /usr/bin/python3
Paths are operator configuration, not hard-coded server/user paths in the source.
No password, token or API key belongs in either configuration file.

Episode JSON, schema_version: enzyme-environment-episode/1
  runtime: path to the runtime JSON
  task: path to the canonical shared task JSON
  candidates: path to CSV with exactly candidate_id,mutation,sequences
  predictor: kind, path, sha256; kind is linear or esm_cache
    linear: optional model_kind, default substitution_pair_one_hot
    esm_cache: required pinned pool_fingerprint; all five-model scores required
  output: NEW output directory, outside original source/account profile
  backend: offline or live
  condition: base or specialist
  practice: optional train/development CSV paths; see validation below
  observation_format: compact (default) or full
  budget: optional Budget field overrides, within hard host-enforced caps
  role_rounds: optional integer 1-3, default 2
Relative artifact/output paths resolve against the episode configuration file.
All predictor/configuration hashes must come from a trusted operator freeze,
not from an agent-authored request claiming that its own prediction is trusted.

  enzyme-env check-runtime --runtime runtime.json
  enzyme-env run --config episode.json
Live additionally requires --allow-live-model and an existing authorized profile.
It uses the currently pinned gpt-6.1-sol model and host-only native authorization.
There is no login, refresh, fallback provider or automatic retry on failure.
Offline native runs execute the actual native engine with scripted HTTP responses;
their reported usage is synthetic and they do not consume live model quota.

INPUT AND EXECUTION PROTECTION
Candidate labels and unknown fields are rejected; sequence/mutation/reference
consistency is checked. Practice files have candidate_id,mutation,sequences,
experimental_score and optional position. Candidate/practice mutation-position
overlap, duplicate IDs, nonfinite outcomes and malformed rows are rejected.
Omitted practice data stay absent; explicitly supplied empty files fail.
File sizes, regular-file paths, hashes and unchanged input/source metadata are
checked. Outputs remain private and existing output paths are not replaced.

Compact observations omit repeated full sequences, NOT scientific information:
the task reference plus each explicit single substitution exactly reconstructs
the original sequence. Candidate IDs are retained. Both conditions use the
same format and allowed scientific tools. All original candidate input bytes
remain in the private execution manifest.

The isolated native engine has three actions: benchmark_read, benchmark_score
and one-shot benchmark_submit. There is no generic terminal, web proxy, paid
scientific-job submission or operator-answer read. Role responses cannot
execute tools; host semantic validation and actual Policy dispatch are required.
Critique evaluates proposals, never experimental activity. The next proposal
receives full prior critique AND actual observations, not just parent links.

The termination policy is accepted_selection/v1 for BOTH conditions. After the
host validates and accepts ten ranked IDs, an external dispatcher ends the
episode without another model call. The report distinguishes accepted_selection
from native_conversation_completed: no final chat completion is fabricated.
An accepted submission alone is insufficient for success: budget, isolation,
source/input integrity, audit and worker exit checks must also pass.

Shared model caps include EVERY role and coordinator request. Unique-scoring,
repeated/cache use, request/output bytes, time and returned token use are audited.
An in-flight completion can cross an observed total-token cap: this is not a
hard billing guarantee. Guest limits use two CPU-affinity slots and 2 GiB virtual
address space; this is not an aggregate host/cgroup OOM guarantee.
Valid usage is recorded even for the response that crosses a cap. A failed
episode remains failed; a later development protocol never rewrites its result.

OUTPUTS
report.json: execution status, accounting, integrity/isolation and resources.
host_only/result/selection.csv: ten known IDs and unique ranks.
host_only/audit.jsonl: host-owned hash-chained action/model audit.
host_only/specialist_records.json: complete structured research trace, if used.
host_only/execution_manifest.json: pinned inputs, code, runtime and budget.
host_only/harness_source/: exact external package source snapshot.
source/: private read-only runtime export of the separately supplied native agent.
No raw provider response bodies or account credentials are saved in these reports.
Operator-held labels/evaluator stay outside this episode. This executable does
not itself perform or certify an independent blinded scientific comparison.

DEVELOPMENT TESTS
  python -m unittest discover -s tests -p test_environment_portable.py -v
Optional pytest/HTTPX fixtures cover invalid inputs, role budgets, hallucinated
evidence, malicious tool responses, timeouts and failure closure without billing.
Clean wheel installation and native-isolation execution are distinct checks;
reuse of an existing native SDK is not a second-machine clean SDK installation.

STATUS AND RELEASE
Prior local live development selected identical ordered IDs with/without the
specialist (20 candidates): base 33.27 s / 29,090 tokens; specialist 61.06 s /
53,204 tokens. This is extra cost without a changed selection in that exercise,
not evidence of improvement or a general conclusion about enzyme workflows.
The 200-candidate final repeated study, full platform handoffs, new molecular
model and cross-family/chemistry tasks remain separate deliverables.
Company-approved code licensing, dependency/data/model rights and maintainer
review remain required before public release. No license is invented here.

OFFICIAL API REFERENCES
https://developers.openai.com/api/docs/guides/function-calling
https://developers.openai.com/api/docs/guides/structured-outputs
