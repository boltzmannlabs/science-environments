# Task: crispr_plant_editing_012

**Task family:** application-aware CRISPR design — **plant / crop editing**.
**Status:** INACTIVE — this task documents the routing refusal and the activation
requirements; no design workflow runs until a validated species adapter exists.

## Description

Plant genome editing requests are refused at routing with an honest inactive-profile
response (`NEEDS_INPUT` / inactive profile). This task records why the gate exists and
what activation requires. It is retained in the task set so the refusal itself follows
the same contract as every runnable task: deterministic routing, logged decision,
explicit next requirements.

## Target

**None resolved while inactive.** Targets arriving with `application:
plant_genome_editing` are refused before reference resolution; the
[012 example brief](../config/012_plant.request.example.json) documents the refusal path
(audit-mode syntax only).

## Design Constraints

- **No plant-specific activity-prediction model was verified** in the 2026-11-10
  curation sweep — plant modes of live design tools (CRISPR-P2.0, CRISPR-GE,
  Cas-Designer, CHOPCHOP plant genomes) reuse mammalian/zebrafish scores.
- Cross-expression-system transfer is weak (Haeussler 2016: U6 vs T7/IVT scores do not
  transfer); cross-kingdom transfer is weaker still — human models are never applied to
  plant targets (environment scope rule, same principle as the siRNA environment's plant
  gate).
- Tool availability is not authorization: the curated plant tools are recorded for the
  activation phase in [MODELS_AND_TOOLS](../MODELS_AND_TOOLS.md).

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + gate | Recognize plant target; refuse design/evaluate generation. | Inactive-profile response with this task as reference. |
| 2. Explain | State why: no validated plant activity model; no species adapter; human-model transfer prohibited. | Logged routing decision. |
| 3. Activation path | Present the activation requirements below if the user wants to proceed. | Requirement list delivered. |
| 4. Activation (when met) | Dated activation decision recorded in [STATUS](../STATUS.md); species adapter built and validated before any run. | New protocol event. |

## Expected Output

While inactive: an honest refusal record — no candidates, no scores, no approximated
predictions. After activation (future): standard typed bundle under
`results/012_plant-editing/`.

## Constraints

No silent degradation to mammalian scoring under any weighting; no partial activation
(enumeration-only runs still require the declared species reference).

## Important Instructions

Activation requires: (1) declared species reference genome + annotation (versioned,
checksummed); (2) a validated activity model for the species/system, or an explicit
rules-only mode with the model gap stated per run; (3) species-specific off-target
reference and search policy; (4) a dated activation decision in STATUS. Published
anchors for the activation phase (CRISPR-P2.0 — Liu 2017 *Mol Plant*; CRISPR-GE — Xie
lab; Cas-Designer — Park 2015 *BMC Genomics*; CHOPCHOP plant genomes — Labun 2019
*NAR*) are curated, not executed. Run slots NOT_EXECUTED.
