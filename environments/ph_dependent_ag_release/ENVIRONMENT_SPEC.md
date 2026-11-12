# Working environment: pH-dependent antigen binding and release

Use this guide to take a pH-dependent binding task from its inputs to actual computational results. The task can ask for binding at one pH and release at another, in either direction. Use the conditions in the task rather than assuming that acidic pH always means release.

Run this as a **model-first, simulation-second workflow**. First generate or prepare candidates, run the relevant prediction and static-scoring stages, and freeze a shortlist. Then use molecular simulations to assess that shortlist and calculate the requested trajectory-based quantities. Choose suitable implementations yourself and use the shared project environment across cases.

The task file is the specific contract. Its sequences, protected regions, conditions, calculation definitions and requested outputs take priority over general defaults here. Use this guide to fill in routine workflow decisions, not to change the task.

## Start with the actual question

Before generating anything or starting a long calculation, write down:

- The target, antibody or binder format, construct boundaries and molecular context.
- The intended binding-favored condition, `pH_on`, and release-favored condition, `pH_off`, or the full requested pH range.
- Whether the job is to analyze fixed sequences, evaluate a fixed panel, redesign a parent, generate new candidates, or calculate binding thermodynamics or kinetics.
- Which quantities are primary objectives and which are supporting quality checks.
- The allowed sequence edits, framework constraints, controls, compute budget and completion criteria.

A fixed-sequence task starts with input/model checks and proceeds to its requested calculations. A fixed-panel task evaluates that complete panel; it does not undergo a design-selection competition. Generate new sequences only when the task asks for design. If the task asks for a local contact probability, complete that calculation rather than expanding it into an unrelated affinity campaign.

The general route is:

`verify inputs → prepare target and scaffold → generate permitted candidates → predict structures and poses → model pH states → score both conditions → run model-based checks → freeze finalists → run matched simulations → validate the computational predictions → rank and report`

Some tasks need an unbound antibody ensemble, some need a complex, and some need both. Keep those contexts explicit throughout the run.

## Candidate selection and simulation planning

Choose the scale of each stage from the task, candidate diversity, uncertainty and available compute. This guide does not prescribe candidate, finalist or replica counts. Record the selection rules and a finite compute/attempt budget before candidate evaluation.

| Stage | What advances |
| --- | --- |
| Initial generation | Generate unique, sequence-valid candidates within the declared budget. Save every attempt, including duplicates, invalid designs and failures. |
| Structure/pose prediction | Select through the declared sequence, constraint and diversity checks. Save actual structure/complex predictions and their quality metrics. |
| Detailed model-based pH assessment | Evaluate eligible candidates using matched on/off conditions, protonation treatment and comparable scoring definitions. |
| Simulation finalists | Select eligible designs using the declared quality, pH-preference, uncertainty and diversity criteria. Record the primary structure/pose and any justified alternate poses for each candidate. |
| Baseline/control | Include the unchanged parent when available and all task-required controls. Remove identical duplicates while retaining their role annotations. |
| Independent production replicas | Follow the task's replica protocol. When unspecified, justify the replication plan using the endpoint, expected variability and available compute; assess its adequacy through uncertainty and convergence checks. |

Do not pad the shortlist with invalid candidates. Keep the eligible set and explain selection or exclusion decisions. Distinguish unique designs, structural systems and simulation jobs. Additional microstates, pH-ladder points, alternative poses, free-partner calculations or sampling windows expand the queue and must be listed explicitly. Pilot and equilibration runs are separate from production.

**Fixed-case tasks retain their complete required panel.** Simulate every system, condition, representative and replica required by the task file. Do not truncate mandatory variants or cluster representatives to fit a design shortlist. Generate new sequences only when the task asks for design.

Freeze `selection_rules.json`, `model_shortlist.csv` and `simulation_queue.json` before production. The queue should identify each candidate/control, primary pose, molecular context, protonation treatment, pH, replica, seed, sampling budget and required endpoint. Set any reserve-candidate policy or follow-up-round budget in advance and keep failed or unfavorable results.

## Phase I — complete the relevant modeling stages first

Work through the stages below before candidate-validation simulations. "Model-first" includes learned predictors, structure builders, geometric calculations and static physics-based scoring. It does not mean loading every available model or repeating several interchangeable predictors without a reason. Use the stages that apply to the task and explain any important omission.

