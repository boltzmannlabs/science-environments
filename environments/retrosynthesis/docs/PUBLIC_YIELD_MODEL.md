# SRG-06 public yield model

The revised Step 6 uses an existing pretrained scientific model locally. Building
and validating a replacement custom model is deferred at the user's request.
The earlier C–N model and its unsuccessful improvement experiment remain recorded
in [CN_CONDITION_MODEL.md](CN_CONDITION_MODEL.md); this integration does not turn
that negative result into a passed scientific improvement gate.

## Selection and scope

[ReactionT5v2-yield](https://huggingface.co/sagawa/ReactionT5v2-yield) is the selected
practical pretrained baseline: its yield head, public weights and inference code
are available, and REBOLT already contains the upstream checkpoint. Selection
does **not** establish that it is the best model or state of the art on our tasks.
The [official repository](https://github.com/sagawatatsuya/ReactionT5v2) and
[paper](https://doi.org/10.1186/s13321-025-01075-4) describe the model's training
and published evaluations; those reported results are not our benchmark results.

| Candidate | Fit for this immediate integration | Decision |
|---|---|---|
| ReactionT5v2-yield | Public pretrained reaction-yield head; local assets available | Selected baseline |
| [ReaDISH](https://github.com/Meteor-han/ReaDISH) | Pretrained representation with downstream yield fine-tuning workflow | Defer task-specific fitting |
| [YieldBERT](https://github.com/rxn4chemistry/rxn_yields) | Dataset-specific yield workflows and training/evaluation recipes | Relevant future comparator; not shown inferior |
| [Parrot](https://github.com/wangxr0526/Parrot) | Reaction-condition generation rather than this yield endpoint | Separate future capability |
| REBOLT ReactionT5 v1 | Existing legacy loader and checkpoint conventions | Reuse audit context; prefer pinned v2 implementation |

These are suitability findings, not an empirical head-to-head model leaderboard.
Research LLM roles continue to use Agent Scientist's main profile. ReactionT5 is
a scientific prediction tool and does not replace the coordinating LLM.

## Verified model assets

- Upstream model revision: `f0658bfd360bceaaf560f11b850781c50221fe0b`.
- Cached upstream binary SHA-256:
  `29f5cc9a91aaa74b768d348d18f1bf0e01914f480102cf94142015a6a52cb3d9`.
- The 293 tensors were read with `weights_only=True`, converted to safetensors
  and checked for exact tensor equality after conversion. No training occurred.
- Local asset directory:
  `/home/boltzmann6/srg-models/reactiont5v2-yield-f0658bfd`.
- Original tokenizer parity was tested. The yield forward path omits the unused
  vocabulary `lm_head`; all weights used for yield inference load strictly.
- Model metadata declares MIT. Keep upstream attribution with redistributed assets.

The [model manifest](../artifacts/steps/srg-06/public-model-v1/model-manifest.json)
pins each required asset, revision and inference runtime. The supplied settings
are CPU, four threads, a 512-token limit and a 300-second predictor timeout.
[Model provenance](../artifacts/steps/srg-06/public-model-v1/model-provenance.json)
records the checkpoint verification and conversion. Runtime inference is local
and offline; it does not download weights or execute model-repository code.

The publisher-class reference loader and this worker produce exactly the same
numeric output with the pinned weights: 64.07570648 for the model-card example.
The card's printed 19.1666 is not reproduced; its cause remains unresolved.
All 293 used reference tensors match the checkpoint, and token IDs match the
official tokenizer for all 96 pilot inputs. This establishes adapter parity for
the pinned runtime, not reproduction of every published result. The preserved
`inference-parity.json` and `reference-loader-parity.json` record both findings.

## Calling the environment

Run from the `synthesis-route-gym` directory with the existing local environment:

```bash
.venv/bin/python -m synthesis_route_gym predict-yield \
  --task artifacts/steps/srg-06/public-model-v1/pilot-task.json \
  --model artifacts/steps/srg-06/public-model-v1/model-manifest.json \
  --input artifacts/steps/srg-06/public-model-v1/pilot-request.json \
  --output artifacts/reproduction/public-yield.json
```

The command creates a budgeted episode and invokes `predict_reaction_yield`.
Its report contains `action_result` and `episode`; predictions are under
`action_result.result.data.predictions` when the action succeeds.
On `agent`, `replay` or `plan`, add `--reaction-yield-model` followed by the same
manifest path. This binds the capability and exposes its schema to Agent
Scientist. Availability alone does not make a fixed search policy call it.

Each request supplies 1–100 candidates with unique `id`, nonempty `reactants`,
optional `reagents` and a `product`, all chemical participants expressed as SMILES.
Use the reagent list for catalysts, bases and solvents where their identities are
known. Outcome labels and extra input fields are rejected. Canonicalization
preserves complete components, stereochemistry and repeated participants.

Each output preserves the candidate ID and reports `scored` or `abstained`,
`predicted_yield_percent`, `raw_yield_percent`, `reason`, model version and domain.
A scored value must be finite and within 0–100. Unsupported tokens, excessive
input length, nonfinite output or an out-of-range yield cause abstention rather
than silent truncation or clipping. A finite out-of-range raw value is retained
for diagnostics while the accepted prediction is null. Unknown chemical-domain
transfer can still receive a score: abstention is not a complete OOD detector.

## Scientific and operational limits

The model receives molecular identities, not temperature, reaction time, amounts,
concentrations or workup. It therefore cannot optimize those factors through this
interface. A yield prediction is neither a calibrated hit probability nor an
experimental measurement. Output metadata always states `predicted`,
`not_calibrated` and `model_yield_not_experimental_feasibility`.

The tool does not certify feasibility, stock compliance, safety, purity or
scale-up behavior. It does not fill in missing route conditions or automatically
change `rank_routes`. Steps 7 and 8 still need explicit condition-candidate and
route-decision policies, with matched-budget evaluation of whether model use
actually improves those decisions. Existing route validation remains required.

Calls consume scientific-tool and episode budgets. A shorter host episode
deadline discards late output; the subprocess also has its own hard timeout.
Host cancellation is not immediate subprocess cancellation: a child may continue
until completion or its configured timeout. Model, adapter, worker and runtime
identity changes are recorded in the binding and invalidate incompatible resume.

## Development pilot and evidence

The [frozen pilot plan](../artifacts/steps/srg-06/public-model-v1/pilot-plan.json)
selects 96 recipes across 12 products from the previously used JNJ development
source: product hashes determine products and record IDs determine recipes,
without selecting on outcomes. Outcome labels stay outside predictor inputs.
Compare fixed record-ID ordering against descending yield predictions, with
record-ID tie breaking and a 300-second compute ceiling per arm. Exclude
abstentions from choices; a missing choice counts as failure.

Score top-1 and top-3 retrieval of source CAD response at least 10. These are
**transfer-ranking** checks, not yield-error or hit-probability calibration tests.
The data are already development data; upstream ORD training overlap has not
been ruled out. No final reserved data are used, and no independent-generalization
claim follows. All 96 recipes were scored in 31.88 seconds (one metered host
call). Both orders selected a screening hit for 2/12 products at top 1. At top 3,
fixed ordering retrieved a hit for 6/12 products and the model for 7/12.
The primary top-1 result is a tie; the secondary difference is small and does
not establish superiority. See
[pilot-evaluation.json](../artifacts/steps/srg-06/public-model-v1/pilot-evaluation.json).

## Replacing the predictor and maintenance

Implement `ReactionYieldPredictor` with `.predict(candidates)`, `.metadata`,
`.artifact`, `.configuration` and `.timeout_seconds`. Return the same ordered
prediction/abstention records. Inject the object through
`SynthesisRouteEnv(..., reaction_yield_predictor=predictor)` or
`create_app(..., reaction_yield_predictor=predictor)`; resume needs the same binding.
A new model architecture needs its own adapter implementing this protocol;
changing this ReactionT5 manifest alone does not support arbitrary architectures.

The environment/tool maintainer owns contracts, accounting and compatibility;
the scientific-model maintainer owns checkpoint provenance and inference parity;
the benchmark maintainer owns leakage audits and independent outcome scoring.
Version the manifest schema, model revision, asset hashes and adapter together.
Acceptance requires schema, abstention, timeout, tamper/resume, API and CLI tests,
plus real local inference. Scientific superiority requires a separate valid
comparison and remains distinct from accepting this replaceable integration.
