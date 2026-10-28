# SRG-06 source-scoped C–N condition model

Status (2026-10-27): local implementation and fixed development evaluation
complete. **The primary improvement gate failed; SRG-06 scientific acceptance
remains open.** The candidate is an optional experimental artifact, not a new default.
Owner: scientific-model, data and environment maintainers. All work is local.

## Why a separate model

The existing Doyle predictor covers one fixed-partner C–N screen. Its previously
inspected test is development evidence; its top-5 and top-10 choices lost to
condition means. Its artifact and historical results remain unchanged. Neither
those data nor the reserved Suzuki source is a fresh final test for this step.

Fresh source: Neves et al., [Robust out-of-distribution prediction of
Buchwald–Hartwig reactions](https://pmc.ncbi.nlm.nih.gov/articles/PMC13593570/),
with the [curated CSV](https://raw.githubusercontent.com/schwallergroup/bh-hte-ood/3a44e398d9fed3f08cf396f1153be2960193f581/data/BH_HTE_Curated_Dataset_v20260219.csv).
Repository revision: `3a44e398d9fed3f08cf396f1153be2960193f581`.
CSV SHA-256: `247473787c33fb22ee48a4177593188f2a2c6ef140756566fe4610fee89ba333`.
The [dataset record](https://zenodo.org/records/19636649) declares CC-BY-4.0;
repository software is Apache-2.0. Raw data stays in host-private local storage.

Only source `JNJ HTE 2024` (published alias JnJ25) is eligible. It contains 11,328
records before our structural/deduplication checks. Other sources, including
Doyle and sources with different measurement methods, are excluded from this
experiment. Upstream fitted descriptors, clusters, names and source identifiers
are never model features.

## Endpoint and limits

The endpoint is a **source-reported screening response at least 10**. The stored
binary labels agree with `response >= 10`, including 111 records exactly at 10.
The source uses UPLC-MS-CAD. There are 52 recorded responses above 100, so this
value is not treated as a bounded isolated-yield percentage. Those finite values
remain eligible for the binary endpoint; filtering them would select on outcomes.
No individual outcomes or candidate rankings were inspected during this audit.

The model predicts a screen-hit score for an explicit candidate comprising aryl,
amine, catalyst, base, solvent and target product. It does not establish reaction
feasibility, isolated yield, impurity control, scale-up behavior or complete
experimental conditions. Structural checks are not proof of experimental success.

## Frozen development design, before fitting

All records from this publication belong to the overall **development** tier.
Internal product/scaffold partitions measure within-source generalization; they
are not the reserved final evaluation and do not create independent publications.
The protocol's formal Q1 promotion criteria and final seal remain pending.

1. Audit exact source/schema/hash, finite nonnegative response and the published
   binary-label rule. Require complete valid structures and the supported aryl
   halide/amine C–N product edit. Preserve an exclusion/duplicate audit. Duplicate
   chemical inputs retain their first source position, independently of outcomes.
2. Group canonical products by nonchiral Murcko scaffold, falling back to full
   canonical product for acyclic molecules. Keep all same-product variants
   together. Hash-order groups using seed 20261027 and allocate approximately
   60% training, 15% development selection, 10% calibration and 15% assessment.
3. Construct six 128-bit, radius-2 chiral Morgan role fingerprints using only
   decision-time structures. Predictors receive no labels, source-row positions,
   reported responses or upstream fitted features.
4. Compare global hit means, smoothed training condition hit rates and two
   ExtraTrees classifier configurations representing the earlier algorithmic
   family. This is a refitted classifier baseline, not the old Doyle yield
   artifact. Candidate models are two RandomForest classifiers and one
   alternative ExtraTrees configuration. Use 128 trees, depth 18, fixed seed
   and two fitting threads. Record every configuration and result.
5. Select each arm on development macro top-1 binary simple regret, then top-5
   regret, Brier score and stable configuration name. Average product decisions
   within each scaffold group before averaging groups. Missing choices incur
   regret 1; all-negative pools remain in the denominator. All arms receive the
   same source/structural candidate pools. Mean baselines retain their global
   fallback and are not forced to copy the learned model's abstention policy.
6. Refit selected algorithms on training plus development only. Fit isotonic
   score calibration using only calibration groups. Freeze artifacts, assessment
   candidate pools, scores and ordered choices before evaluating assessment
   outcomes. Choices sort by calibrated score, raw score and then record ID;
   the raw-score tie-break preserves ordering through isotonic plateaus. No
   tuning follows that evaluation.
7. Report per-group wins/losses, top-1/top-5 regret, Brier score, reliability
   bins, novel components, abstention and costs. A paired 10,000-resample group
   bootstrap is descriptive within this source, not a source-population guarantee.

The predeclared experimental candidate gate is at least 5 percentage points
reduction in top-1 binary regret against the strongest development-selected
baseline, with the descriptive 95% bootstrap lower bound above zero. Failure
retains the incumbent/default and the negative result. Passing does not authorize
formal Q1 promotion or satisfy all source-independent scientific claims.

## Model and tool contract

`score_cn_conditions` is separate from the existing `predict_conditions` yield
tool and does not silently change `rank_routes`. One batch contains explicit
candidate IDs and six role structures. Every candidate returns either a bounded
predicted hit score or a typed abstention with a reason. Unseen condition species,
unsupported product edits and insufficient substrate similarity trigger the
declared applicability policy. Thresholds are fixed before evaluation.

Models use validated numeric JSON trees and monotonic calibration arrays, never
pickle or executable deserialization. Feature versions, training component
identities, source/partition hashes and model versions are bound to each artifact.
Host configuration explicitly loads the new model. Tool calls use the existing
budget, timeout, evidence-projection and checkpoint-identity mechanisms.

Acceptance requires tests for leakage-safe grouping/features, separate calibration,
prediction-before-evaluation, artifact parity/validation, mixed-batch abstention,
CLI/API integration, counter persistence and immutable historical artifacts.
Scientific improvement and implementation status will be reported separately.

## Source audit before training

All 11,328 selected rows passed the six-role structural check, with no duplicate
chemical inputs or excluded rows. All eight source additive flags were zero.
There are 703 distinct nonchiral product-scaffold groups, not 703 independent
publications. No split hit prevalence or individual response was printed.

| Internal partition | Records | Scaffold groups |
|---|---:|---:|
| Training | 6,553 | 421 |
| Development selection | 2,230 | 105 |
| Calibration | 1,124 | 70 |
| Assessment | 1,421 | 107 |

The [aggregate audit](../artifacts/steps/srg-06/cn-data-audit.json) and
[source provenance](../artifacts/steps/srg-06/cn-data-provenance.json) record source
integrity, the threshold definition, missingness, license and grouping decisions.

The six input roles do not encode temperature, time, concentration, loading,
scale or workup. This model ranks the source's encoded tuples; it does not
optimize those omitted process variables or establish transfer across them.

## Observed result and failure analysis

One fixed experiment compared seven predeclared configurations. Development
selection chose `rf_leaf2` as candidate and `legacy_et_leaf2` as strongest
baseline. Each selected model was refitted on 8,783 training/development rows;
isotonic calibration used 1,124 separate rows. Assessment used 1,421 rows across
129 product pools and 107 scaffold groups. The measured experiment time was
162.30 seconds after source loading, with two fitting threads and no GPU or LLM.

| Internal assessment metric (lower regret/Brier is better) | ExtraTrees baseline | Random Forest candidate |
|---|---:|---:|
| Top-1 group-macro binary regret | 28.50% | 32.24% |
| Top-5 group-macro binary regret | 11.68% | 10.12% |
| Calibrated candidate-level Brier score | 0.19101 | 0.15263 |
| Scored candidates / all candidates | 1,421 / 1,421 | 1,421 / 1,421 |

Regret measures the missed opportunity to choose a recorded hit when one exists;
it is not isolated yield or a general reaction failure rate. The candidate's
top-1 regret was **3.74 percentage points worse**. Baseline-minus-candidate
regret reduction was -3.74 pp, with descriptive paired bootstrap interval
**[-9.35, +0.93] pp**. This fails both the required 5 pp gain and positive lower
bound. There were 2 scaffold-group wins, 6 losses and 99 ties.

Top-5 regret and Brier score improved, but neither replaces the predeclared
primary criterion. Moreover, 66 of 129 pools have at most five candidates, so
top-5 retrieval is partly an exhaustive-pool result. Sixteen pools have no
recorded hit; they remain in all denominators. The assessment has no unseen
catalyst/base/solvent identities, although 208 candidate rows have unseen amines
and 192 have unseen aryl identities. No assessment row triggered abstention;
deliberate out-of-domain integration checks establish software behavior only.

Calibration reduced assessment Brier score for both arms: baseline 0.23975 to
0.19101; candidate 0.15423 to 0.15263. This is a probability-score improvement,
not proof of transferable calibration or chemical feasibility. Candidate top-1
regret was better on development (20.79% versus 27.46%) and worse on assessment.
The observed selection gain did not generalize. Dataset shift, coarse features
and limited independent evidence are possible explanations, not established causes.

The experiment was not retuned after assessment. The earlier Doyle artifact and
default route selection remain unchanged. A future attempt needs a new frozen
development design and genuinely untouched assessment evidence; this assessment
is now inspected development data. Search benefit and the matched-budget
non-agent/main-agent/specialist comparison remain separate later evaluations.

## Local use and reproducibility

Artifact: [candidate-model.json](../artifacts/steps/srg-06/experiment-v1/candidate-model.json).
Model version: `srg06-cn-training-v1-rf_leaf2`.
Schema: `srg-cn-condition-hit-model-v1`.
Features: `cn-morgan-radius2-chiral-128-per-role-v1`.
Artifact SHA-256: `4b04d18aef63e7e26250236e6a960ff70f6096c72b413d96261decf07c00ffd2`.
Evidence status is always predicted; scientific promotion is not accepted.

From the package directory, a fresh output directory reproduces the frozen
experiment. The input must be the exact pinned CSV; do not reuse an existing
output directory or reinterpret a replay as a new held-out experiment.

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 \
.venv/bin/python scripts/train_cn_condition_model.py \
  --dataset /home/boltzmann6/srg-data/srg06/BH_HTE_Curated_Dataset_v20260219.csv \
  --dataset-sha256 247473787c33fb22ee48a4177593188f2a2c6ef140756566fe4610fee89ba333 \
  --output /absolute/path/to/new-experiment-directory
```

To explicitly enable the experimental scorer in a local environment:

```python
from synthesis_route_gym.cn_model import CNConditionModel
from synthesis_route_gym.environment import SynthesisRouteEnv

model = CNConditionModel.load("artifacts/steps/srg-06/experiment-v1/candidate-model.json")
env = SynthesisRouteEnv(task, cn_condition_model=model)
result = env.dispatch("score_cn_conditions", {"candidates": candidates})
```

Here `task` is the existing validated environment task and `candidates` is a
list of explicit six-role candidate inputs with unique IDs. This tool scores
supplied choices; it does not generate conditions or change route ranking.
The [scientific tool contract](SCIENTIFIC_TOOL_CONTRACTS.md) describes CLI/API
configuration, output fields, metering and host responsibilities.

## Verification and evidence

- **885 tests passed**, 0 failed/skipped, **93.34% branch-inclusive package
  coverage**. The new training module has 100% combined coverage; data/model
  modules exceed 93%. The existing upstream Starlette/httpx warning remains.
- Real-model smoke matched committed predictions, exercised a deliberate
  out-of-domain abstention, local CLI replay, budget accounting and checkpoint
  resume/idempotency. It made no LLM calls.
- A distinct post-fit audit reconstructed source identities and threshold labels
  directly from the CSV, checked all 1,421 assessment candidates and all 129
  top-1 selections per arm, and recomputed both macro regrets. This is automated
  source-record consistency checking, not independent experimental reproduction
  or human chemical-process validation.
- All 47 frozen Python files and 11 historical artifacts matched their hashes.
  The reserved final data and Agent Scientist main profile were unchanged.

Evidence: [aggregate results](../artifacts/steps/srg-06/experiment-v1/summary.json),
[frozen recipe](../artifacts/steps/srg-06/experiment-v1/recipe.json),
[pretraining freeze](../artifacts/steps/srg-06/pretraining-freeze.json),
[source-result audit](../artifacts/steps/srg-06/source-result-verification.json),
[real-tool smoke](../artifacts/steps/srg-06/real-tool-smoke/receipt.json),
[separate review](../artifacts/steps/srg-06/review.json),
and [step receipt](../artifacts/steps/srg-06/acceptance.json).