| Stage | Action | Required record |
| --- | --- | --- |
| 1. Define the run | Fix on/off conditions, molecular format, task mode, protected regions, objectives and budget. | Protocol, metric definitions, control list and proposed funnel. |
| 2. Verify identities | Check target and binder sequences, species/isoform, construct boundaries, chains, residue numbering and fixed substitutions. | Input hashes and sequence-to-coordinate maps. |
| 3. Prepare the target | Select the relevant assembly and epitope context; handle missing regions, glycans, waters, cofactors and cropped ends. Predict missing structure when necessary. | Prepared target models, repair log and uncertainty flags. |
| 4. Prepare the scaffold or parent | Establish chain pairing, loop definitions, disulfides, protected residues and canonical framework geometry. | Verified parent/scaffold, editable mask and constraint checks. |
| 5. Generate permitted candidates | For design tasks, generate sequences and, when needed, backbones or recognition-loop conformations. For fixed cases, retain only the supplied panel. | Full candidate sequences, edit traces, seeds and generation history. |
| 6. Apply sequence checks | Remove duplicates and invalid edits. Check loop lengths, cysteine patterns, unexpected motifs and sequence liabilities relevant to the task. | Eligibility decisions with reasons; retain rejected entries. |
| 7. Predict binder structures | Build/refold eligible candidates and assess framework preservation, loop geometry, clashes and local uncertainty. | Candidate-specific structures and actual prediction outputs. |
| 8. Establish complexes | Generate or refine multiple target-binding poses when a verified pose is not supplied. Respect the epitope and full target context. | Pose ensembles, chain/atom maps and the declared primary-pose rule. |
| 9. Evaluate structural plausibility | Assess interface contacts, burial, unsatisfied polar groups, geometry and confidence; check consistency across seeds or starting models where useful. | Actual per-candidate quality metrics and pose-selection decisions. |
| 10. Model protonation | Estimate pKa values and build plausible charge/tautomer microstates for both partners, both conditions and relevant bound/unbound contexts. | Residue-state registry, assumptions and static-estimator outputs. |
| 11. Assess pH preference | Run compatible pH-aware scoring or state-aware design/energy assessment at the on and off conditions. Include the cost or assumed populations of alternative states when the method supports it. | Separate on/off scores, units, definitions, microstate support and predicted contrast. |
| 12. Check the parent and controls | Apply the same model-based calculations to matched controls. Compare on-state retention as well as the desired condition contrast. | Baseline comparisons and uncertainty/coverage flags. |
| 13. Run requested property models | If included in the task, calculate solubility, aggregation propensity, surface charge, sequence humanness or other defined properties. Assess their applicable construct and pH range. | Candidate-specific predictions, scales and applicability limits. |
| 14. Check specificity when requested | Compare declared decoys or related target constructs at matched conditions, with the same scoring and pose policy. | Target/decoy results, panel coverage and uncertainty. |
| 15. Resolve major model disagreement | Inspect competing poses, charge states and inconsistent predictions. Use a declared alternative assessment or sensitivity branch where it adds information. | Disagreement log and explicit unresolved assumptions. |
| 16. Rank and freeze | Apply the predeclared eligibility, on-state, selectivity and diversity rules; select eligible designs according to the task and the declared selection plan. | Frozen shortlist, selection rationale and explicit simulation queue. |

No production MD, constant-pH trajectory sampling or enhanced-dynamics validation belongs in this first phase. Static geometry refinement is allowed; identify it as minimization/refinement. A small software/runtime probe is a capability check, not candidate-validation evidence.

Model outputs are **predictions for the actual candidates**. Save their native outputs, model/weight versions, seeds and input representations. A model's training accuracy or a filtering cutoff is not a result for a generated candidate. If a predictor does not represent pH or protonation, repeating it with a different pH label does not create a pH-dependent calculation.

Static microstate populations are estimates under the chosen assumptions. They are not sampled protonation occupancies or trajectory contact frequencies. Keep those fields separate so Phase II can assess them without silently substituting one for another.

The detailed preparation and modeling guidance follows. Apply it to all eligible candidates at the appropriate funnel stage, then cross the simulation gate.

## Useful approaches to have available

