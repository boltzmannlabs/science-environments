# Denovo Enzyme Design — Research Notes

## Scope and rationale

The [environment specification](../../environments/Denovo-Enzyme-Design/ENVIRONMENT_SPEC.md) separates generation readiness from final reaction-profile qualification. Its scope is soluble, cofactor-free monomers and homodimers; each assembly/reaction combination needs stage-appropriate inputs and capabilities. Mechanism-specific profiles provide catalytic roles, states, evidence rules and supported conditions for the corresponding assessments.

The proposed workflow screens sequence properties and folding before more expensive complex, state and chemistry evaluation. Folding confidence and substrate-pose scores are treated as separate evidence from catalysis. Solubility and aggregation are separate required criteria. An optional reinforcement-learning controller chooses permitted actions while the scientific acceptance rules remain fixed.

These scientific requirements are not measured outcomes. A local fixed execution-and-recovery controller is included, but no qualified reaction profile, trained policy or enzyme benchmark is delivered by this package. Illustrative requests and reward coefficients are not experimentally established settings. Fallback limits are ceilings, not runtime estimates.

## Provenance and repository review

The source is the Denovo Enzyme Design developer handoff dated 22 October 2026. The package reorganizes that specification into task, input/configuration contracts and acceptance requirements. Scientific references and task-format attribution are maintained once in [references.md](references.md).

The target repository was retrieved on 26 October 2026. Its README, CONTRIBUTING.md, LICENSE and PR template were read. The environment and research directories follow the current layout. The [repository license notice](../../LICENSE) explicitly leaves license selection pending; it grants no license. Third-party assets retain their separate access and licensing requirements.

## Open work

- Assign a tracking issue and scientific/software reviewers; use the repository's contribution process for follow-up work.
- Qualify an initial reaction profile and its controls, uncertainty policies and operating domain.
- Select and pin implementations, models and data; verify applicability to newly designed sequences.
- Connect and validate the scientific adapters through the implemented controller; verify actual resource reservation, metering and evaluation.
- Validate the full computational workflow before benchmarking fixed and frozen RL execution under equal resource limits.

