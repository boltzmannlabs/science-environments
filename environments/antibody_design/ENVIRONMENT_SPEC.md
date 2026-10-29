# Antibody Design — Environment Specification

**Environment ID:** `antibody_design`

**Research scope:** reference-guided monoclonal design, target-only antibody discovery, and bispecific antibody design.

**Current implementation:** all nine tasks have family-specific profiles and request/result schemas. Reference-guided monoclonal tasks have preflight and bundle-integrity tests. Target-only, bispecific design, and evidence-assessment tasks have schema and declared-identifier checks, without scientific execution or independent grading. All task Markdown files remain under `tasks/`; see the [task catalog](README.md).

**Maturity:** Specification. This environment does not include a scientific executor, qualified prediction adapters, or experimentally validated designs.

## 1. Purpose and repository organization

Define clear, reproducible antibody-design tasks for an Agent-Scientist environment, with explicit inputs, outputs, evidence requirements, and limits. The environment-wide specification covers the three research cases; the first implemented testing scope remains monoclonal design with a supplied reference.

The [repository README](../../README.md) places environment requirements, configuration, tasks, and applicable tests in `environments/<environment-name>/`, and supporting research in `research/<environment-name>/`. The [contribution guide](../../CONTRIBUTING.md) also permits small example outputs and validation summaries in `results/`. Apply those responsibilities here:

| Location | Responsibility |
| --- | --- |
| `README.md` | Concise environment overview, task families, current readiness, and layout. |
| `ENVIRONMENT_SPEC.md` | Shared requirements and distinctions between task families; current versus planned support. |
| `config/` | Environment registration, family profiles, request/result/protocol schemas, JSON request examples, metric definitions, and validation dependencies. |
| `tasks/` | The nine agent-facing Markdown task instructions only. JSON request examples live beside their family configs. |
| `tests/` | All validation code, acceptance criteria, test fixtures, and testing helpers. The current scenario suite is `monoclonal_antibody_with_reference/`. |
| `results/` | Small example outputs and generated validation reports; no test implementation. |
| `../../research/antibody_design/` | Research findings, references, source limitations, and the existing benchmark brief. |

Do not duplicate research papers or task instructions inside test folders. Supporting criteria documents describe what tests must establish; they are not extra agent tasks. Keep research sources in the [reference catalog](../../research/antibody_design/references.md), with findings in [research notes](../../research/antibody_design/research-notes.md).

## 2. Task families and current support

These cases differ in their starting information and molecular requirements. An optimization objective such as humanization is separate from the task family; a molecular format such as Fab is separate from both.

| Case | Starting information | Intended task outcome | Current package status |
| --- | --- | --- | --- |
| Reference antibody + target | Defined target and a supplied paired heavy/light reference antibody, with provenance and permitted changes. | Reference-derived candidates, a comparable reference baseline, and evidence for the declared objective. | Active specification, schemas, and contract tests. |
| Target only | Defined target; no supplied antibody known to bind it. Format/framework choices and other method-required context must still be declared. | Candidate binding hypotheses with traceable origin and evidence; no invented reference or reference-improvement claim. | Dedicated target-only schemas and declaration checks; no executor or scientific acceptance suite. |
| Bispecific antibody | Two intended binding specificities and a declared molecular architecture; parental binders may be supplied, partly supplied, or absent. | An assembly-aware candidate definition, evidence for each specificity, and evidence for the intended combined mechanism. | Design and assessment schemas with declaration checks; no executor or scientific acceptance suite. |