Several computational approaches fit this objective. Pick the one that answers the task and combine approaches when they address different parts of it.

| Approach | What it does | What to watch |
| --- | --- | --- |
| Existing-interface redesign | Changes permitted residues around a known interface and evaluates both pH conditions. | Preserve binding in the on condition while assessing the off condition. A mutation can weaken both. |
| Protonation-aware local design | Changes the neighborhood around a titratable site to favor a particular charge state or interaction network. | A learned state-preference score is a design signal; it is not automatically a pKa or physical binding free energy. |
| De novo interface generation | Builds candidate recognition loops or binders around an allowed target surface, then designs and checks their sequences. | Use a generator appropriate to the requested molecular format. A generic miniprotein scaffold is not a conventional antibody. |
| Conformation and hydration analysis | Samples how protonation changes loop geometry, domain orientation, contacts and solvent access. | Keep local structural and hydration results distinct from whole-complex affinity. |
| Folding-coupled switching | Uses a buried charge or hydrogen-bond network to change the binder's conformational stability with pH. | Establish whether the task permits this mechanism. Keep it distinct from an interface switch with an intact fold. |
| Protonation-linked binding calculations | Includes the protonation ensembles of the complex and separated partners in a binding calculation. | The bound and unbound states may have different protonation preferences. Using one assignment everywhere can miss the effect being studied. |

Histidine is one possible handle, not a required ingredient in every design. Acidic residues, altered hydrogen-bond networks, buried charges, water access and heavy/light-chain packing can also matter. Include the target's titratable groups when they affect the interface.

## 1. Get the inputs straight

Use supplied input-only files first. Public structural and sequence records can fill gaps without consulting outcome material. Check the species, isoform, mutations, tags, linkers, residue coverage, assembly and chain identities before using a record.

For antibody systems, establish the heavy/light pairing, numbering convention, insertion codes, variable-domain boundaries and recognition-loop definitions. Distinguish full antibody, Fab, Fv, scFv and VHH constructs. A fragment calculation does not automatically describe the geometry or avidity of a full antibody.

Create a residue map that connects full polymer sequence positions, antibody numbering, coordinate labels and simulation indices. Add an atom map when an energy or geometric metric uses a specific atom selection. Verify the starting residue before applying any fixed substitution.

Preserve the input coordinates and sequences. Save hashes, structural identifiers, retrieval dates and the reason for selecting a particular assembly. If there are multiple eligible starting structures, define their inclusion rule before scoring them.

If an essential sequence, fixed edit map or construct definition is missing, request an input-only package or mark that part as needing input. Do not invent a sequence or quietly replace the intended system with a convenient one.

## 2. Prepare the target and antibody

For the target, check that the selected domain contains the intended epitope and enough surrounding structure to support it. Look for missing loops, alternate conformations, unresolved side chains, oligomer contacts, glycans, cofactors, metals and membrane proximity. Decide which are relevant to the modeled interface and record the treatment of each.

Avoid introducing artificial charged ends close to the interface when cropping a construct. Preserve the intended terminal chemistry, disulfides and covalent connectivity. Keep plausible structural waters when they may bridge contacts or control a buried site's hydration. If waters are removed or rebuilt, log that choice.

For the antibody, check sequence-to-structure agreement, chain pairing, loop geometry, disulfides, unusual residues and heavy/light-domain packing. Repair only what is needed. If coordinates must be predicted, preserve multiple plausible starting models where the uncertainty matters and keep model provenance separate from deposited coordinates.

A change to the binder's sequence or to a nearby target residue changes the local environment. Revisit its protonation and preparation rather than copying the parent's assignments without checking them.

Use compatible physical parameters for proteins, solvent, ions and any retained nonprotein components. Verify charge, residue templates, atom names, bond connectivity and exclusions before simulation. An unsupported component needs a justified parameterization or an explicitly limited model.

## 3. Establish pH states during modeling, then sample them during validation

In Phase I, use static pKa/protonation predictions and explicitly defined state models. Actual constant-pH dynamics and sampled state populations belong to Phase II. The overview below explains which approach can supply which endpoint.

A pH label in a filename does not change a simulation. State how pH enters the calculation and which residues or chemical groups can respond.

Choose among these levels according to the endpoint:

