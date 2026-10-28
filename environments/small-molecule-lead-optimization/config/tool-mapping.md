# Boltzmann capability mapping for lead optimization

**Status: reference mapping for specification review.** Inspected locally on 28 October 2026. This document neither registers tools nor implements runtime integration. Inclusion here does not make a tool mandatory, enable access, or establish that its worker has completed a scientific job.

The task will declare the capabilities it permits. The agent's tool selection remains subject to that task, available evidence, budgets, and the current authorized connector. No fixed tool order, ranking weights, property cutoffs, or numerical budgets are selected by this mapping. Target-specific choices belong in tasks.

## Source and contract ownership

- Inspected repository: [Agent-Scientist](https://github.com/boltzmannlabs/agent-scientist), local HEAD `062351dd048c142840f78ea198f22417d983ccda`.
- Canonical catalogue: `plugins/boltzmann/skills/boltzmann-tools/references/tool-contracts.v1.json`, schema version `2`.
- SHA-256 of the inspected catalogue bytes: `dd4319d26172a4bb2143d295626da4b2ec36bf5d31386b483cdc33cea5b9f169`.
- File rules and limits remain in the adjacent `file-input-contracts.v1.json` and `input-limits.v1.json`. See the [upstream contract guide](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/CONTRACTS.md).

All module paths below are relative to `plugins/boltzmann/skills/boltzmann-tools/references/`. They identify the generated documentation to read with the canonical request before execution. This file deliberately supplies no second set of payload schemas, field aliases, or file-format rules. The source checkout contained unrelated local edits; recording its HEAD and catalogue hash is not a clean-release or compatibility certification.

## Module references

| Key | Exact generated module path | Inspected source |
| --- | --- | --- |
| M1 | `modules/small-molecule-optimization.md` | [Molecule Optimization](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-optimization.md) |
| M2 | `modules/small-molecule-qspr.md` | [QSPR Modelling](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-qspr.md) |
| M3 | `modules/small-molecule-screening.md` | [Virtual Screening](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-screening.md) |
| M4 | `modules/small-molecule-toolbox.md` | [Toolbox](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-toolbox.md) |
| M5 | `modules/small-molecule-enumeration.md` | [Enumeration and Dataset Creation](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-enumeration.md) |
| M6 | `modules/small-molecule-pharmacophore-generation.md` | [Pharmacophore Generation](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-pharmacophore-generation.md) |
| M7 | `modules/small-molecule-structure-generation.md` | [Structure-Based Generation](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-structure-generation.md) |

## Known-lead optimization capabilities

These jobs are candidates for proposing modifications around supplied leads or lead-series information. None automatically proves that a generated molecule preserves a required scaffold, mechanism, or measured activity; those conditions need task-specific evidence.

| Exact job name | Module | Potential role and boundary |
| --- | --- | --- |
| `Fragment_Based_Optimization` | M1 | Optimize a reference molecule using fragments from a supplied molecular library. Library and reference provenance remain part of the task. |
| `Lead_Generation_Graph_GA` | M1 | Generate and optimize candidates from a starting molecule with Graph GA. Assess returned candidates against the declared lead constraints. |
| `Lead_Optimization_Mcts` | M1 | Optimize a reference molecule with Monte Carlo tree search. Returned candidates still require identity and evidence checks. |
| `Lead_Generation_Mars_Plus` | M1 | Generate and optimize candidates from a starting molecule. Method-internal scores do not establish experimental improvement. |
| `Lead_Generation_Reinvent` | M1 | Property-guided candidate generation with documented fine-tuning/model-reference modes. It is not a universal direct-seed editing interface; a task must justify its connection to the starting series and assess the outputs. |
| `Lead_Generation_Augmented` | M1 | Candidate generation with the documented augmented-generation workflow and optional fine-tuning context. Lead retention is not guaranteed by the job name. |

## Map each objective to an actual capability

An optimization algorithm name does not establish which scientific objective its deployed request can optimize. Before selecting an action, classify each task objective separately using the current [canonical catalogue](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/tool-contracts.v1.json). The classifications below describe inspected contract support, not tested worker behavior.

| Objective/capability situation | What the inspected contract establishes | Permitted interpretation and next step |
| --- | --- | --- |
| **Property-directed optimization request supported** | All six M1 optimization jobs expose a selection of built-in property models with bounds. Their model-name enums include exact identifiers such as `Solubility`, `Lipophilicity`, `Clearance`, and `hERG`. | A task may request those documented property-directed controls when the selected endpoint, model scale, bounds, and model applicability have been reviewed. The contract does not establish the internal reward formula, weighting, calibration, or that all returned molecules satisfy the requested bounds. Assess outputs and compare against compatible baseline evidence. |
| **Target endpoint assessed afterward** | `global_binding_affinity` and `global_ic50` are separate M2 prediction jobs with compound–protein inputs. Their exact job names are absent from the six M1 built-in property-model enums. The inspected M1 schemas do not document a protein-sequence/pocket-driven reward or a way to wire either predictor into the optimizer. | The agent can generate permitted candidates, assess the target endpoint through the separate predictor, compare compatible observations, and use that evidence to revise a later investigation. Report this as assessment after generation; do not claim the generator internally optimized that target score. |
| **Custom objective conditionally supported by the request shape** | The six M1 jobs expose custom-property-model references and bounds, but the schema does not identify any particular deployed model or prove its endpoint, training provenance, scale, applicability, or compatibility. Some modes also require an existing fine-tuned generator artifact; that is distinct from the property-model reference. | Treat a target-specific custom objective as unverified until an actual accessible model and its endpoint/scale, development data, and optimizer compatibility are established. A string that passes schema validation is insufficient. No compatible model ID is supplied by this environment. |
| **Objective not currently mapped to a supported optimizer control** | No arbitrary reward callback, docking-service callback, or user-defined composite-objective interface is documented in the inspected M1 contracts. Some schemas accept additional properties; that does not document executable semantics for invented inputs. | Record the objective as unsupported for internal optimization. If a compatible separate assessment exists, use it only under the preceding assessment category. Otherwise record the missing capability and resolve the task scope before claiming that objective can be evaluated or optimized. |

### Contract evidence and limitations

The inspected evidence is the model-name enumeration inside each M1 job's request schema, its custom-model reference declaration, and the separate M2 job definitions. These declarations are the source for the distinctions above; they are not a second schema maintained here. In particular:

- Selecting `Solubility` or `hERG` establishes a documented property-model control, not a universal unit, a direction of biological improvement, an experimental endpoint, or a meaningful bound for every task. The declared task objective must be reconciled with the actual model's output semantics before a request is considered suitable.
- `global_binding_affinity` is an exact prediction job name, not an optimizer's built-in model identifier. Do not substitute it, `global_ic50`, a target name, or a job ID for a model identifier merely because the strings fit a request field.
- Model names can overlap across optimization and `Property_Prediction` while the deployed model identity/version remains unknown. A matching label alone does not prove the scores are directly comparable; obtain the available model provenance or report that comparison limitation.
- Fine-tuning a generator on compounds from a series is not proof of target-activity-directed optimization. Training a property model requires its own data and evaluation review; hidden task answers must stay outside training and model selection.

### Concrete task categories

**Property improvement around a lead.** A task might ask for improved solubility while preserving an explicitly defined liability endpoint or scaffold feature. `Solubility` and, where appropriate, `hERG` are present in the M1 built-in model enums. This establishes a possible property-directed request. The task must still define the endpoint interpretation and accepted bounds, confirm that the chosen controls express the intended objective, and assess the actual baseline and candidate outputs. Neither their labels nor this example selects success thresholds.

**Binding or inhibitory-potency improvement for a named target.** A task might ask for analogues of a supplied lead with improved target-associated predictions. The current mapping establishes separate NESSO/IC50 prediction and docking capabilities, with their own evidence limits. It does not establish an internal target reward in Graph GA, MCTS, MARS Plus, REINVENT, Augmented, or fragment-based optimization. A justified workflow can propose candidates using documented controls and then assess their target scores; an end-to-end claim of target-directed internal optimization remains unverified without a compatible documented custom-model route or another established optimizer contract.

**Selection from a measured library.** A task can restrict candidates to declared molecules and ask the agent to prioritize them using permitted evidence. This is a selection task; it does not require internally optimizing a generative reward. Its protected assay measurements apply only to the recorded molecules and cannot score new analogues.

## Property and target-associated assessment

| Exact job name | Module | Potential role and boundary |
| --- | --- | --- |
| `Property_Prediction` | M2 | Obtain selected molecular-property predictions. Preserve each returned model endpoint, scale, and available uncertainty information. |
| `global_binding_affinity` | M2 | Obtain a NESSO score for compound–protein pairs. The contract describes lower comparable scores as stronger predicted binding, without establishing physical energy units or measured affinity. Production acceptance/artifacts were not live-verified in the inspected notes. |
| `global_ic50` | M2 | Predict inhibitory potency for compound–protein pairs. Confirm actual returned columns and units; predicted IC50/pIC50 is not a measured assay result or automatically a binding-affinity endpoint. |

## Screening and candidate-set review

| Exact job name | Module | Potential role and boundary |
| --- | --- | --- |
| `QSPR_Screening` | M3 | Apply selected property/ADMET filters to a library. Filter choices and their interpretation must come from the task. |
| `Similarity_Screening` | M3 | Compare candidates with reference compounds. Similarity can support a declared series constraint; it does not prove preserved potency. |
| `Substructure_Screening` | M3 | Apply declared inclusion/exclusion substructure rules. A flagged or unflagged pattern is not a complete toxicity assessment. |
| `Novelty` | M3 | Compare candidates against a selected reference collection. Results describe that collection and search mode, not universal chemical or patent novelty. |
| `Butina_Clustering` | M3 | Organize a library by molecule/scaffold fingerprint relationships. Clusters may support diversity review; they are not activity rankings. |
| `K_Means_Clustering` | M3 | Organize candidates using the documented feature-based clustering mode. Cluster settings and any selection policy require task justification. |
| `Pharmacophore_Screening` | M3 | Screen against a compatible existing hypothesis artifact. Compatibility and reported service-cost notices require review; a feature match is supporting evidence. |

## Optional structural assessment

These capabilities apply when a task supplies the necessary target structure and structural context. They are not prerequisites for every general lead-optimization task.

| Exact job name | Module | Potential role and boundary |
| --- | --- | --- |
| `Binding_Site_Prediction` | M4 | Predict candidate pockets with fpocket. A predicted pocket is not proof of the relevant functional binding site. |
| `Vina_basic_docking` | M4 | Predict poses and docking scores within a declared search region. Inspected notes report historical worker failures with recovery unverified; follow upstream execution notices. |
| `Vina_Flexible_Docking` | M4 | Dock with explicitly selected flexible receptor residues. Required structural selections and interpretation remain task-specific. |
| `Vina_Score_only_docking` | M4 | Score supplied poses. Do not report a new docking search or experimentally measured affinity. |
| `Diffdock` | M4 | Predict poses in blind-docking mode. Its confidence information is not interchangeable with a Vina energy score. |

## Optional candidate-generation and model support

These capabilities are mapped for tasks that explicitly need them. Their existence does not make general de novo generation, model training, or dataset collection a required stage of lead optimization.

| Exact job name | Module | Potential role and boundary |
| --- | --- | --- |
| `Molecule_Enumeration` | M5 | Enumerate R-group alternatives around a supplied scaffold using supplied building blocks. Check all returned candidates against task constraints. |
| `Structure_Based_Generator` | M7 | Generate candidates conditioned on a binding-pocket structure. This broader generation route requires an explicit task connection to the lead objective. |
| `ligand_pharmacophore` | M6 | Build ligand-based hypotheses from distinct training/validation sets. Historical notes describe missing artifacts despite a reported success; inspect actual outputs and preserve uncertainty. |
| `Pharmacophore_Hypothesis` | M6 | Build a receptor/ligand-structure-based hypothesis. It is a different workflow from ligand-based hypothesis generation. |
| `Pharmacophore_Based_Generator` | M6 | Generate candidates from a compatible hypothesis artifact. Do not assume interchangeability of different hypothesis formats. |
| `Custom_Property_Model_Automl` | M2 | Build a property model from task-approved labelled data. Training/development data must not include protected evaluation answers. |
| `Custom_Property_Model_DL` | M2 | Build a deep-learning property model from task-approved labelled data. Availability of the job does not establish model applicability or generalization. |
| `dataset_creation` | M5 | Create a target/assay-linked platform dataset when permitted by the task. Collection alone does not qualify endpoint consistency or evaluation independence. |

## Execution and evidence boundary

The mapped catalogue entries were marked active and not execution-blocked in the inspected source. That is a source-level classification, not an account-entitlement check, live service test, or evidence that all outputs are usable. No scientific tool was invoked to create this mapping.

Before a real run, use the current installed catalogue and matching complete generated module, including its execution notices. Record the actual revision, contract content, selected model/settings, input identity, job identity, and returned artifacts. If deployment differs from this reference snapshot, review the difference rather than silently submitting a stale request.

Generation, filtering, docking, and prediction outputs need to stay attached to the exact molecule and applicable target/structure context. Their numerical scales are not implicitly comparable. A later benchmark needs its own approved assay endpoint and protected data; none of these tools supplies experimental answers for arbitrary newly generated compounds.
