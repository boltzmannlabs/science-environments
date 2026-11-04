# Enzyme Variant Comparison Protocol

## Question and approaches

Does a native proposer/critic specialist help Agent-Scientist produce stronger computational enzyme variants under equal constraints and maximum budgets?

Compare Agent-Scientist alone with Agent-Scientist using the proposer and critic. Both execute the complete environment workflow, including tool-based initial and revised generation. A historical paper supplies external context; it is not automatically a third executed workflow. A separately run fixed baseline may be added only with its own frozen settings and accounting.

## Freeze before design

Record the exact public parent bundle, task version, chemical state, protected/editable positions, initial and revised candidate limits, required final evidence and evaluation method in `RUN_PLAN.json`. Include numeric scientific-compute, model-token, financial and wall-time ceilings. The starting limits are 24 unique sequences including the parent, at most eight substitutions per variant, at most two sequence-revision rounds, at most 60 scientific submission attempts and up to five final candidates. Require at least one actual results-driven sequence revision unless a documented blocker leaves the run incomplete.

Count all parent and specialist model usage in each approach's total. Record unsuccessful attempts and ambiguous submissions. Share parent preparation and the public task, not candidates or decisions. Do not change a frozen metric or budget after seeing one approach's results. If changed methods are needed, preserve the first comparison and label a new one.

The public specification does not enforce token/cost limits or file isolation. Use SCI's existing limits and the selected execution backend. Prompt-only information boundaries are not a sandbox, and language-model prior knowledge cannot be excluded by hiding local files alone.

## Scientific acceptance

An evaluator separate from the design conversation reviews generation provenance, edit constraints, sequence/structure identity, chemical state, required structure/quality/catalytic reports and revision evidence. Use actual native artifacts; stage declarations alone are insufficient. A proposer/critic conversation does not provide this independence.

Use task-specific evidence-backed acceptance criteria, with uncertainty. Missing justified catalytic ranges may make geometry descriptive rather than a rejection gate; record that choice before selection. Missing measurements or mappings remain unresolved. Do not penalize an unknown result by assigning a numerical zero.

## Common numerical endpoint

Choose one final primary metric for the selected case. Parent and candidates from both approaches must be evaluated with the same method version, settings, units and chemical state. Evaluate selected paper references with that protocol when available, or keep the historical values descriptive. A favorable predictor used to generate candidates should not also be advertised as independent experimental truth. Add an orthogonal evaluator where available and state any shared-model dependency.

The offline helper compares an already-reviewed primary-metric table. It does not execute a method, inspect structures, discover thresholds, establish uncertainty significance or judge whether a proxy measures catalysis.

Protocol JSON fields:

| Field | Meaning |
| --- | --- |
| `parent_id` | Identifier of the exact shared parent. |
| `metric` | One named numerical endpoint, not a mixture of endpoints. |
| `unit` | Exact unit for this endpoint. |
| `direction` | `minimize` or `maximize`. |
| `protocol_id` | Fingerprint/name of the frozen method, settings, input state and evaluation procedure. |
| `min_improvement` | Nonnegative minimum signed change needed to label a numerical improvement; justify it in the frozen protocol. It is not automatically a significance test. |
| `max_selected` | Positive maximum final selection count. |
| `ratio_allowed` | Boolean; true only for a meaningful positive ratio scale, never energies or log-transformed scores. |

The reviewer creates `evaluation_observations.csv` with exact header:

```text
candidate_id,sequence_sha256,metric,value,unit,protocol_id,eligibility,evidence_path
```

Use `true`, `false` or `unknown` for eligibility after reviewing all task requirements. `value` may be blank for unavailable measurements. Every supplied row needs a genuine evidence reference. The helper checks declaration consistency, not the contents of that reference. Keep secondary metrics in the full run observations, not this single-endpoint input.

The design agent seals `selection.csv` with header `candidate_id,rank,sequence_sha256` and a `selection_seal.json` containing `selection_sha256` before receiving evaluator results. Ranks must be unique and contiguous from 1; the parent and duplicate sequences are excluded. The seal detects changes to the file, not when it was created or who could access labels.

From the repository root:

```bash
python -B environments/enzyme-variant-optimization/scripts/evaluate_results.py --protocol /path/to/frozen_evaluation.json --observations /path/to/evaluation_observations.csv --selection /path/to/selection.csv --seal /path/to/selection_seal.json
```

The paths above describe reviewer-owned run artifacts, not tool submission payloads. The command prints JSON and never submits jobs or changes the selection. A nonzero exit means malformed/incompatible declarations; `incomplete` is a valid report with missing evidence, not a completed scientific comparison.

## Reporting

Report each approach's workflow completion, actual generated unique sequences, supported final candidates, signed parent-relative metric changes, mandatory failures and unresolved evidence. Add runtime, queue time, model usage, scientific-resource usage, cost with original units, and repeat variability where available. A single repeat is a case comparison, not a general performance claim.

Only a fully observed eligible selection receives an aggregate numerical score. No qualifying selection and missing evidence are different outcomes. Numerical improvement in a computational endpoint does not establish experimental improvement. Retain unfavorable and incomplete results.

## Reference information

[Reference values](REFERENCE_VALUES.md) are operator/evaluator material. Keep that file and target-study winner data out of tested-agent inputs. It contains literature observations, not outputs generated by this environment.