- **Static protonation screening:** estimate pKa values or propose plausible charge and tautomer assignments. Useful for preparing states and narrowing a search.
- **Several fixed microstates:** evaluate explicitly defined alternatives and their structural consequences. Use justified state populations if combining them into an equilibrium estimate.
- **Constant-pH sampling:** allow protonation to change with the environment and conformation. Needed when the task asks for a sampled protonation population or its coupling to structural dynamics.
- **An imposed charge-state contrast:** test a defined mechanistic perturbation. Label it as such; it does not establish that the imposed transition occurs at the nominal pH.

Check histidine tautomers as well as its neutral and positively charged forms. Consider acidic and basic side chains, free termini and other relevant titratable groups supported by the chosen method. Preserve disulfide chemistry; a disulfide cysteine is not a freely titrating thiol.

For constant-pH sampling, verify the exact implementation, supported residues, reference compounds, force-field corrections, solvent treatment and charge-compensation approach. A standard dynamics executable is not automatically a constant-pH implementation. Methods may require particular correction potentials, solvent relaxation steps, buffer particles or a specific treatment of long-range electrostatics.

Sampling and parameterization both matter. A residue trapped in one rotamer may also appear trapped in one protonation state. Check those degrees of freedom together. Record how intermediate titration states are treated instead of forcing them into a binary population after the fact.

Use a pH ladder when a transition curve or pKa is requested. Two endpoint calculations can establish an endpoint contrast, but not a well-resolved transition location or slope. A single-site titration fit is an assumption; coupled sites may need a coupled-state description.

## 4. Generate candidates when design is requested

Start from the parent's computed baseline under the declared protocol. Decide whether the design will change an existing interface, an internal network, a domain interface or an entirely new recognition surface.

Define an editable residue mask and protected positions. Respect the requested framework sequence, loop lengths, disulfides, construct boundaries and target epitope. For a fixed-framework task, preserve the canonical framework and verify it after a permitted rigid-body alignment. Keep canonical design structures separate from any relaxed assessment copies.

Generate a declared candidate budget using multiple seeds or starting conformations when useful. For each candidate, save the full sequence, parent relationship, edit trace, structure and generation settings. Deduplicate sequences and retain a record of rejected candidates.

If the generator does not represent pH, use it to propose geometry and sequence, then perform explicit paired-state assessment. If it does represent charge states, record what those states mean and how they map to the later physical model. In either case, evaluate the on and off conditions separately.

Balance the intended pH contrast with on-state interaction quality and the structural constraints in the task. Avoid selecting a candidate merely because it is poor in the off condition. The same change may have destroyed the on-state interface or the binder fold.

Keep a diverse shortlist across sequence, pose and proposed mechanism. Use the declared model-stage funnel: inexpensive validity checks, structure/pose prediction, then detailed static pH assessment. Candidate-validation simulations start only after the finalist gate. Freeze the filtering and ranking rules before inspecting the final outcomes.

## 5. Establish plausible complex poses

Use an available, identity-matched complex when the task supplies one. Otherwise generate and refine multiple plausible poses, respecting any allowed epitope or structural constraints. Keep alternative starting poses distinguishable.

Check chain assignment, steric clashes, buried unsatisfied polar groups, interface contacts, accessible surface burial and compatibility with the full target context. Check whether a crop, omitted glycan or missing neighboring chain has created an artificial binding surface.

Structure confidence and predicted interface confidence can help select which poses to investigate. Record their actual per-design outputs, input representation and score scale. A cutoff or a model's general accuracy statistic is not a candidate-specific result. Structure confidence alone does not establish a pH switch.

If a valid reference complex is supplied for the assessment, calculate interface or ligand RMSD and native-contact recovery with an explicit alignment and chain mapping. Without such a reference, report pose consistency and computational interface assessments rather than inventing a native-structure accuracy.

## Simulation gate — freeze the model-stage decisions

Before creating production jobs, confirm that:

- Each selected sequence and structure satisfies the task's constraints and has an explicit primary-pose or starting-model choice.
- The on/off conditions, molecular context, protonation treatment and requested simulation observables are defined.
- The baseline and required controls are included, and the candidate count is consistent with the frozen funnel or fixed-case requirements.
- Every finalist has its model predictions saved, including unfavorable values, uncertainty and any unresolved assumptions.
- A compatible physical model and valid analysis route exist for the requested simulation endpoints.
- The production queue, sampling/extension policy and resource budget are recorded.

