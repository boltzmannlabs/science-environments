# De novo enzyme design — research notes

## Scope and rationale

The [environment specification](../../environments/Denovo-Enzyme-Design/ENVIRONMENT_SPEC.md) describes designing candidates for a requested conversion using a qualified reaction profile. Its initial scope is soluble, single-chain, cofactor-free enzymes. Mechanism-specific profiles provide the catalytic roles, states, evidence rules and supported operating conditions.

The proposed workflow screens sequence properties and folding before more expensive complex, state and chemistry evaluation. Folding confidence and substrate-pose scores are treated as separate evidence from catalysis. Solubility and aggregation are separate required criteria. An optional reinforcement-learning controller chooses permitted actions while the scientific acceptance rules remain fixed.

These are design requirements, not measured outcomes. No qualified reaction profile, scientific execution, trained policy or enzyme benchmark result is delivered. The illustrative request and reward coefficients are not experimentally established settings.

## Provenance and repository review

The source is the Boltzyme developer handoff dated 22 October 2026. The package reorganizes that specification into task, input/configuration contracts and acceptance requirements. Scientific references and task-format attribution are maintained once in [references.md](references.md).

The target repository was retrieved on 26 October 2026. Its README, CONTRIBUTING.md, LICENSE and PR template were read. The environment and research directories follow the current layout. The [repository license notice](../../LICENSE) explicitly leaves license selection pending; it grants no license. Third-party assets retain their separate access and licensing requirements.

## Open work

- Assign a tracking issue and scientific/software reviewers; use the repository's contribution process for follow-up work.
- Qualify an initial reaction profile and its controls, uncertainty policies and operating domain.
- Select and pin implementations, models and data; verify applicability to newly designed sequences.
- Implement orchestration, immutable evidence handling, budget enforcement and evaluation.
- Validate the full computational workflow before benchmarking fixed and frozen RL execution under equal resource limits.

The [acceptance plan](../../environments/Denovo-Enzyme-Design/tests/ACCEPTANCE.md) separates completed specification checks from these future implementation and scientific requirements.
