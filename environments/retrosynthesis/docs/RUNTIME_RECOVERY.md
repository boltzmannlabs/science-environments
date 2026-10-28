# SRG-03 runtime accounting and local recovery

Scope: reliable execution and auditable failure handling. This step does not
establish improved chemistry, learned-model quality or specialist benefit. All
live research roles still resolve Agent Scientist's main profile. The acceptance
receipt records which checks actually ran.

## Accounting and final submission

`SharedLedger` reserves resources before each admitted model request. Canonical
provider usage replaces that request's reservation immediately; identical
settlement replay is idempotent and conflicting usage rejects. Stage telemetry
adds only unaccounted usage. Failed/unconfirmed requests retain conservative
reservations. Reported usage overruns remain visible and stop further admission.

The native adapter permits one SDK wire attempt per admission. Hidden retries,
probes and reconnects cannot issue another unmetered attempt; outer retries need
new admission. SDK retries must be disabled. Unsupported API modes fail closed.
This integration depends on the inspected Agent Scientist client lifecycle and
needs revalidation after host upgrades. No global profile/provider configuration
is modified.

Initial `AgentBudget` defaults protect one main model call, one tool call, 10% of
tokens and 10% of wall time from optional specialist work. These are development
settings, not optimized benchmark settings. Main optional work is also fenced
when finalization is due; the native final request exposes submission only. An
empty submission is valid. Conversation completion without required submission
is incomplete; the host never invents a shortlist. Comparable arms share caps
and end policy.

Specialist reports use bounded summaries with role, completion, truncation and
proposal status; earlier histories are not copied into later prompts. Compact
`inspect` returns a task hash, counts, route IDs and usage. Exact inventory queries,
bounded inventory/evidence pages and ID-based details retain access to public
inputs without repeatedly serializing the full stock into context.

## Persistence and restart

CLI agent episodes create environment and runtime stores:

```bash
.venv/bin/python -m synthesis_route_gym agent \
  --task /path/to/public-task.json --output /path/to/result.json \
  --episode-dir /path/to/episode \
  --scientist-python /path/to/scientist-python \
  --scientist-source /path/to/Agent-Scientist
```

Repeat with `--resume` after interruption, keeping configuration unchanged.
Without `--episode-dir`, storage defaults to `OUTPUT.episode`. New runs refuse
existing stores. These commands can make live requests; the acceptance smoke
uses a clearly labeled injected backend.

Stores use checksummed revisions, atomic HEAD updates, fsync and revision checks
that reject stale writers before effects. The pattern was adapted from SynthChem's
campaign store without importing its launcher or adding a runtime dependency.
Paths remain host-owned. Checksums detect corruption, not a hostile owner rewriting
the whole store; external anchors are needed for that threat.

Runtime state binds prompt/task, schemas, profile model/provider, budget and
progress. Host state additionally binds scientific model file contents, configured
tool paths, timeout, seed and SRG implementation hashes. Changed bindings reject
resume. External repositories, checkpoint weights and dependency contents are
not all pinned by these paths; later tool-version contracts must close that gap.

Pending provider requests keep reservations. Interrupted stages restart within
the remaining allowance; completed stages are not replayed. Downtime counts
against the original deadline; backwards wall clocks reject recovery. The bridge
requires host persistence acknowledgement before proceeding past a checkpoint.

Host-generated action IDs return saved receipts for identical completed calls;
conflicting payloads reject. Action reservations precede effects. Restart with
an unresolved action records interruption and closes the episode without retrying
uncertain external work. Closed episodes can be read for reporting without model
execution. Controlled bridge failures preserve partial results and usage. Expired
episodes do not launch models; remaining time bounds bridge startup and execution.

## Cancellation and limits

Cancellation fences actions and discards late results. Callback waiting is
bounded; the bridge terminates its child runtime process group. Daemon-thread
cancellation cannot kill arbitrary external jobs; adapters must enforce their
own process/job cancellation. No remote termination is inferred from local timeout.

An interrupted write leaving an orphan revision fails closed and requires explicit
recovery. Storage failure stops further effects; it does not roll back admission.
IPC messages are limited to 8 MiB. Checkpoints are host-private and may contain
public task inputs and agent messages, but never require evaluator outcomes.

Offline tests cover settlement, retained unknowns, retries, finalization reserves,
profile fences, idempotency, stale writers, interrupted actions, deadlines,
checkpoints, cancellation, compact observations and CLI resume. Live-provider
compatibility/performance and scientific gains remain later validation work.

## Reproduce the offline acceptance smoke

```bash
.venv/bin/python scripts/run_runtime_smoke.py \
  --output artifacts/steps/srg-03/smoke-v2 \
  --public-bundle artifacts/benchmarks/srg02-v1 \
  --public-manifest-sha256 08cb21fd9354a650de1cac0fb9a589d6865e37859303bf9ac43f8c91b4adbe54
```

Use a fresh output directory. The script uses an injected backend and a temporary
fixture profile; it never calls a real LLM or changes the user's profile. It reads
only the public manifest, selected smoke task and stock. The public input loading
measurement is not comparable to the earlier whole-bundle validation workflow.

SRG-04 adds scientific checkpoint version 2, explicit source mode and usage-history
validation. Version 1 stores require an explicit migration before use with the
new scientific configuration; no automatic migration resets resources. See
[SCIENTIFIC_TOOL_CONTRACTS.md](SCIENTIFIC_TOOL_CONTRACTS.md).