The [acceptance plan](../../environments/Denovo-Enzyme-Design/STATUS.md#acceptance) separates completed specification checks from these future implementation and scientific requirements.

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

## Autonomous preparation and review policy

The initial L-DEX attempts repeatedly returned preparation choices to the user and treated missing profile qualification as a reason to stop before reference/tool tests. The revised execution instructions assign preparation, routine choices and evidence review to the agent. The request schema now explicitly represents the resolved execution request. The agent can select documented research assumptions and use bounded local pilot defaults; it must preserve explicit user requirements, resource entitlements and test conditions.

Preparation, exploratory generation and final qualification have distinct admission rules. Scoped tests establish capability and control evidence; a reviewed generation contract permits exploratory candidates before complete chemistry qualification. Development fixtures do not count as successful designs. Final qualification still requires actual checks and current evidence; reviewer opinion cannot override failure or uncertainty.

The persistent controller invokes separate execution/review roles, records actionable recovery decisions and resumes within the same policy. Setup and campaign costs are reported separately without silently multiplying the allowance. Explicit deadlines and existing service limits remain binding. Stage acceptance is distinct from all-rules enzyme qualification. Scientific adapters, profile qualification and end-to-end benchmarks still need evidence. Shared preparation and verified infrastructure should be reused across tool-selection conditions, while candidate outcomes remain separate.

The L-DEX development runs exposed the cost of universal preflight qualification, repeated environment setup and isolated continuation prompts. Policy version 2.0 replaces those admission and recovery rules; it does not turn the historical development structures into qualified enzyme candidates. Its software tests must remain separate from chemistry and protein-quality validation.

## Execution failure diagnosis — 27 October 2026

Inspection of the retained development reports and pinned source identified distinct problems. These findings explain the attempted runs; they do not establish that every version of a method has the same limitations. Source links are in [references](references.md#execution-diagnostics).

| Observed problem | Diagnosis and next technical check |
| --- | --- |
| Repeated requests for routine settings | Instructions assigned decisions to agents, but the controller accepted an unstructured `needs_input` decision. It now requires a permitted reason/item and recorded resolution attempts; routine questions return to internal repair. Whole-run entry through the controller is explicit. |
| Prescribed generator's legacy symmetry run crashed | At the inspected revision, `idx_pdb` is read before assignment in the active legacy symmetry path. Correcting that variable alone did not establish symmetry: retained local trials returned one chain or nonequivalent chains. Validate actual two-copy output, symmetry, motif placement and substrate handling together before enabling this combination. |
| Agent-selected full-assembly trial timed out | The recorded 440-residue attempt used CPU and exceeded its 360-second limit. A later reduced 164-residue assembly took about 828 seconds. This is evidence of inadequate execution configuration for that trial, not evidence that the reaction is undesignable. Test a compatible accelerator and estimate the intended-size workload before submission. |
| Reduced backbone retained residue labels but distorted the site | The reported joint motif CA RMSD is 4.855 Å. Source inspection shows the final sampling branch copies the predicted coordinates without passing through the motif-preserving denoiser; the output writer saves those coordinates and uses input sequence labels. This is a plausible contributor requiring a traced reproduction, not a proven sole cause. Check the atom/residue mapping and motif mask through the final step; an adapter correction must also preserve backbone continuity, clashes and assembly geometry. |

For the next generator integration test, retain the resolved design size and target chemistry, verify the joint assembly/motif/ligand capability, and audit the actual final coordinates before sequence design. A shorter scaffold is not intrinsically invalid in de novo design, but shortening a development fixture does not demonstrate the intended task. Do not repair a geometric score by copying coordinates into a finished model without re-evaluating the resulting structure. In agent-selected mode, use a compatible alternative after capability testing; preserve the exact implementation condition in the prescribed-tool comparison.

Evidence inspected: `LDEX_Environment_Test/tools_specified/integration_session/report.txt`; `agent_selected_tools/integration/scaffold_phase_status.json`; the latter condition's `scaffold_generation_fixture/short_c2_apo/extended_retry/retry_result.json` and `motif_geometry_check.json`. These are external development artifacts, preserved unchanged. Individual generator/sequence fixtures have run. A complete pilot carrying one new candidate through folding, assembly, solubility, aggregation and catalytic chemistry has not run; software control-flow tests cannot fill that evidence gap.

## Bounded scientific integration pilot — 27 October 2026

Local evidence is retained under `LDEX_Environment_Test/fast_pilot_20261027/`, separately from reusable environment code. Two actual full-size apo scaffold jobs produced two 232-residue chains each, followed by tied sequence design. Generation took 290.97 and 294.83 seconds; sequence design took 5.78 and 5.63 seconds. These are individual model runtimes, not total elapsed pilot time. Inputs, output coordinates, sequences, failed calls and pinned src/model hashes remain in that evidence directory.

Tracing the first run confirmed motif backbone movement at the final sampling step; earlier sampled steps retained the motif backbone. Joint nine-residue motif CA RMSD was 3.19 Å. A bounded second run retained local backbone context around the same catalytic identities and reduced that CA RMSD to 0.17 Å. The second design retained 40 reference backbone residues per chain and generated the remaining 192; all nine designated catalytic residue identities survived sequence design. This supports that input adjustment for further testing, not universal applicability or catalytic qualification. Symmetry was imposed by generation and is not independent assembly evidence.

Raw peptide geometry still needs repair and re-evaluation. No independent fold/assembly, aggregation, target-bound catalytic-state or reaction-path calculation has been accepted. A property job for the first design and matched reference was accepted remotely; its results were not recovered. The first design's multimer submission has no recovered job identifier and must not be duplicated until reconciled. A subsequent status attempt failed at the plugin authorization/connectivity check; the available error does not distinguish those causes. The improved second design was not submitted remotely. There are zero qualified enzymes and no supported property improvement claim.

The pilot used assistant-orchestrated scripts plus live harness calls, not a scientifically complete traversal of the execution controller. Its successful local model stages do not establish readiness for a larger full scientific campaign. Preparation/repair/generalization changes remain reusable: per-call deadlines, preservation of remote submission uncertainty, application of delegated routine autonomy, and request-bound generation profiles. Enzyme-specific residue maps, lengths, conditions and outcomes remain case-study evidence. The new request-binding check prevents accidental profile transfer; scientific applicability still requires review.