An unresolved noncritical prediction can be tested during validation if its interpretation is explicit. Missing identity, unsupported chemistry or an undefined mandatory endpoint needs resolution before the affected job can count as a valid assessment.

Do not overwrite the model ranking after seeing simulation results. Keep model-stage selection and simulation-stage findings in separate columns. A candidate with an unfavorable simulation result remains part of the run history; a technical repair or a later design round gets its own recorded decision.

## Phase II — use simulations to assess the finalists

Run simulations on the frozen finalists, matched controls or the complete fixed-case panel. The following steps assess the model-based predictions and produce the task's required dynamic observables. Simulations may support, weaken or leave a prediction unresolved; none of those outcomes is predetermined.

1. **Finalize the physical systems.** Check parameters, solvent, ions, bonds, restraints, atom selections and both pH branches.
2. **Minimize and equilibrate.** Follow a declared preparation protocol and verify that the starting conditions are physically interpretable.
3. **Check the runtime path.** Run a short pilot and verify trajectory, energy and state outputs before production.
4. **Sample protonation when required.** Use an appropriate constant-pH method for populations or protonation/conformation coupling. Do not replace it with a permanently charged residue.
5. **Run production replicas.** Use the task's duration and replica protocol, or a justified, predeclared plan when unspecified. Assess replication and sampling through endpoint-specific uncertainty and convergence checks.
6. **Add enhanced sampling when justified.** Use it for the relevant slow coordinate or an explicit task requirement, preserving the information needed for valid analysis.
7. **Calculate the frozen endpoints.** Evaluate the same selected residues, contacts, energies, coordinates or thermodynamic quantities across conditions.
8. **Check computational reliability.** Inspect observable-specific sampling, replica consistency, estimator support and uncertainty. Apply the predeclared extension rule if needed.
9. **Compare model predictions with simulation findings.** Keep the two evidence stages distinct and report agreement, disagreement and unresolved cases.
10. **Finalize the shortlist and result bundle.** Rank by the task's criteria, preserve every evaluated finalist/control and freeze the outputs for later independent comparison.

Record additional validation branches explicitly. For example, unbound partners, alternate poses, extra charge states, separation windows or a pH ladder are extra jobs, not additional unique designed finalists. Use them when the task's endpoint requires them rather than automatically running every possible branch.

## 6. Build matched physical systems

Make each pH pair comparable. Use common eligible starting coordinates where practical and the same construct, physical parameters, solvent model, ionic conditions, temperature, pressure, restraints and preparation policy, except for the variable being tested.

Keep initial titration assignments separate from the sampled or fixed states used in production. Record any pH used during preparation independently from the production condition. Do not relabel one as the other.

When a binding calculation requires the complex and separated partners, prepare all states under a consistent thermodynamic definition. Allow for different protonation preferences after separation. Keep conformational relaxation, restraint and standard-state contributions explicit where they are required.

For local-energy tasks, freeze exactly what is interacting: the whole residue or a side-chain group, all solvent or a defined local water region, the selected energy components and the treatment of long-range interactions. Those choices change the numerical quantity.

Confirm the box, boundary conditions, solvent clearance, ion treatment and electrostatic settings are suitable for the actual system. Keep periodic images from creating unintended protein contacts. Record any net-charge handling or finite-size correction needed by the calculation.

## 7. Run a pilot, then production

Before a long run, perform a small end-to-end capability check: preparation, parameter loading, minimization, dynamics or titration, trajectory writing and the requested analysis. Check a few frames manually against the saved atom and residue selections.

Look at energy behavior, temperature and pressure, density where applicable, restraints, bond integrity, clashes and protonation records. Verify that required states are actually represented and that the chosen hardware path runs correctly. The pilot is a setup check, not the final scientific result.

Use the sampling budget in the task. If it leaves the budget open, declare an initial plan and observable-based extension rules. Use independent seeds and additional starting models when appropriate. There is no universal simulation duration that guarantees all antibody loops, water networks and titration states are sampled.

Choose enhanced sampling for a stated reason: slow loop rearrangement, trapped charge/conformation states, poor overlap or an explicit task requirement. Save the bias and exchange histories needed for analysis. Estimate equilibrium populations through a valid estimator or reweighting method; biased frame counts are not automatically equilibrium probabilities.