Bispecificity can involve different antigens or distinct epitopes on one antigen. It is not synonymous with two binding sites: a conventional bivalent antibody need not be bispecific. Whether both targets must be engaged simultaneously depends on the proposed mechanism. These distinctions follow the [FDA's bispecific antibody guidance](https://www.fda.gov/media/123313/download).

## 3. Case A: reference antibody and target supplied

The active [reference-guided task](tasks/mab_reference_guided_design.md) targets human EGFR (ERBB1) with cetuximab as its reference antibody. Its reusable request contract accepts target context, exact paired reference sequences, molecular format, sequence scope, reference annotations, objective, edit policy, protocol, seed, and budget.

The current reference-required objectives are `reference_guided`, `affinity_maturation`, `humanization`, `developability_optimization`, `specificity_optimization`, and `mechanism_optimization`. These labels specify different evaluation questions; they do not indicate six implemented design algorithms. Supported product contexts are IgG, Fab, and F(ab')2, with variable-domain or compatible chain-level sequence scopes. VHH and scFv require different representation contracts and are not accepted formats in the present validator.

Required distinctions:

- Preserve the reference identity and heavy/light pairing. Each candidate must identify its reference parent and current sequence digest.
- Establish a reference baseline under the same target context and comparable evaluation conditions as candidates.
- State which properties should improve, which should be retained, and which are hard constraints. A passing absolute score alone does not demonstrate improvement over the reference.
- Retain unsuccessful and unresolved outcomes. Do not fill a shortlist with candidates lacking mandatory evidence.

Published reference-based antibody optimization includes experimental assessment of proposed variants; it does not establish that a model score alone demonstrates improvement. This motivates keeping computational predictions and measured comparisons separate. [Hie et al.](https://pubmed.ncbi.nlm.nih.gov/37095349/)

The existing `denv_antibody_001` profile is one reference-guided example, with [general](tasks/denv_antibody_001.md) and [capability-detailed](tasks/denv_antibody_001_tools.md) presentations. Both retain identical scientific requirements and budgets. The DENV profile does not define the entire environment.

## 4. Case B: target supplied without a binding-antibody reference

This case addresses discovery rather than modification of a known binder. “Target only” describes the absence of a supplied binding reference; it does not mean an antigen name or sequence is sufficient for every design method.

The current [target-only task](tasks/mab_target_only_design.md) specifies human EGFR (ERBB1), with no supplied binding-reference antibody or imposed reference epitope.

The task must declare target identity and construct, presentation context, available structural information, epitope constraints or uncertainty, requested antibody format, framework/scaffold assumptions, evidence requirements, and budget. Method-specific missing inputs must be reported instead of inferred. A framework template is not a binding-reference baseline.

Candidates need origin records, sequence identity, independent evaluation, and explicit uncertainty. Any comparison to a known binder must identify it as an external comparator and account for benchmark leakage. Record whether candidates were generated, retrieved, or selected from a supplied library; those are different experimental questions.

Recent de novo antibody work combines computational proposals with experimental screening and characterization. Its published results support studying this case, not assuming arbitrary targets are solved or that every antibody format transfers unchanged. [Bennett et al., published online 2025](https://www.nature.com/articles/s41586-025-09721-5)

**Implemented contract:** the [target-only profile](config/monoclonal_target_only/profile.yaml) requires explicit reference absence and candidate-origin declarations. Its dedicated schemas support the [task](tasks/mab_target_only_design.md); the reference-required schema still rejects `de_novo`. Scientific generation, protocol qualification, and independent evaluation remain unimplemented.

## 5. Case C: bispecific antibody design

The current [bispecific design task](tasks/bispecific_antibody_design.md) specifies HER2 biparatopic design with zanidatamab as the reference antibody and binding specificities for extracellular domains II and IV. The reference name alone does not supply molecular inputs or establish equivalent geometry or activity. The broader family contract also supports two different antigens.

The task must define the two binding specificities, intended mechanism, architecture, chain identities, valencies, and supplied parental evidence. If only one parental binder is available, the missing binding component remains a separate discovery requirement.

Evaluate the assembled molecule as well as its components. Arm-level binding alone does not establish correct assembly or the intended combined behavior. Research on parental-antibody selection demonstrates the importance of compatible heavy/light-chain pairing for relevant bispecific formats. [Gong et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33397191/)

The proposed evidence contract must distinguish component identity, assembly integrity, each specificity, mechanism-dependent joint engagement, and whole-product developability. Do not assume a universal four-chain architecture, infer clinical benefit from dual binding, or treat two independent antibody outputs as a bispecific result.

**Implemented contract:** the [bispecific design profile](config/bispecific_design/profile.yaml) declares named chains, two specificities, arm assignments, and whole-molecule evidence. Cellular and CNS assessment tasks have separate dataset/decision profiles in `config/bispecific_assessment/`. These declaration checks do not establish assembly, mechanism, or delivery performance. The reference-paired FASTA bundle is not imposed on bispecific architectures; scientific executors and independent evaluators remain required.

## 6. Shared evidence and evaluation requirements

The following are environment-design requirements; their scientific enforcement is not fully implemented:

| Area | Required distinction |
| --- | --- |
| Molecular identity | Exact target constructs, candidate sequences, format, chain identities, and source provenance. File hashes establish integrity, not biological correctness. |
| Structural evidence | Separate antibody folding from target-complex plausibility. Record missing structures, mapping uncertainty, and the domain of applicability of the method. |
| Binding and function | Keep predicted interaction scores, measured affinity/kinetics, binding assays, and functional endpoints separate. Confidence scores are not affinity measurements. |
| Developability | Treat stability, aggregation, solubility, expression-related risk, polyreactivity, and immunogenicity indicators as distinct evidence. |
| Comparisons | Use a matched reference for reference-guided work; declared comparators for target-only work; component and whole-molecule comparisons as appropriate for bispecific work. |
| Reproducibility | Record request and artifact hashes, model/harness/tool revisions, method availability, seed, isolated workspace, and actual resource use. |
| Evaluation integrity | Freeze rules and budgets before evaluation; keep held-out outcomes out of agent-visible task inputs; avoid uncalibrated combinations of unlike endpoints. |

The [metric catalog](config/shared/metric-catalog.json) supplies identifiers and scopes, not universally valid thresholds. The [protocol schema](config/shared/protocol.schema.json) describes required declarations, not a scientifically qualified protocol. Missing evidence remains unresolved; a favorable score cannot compensate for a mandatory failed rule. Wet-lab measurements may be supplied as external evidence, but the package does not execute assays.

## 7. Configuration, outputs, and status semantics

The [configuration guide](config/README.md) explains the files currently implemented. `environment.yaml` catalogs all task specifications and separately records their implementation status. A single `config/` directory contains shared definitions and four family folders: `monoclonal_reference`, `monoclonal_target_only`, `bispecific_design`, and `bispecific_assessment`. Each task selects its own profile; no universal configuration silently applies to every family. Reference-only bundle settings remain explicitly scoped in the environment catalog.

Current completed reference-guided bundles contain `designed_sequences.fasta`, `metrics.json`, `shortlist.csv`, `report.md`, and referenced evidence. They include exactly one declared reference record, exclude that reference from the designed shortlist, and preserve paired-chain identity. See the [result contract](results/README.md). Target-only results record candidate origins; bispecific design results record named chains and arm/whole-molecule evidence. Assessment results wrap task-specific answer fields with request hash, status, evidence, and limitations. These schemas are versioned separately from the reference bundle.

| Status | Current meaning |
| --- | --- |
| `CONTRACT_VALID` | Schema and declared identifiers agree; incomplete inputs may still pass. |
| `ASSESSED` / `INDETERMINATE` | Assessment response declarations, not independently verified decisions. |
| `NEEDS_INPUT` | Required declared input artifacts are missing or invalid. |
| `PROTOCOL_REQUIRED` | Required protocol evidence or compatible method declarations are absent or invalid. |
| `CONTRACT_READY` | Preflight contract checks passed; scientific readiness remains unverified. |
| `BLOCKED` | A declared execution dependency prevents progress. |
| `QUALIFIED` | The requested candidate count passes all declared computational rules. |
| `PARTIAL` | Some, but fewer than requested, qualify. |
| `NO_QUALIFYING_DESIGNS` | Evaluated candidates have verified mandatory failures; unresolved work alone is insufficient. |
| `INCOMPLETE` | No candidate qualifies and unresolved work prevents a completed conclusion. |
| `CANCELLED` | Execution was cancelled; preserve available evidence. |

Malformed requests and task/schema mismatches are rejected. The `tests/task_contracts.py --task ...` command supports all registered profiles; the existing `preflight` and `bundle` commands remain reference-only. Status consistency checks for the newer families do not reproduce their scientific conclusions. `QUALIFIED` does not establish experimental activity or safety.

## 8. Testing, scientific readiness, and source dates

All executable validation and test support lives in `tests/`. The current scenario suite covers reference-guided monoclonal contracts, the DENV example, prompt parity, and declared criteria. See the [acceptance plan](tests/monoclonal_antibody_with_reference/ACCEPTANCE.md) and [coverage/gaps review](tests/monoclonal_antibody_with_reference/COVERAGE.md). `tests/test_configurations.py` additionally checks all task profiles, shared-schema resolution, invalid declarations, and response integrity. Passing these checks does not test target-only or bispecific design capability.

Remaining implementation gaps include a scientific executor, qualified adapters, verified biological examples, independent edit-mask and structural-identity checks, and a justified reference-improvement calculation. The additional families now have task profiles, schemas, and configuration checks. They still need full result-bundle validation, task-specific scientific evaluators, and independently reviewed end-to-end cases before scientific execution can be claimed. Research coverage, specification completeness, software checks, and scientific validation must be reported separately.

The DENV example retains its **2024-09-01** cutoff. The broader research review includes later publications, clearly dated in the [reference catalog](../../research/antibody_design/references.md). A later paper does not establish eligibility for the frozen DENV profile; each future task must declare its own evidence and method-availability policy.
