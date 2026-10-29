# SRG-04 scientific capabilities and evidence boundary

Version: `srg-scientific-tool-v1`. Owner: environment/tool maintainer. The host
integration maintainer owns configuration, metering and adapter cancellation;
source reviewers own attestations; benchmark maintainers freeze corpus/access
policy/budgets. These are responsibilities, not invented staffing or laboratory
review claims.

## Registry and results

`ToolRegistry.describe()` publishes input, output-data and full-result JSON
schemas, canonical names/aliases, scope, evidence class, declared version,
timeout, accounting unit and availability. A configured callback is not proof
that its model is installed, executed or scientifically validated.

| Action | Supported host binding | Interpretation |
|---|---|---|
| `expand` | Existing LocalRetro or explicit expansion callback | Predicted precursors; salts/stereo/multiplicity retained |
| `predict_conditions` | Existing host condition ranker | Predicted yields and supplied uncertainty labels |
| `predict_reaction_yield` | Pinned local ReactionT5v2-yield or replacement predictor | Uncalibrated predicted yield for supplied recipes; explicit abstention |
| `score_cn_conditions` | Optional host C–N screen-hit JSON model (SRG-06) | Predicted source-specific screening hit; typed abstention outside scope |
| `retrieve_sources` | Frozen public corpus in retrieval mode | Located source claims, not automatic verification |
| `forward_check` | Explicit forward callback; otherwise unavailable | Predicted product match; omitted coproduct balance unknown |
| `observe_condition` | Explicit finite smoke/development replay | Only queried recorded outcome; no new experiment |
| `predict_impurities` | Existing local impurity adapter when configured | Hypotheses; no measured occurrence or concentration |
| `compare_process` | Stored routes and task inventory | Comparable supplied estimates; incomplete basis unranked |
| `retrieve_biocatalysis` | Frozen documented transformations in retrieval mode | Recorded participants; enzyme availability/activity unknown |

`capabilities` provides discovery. Canonical actions are in Agent Scientist's
restricted schema and authenticated local API. Aliases share canonical identities
and counters; they do not expand tool permissions.

Scientific results contain `schema_version`, `capability`, `status`, `data`,
`error`, `provenance`, `usage` and `evidence_kind`. Status is `ok`, `error` or
`unavailable`. Projections discard raw metadata and reject malformed chemistry,
nonfinite data and mismatched IDs. Host timeout/policy failures use the same
envelope. Expansion/condition actions retain legacy data fields and additionally
include the complete envelope as `tool_result`.

Ranking batches eligible conditions through this contract, records its scientific
call and uses validated host predictions. User-supplied yields cannot become model
scores. Invalid/unavailable attempts count; backend invocations and observations
are separately reported. Repeated completed action IDs reuse receipts without
another charge.

The SRG-06 `score_cn_conditions` extension accepts 1–1,000 candidates with unique
IDs and explicit `aryl`, `amine`, `catalyst`, `base`, `solvent` and `product`
SMILES. The host can load it with `--cn-condition-model PATH`, or pass a
`CNConditionModel` as `cn_condition_model` when constructing the environment or
local API. It is unavailable unless configured. The default route ranker and
the Doyle yield model are unchanged.

Each returned prediction has `status` (`scored` or `abstained`), `hit_score`,
`raw_hit_score`, `reason`, `model_version`, `domain`, `calibration_kind` and
`evidence_status: predicted`. The actual SRG-06 model supplies both bounded
scores for a scored row and nulls plus a reason for an abstention. The generic
callback contract permits omitted raw scores; the SRG-06 experiment requires
them for its frozen ranking tie-break. Artifact identity participates in
checkpoint compatibility. See [the model card and experiment](CN_CONDITION_MODEL.md)
for the precise endpoint, validation status and applicability limits.

## Pretrained reaction yield

The revised SRG-06 `predict_reaction_yield` capability accepts 1–100 unique
candidate IDs with `reactants`, `reagents` and `product` SMILES. Its manifest is
host-only; requests cannot select model paths or include outcome labels. Output
identity/order is checked, the host pins model version and predicted evidence,
and output values are finite/bounded or explicitly abstained. It does not alter
`rank_routes` or turn yields into feasibility probabilities. Configure it with
`--reaction-yield-model MANIFEST` or `reaction_yield_predictor=`. The
[model guide](PUBLIC_YIELD_MODEL.md) documents actual local inference, replacement
interface and the separate development diagnostic.