When starting unbiased trajectories from selected representatives, account for how those representatives were selected. Equal trajectory lengths from different clusters do not automatically reproduce equilibrium cluster populations.

For exchange methods, inspect exchange behavior and movement across the relevant states. For free-energy windows, inspect overlap and sampling within each window. For accelerated dynamics, retain the quantities needed to check reweighting support. A smooth-looking curve is not enough by itself.

## 8. Calculate the task's actual outputs

Use the same analysis definitions across matched systems. Correct periodic imaging, align appropriately and keep the analyzed frame range and stride explicit. Save frame-level quantities where practical so each summary can be checked.

| Quantity | What to save | What it means |
| --- | --- | --- |
| Protonation probability | Charge/tautomer history, retained samples, transitions, effective sample size and uncertainty. | A sampled state population under the declared method and condition. |
| Contacts and hydrogen bonds | Residue/atom pairs, geometric rules, frame indicators, weights and denominators. | A defined interaction frequency, with bounds kept distinct from point estimates. |
| Local hydration | Water selections, occupancies or densities, selection geometry and time series. | Solvent access around the selected region. |
| Local interaction energy | Electrostatic, van der Waals and total terms, selections, units and uncertainty. | The specified local nonbonded quantity, not whole-complex binding free energy. |
| RMSD and RMSF | Alignment, reference, atom set, residue map and per-frame or per-residue values. | Structural deviation or fluctuation under that definition. |
| Domain orientation | Domain-frame definition, handedness, angle conventions, distance definition and distributions. | Relative domain geometry; account for angular periodicity. |
| Conformational clusters | Features, alignment, algorithm, cutoff, frame count, assignments and representatives. | Method- and sampling-dependent structural grouping. |
| Relative conformational PMF | Coordinates, grid, probability, reweighting support, units and zero convention. | Relative free energy along the sampled coordinates, not automatically binding free energy. |
| Binding-energy or affinity estimate | Full method definition, states, corrections, units and statistical uncertainty. | Only the thermodynamic quantity that the calculation actually estimates. |

Apply each metric only to a construct that actually contains the required regions. A single-domain binder has no heavy/light-domain orientation; mark that quantity as not applicable rather than creating an artificial comparison.

For weighted contact probabilities, keep the estimator explicit: `sum(weight × indicator) / sum(weight)`. Report percentages or fractions consistently. A difference in percentages is a percentage-point change unless a ratio is explicitly calculated.

For a conformational PMF, record the probability estimator, binning, temperature and normalization. Each separately normalized surface has its own arbitrary zero. Empty or unsupported bins remain unsupported; do not fill them with invented finite energies.

For clustering, report how the count changes with analyzed sampling. More frames, a tighter cutoff or a different feature set can create more clusters without implying a stronger biological effect. Use a conditional comparison when the required analysis definition is missing.

## 9. Use binding thermodynamics or kinetics only when needed

An interface score is useful for ranking under one scoring protocol. An end-point continuum-solvent calculation is a more detailed energy estimate with its own approximations. A binding free-energy calculation needs a defined thermodynamic path, adequate sampling and the relevant corrections. Keep those categories distinguishable in the output.

For pH-dependent binding free energies, include the proton reservoir and the bound/unbound protonation ensembles consistently. A calculation of the complex alone, or a local residue-water energy, does not provide the complete binding quantity. Consider site coupling instead of automatically treating every residue as independent. Combine microstates through a valid statistical-mechanical treatment of their populations and proton chemical potential; an arithmetic average of their binding-energy scores is not an ensemble binding free energy.

If the task calls for a free-energy separation profile, define the bound state, separation coordinate, orientation treatment, restraints, integration limits and standard state. A barrier or a PMF minimum is not automatically a standard binding free energy.

Use alchemical mutation calculations only with supported topology changes, sampling and a consistent treatment of altered charge/protonation. Check overlap, thermodynamic-cycle consistency and relevant corrections. Preserve the baseline and mutation state definitions.

Calculate an off-rate or residence time only through a method that supports a kinetic interpretation and provides the required physical-time treatment and event statistics. Ordinary biased escape times and forced pulling work are different observables. A trajectory that stays bound supplies a sampled observation, not a measured zero off-rate.

