# Denovo Enzyme Design — Research Notes

## Scope and rationale

The [environment specification](../../environments/Denovo-Enzyme-Design/ENVIRONMENT_SPEC.md) describes designing candidates for a requested conversion using a qualified reaction profile. Its specified scope is soluble, cofactor-free monomers and homodimers; each assembly/reaction combination still needs qualified scientific evidence and executable capabilities. Mechanism-specific profiles provide the catalytic roles, states, evidence rules and supported operating conditions.

The proposed workflow screens sequence properties and folding before more expensive complex, state and chemistry evaluation. Folding confidence and substrate-pose scores are treated as separate evidence from catalysis. Solubility and aggregation are separate required criteria. An optional reinforcement-learning controller chooses permitted actions while the scientific acceptance rules remain fixed.

These are design requirements, not measured outcomes. No qualified reaction profile, scientific execution, trained policy or enzyme benchmark result is delivered. The illustrative request and reward coefficients are not experimentally established settings.

## Provenance and repository review

The source is the Denovo Enzyme Design developer handoff dated 22 October 2026. The package reorganizes that specification into task, input/configuration contracts and acceptance requirements. Scientific references and task-format attribution are maintained once in [references.md](references.md).

The target repository was retrieved on 26 October 2026. Its README, CONTRIBUTING.md, LICENSE and PR template were read. The environment and research directories follow the current layout. The [repository license notice](../../LICENSE) explicitly leaves license selection pending; it grants no license. Third-party assets retain their separate access and licensing requirements.

## Open work

- Assign a tracking issue and scientific/software reviewers; use the repository's contribution process for follow-up work.
- Qualify an initial reaction profile and its controls, uncertainty policies and operating domain.
- Select and pin implementations, models and data; verify applicability to newly designed sequences.
- Implement orchestration, immutable evidence handling, budget enforcement and evaluation.
- Validate the full computational workflow before benchmarking fixed and frozen RL execution under equal resource limits.

The [acceptance plan](../../environments/Denovo-Enzyme-Design/tests/ACCEPTANCE.md) separates completed specification checks from these future implementation and scientific requirements.

## Homodimer research and resulting requirements — 26 October 2026

The evidence is indexed in [references](references.md#assembly-and-homodimer-evidence). The following are proposed requirements derived from that evidence, not new design results.

| Research finding | Required workflow change |
| --- | --- |
| Biological assemblies differ from crystallographic asymmetric units. | Resolve assembly ID, transformation operators and evidence before generation; retain ambiguity when sources conflict. |
| A homodimer uses one sequence in two copies. | Tie equivalent sequence positions and design the interface in assembly context; count one candidate and one unique sequence. |
| Identical subunits can adopt asymmetric states. | Declare design symmetry separately from site occupancy and catalytic-state symmetry; do not impose simultaneous reaction at both sites. |
| A credible subunit fold does not establish a correct dimer. | Independently assess the full assembly, each chain and its interface; retain controls and applicable uncertainty. |
| Global averages can conceal a bad interface or site. | Keep chain/site/interface outcomes separate and require every mandatory rule to pass. |
| Catalytic and interface roles vary by enzyme. | Establish site membership from evidence, retain partner effects and qualify any representative-site equivalence before reuse. |

Interface evaluation combines relative arrangement, contacts/burial, physical integrity, applicable confidence and the profile's alternatives/controls. It does not infer solution dissociation constants or catalyst activity from a single confidence score. Assembled and dissociated surface exposure have different meanings; sequence-based solubility alone does not establish soluble, correctly assembled protein.

The agent reviews these data before promotion. A preparation fault may justify a bounded repair/retry; contradictory or missing evidence stays unresolved; a verified design failure requires rejection or allowed redesign. Such decisions are auditable in fixed mode as well as RL. They cannot modify the frozen assembly, sequence ties, chemistry or acceptance limits.

## L-DEX YL as a prospective homodimer test

The 1JUD record assigns a C2 homodimer, although its asymmetric unit contains one protein-chain instance. It reports 232 deposited residues, 220 modeled residues and 2.50 Å resolution. Missing coordinates must not be treated as an intentionally shorter sequence or filled without recording modeling uncertainty. The structural paper locates an active-site cavity within each subunit's domains and identifies an interface-forming subdomain; it does not establish that isolated-chain design is an equivalent task.

The mechanism literature supports a covalent intermediate followed by hydrolysis and enzyme regeneration. Retaining an initial reactive pose alone is therefore insufficient. Exact site/state definitions, interface limits, chemistry protocols and uncertainty thresholds still need profile-specific qualification.

The reaction nomenclature also supports the example's (S)-substrate to (R)-product stereochemical direction. This literature check does not validate the example's molecular files or atom mapping; those are runtime requirements.

The new request example demonstrates how to request this assembly and reaction. Its conditions, length range, counts and compute limits are illustrative. No atom-mapped motif, independently qualified profile, raw prior candidate artifacts or new simulation results are supplied. Before comparison, obtain the previous sequence/assembly files and preparation settings, then re-evaluate the reference, prior design and new candidates with matched assembly/site coverage and resource accounting. Prior reported predictions remain predictions.

## Acceptance boundary

Version 2.0 specifies both routes and adds structural/semantic contract tests using explicitly synthetic fixtures. It does not install scientific adapters or demonstrate dimer formation, folding or catalysis. Qualification of a real monomer profile and a real homodimer profile, including missing-partner and broken-interface controls, remains required. Cofactor support, heterodimers and larger assemblies are separate extensions.

## Scientific audit — 26 October 2026

The literature supports the core assembly requirements. The review corrected ambiguities in the specification and its task/configuration contracts:

| Point requiring clarification | Correction |
| --- | --- |
| Reference assembly versus operating conditions | Record concentration and its basis when relevant, together with solution/ligand conditions. A native dimer assignment is not evidence of stability under all conditions. |
| Activity comparison | Declare subunit, complex or active-site normalization; incompatible or unknown bases cannot establish an improvement. |
| Energy versus free-energy barriers | Separate stationary-point/path validation from sampling, estimator and convergence evidence. Neither alone automatically predicts whole-cycle kinetics. |
| Fixed motif and asymmetric states | Preserve catalytic identities while allowing declared motion and chemical-state changes. Evaluate resting partner sites in their own state. |
| Independent prediction and de novo claims | Disclose shared inputs, templates and restraints; record scaffold provenance and reference similarity. Agreement, low sequence identity or a new sequence alone is insufficient evidence of function or a newly generated scaffold. |
| Delivered status and RL rewards | Describe computational qualification as the intended runtime outcome. The reward is a proposed control configuration, not a validated biological objective. |

The supporting primary studies and reporting guidance are listed in [references](references.md#scientific-audit-conditions-kinetics-and-chemistry); assembly and reaction sources appear in the preceding section. These corrections are requirements inferred from the evidence. They do not establish universal predictors, numerical gate thresholds, an executable environment or successful enzyme design. Scientific profile qualification and benchmark execution remain outstanding.