## Source access and review

Default `closed_information` blocks source and biocatalytic retrieval, including
custom callbacks. `evidence_retrieval` uses a frozen corpus and explicit shared
retrieval allowance. Compared arms must use identical corpus fingerprints, modes
and caps; retrieval-assisted results form a separate track. This step does not
authorize access to reserved final outcomes.

`SourceRecord` requires document identity, locator, HTTP(S) URL, canonical reaction
participants, stereochemical/condition scope, retrieval time and source-content
digest. Private/evaluator visibility, embedded outcomes, unknown fields and
file/credential-bearing URLs reject. Retrieval checks pinned corpus identity and
query filters, then projects bounded records as `source_claim` / `not_attested`.

Separate host-only attestations bind record/reaction/content hashes, review time
and expiry. Stale/mismatched reviews do not establish support; predicted/proxy
records cannot be promoted with a reviewer string. Hashes establish identity, not
truth. Source review is not experimental reproduction, human review or independent
benchmark truth. Condition equivalence needs actual source/query comparison.

The environment can assess cited, retrieved records with separately supplied
host attestations through the existing trusted-evidence interface. It does not
modify task input or elevate retrieval by itself. Hidden evaluator reviews must
never populate this research channel. Host curation is trusted: schemas cannot
detect answers falsely labeled public, and same-user filesystem permissions are
not an adversarial sandbox.

## Host configuration and observations

`load_science_config(path)` accepts strict `srg-science-config-v1` JSON. Unknown
keys, duplicate JSON keys, nonfinite numbers and files above 20 MB reject. No
backend executable, provider, model or evaluator paths are accepted. Source URLs
are identifiers; the loader performs no fetch.

Pass `--science-config /path/to/config.json` with `agent`, `plan` or `replay`.
The model sees allowed observations, not this file or unqueried replay rows.
A minimal configuration is:

```json
{
  "schema_version": "srg-science-config-v1",
  "source_access_mode": "closed_information",
  "scientific_limits": {"retrieval_calls": 0, "observation_calls": 0}
}
```

Optional inline condition replay requires a smoke/development role, source,
substrate, candidate conditions, recorded outcomes, dataset digest and study
budget. Final roles and dataset paths reject. Observation allowance cannot exceed
the remaining study budget. Optimizer policies and broad measured validation remain
later work. `inspect` provides bounded `condition_offset`/`condition_limit` pages
of IDs and conditions without yields or optimum. The prompt declares mode and caps.

## Persistence and versioning

Checkpoint version 2 records registry identity, access mode, limits, canonical
usage and retrieved IDs. Resume checks configuration and event/pending history.
Late/discarded results cannot retain source IDs. Interrupted actions keep charges.
Version 1 checkpoints require explicit migration; they are not silently reset or
rewritten. Accepted snapshots and receipts remain unchanged.

Cache keys include canonical input and model/configuration, stock and evidence
fingerprints. Actual search caching belongs to SRG-05. Artifact digests are labeled
host declarations; inspectable source/config hashes are recorded, but external
weights and installations are not all independently verified. Unknown versions
must be pinned before confirmatory comparison.

Waiting is bounded by capability and episode deadlines. External jobs require
adapter-owned termination. Models cannot replace source corpora, private replay
tables, bindings or resource policies through actions.

## SynthChem reuse and verification scope

Adapted contract ideas: unknown/interval preservation, common cost basis, source
locators/content identity and feedback provenance. No upstream implementation was
copied or launcher activated. SynthChem declares Apache-2.0, but its copied root
lacks LICENSE/NOTICE; no independently reviewed license grant is asserted.

Process comparisons require matching target, scale, currency, inventory, purity
basis and exclusions, with valid quote metadata. Missing costs are not zero;
no manufacturing-savings claim follows. Biocatalytic matches preserve multiplicity
and do not infer enzyme suitability from product matching. Full application
workflows, new model improvement and specialist validation remain later tickets.

Reproduce the offline smoke with a fresh directory:

```bash
.venv/bin/python scripts/run_tool_contract_smoke.py \
  --output artifacts/steps/srg-04/smoke-reproduction
```

The smoke blocks network/subprocess use, uses synthetic fixtures and injected
callbacks, and exports the versioned API/tool contract. It does not establish real
measurements, model accuracy or route improvement. Acceptance evidence is linked
in [PROGRESS.md](PROGRESS.md).