## 10. Validate the calculation computationally

Check numerical reliability at several levels:

1. **Input validity:** sequence/structure identity, residue maps, construct boundaries, charge assignments and permitted edits agree with the task.
2. **Implementation validity:** the selected implementation supports the chemistry and endpoint. Check units, selections, sign conventions and a small known or independently calculated example where useful.
3. **Structural validity:** the intended fold, connectivity and molecular context remain interpretable. Separate local rearrangements from large-scale fold disruption.
4. **Sampling quality:** independent runs, time blocks, relevant state transitions and estimator support give a consistent picture. Examine the requested observable rather than relying only on backbone RMSD.
5. **Method sensitivity:** for important unresolved choices, use a predeclared sensitivity branch or an independent calculation where practical. Keep alternatives separate instead of averaging incompatible definitions.

Report trajectory spread, standard error and confidence intervals as different quantities. Account for autocorrelation and the number of independent runs; saved frames are not automatically independent observations. A narrow statistical interval does not remove uncertainty from the physical model or starting pose.

Useful controls include the unchanged parent, identical-condition repeats, common starting poses and a declared charge-state perturbation. Add a fixed control sequence, reversed condition or decoy only when it helps answer the task. Keep the same analysis and sampling policy for the controls.

For a proposed pH switch, inspect both the desired condition contrast and the on-state behavior. Distinguish interface rearrangement, folding-coupled response, loss of the intended fold and inadequate sampling. State which mechanism the computed evidence supports.

## 11. Compare conditions and select candidates

Define the direction before ranking. For a consistent lower-is-better binding score, `score_off − score_on` is positive when the score favors the on condition. Call it a score contrast unless the underlying method establishes a binding free-energy contrast.

For a properly defined binding free energy, use `ΔΔG_switch = ΔG_bind(off) − ΔG_bind(on)`. Interpret it alongside the on-state result and uncertainty. Compare a variant with its matched parent using the same definition at both conditions.

Only convert a thermodynamic binding free-energy difference into an affinity ratio when the states, temperature, standard-state treatment and equilibrium definition justify that conversion. Do not exponentiate arbitrary docking or learned-model scores to produce a dissociation constant.

Before simulation, rank eligible candidates using the frozen model-based objectives and constraints. After simulation, apply the declared final decision rule using the simulation results and keep both rankings visible. A Pareto shortlist can be more useful than collapsing pH contrast, on-state quality, fold integrity and uncertainty into an arbitrary weighted sum. Preserve individual metrics and rejected candidates either way.

When design iterations are allowed, choose the next changes from the computed mechanism and record the reasoning. Each new sequence goes back through Phase I before a later validation round; do not quietly change a frozen finalist during its simulation assessment. Reassess affected protonation states and both conditions. Keep a complete design history and stop at the declared budget or supported completion rule; do not keep changing definitions until a preferred result appears.

Aggregation, solubility, surface charge, sequence liabilities or humanness can be additional computational objectives when requested. Identify their definitions and applicable molecular scope. A general developability prediction is not a replacement for a pH-dependent binding calculation.

## Model predictions and simulation validation have different roles

Keep the evidence stage attached to every result:

| Model-stage result | Possible simulation assessment | Scope of the conclusion |
| --- | --- | --- |
| Predicted binder fold or complex pose | Framework/interface stability, pose drift and contact persistence under the selected conditions. | Stability over sampled trajectories supports structural consistency; it is not the same as a native-pose accuracy measurement. |
| Static protonation or pKa estimate | Sampled state probabilities, titration behavior and state/conformation coupling. | Report static and sampled estimates separately, including unsupported or poorly sampled states. |
| Predicted pH-dependent interaction contrast | Matched pH-specific interaction ensembles and the requested local or binding-energy calculation. | A local interaction change assesses its proposed mechanism; a binding-affinity claim requires a binding quantity. |
| Predicted hydration/charge-network change | Water occupancy, hydrogen-bond probabilities and local interaction-energy distributions. | These are defined mechanistic observables, not interchangeable with a dissociation constant. |
| Predicted on-state retention | On-state structural, interface and task-defined energetic assessments relative to the baseline. | Evaluate on-state behavior separately from off-state weakening. |
| Predicted release or unbinding pathway | A supported separation/free-energy or kinetic protocol, when requested. | Contact loss, pulling work, a PMF barrier and an off-rate remain different outputs. |

