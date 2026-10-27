# Monoclonal Antibody Design — Environment Specification

**Environment ID:** `antibody_design`

**Primary reusable task family:** paired-chain monoclonal antibody design and computational assessment

**Concrete profile:** `denv_antibody_001`

**Maturity:** Computational task and contract specification; DENV and target-agnostic contract validators are implemented. This package does not claim to ship or qualify any prediction model, adapter, or threshold.

## Objective

Define computational-only tasks that use a supplied antigen profile and, in the primary lane, a supplied monoclonal reference antibody. Preserve the declared target construct, antibody format, heavy/light pairing, and edit policy. Evaluate antibody structure, antigen-interface plausibility, predicted binding, target specificity, mechanism compatibility, and developability as distinct questions. Do not execute or claim wet-lab results.

The first supported design lane is reference-guided paired-chain monoclonal design. Its product contexts are full-length IgG, Fab, and F(ab')2; each request separately declares whether sequences are variable domains, Fab chains, or full-length chains. scFv and VHH/nanobody formats have different chain architectures and remain separate extensions. The lane's objectives are affinity maturation, humanization, developability optimization, specificity optimization, or mechanism optimization. Each request freezes one primary objective, allowed edits, required evidence domains, protocol, seed, and candidate budget. The target-only design task is a secondary mode without a reference baseline. Bispecific templates remain separate extensions and do not define this initial monoclonal contract.

`denv_antibody_001` is the first concrete profile: DV87.1-derived variants against DENV-2 envelope EDIII, with framework and heavy/light pairing preserved. Its 2024-09-01 cutoff applies only to that profile. A reusable monoclonal request carries its own cutoff and protocol.

The first task concerns a reference-antibody variant study, rather than an unrestricted de novo minibinder. No 55–80-residue constraint is inherited from the illustrative cytokine task.

## Inputs and frozen protocol

The DENV [request contract](config/request.schema.json) records that profile's antigen/reference artifacts and execution settings. The [generic mAb request contract](config/generic-antibody-request.schema.json) records target constructs and presentation context, optional antigen variants, product format and sequence scope, isotype/Fc policy, reference lineage, objective, editable regions, required evidence domains, candidate count, seed, protocol artifact, and computational budget. All input artifacts are staged beneath an explicit input root and identified by relative path and SHA-256. Paths escaping that root are rejected.

Exact sequences, structures, chain mapping, and framework annotations are prerequisites. A declaration of sequence identity is not structural verification. Biological validation must reconcile each sequence with its construct and coordinates before an external scientific adapter is admitted.

Sequence artifacts use one plain-text protein sequence or one single-record FASTA sequence with standard amino-acid symbols. The generic preflight verifies file hashes and sequence syntax; completed reference-guided bundles also verify that the reference record exactly matches the supplied heavy- and light-chain sequence artifacts.

The [protocol contract](config/protocol.schema.json) freezes rules, measurement units/scales, methods and their immutable revisions, qualification evidence, and ranking. For a generic request, the validator maps its requested evidence domains to required protocol groups. For example, `developability` requires separately declared stability, aggregation, solubility, expression, and polyreactivity rules. Function and specificity rules must use antigen–antibody scope. The package supplies no qualified scientific protocol or universal biological thresholds.

The two DENV task variants share one profile protocol and budget. A general-task run can select implementations, but changing a metric definition or calibration requires a separately qualified protocol and prevents a direct same-protocol comparison. Keep tool-specific prompts and retrospective outcomes outside the method-neutral task workspace. Do not mount the entire benchmark-authoring directory as agent-visible task input.

## Execution stages

These are contracts for an external executor, not implemented molecular-design instructions.

| Stage | Required operation | Evidence and purpose |
| --- | --- | --- |
| 1. Prepare | Resolve the request, validate biological identity, freeze the protocol and limits. | `00_inputs/`: exact inputs and hashes; stop on missing identity or unqualified methods. |
| 2. Establish the reference | Assess the supplied reference under the same conditions as candidates. | `01_reference/`: baseline evidence and explicit chain/construct identity. |
| 3. Register candidates | The configured Agent-Scientist run may use an already available, protocol-qualified computational design capability; register its outputs and check pairing, uniqueness, framework constraints, and lineage. | `02_candidates/`: candidate identities and exclusions. This package specifies the contract and does not itself generate or optimize sequences. If no eligible design capability is exposed, stop with `BLOCKED` or `PROTOCOL_REQUIRED`. |
| 4. Assess structure | Assess antibody/complex confidence and coordinate integrity. | `03_structures/`: structures, confidence companions, and local uncertainty. |
| 5. Assess target binding | Evaluate antigen–antibody interface evidence and relative predicted binding. | `04_interfaces/`: metrics with explicit antigen and antibody scope; internal heavy/light-chain confidence is insufficient. |
| 6. Assess specificity and function | Evaluate the declared homolog/variant panel and computational mechanism evidence when required. | `04_specificity_function/`: per-target outcomes, method applicability, uncertainty, and missing evidence. |
| 7. Assess developability | Evaluate stability, aggregation, solubility, expression-related, polyreactivity, and immunogenicity indicators separately. | `05_developability/`: computational descriptors, applicability, scales, and uncertainty. |
| 8. Assess dynamics | Where required by the frozen request, evaluate numerical trajectory evidence and interface persistence. | `06_dynamics/`: numerical deviations/fluctuations and convergence qualifications; no simulation parameters are prescribed here. |
| 9. Evaluate | Apply frozen rules to current evidence and rank eligible unique pairs. | `07_evaluation/`: PASS, FAIL, or UNRESOLVED per rule, including rejected candidates. |
| 10. Export | Package the shortlist, paired sequences, metrics, computational run manifest, and limitations. | `08_results/`: the final bundle, exact counts, stop reason, and resource use. |

A verified failure can stop expensive dependent work. A missing required result cannot pass. Any changed candidate must receive current sequence-bound evidence; old measurements cannot be reused by changing an identifier.

## Documented implementation choices

The tool-specific arm names only the methods present in the supplied dengue documents:

| Documented name | Role supported by the documents | Unresolved implementation detail |
| --- | --- | --- |
| Stability-Binding DDG (backend job `stability-binding-ddg`) | CDR-variant stability assessment and reported mutational ranking | Exact release, interface, settings, and the returned DDG sign convention |
| PRODIGY | Predicted binding free-energy estimation | Version, conditions, and comparison conventions |
| ipSAE | Interface-confidence assessment | Version, score definition, chain direction, and required confidence companions |
| Unspecified | Antibody-antigen complex generation, docking, developability endpoints, molecular dynamics | Implementations and scientific settings must be supplied and qualified |

Generic diffusion, flow, reinforcement-learning, and hallucination descriptions in the narrative do not identify reproducible implementations. They do not create mandatory additional software dependencies or authorize a controller implementation.

## Metric semantics and qualification

The [metric catalog](config/metric-catalog.json) defines antibody-specific metric names and endpoint boundaries; it does not assign pass thresholds. Every protocol rule declares a catalog metric, units, scale, scope, method, operator, and threshold. Identity predicates may be represented as 0/1 with an explicit binary scale. Thresholds come from the qualified protocol, not historical candidate values. Units and scales must agree exactly between a rule and its result. The generic task contract includes distinct `function` and `specificity` groups; an assay record schema preserves the provenance and censoring of any external measured evidence supplied to the computational benchmark.

Use a declared 0–100 scale for pLDDT or an explicitly identified normalized scale. Treat pTM, ipTM, and ipSAE as distinct metrics. Keep predicted energy, folding-stability change, measured Kd, and ELISA EC50 separate. Antigen-interface evidence must use `antigen_antibody` scope; a heavy/light-chain interface cannot satisfy it.

Resolved rule evidence requires a finite value, a known method, matching sequence hash, and accessible hashed artifacts. Null values are UNRESOLVED with a reason. Resolved values are tested against the frozen predicate; submitted PASS/FAIL labels are not trusted. The validator checks the declared artifacts and labels, not the scientific validity of the underlying calculation.

Eligibility is the conjunction of every required rule passing. Required failures or unresolved outcomes cannot be compensated by favorable binding/confidence scores. Ranking uses a frozen ordered list of required, non-equality rules, with candidate ID as the final tie-break. Return only the requested number of eligible unique sequence pairs. This deterministic ordering is a reproducibility convention; it is not a validated therapeutic-utility score.

## Status and failure contract

| Status | Meaning |
| --- | --- |
| `NEEDS_INPUT` | Essential biological artifacts or annotations are missing. |
| `PROTOCOL_REQUIRED` | A qualified, complete, cutoff-compatible protocol is missing. |
| `BLOCKED` | An external execution dependency or infrastructure requirement failed. |
| `QUALIFIED` | The requested number pass all declared computational rules. |
| `PARTIAL` | At least one, but fewer than requested, qualify. |
| `NO_QUALIFYING_DESIGNS` | No candidate qualifies and all assessed candidates have a verified required failure. |
| `INCOMPLETE` | No candidate qualifies and unresolved work prevents a completed negative conclusion. |
| `CANCELLED` | Execution was cancelled; preserve available evidence. |

`QUALIFIED` means qualified under the declared computational contract. It does not establish experimental binding, monomericity, neutralization, clinical safety, or activity across all dengue serotypes. Record runtime, CPU/GPU use, and remote cost units independently. Exceeding a declared budget is a contract failure; missing resource measurements cannot be replaced by invented zeros.

## Result contract and validation boundary

The DENV [metrics schema](config/metrics.schema.json) preserves the original profile's `DV87.1` record. Target-agnostic tasks use [generic-antibody-metrics.schema.json](config/generic-antibody-metrics.schema.json); it allows an optional declared reference, records the design mode and sequence scope, and links typed assay records. The [assay record schema](config/mab-assay-record.schema.json) is for externally sourced or previously generated measurements; no assays are executed by this package. Preflight reports contain no candidate or assay results; completed computational runs require the full bundle.

`validation.py` implements DENV and target-agnostic request preflight, artifact integrity, qualified-protocol checks, threshold recomputation, sequence-bound evidence, assay-record provenance, deterministic shortlist consistency, and FASTA/CSV cross-checks. It does not run inference. The Agent-Scientist run manifest records provider/model revision, harness revision, task/system prompt hashes, enabled-tools hash, execution backend, environment digest, isolated workspace, and seed. An available local or remote scientific tool may be used only when its exact adapter, revision, and evidence are present in the frozen protocol; installation or visibility alone is not qualification.

## Evaluation integrity and remaining work

Retrospective experimental results and historical candidate rankings belong to the evaluator. The supplied experimental sample labels do not yet establish an unambiguous candidate mapping. No experimental outcomes or historical winning sequences are shipped as task answers.

The two task arms must use equal budgets, shared inputs, a frozen evaluator, and separately recorded actual implementations. Report completion, unresolved fractions, valid-output rate, and computational qualification separately. Do not claim scientific benchmark success from passing the package tests.

Live model/tool execution, biological-input identity verification, complete scientific protocol qualification, temporal eligibility, and scientific review remain outside the current package maturity. The generic contracts make those dependencies explicit and fail closed when their inputs or protocol evidence are absent.