Record a per-candidate computational outcome such as `SUPPORTED`, `NOT_SUPPORTED` or `INCONCLUSIVE` for the requested hypothesis, with its metric-based reason. Keep that scientific outcome separate from whether the job ran successfully. A successful executable run does not by itself validate a pH-switch prediction.

Keep the already-required simulation checks and uncertainty assessment even when the model rank is strong. Conversely, do not invent a separate binding-affinity objective when the task only asks to calculate a contact, orientation or local hydration quantity.

## 12. Keep execution practical

Use one shared project environment across molecule types and cases. Reuse compatible installations and record explicit paths for external executables. Verify required versions, model weights, optional components and open-source or eligible academic/noncommercial access before relying on them. Public source code does not guarantee that every dependency or weight file has the same terms.

Check the actual CPU, GPU memory, driver, available storage and implementation support. Distribute independent jobs where supported; multiple GPUs do not automatically accelerate every calculation. Keep changes to the shared environment recorded and avoid silently replacing dependencies used by an active run.

Run long jobs in a persistent session with logs and checkpoints. Record how to reconnect, resume a run and identify its current stage. Save enough metadata to distinguish new production from a restart and avoid counting duplicated frames after recovery.

Fix routine failures and continue independent work. If a required capability is unavailable, identify a scientifically valid alternative and test it. If the alternative changes the endpoint, record that change and keep its result separate. An unsupported mandatory calculation remains unexecuted rather than receiving a placeholder result.

## 13. Save a complete result bundle

Use the output directory specified by the task. Keep generated artifacts separate from task definitions and immutable inputs.

```text
<run_id>/
  inputs/
  prepared/
  candidates/          # when generation is requested
  model_outputs/
  selection/
  simulations/
  analysis/
  figures/
  logs/
  input_manifest.json
  protocol.json
  run_manifest.json
  metrics.json
  model_predictions.csv
  model_shortlist.csv
  selection_rules.json
  simulation_queue.json
  validation_summary.csv
  summary.csv
  report.md
```

The input manifest records identities, hashes, construct details and residue/atom maps. The protocol records conditions, physical parameters, sampling plans and metric definitions. The run manifest records the actual implementations, versions, commands, seeds, devices, durations, restarts and artifact paths.

For every metric, retain the system/candidate, condition, molecular context, value, units, estimator, atom selection, sample count, weighting, uncertainty type, raw-artifact path and calculation status. Add `evidence_stage` such as `MODEL_PREDICTION`, `STATIC_ASSESSMENT` or `SIMULATION_RESULT`, and preserve the model/implementation version that produced it. Use a missing value with a reason for an unexecuted or undefined quantity; do not use zero as a placeholder.

The report should say what ran, the number of unique candidates at every gate, the number of finalist structures versus simulation jobs, which computations completed, what the numerical results show, how reliable they are, and which definitions or inputs remain unresolved. Include a model-prediction-versus-simulation table for each evaluated finalist or fixed-case system. Retain unfavorable and inconclusive outcomes. Keep method-dependent diagnostics separate from directly comparable primary outputs.

## 14. Finish cleanly and keep the run independent

For the default design workflow, completion includes the model stages and the required finalist simulations. Model-stage completion alone is screening completion, not simulation validation. A fixed-case task is complete when its own mandatory calculations have run and its numerical outputs and execution evidence are saved. Preparation alone, a pilot, or an unexecuted script is not completed production. Use the task's completion labels and give a specific reason for any incomplete endpoint.

For blind execution, use this guide, the task, supplied input-only records, authoritative structure/sequence data and implementation documentation. Do not search for case papers, supplements, stored answers, earlier outcome tables or prior conversation logs. Keep file discovery inside the permitted task, input, software and run-output locations.

Freeze the final results and their hashes before a separate evaluator reads comparison material. Definitions and input choices stay fixed during that later comparison. If two quantities are not comparable, report the mismatch rather than modifying the completed run to fit an answer.

The final deliverable is an auditable computational result: the requested quantities, the physical and numerical definitions behind them, and the files needed to rerun the calculation.
