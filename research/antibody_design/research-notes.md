# Monoclonal antibody design: evidence and implications for this environment

**Research scope:** reference-guided monoclonal design, target-only antibody discovery, and bispecific design. **Current release:** five benchmarked monoclonal task specifications with matching references, plus two standalone fixed-framework VHH prompts. See the [environment specification](../../environments/antibody_design/ENVIRONMENT_SPEC.md) and [current status](../../environments/antibody_design/status.md). The research notes below retain historical design context; references to earlier task contracts and validation describe the retired implementation.


**DENV task knowledge cutoff:** 2024-09-01  
**Environment-design review updated:** 2026-10-27  
**Scope:** Antibody sequence/structure representation, antigen-interface assessment, early developability, the supplied DENV-2 DV87.1 case, and a broader task taxonomy for an Agent-Scientist antibody environment. Post-2024 sources below inform future environment design only; they do not change the frozen cutoff or eligibility of methods in `denv_antibody_001`.

## Findings to encode

### 1. Make antibody identity and numbering explicit

A monoclonal antibody is not a generic single-chain protein. This benchmark concerns a paired heavy chain and light chain. A sequence record must declare whether it contains variable domains, Fab chains, or full-length immunoglobulin chains. Keep chain pairing stable across prediction, scoring, FASTA export, and candidate lineage. A VH-only structure or an independently predicted VL is not evidence for a correctly assembled antibody.

Framework and CDR claims depend on the numbering convention and sequence/structure mapping. IMGT numbering defines standardized variable-domain framework and CDR regions and supports comparisons across chain types and structures ([Lefranc et al., 2003](https://pubmed.ncbi.nlm.nih.gov/12477501/)). The task therefore requires the numbering scheme, per-chain annotation, insertion handling, and explicit allowed edit mask. “Preserve framework” must be checked against that mapping; raw sequence positions alone are insufficient.

### 2. Treat a predicted complex as a hypothesis

Antibody–antigen complex prediction remains a difficult, distinct problem from folding each partner. The pre-cutoff antibody docking benchmark work describes broad cases and difficulty variation ([Zhao et al., 2024](https://pubmed.ncbi.nlm.nih.gov/38385879/)); a 2023 assessment documents failures of sequence-only complex prediction on many antibody–antigen examples ([Jalali et al., 2023](https://pubmed.ncbi.nlm.nih.gov/37782047/)). Interface confidence, local chain confidence, and physical binding affinity are different evidence types. Require antigen-to-antibody scope, the selected complex, confidence companions, chain direction, and the exact method version. A high score alone does not prove that an interface is correct.

For dengue EDIII, model construct identity and structural context matter. Work on dengue DIII reports conformational exchange and antibody epitopes that may be partly inaccessible on the virion surface, depending on E-protein packing ([Lim et al., 2016](https://pubmed.ncbi.nlm.nih.gov/26637461/)). Thus an isolated-domain model can support local compatibility while leaving native-particle accessibility unresolved. The input contract now requires construct, chain, sequence, residue-map, and binding-region provenance; an isolated EDIII result must not be described as virion binding.

### 3. Keep binding, neutralization, and safety claims separate

The supplied case is centered on DENV-2 envelope EDIII and the starting antibody DV87.1. Historical EDIII-focused work provides biological rationale for studying this region ([Crill and Roehrig, 2001](https://pubmed.ncbi.nlm.nih.gov/11462053/)); it does not validate any sequence in this benchmark. The case files report predicted energies/confidence and ELISA binding entries. These are not a measured equilibrium Kd, a viral neutralization concentration, or clinical effectiveness.

The task now records each endpoint by name and evidence source. The ELISA deck's repeated non-reference clone label does not establish which sequence or computational candidate produced each entry. The label-to-sequence relation remains unresolved and must not be guessed. No wet-lab value is used as a computational rule threshold or agent-visible answer.

Dengue antibody function also has a serotype and particle-context boundary. Prior monoclonal-antibody work discusses neutralization and antibody-dependent enhancement as separate outcomes ([Dejnirattisai et al., 2015](https://pubmed.ncbi.nlm.nih.gov/25501631/)). This environment may report predicted DENV-2 EDIII binding; it cannot infer ADE risk, cross-serotype breadth, or clinical protection from interface confidence or an ELISA EC50. Those are outside the computational bundle's demonstrated evidence.

### 4. Treat developability flags as risk indicators

Antibody developability includes conformational, chemical, colloidal, and interaction-related liabilities; it is not captured by a single “stability” number ([Mieczkowski et al., 2023](https://pubmed.ncbi.nlm.nih.gov/36880643/)). Sequence/structure predictors can flag risks, but do not measure expression titer, aggregation under formulation conditions, or clinical immunogenicity.

Antibody-focused computational guidelines examine CDR length, surface hydrophobicity, CDR charge, and heavy/light surface-charge asymmetry ([Raybould et al., 2019](https://pubmed.ncbi.nlm.nih.gov/30765520/)). These are useful candidate-level descriptors to include when qualified; they are not universal acceptance thresholds. A 2023 review found that model generalization and consistency with experimental developability assessments remain challenges ([Murray et al., 2023](https://pubmed.ncbi.nlm.nih.gov/37072706/)). Consequently, this package requires metric definitions, scale, calibration/applicability, uncertainty, and the supporting artifact. It prohibits interpreting an in-silico pass as experimental monomericity, solubility, expression, or safety.

## Audit of the supplied dengue case files

The supplied documents describe an optimization study of DV87.1 against DENV-2 EDIII, with CDR-focused variation and framework preservation. They name StabDDG, Boltz/Boltz2, PRODIGY, and ipSAE. They also describe docking, aggregation/solubility/expression/immunogenicity assessment, and molecular dynamics, but do not consistently name a concrete implementation for each of those capabilities. Generic references to diffusion, flow-based optimization, reinforcement learning, and hallucination do not provide a runnable implementation contract.

The reported evidence is not a reproducible run bundle. The presentation describes a 200-to-141-to-nine screening funnel, while the case narrative describes 200-to-nine. The final candidate table and narrative give different views of confidence and developability; the narrative highlights several candidates for dynamic stability, while the presentation says five had superior dynamics. The wet-lab presentation repeats one non-reference clone label across multiple EC50 entries and does not expose an unambiguous mapping to computational candidate IDs. These discrepancies are represented as **unresolved provenance**, not reconciled by inference.

The task now asks for full paired sequences, antigen and antibody constructs, coordinates, explicit chain mapping, numbering, immutable method identity, raw per-candidate outputs, sequence-to-evidence hashes, and the experimental sample crosswalk before candidate-specific conclusions can be reproduced. The package does not adopt historical reported score ranges or shortlist membership as thresholds.

## Changes applied to the environment

- Added a paired-chain antibody input contract and result checks tailored to monoclonal-antibody identity and evaluation.
- Required explicit antibody format, heavy/light identifiers, numbering convention, framework annotations, antigen construct, and residue mapping.
- Added antigen–antibody interface scope checks so internal VH–VL confidence cannot satisfy target-binding evidence.
- Added sequence-hash linkage to every metric, paired FASTA/CSV consistency, and reference exclusion from the designed shortlist.
- Added distinct task variants with shared scientific requirements: one names only the methods found in the dengue documentation; the other is method-neutral.
- Preserved the 2024-09-01 cutoff as a protocol gate. A method's mention in a retrospective document is not proof of release-date eligibility.
- Classified missing sequence/structure data, tool identities, candidate mapping, and thresholds as concrete readiness gaps.

## Broader monoclonal-antibody design workflow

The DENV task is one target-specific instance. A reusable monoclonal-antibody environment also needs to distinguish the **design mode** and the level of biological context available:

1. **Reference-guided optimization:** requires a verified heavy/light pair and a comparable baseline. A known target-bound structure enables constrained CDR redesign; a sequence-only reference does not establish the starting pose.
2. **Target-only discovery:** requires a defined antigen construct, intended molecular format, framework-selection policy, epitope/search policy, and controls. Without a supplied reference, the task cannot claim affinity improvement or reference lineage.
3. **Bispecific design:** requires two target profiles, arm assignments, molecular architecture, valency, chain assembly, Fc behavior, and a rationale for simultaneous engagement. A pair of individually plausible arms does not establish a functional whole molecule.
4. **Evidence-only assessment:** some benchmark tasks assess whether experimental or model-derived data support a mechanism or advancement decision. These tasks must not silently become sequence-generation tasks; they require the underlying data and the decision rule.

Published computational pipelines occupy different parts of this workflow. RosettaAntibodyDesign (RAbD) is a structure-based framework for sampling CDR structures and sequences in the context of an existing antibody–antigen complex; its paper reports extensive computational benchmarking and experimental testing of selected redesigns ([Adolf-Bryfogle et al., 2018](https://doi.org/10.1371/journal.pcbi.1006112)). DiffAb conditions joint CDR sequence/backbone design on an antibody–antigen complex, so its setup presumes a structural target context rather than a target sequence alone ([Luo et al., NeurIPS 2022](https://papers.neurips.cc/paper_files/paper/2022/file/3fa7d76a0dc1179f1e98d1bc62403756-Paper-Conference.pdf)). ImmuneBuilder-family work predicts antibody variable-domain structures and per-residue uncertainty; antibody-only structure prediction is a different task from predicting the antibody–target pose ([Abanades et al., 2023](https://doi.org/10.1038/s42003-023-04927-7)). The ABAG-docking benchmark provides nonredundant antibody–antigen complexes for evaluating docking approaches, underscoring that complex prediction needs its own test set and difficulty-aware reporting ([Zhao et al., 2024](https://pubmed.ncbi.nlm.nih.gov/38385879/)).

These papers support a **pipeline family**, not one universal end-to-end method: target/epitope preparation; paired-antibody or scaffold definition; CDR sequence/structure generation or constrained redesign; antibody structure assessment; complex-pose assessment; specificity and function assessment; developability screening; and experimental validation. Target-only design and redesign from a known complex must be evaluated separately. Computational sequence recovery, structural similarity, energy, or confidence metrics are not experimental discovery rates.

## Additional requirements from the broader evidence

### Reference, target, and objective

- Record whether the task is de novo discovery, reference-guided optimization, affinity maturation, humanization, or developability redesign. The reference field is mandatory for reference-derived claims and explicitly null for a target-only task.
- Store complete paired VH/VL sequences, antibody format, numbering convention, chain annotations, origin, isotype/Fc design, and reference assay evidence. Record the full target sequence separately from each assay construct and structure.
- Record target isoform/strain, construct boundaries, oligomeric partners, cell-surface or soluble presentation, membrane orientation when relevant, known post-translational modifications, glycan state where known, and residue-number mapping. Epitope accessibility can change with glycosylation and antigen conformation; the MUC1 glycopeptide study demonstrates that glycosylation may alter the recognized antigen conformation rather than simply provide direct antibody contacts ([Movahedin et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28025250/)).
- Require a mechanism-of-action statement and link it to the relevant functional assay. Binding-only, blockade, agonism, neutralization, depletion, and internalization are different objectives. A 2022 CD27 study showed that epitope location and Fc engagement can affect agonist activity ([Heckel et al., 2022](https://pubmed.ncbi.nlm.nih.gov/35288635/)).

### Computational evidence and validation

- Separate antibody-domain fold confidence, CDR-loop uncertainty, antigen–antibody pose confidence, interface geometry, predicted interaction energy, and measured affinity. Complex-prediction benchmarks show why confidence scores should be treated as evidence with limitations, not as a binding result.
- Use a target-specific epitope and paratope map, residue-level contacts, steric accessibility, and alternative target conformations when the biological target is flexible, oligomeric, glycosylated, or membrane-anchored.
- Freeze held-out splits by antigen/epitope and sequence/structure similarity. Prevent near-duplicate complexes, paired sequences, or target-family leakage from making evaluation appear stronger than generalization.
- Use orthogonal evidence where possible. Keep method, model/version, input chain order, residue map, settings, confidence companions, raw files, and hashes with each candidate's sequence-bound result.

### Binding, specificity, and function

- Keep equilibrium affinity (`Kd`), kinetic rates (`kon`, `koff`), avidity-dependent binding, ELISA concentration-response, cell binding, and mechanism-specific potency separate. A surface-based binding assay can be sensitive to immobilization and mass-transport conditions; high-affinity measurements may need an orthogonal solution-phase method ([Estep et al., 2013](https://pubmed.ncbi.nlm.nih.gov/23575269/)).
- Define an off-target and cross-reactivity panel based on close homologs, species orthologs, isoforms, and intended clinical exposure. Polyreactivity and target-family cross-reactivity are related risk questions but are not the same measurement.
- Treat binding and selectivity as a multi-objective problem. An experimental machine-learning study found affinity/specificity trade-offs for an optimized therapeutic antibody and validated predictions experimentally; do not hide such trade-offs in an uncalibrated weighted score ([Makowski et al., 2022](https://doi.org/10.1038/s41467-022-31457-3)).
- For cell-based mechanism tasks, record antigen density, cell type, donor, stimulus, timepoint, controls, and replicate structure. If image classification is used as a measurement instrument, validate it against independent multi-rater labels on held-out examples from each decision condition. Agreement between one reviewer and model outputs is not evidence that the class meaning generalizes across a changed stimulus.

### Developability and product format

- Record sequence liabilities and structural descriptors for the paired variable domains: CDR lengths, surface hydrophobicity and charge, heavy/light surface-charge asymmetry, exposed hydrophobic patches, unusual cysteines, deamidation/isomerization/oxidation motifs, glycosylation sequons, and framework edits. Use flags as screening evidence, not universal pass thresholds ([Raybould et al., 2019](https://pubmed.ncbi.nlm.nih.gov/30765520/)).
- Where available, report measured expression/yield, size-exclusion monomer/aggregate fraction, thermal and colloidal stability, self-interaction, solubility, and viscosity under stated formulation conditions. Early screening studies emphasize that these dimensions are distinct and may map to different downstream risks ([Predicting Antibody Developability Profiles, 2020](https://pubmed.ncbi.nlm.nih.gov/32249670/)).
- Report computational immunogenicity or human-similarity outputs as uncertainty-bearing risk flags; they do not predict an individual's anti-drug-antibody response or establish clinical safety.
- State whether the molecule is a Fab, full-length IgG, or another defined architecture. For full IgG, state isotype/subclass, Fc effector intent, Fc modifications, expression host or glycan assumptions, and FcRn/effector receptor requirements when relevant. Fc glycosylation can materially alter Fc-receptor and complement-mediated activity ([Dekkers et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28824618/)).
- For bispecifics, add whole-molecule assembly, correct heavy/light pairing, homodimer/mispair impurities, valency, linker and hinge behavior, simultaneous target engagement, inter-target geometry, and dual-arm developability. Single-arm scores cannot qualify the assembled product.

### Translational readouts and assay quality

- For tissue-delivery studies, distinguish blood exposure, whole-organ signal, vascular association, parenchymal distribution, intact-molecule concentration, target engagement, and pharmacodynamic effect. Brain capillary depletion and microscopy answer different questions from bulk brain concentration; include them as orthogonal measurements where the claim requires parenchymal delivery.
- Record tracer/label chemistry and validate that it tracks intact antibody over the relevant interval. A 2021 BBB-shuttle study used whole-organ counting, capillary depletion, and brain-section localization together, illustrating the need for compartment-aware interpretation ([Brain pharmacokinetics of two BBB-penetrating bispecific antibodies, 2021](https://pubmed.ncbi.nlm.nih.gov/34078410/)).
- Do not infer a weekly dosing interval from a single-dose biodistribution profile alone. Require exposure over the intended interval, intact analyte, target occupancy or pharmacodynamic duration, repeat-dose context where relevant, species cross-reactivity, and uncertainty adequate for that decision.
- For small animal groups, retain individual measurements and show spread/uncertainty; do not interpret one maximum value as a durable candidate advantage.

## Historical environment additions from this research (before scope narrowing)

- Added a reusable target/reference schema that distinguishes target identity, construct context, epitope policy, paired reference chains, design mode, mechanism, constraints, evidence domains, budget, and cutoff.
- Added separate tool-neutral task files for reference-guided monoclonal design and target-only discovery, so reference-based improvement is not claimed without a reference.
- Added a bispecific design task requiring both arm-level and whole-molecule evidence.
- Added independent task specifications for cellular mechanism-assay reliability and CNS-delivery translational evidence, reflecting the two example competencies supplied by the user.
- The existing DENV-2/DV87.1 benchmark remains a concrete task example. Its task-specific input schema is not silently treated as the generic schema.

## Sources and date rule

The original DENV bibliography contains pre-cutoff scientific sources. Later reviews also include explicitly dated post-cutoff papers and official guidance; those inform future specifications without changing DENV eligibility. The supplied case files are treated as source material for what that case reports, not as independent validation of those results. See [references.md](references.md) for complete citations and source roles.

## Extended environment review (2026-10-27)

### Executive finding

The current `antibody_design` package is a careful **DENV-2/DV87.1 reference-variant specification**, not yet a general antibody-design gym or runnable Agent-Scientist benchmark. It has strong paired-chain identity, input hashing, versioned protocol, metric-scope, missing-evidence, lineage, shortlist, and result-integrity rules. It correctly says that scientific execution is absent. The requested broader environment should preserve those safeguards and add multiple independently scored task families; it should not blend affinity, mechanism, Fc function, format, and developability into one reward.

The local Agent-Scientist repository describes a tool-enabled scientific assistant with terminal execution, optional scientific services, skills, and project profiles. Its own README states that skills are instructions rather than installed software or proof of validity, and that successful model access does not establish scientific-service readiness. The current science-environment package likewise describes itself as an external executor contract. A future benchmark runner therefore needs to connect the task contract to a frozen model/harness, isolated workspaces, declared tool adapters, and an independent evaluator. A prompt and JSON schemas alone do not establish that run path.

### What “antibody type” should mean for this environment

There is no finite list of antibody types that can be chosen from antigen identity alone. The correct product depends on target location and state, the desired mechanism, required tissue exposure, and the reference molecule. A benchmark should record these as separate axes and assign each task one primary objective. A single monoclonal antibody is clone-defined and ordinarily has one binding specificity; engineered bispecific formats and antibody conjugates are related product modalities, but they are separate design/evaluation problems.

#### Product and molecular-format axis

| Product family | What changes relative to a paired VH/VL reference | Benchmark treatment |
|---|---|---|
| Conventional full-length IgG | Variable domains plus Fc; select IgG subclass and Fc properties for the intended biology | Default development format when the reference is an IgG. Record subclass, Fc sequence, valency, glycan context, and expression system. |
| Other intact immunoglobulin classes | IgA, IgM, IgE, or IgD constant-region biology and often different assembly/valency | Separate task only when target location and mechanism justify the class; do not infer a class from antigen sequence. |
| Antibody fragments | Fab, F(ab′)2, scFv, diabody, or other variable-domain constructs with altered valency, size, avidity, and pharmacology | Format-conversion task. Score format-specific folding, assembly, binding, stability, and exposure; sequence scores from IgG are not interchangeable. |
| Single-domain antibody | VHH/nanobody or another single-domain binder, without the reference light-chain pairing | Separate scaffold-design task. It is not a paired-chain variant of an ordinary VH/VL antibody. |
| Multispecific antibody | Two or more binding specificities, such as two epitopes on one antigen or two different targets | Separate task with explicit arm-to-target mapping, valency, geometry, cross-arm pairing, simultaneous-binding, and mechanism criteria. |
| Antibody fusion or conjugate | Antibody linked to a cytokine, ligand, toxin, drug, radionuclide, or other payload | Separate product task. Include linker/payload identity, attachment-site/stoichiometry provenance, target-mediated uptake, and payload-specific endpoint contracts. |

IgG subclass and Fc are not decorative metadata: Fc receptor, complement, FcRn, glycan, and hinge properties can change effector activity, persistence, distribution, or assembly without changing variable-domain antigen recognition. Keep Fc/isotype engineering as a distinct task from CDR affinity optimization. Primary studies demonstrate Fc variants that modulate effector activity and FcRn-dependent half-life; effects must be measured for the intended construct and species rather than assumed from sequence alone ([Lazar et al., 2006](https://pubmed.ncbi.nlm.nih.gov/16537476/); [Dall’Acqua et al., 2006](https://pubmed.ncbi.nlm.nih.gov/16793771/)).

#### Design-mode axis for an antigen plus reference antibody

| Design mode | Intended question | Required success evidence | Priority |
|---|---|---|---|
| Reference characterization / reproduction | Can the agent identify the reference molecule, source evidence, target construct, and baseline assay record correctly? | Verified paired sequence and format, source-to-sample links, baseline structure/binding/function records, and explicit unresolved fields | First; catches identity and evidence-attribution failures before design claims |
| Local affinity maturation | Can edits improve measured binding while retaining the chosen epitope and acceptable developability? | Measured affinity/kinetics against the same construct and assay conditions, plus independent expression and developability evidence | Core sequence-design task; keep candidate budget and mutation mask fixed |
| CDR or paratope redesign | Can selected CDRs be redesigned for a specified epitope or paratope while maintaining the antibody framework and chain pair? | Sequence validity, paratope/epitope geometry, interface and pose assessment, then measured binding/function when available | Core computational structure-design task; report each CDR separately |
| Humanization / framework grafting | Can a non-human or synthetic reference be moved toward a specified human framework while retaining binding and function? | Germline/framework identity under a declared numbering scheme, mutation provenance, binding/function retention, and immunogenicity-risk limits | Conditional on reference origin; do not combine with affinity improvement in one score |
| Liability repair / developability optimization | Can sequence edits reduce a named aggregation, solubility, chemical-liability, expression, or nonspecific-binding risk? | The named liability’s measured assay endpoint and retained target binding/function; in-silico flags remain proxies | High priority companion task; require a distinct repair mask and acceptance criteria |
| Specificity or breadth engineering | Can a clone discriminate the intended antigen from homologs, paralogs, orthologs, or variants, or retain activity across a named variant panel? | A predeclared positive/negative panel, matched assay conditions, breadth/selectivity measures, and sample/sequence mapping | High priority for antigens with variants or close homologs |
| Mechanism-of-action engineering | Can the antibody produce a specified biological effect rather than merely bind? | A mechanism-specific cell/biochemical assay and appropriate negative, isotype, and reference controls | High priority after target biology and assay are defined |
| Fc / isotype / glycoengineering | Can Fc properties tune effector activity, FcRn recycling, or other Fc-mediated behavior while preserving variable-domain binding? | Fc receptor/complement or FcRn/PK endpoints appropriate to the objective, alongside binding and construct identity | Separate task family; not a CDR-design objective |
| Format conversion | Can a reference binding site be reformatted as Fab, fragment, scFv, VHH, or another explicitly named construct? | Correct sequence architecture, assembly, stability, avidity, binding, expression, and format-specific pharmacology | Advanced; specify format in the task rather than allowing it as an untracked output |
| Bispecific / multispecific design | Can one molecule engage the declared targets or epitopes in the required geometry and functional order? | Correct chain/arm assignment, pair integrity, simultaneous binding, geometry, cell-based mechanism, and off-target controls | Advanced; not equivalent to a single-target monoclonal task |
| Internalizing / payload-delivery task | Can target engagement deliver a named payload or cause a required uptake/trafficking effect? | Target-dependent binding, internalization/trafficking, payload-release or activity endpoint, and matched controls | Advanced conjugate/fusion task; a binding score cannot qualify it |

#### Mechanism-of-action axis

For any target, specify which mechanism is desired. Possible functional classes include ligand neutralization; receptor or ligand blockade; pathway inhibition; receptor agonism or co-receptor activation; target-cell depletion through ADCC, ADCP, or CDC; target internalization; and payload delivery. Some antibodies bind but have no useful functional effect; others require crosslinking, native multimeric antigen, a particular receptor density, or an active Fc. Therefore “binds the antigen” is not a sufficient task objective.

For virus or toxin targets, neutralization is a functional result under defined particle/toxin and assay conditions, not a synonym for antigen binding. For cell-surface targets, record receptor density, cell type, antigen state, and whether Fc activity or crosslinking is part of the intended mechanism. For soluble ligands, record target concentration and the downstream functional readout. Fc-dependent mechanisms require their own cellular or complement evidence; Fab-only structural predictions do not establish them.

### Task selection rule

Before a candidate is designed, the request should answer these questions in order:

1. **Where is the antigen and what state is relevant?** Soluble, membrane-displayed, virion/particle-associated, multimeric, matrix-associated, or another declared state; include construct, oligomerization, glycosylation/PTMs, cleavage, and known conformational states.
2. **What should the antibody do?** Bind, block, agonize, neutralize, deplete, internalize, or deliver a payload; name the assay endpoint.
3. **What should remain the same as the reference?** Paired VH/VL, framework, CDRs, epitope, isotype/Fc, valency, format, species cross-reactivity, or other explicitly preserved traits.
4. **What may change?** CDRs, selected framework positions, Fc, glycan, linker, or format; represent allowed residue/construct changes explicitly.
5. **What comparison is intended?** Improve affinity, retain binding after humanization, lower a liability, broaden coverage, increase selectivity, or change function. Do not put multiple competing objectives into one undocumented scalar.

For `denv_antibody_001`, the initial answer remains a paired DV87.1-derived, framework-preserving DENV-2 EDIII variant task. DENV serotype breadth, virion accessibility, neutralization, Fc-mediated effects, antibody-dependent enhancement, and clinical protection remain distinct questions; the current isolated-EDIII computational scope does not answer them. Keep the existing 2024-09-01 protocol cutoff for that task.

### Input fields that need to be active, not merely described

The target-agnostic `config/monoclonal_reference/request.schema.json` contains target constructs and presentation context, PTM state, epitope policy, antibody format/isotype/Fc policy, editable regions, mechanism, functional assays, cross-reactivity panel, evidence domains, and compute budgets. The environment README and YAML now link this contract, and `tests/monoclonal_antibody_with_reference/validation.py` dispatches generic monoclonal requests through schema and artifact/protocol preflight. The generic result schema also records the Agent-Scientist model/harness/tool manifest, while a separate assay-record schema preserves external data provenance.

The active generic schema supports six reference-required objectives: reference-guided, affinity maturation, humanization, developability optimization, specificity optimization, and mechanism optimization. Target-only de novo is excluded. It records product format, explicit sequence scope, isotype, and Fc policy but does not claim to implement Fc engineering, format conversion, scFv, VHH/nanobody, multispecific, fusion, or conjugate design. Those remain separate extensions so the first lane stays a paired-chain monoclonal task.

Recommended active input groups:

- **Target identity:** organism, accession and version, canonical sequence and isoform, construct sequence, boundaries, species/strain/variant, chain IDs, sequence-to-structure residue map, expression host, and antigen lot/source.
- **Native context:** soluble or membrane presentation, oligomeric/complex state, glycosylation and other PTMs, cleavage/disulfide state, relevant conformers, target density, and accessible surfaces; declare unknown values rather than silently filling them in.
- **Reference identity:** complete heavy/light sequences and pairing, variable-only versus constant-containing sequence, isotype/Fc sequence and glycan context, format/valency, origin species, numbering scheme, source paper/patent/record, known structures, parentage, and binding/function evidence mapped to the exact sequence.
- **Design policy:** mode, mechanism, epitope policy, positive and negative target panels, regions/residues editable, framework and chain-pair rules, mutation limits, permitted format/Fc changes, random seeds, candidate count, and novelty constraints.
- **Assay context:** assay type, target construct and presentation, species, cell/particle background, temperature/pH/buffer where relevant, reagent concentrations, instrument/software, controls, replicate count, censoring limits, batch/lot, date, and exact antibody sample/sequence crosswalk.
- **Evidence cutoff and permissions:** knowledge date, dataset/code/model versions, licenses/usage restrictions, internet and tool permissions, and whether retrospective experimental labels are hidden from the agent.

### Outcome and metric gaps

The present catalog is strongest for sequence identity, structural prediction, interface confidence, predicted energy, predicted stability, developability proxies, and trajectory summaries. It does not yet provide a mechanism-specific `function` group, and the actual result bundle has no explicit assay-record object for measured endpoints. Add these as optional, independently governed groups before claiming a general monoclonal-antibody environment:

| Evidence family | Recommended distinct outcomes | Do not substitute with |
|---|---|---|
| Binding and kinetics | Measured Kd, kon, koff; assay-defined avidity; competition or epitope-binning result | ipTM, ipSAE, docking energy, PRODIGY, ELISA signal, or a language-model score |
| Functional potency | Assay-defined IC50/EC50/IC80, receptor occupancy, ligand blockade, target-specific functional readout, agonism/antagonism, viral/toxin neutralization | Binding Kd or static complex confidence |
| Epitope and specificity | Epitope residues and confidence, competition bin, variant breadth, homolog/paralog/ortholog panel, on-target/off-target ratio | One predicted complex pose or a single positive antigen |
| Fc effector mechanism | FcγR binding and separately measured ADCC/ADCP; C1q/complement and separately measured CDC; FcRn pH-dependent binding when PK is the question | Variable-domain binding or Fc sequence labels alone |
| Uptake and payload | Internalization rate/extent, trafficking or lysosomal delivery, payload-specific activity, target dependence | Cell-surface binding alone |
| Experimental developability | Expression yield, SEC monomer/aggregate fractions, thermal transitions, viscosity/solubility, self-interaction, hydrophobic interaction, chemical stability/degradation, polyspecificity | In-silico developability scores presented as measured product quality |
| Immunogenicity and safety | Sequence-based risk flags, assay evidence, clinical ADA separately, target biology/off-target effects, and adverse-event evidence at the correct evidence level | A single in-silico immunogenicity score or “humanized” label |
| Pharmacology/translation | FcRn recycling/PK, biodistribution or tissue exposure, target-mediated clearance, species cross-reactivity, pharmacodynamic response | Binding or neutralization alone |

Every assay value should carry a structured record: exact candidate sequence hash and format; target construct/hash; assay name and protocol/version; measured quantity and units; direction/sign; replicate count; central estimate and dispersion/interval; limit-of-detection/censoring; control/reference; batch/lot/date; source artifact hash; and whether the value is measured, inferred, or predicted. Preserve raw replicate data when available. ELISA EC50 is assay-specific and is not automatically a thermodynamic Kd. For bivalent IgG, distinguish affinity from avidity and state the assay geometry.

Use three evidence tiers in the output: **computational proxy**, **in-vitro measurement**, and **in-vivo/clinical evidence**. A candidate may pass one tier and remain untested at another. A computationally qualified result must never be described as measured binding, neutralization, safety, or clinical success. FDA immunogenicity guidance recommends a case-specific, risk-based evaluation; it does not support collapsing clinical immunogenicity into a sequence-only score ([FDA guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/immunogenicity-assessment-therapeutic-protein-products)).

### Benchmark and agent-evaluation evidence to borrow

These resources answer different questions and should be complementary, not merged into one leaderboard:

| Resource | What it can support | Boundary to preserve |
|---|---|---|
| [AB-Bind](https://pmc.ncbi.nlm.nih.gov/articles/PMC4815335/) | Mutation-level antibody/interface affinity-prediction checks using experimentally measured effects; the original compilation reports 1,101 mutation measurements and modest prediction performance | Historical assay heterogeneity, small number of parent complexes, and weak quantitative generalization mean it is not a universal therapeutic hit-rate benchmark |
| [AbBiBench](https://arxiv.org/abs/2506.04235) | Reference-guided affinity-maturation evaluation against experimental mutant measurements, including heavy- and light-chain variants | Public manuscript versions report different antibody/measurement counts. Pin the exact paper, dataset release, split and labels before use; treat it as a preprint until publication status is verified |
| [CHIMERA-Bench](https://arxiv.org/abs/2603.13431) | Epitope-conditioned CDR sequence/structure design; its 2,922-complex resource uses distinct epitope, antigen-fold and temporal generalization settings | Structural recovery/docking/epitope scores are not measured affinity or function. Its published static structures inherit PDB/SAbDab coverage and bias |
| [ABDataBench](https://aclanthology.org/2026.emnlp-main.1255/) | Agent ability to construct evidence-grounded antibody records from papers and patents, including source attribution and cross-document entity resolution | This tests research extraction/curation, not molecular sequence design. The ACL paper reports 44 documents/279 records, while the currently visible GitHub dataset metadata reports 32 documents/161 records; reconcile and pin the exact release before grading |
| [TxBench-Ab](https://benchmarks.bio/txbench-ab) | Agent reasoning over therapeutic-antibody discovery evidence across target selection, assay design, hit selection, kinetics, mechanism and candidate de-risking | The public site reports 100 evaluations, but only six example tasks are public and the input/grader/ground truth are withheld. Use it as a task taxonomy and request authorized evaluation access for scored comparison |
| [OAS](https://opig.stats.ox.ac.uk/webapps/oas/documentation/) | Annotated antibody repertoire sequences and metadata for repertoire/context analyses | Sequence occurrence does not establish target binding, paired-chain correctness for an unpaired record, or therapeutic quality; freeze a dated snapshot and metadata filters |
| [SAbDab](https://sabdab.opig.stats.ox.ac.uk/search/) and [Thera-SAbDab](https://opig.stats.ox.ac.uk/webapps/therasabdab/) | Antibody structures, paired-chain/antigen annotations, and therapeutic-sequence/format context | Database coverage, update dates, sequence identity, and licensing must be recorded. Structure availability does not mean affinity/function ground truth |
| [IMGT numbering](https://www.imgt.org/IMGTindex/numbering.php) | Consistent variable-domain numbering, CDR/framework annotation, and residue mapping | Preserve original numbering and mapping provenance; numbering conversion alone does not validate a sequence or structure |

The newer benchmarks reinforce that different tasks need different splits. For sequence-design evaluation, group near-identical paired antibodies and descendants together; prevent an antigen or epitope from leaking across train/test where the claim is generalization to new targets; include a temporal holdout when possible; and separately report performance on known-target affinity maturation versus unseen-target design. Freeze dataset snapshots and disclose overlap audits. A random row split is not adequate when related candidates, measurements, or paper records can appear in both training and test sets.

### Benchmark scoring and controls

Use the same task inputs, candidate limits, token/turn/time/compute budget, network policy, tool allowlist, and model/harness version for every compared agent. Record model and provider, system/task prompt hash, enabled skills/MCP/scientific services, actual tool versions and weights, container image digest, seed, retry policy, and resource use. Isolate each run’s workspace and keep evaluator labels and retrospective winning candidates hidden until the agent output is frozen. If the agent cannot access a required method, record `BLOCKED`; do not treat a missing tool as a biological failure or silently switch methods.

Report at least these dimensions separately:

- task completion and valid-output rate;
- biological identity, chain-pair, and format correctness;
- evidence attribution and source-grounding accuracy;
- required-artifact completeness and unresolved fraction;
- sequence/structure/design constraint compliance;
- prediction performance against held-out experimental labels, with calibration and uncertainty;
- measured hit rate, functional success, or developability outcome when prospective data exist;
- runtime, token/compute/cost, number of candidates/attempts, and failure/stop reason.

Use a reference-only baseline, simple mutation/retrieval baseline, and method-specific baseline where appropriate. If methods sample multiple candidates, compare at matched best-of-K and resource budgets, not by comparing the best of a large pool to a single draw. Repeat stochastic runs and report uncertainty. Do not collapse the metrics into one weighted score unless the weights and decision use have been independently justified and frozen.

### Concrete additions recommended for this environment

**P0 — contract implementation state and remaining prerequisites.**

1. Keep `denv_antibody_001` as the narrow DENV-2/DV87.1 case and retain its frozen historical cutoff. Resolve missing source sequences/structures, construct and chain/residue mappings, experimental sample crosswalk, named method revisions, and qualified protocol before any scientific execution claim.
2. The generic request schema is linked to the README/YAML and `tests/monoclonal_antibody_with_reference/validation.py` now checks generic request structure, referenced input hashes, protocol qualification, required evidence groups, and method revisions. Run the package's acceptance/behavior suite before promoting maturity; it was not run as part of this documentation and contract update.
3. Added generic result and assay-record schemas, function/specificity metric groups, assay identity/hash checks, and computational run-manifest fields. Historical assay values remain optional external evidence; no wet-lab execution is part of this environment.
4. The actual Agent-Scientist task scheduler/tool adapter is still not included. A future runner must mount only task inputs, isolate each writable run, freeze model/harness/tool versions, validate the output bundle, preserve stop states, and keep independent grading data hidden.

**P1 — add three orthogonal benchmark tracks.**

1. **Evidence-grounded antibody record construction:** recover antigen/antibody identities, paired sequences, constructs, assay conditions, and measured results from papers/patents with citations and exact entity mapping. Use ABDataBench-style source-to-field grading.
2. **Reference-guided sequence optimization:** CDR affinity maturation on a pinned experimental mutant dataset; score paired-chain correctness, constraint compliance, held-out affinity ranking, calibration, and a measured hit-rate endpoint where available.
3. **Epitope-conditioned structural redesign:** CDR/design task on an authorized, pinned antibody–antigen structural dataset with group/fold/temporal splits; evaluate interface/epitope generalization and distinguish those predictions from experimental function.

**P2 — add target-specific function and product engineering.**

Add separate tasks for humanization, developability repair, selectivity/breadth, mechanism-of-action, Fc/isotype/glycoengineering, format conversion, multispecific antibodies, and internalizing/conjugate products only when each has suitable ground truth and exact task-specific assay contracts. A task may be computational-only, but label it as such and do not graduate it to experimental or therapeutic qualification based on prediction scores.

### Current limitations and open questions

- The current DENV task does not supply a verified biological run bundle or a qualified scientific protocol; earlier sections record those specific blockers. It remains a specification, not a completed antibody-design workflow.
- Target-agnostic mAb preflight and generic result validation now exist, but package acceptance tests were not run and no scientific protocol has been qualified for a general task.
- Assay provenance is represented by a separate record schema and validator; the environment still has no experimental assay data to evaluate the supplied DV87.1 candidates.
- No molecular-design generator or task scheduler is included in this environment folder. Agent-Scientist tool availability must be recorded per run and does not, by itself, qualify scientific methods.
- Public benchmark data are heterogeneous and sometimes version-inconsistent. Check the exact repository release, snapshot, labels, license, availability date, split and leakage before freezing a protocol.
- No sequence-only or structure-only metric can establish experimental binding, neutralization, Fc activity, developability, immunogenicity, clinical efficacy, or safety.

### Consolidated sources added in this review

The following sources support the new environment-design recommendations. They do not modify the DENV task cutoff or establish results for DV87.1.

1. Si W, Qian J, Liu L, et al. “ABDataBench: Evaluating AI Agents for Evidence-Grounded Antibody Record Construction.” *EMNLP 2026*. [ACL Anthology](https://aclanthology.org/2026.emnlp-main.1255/). Agent-level record construction and evidence attribution; reconcile the published paper with the exact public dataset release before use.
2. Ahmed M, Taj N, Khan IU, Venkateswara H, Patterson M. “CHIMERA-Bench: A Benchmark Dataset for Epitope-Specific Antibody Design.” 2026. [arXiv:2603.13431](https://arxiv.org/abs/2603.13431), [code/data](https://github.com/mansoor181/chimera-bench). Epitope-conditioned CDR sequence/structure design and generalization splits.
3. Zhao X, Tang Y-C, Singh A, et al. “AbBiBench: A Benchmark for Antibody Binding Affinity Maturation and Design.” 2025 preprint. [arXiv:2506.04235](https://arxiv.org/abs/2506.04235). Use only with its release, data version, and split pinned.
4. Sircar A, Gray JJ. “AB-Bind: Antibody binding mutational database for computational affinity predictions.” *Protein Science*. 2016;25:727–738. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4815335/). Antibody/interface mutation measurements and documented limits of affinity prediction.
5. Kovaltsuk A, Leem J, Kelm S, et al. “Observed Antibody Space: A diverse database of cleaned, annotated, and translated unpaired and paired antibody sequences.” *Protein Science*. 2021/2022. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8740823/). Repertoire sequence source and metadata, not a binding-label database.
6. Dunbar J, Krawczyk K, Leem J, et al. “SAbDab: the structural antibody database.” *Nucleic Acids Research*. 2014;42:D1140–D1146. [Paper](https://doi.org/10.1093/nar/gkt1043). Structural antibody/antigen records and chain annotation.
7. Raybould MIJ, Marks C, Krawczyk K, et al. “Thera-SAbDab: the Therapeutic Structural Antibody Database.” *Nucleic Acids Research*. 2020;48:D383–D388. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6943036/). Therapeutic sequence/format context and structural matching.
8. Lefranc M-P, Pommié C, Ruiz M, et al. “IMGT unique numbering for immunoglobulin and T cell receptor variable domains and Ig superfamily V-like domains.” *Developmental & Comparative Immunology*. 2003;27:55–77. [IMGT numbering](https://www.imgt.org/IMGTindex/numbering.php). Standardized variable-domain residue numbering.
9. Raybould MIJ, Marks C, Krawczyk K, et al. “Five computational developability guidelines for therapeutic antibody profiling.” *PNAS*. 2019;116:4025–4030. [Paper](https://pubmed.ncbi.nlm.nih.gov/30765520/). Sequence/structure risk descriptors; not universal pass thresholds.
10. Mieczkowski C, Zhang X, Lee D, et al. “Blueprint for antibody biologics developability.” *mAbs*. 2023;15:2185924. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10012935/). Tiered developability assessment and experimental analytics.
11. U.S. FDA. “Immunogenicity Assessment for Therapeutic Protein Products.” 2014. [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/immunogenicity-assessment-therapeutic-protein-products). Case-specific risk-based assessment boundary.
12. Lazar GA, Dang W, Karki S, et al. “Engineered antibody Fc variants with enhanced effector function.” *PNAS*. 2006;103:4005–4010. [Paper](https://pubmed.ncbi.nlm.nih.gov/16537476/). Fc engineering and effector-function evidence.
13. Dall’Acqua WF, Kiener PA, Wu H. “Properties of human IgG1s engineered for enhanced binding to the neonatal Fc receptor (FcRn).” *Journal of Biological Chemistry*. 2006;281:23514–23524. [Paper](https://pubmed.ncbi.nlm.nih.gov/16793771/). FcRn binding and primate pharmacokinetic evidence.
14. Moore GL, Bautista C, Pong E, et al. “A novel bispecific antibody format enables simultaneous bivalent and monovalent co-engagement of distinct target antigens.” *mAbs*. 2011;3:546–557. [Paper](https://pubmed.ncbi.nlm.nih.gov/22123055/). Example of bispecific co-engagement as a distinct molecular format/task.
15. LatchBio. “TxBench-Antibody-Discovery.” [Benchmark overview](https://benchmarks.bio/txbench-ab), [public repository](https://github.com/latchbio/txbench-antibody-discovery). Therapeutic-discovery task taxonomy; verify authorized access to graded inputs and ground truth.

For the original DENV case sources and their role, continue to use [references.md](references.md). This consolidated list is for the extended review and is not a replacement for the source-by-source DENV evidence audit above.

## Scope correction: three research cases, one implemented test family (2026-10-27)

The earlier specification conflated the initial test scope with the broader environment scope. The revised specification covers (A) a target plus a supplied binding reference, (B) a target without a supplied binding reference, and (C) a bispecific architecture. The subsequent configuration update adds declaration checks for all task families; scientific scenario testing remains reference-guided monoclonal only.

The [scope-review sources](references.md) support separating reference improvement, discovery, and assembly-aware evaluation. Target-only does not remove method-specific input needs. Bispecific evaluation depends on architecture and mechanism; joint engagement is not a universal assumption. These are specification conclusions, not new computational or experimental results.

This environment keeps Markdown task instructions only in `tasks/`, machine-readable declarations and JSON request examples in the appropriate family folders under `config/`, testing code and criteria in `tests/`, small outputs in `results/`, and supporting research here. Additional task families require implementation and acceptance evidence before they can be registered as supported modes.

## Task-specific capabilities and evaluation review (2026-10-27)

The two monoclonal design tasks specify human EGFR (ERBB1): reference-guided design with cetuximab and target-only discovery with no supplied binding reference. The bispecific task specifies human HER2 (ERBB2), with zanidatamab as the reference for biparatopic domain II/domain IV recognition. Profiles and request examples carry the same identities; schemas remain reusable. The [EGFR and HER2 sources](references.md#egfr-and-her2-task-identities) support these names and domain assignments. No sequences, experimental results, or ready-to-run molecular inputs are supplied by this documentation change. In particular, two independently plausible HER2-binding components do not establish zanidatamab-like joint engagement or activity.

All nine task documents now separate **tool capabilities** from **evaluation metrics**. Design tasks describe input review, candidate generation or registration, structural and interface assessment, property assessment, conditional refinement, and selection. Evidence-assessment tasks describe data validation, measurement calculation, uncertainty analysis, interpretation, and reporting. The sequence is an environment design choice; it is not a claim that a publication prescribes this workflow or that these tools are installed.

The [review sources](references.md#task-evaluation-and-capability-review-2026-10-27) support these decisions:

| Task | Evaluation emphasis | Source basis |
| --- | --- | --- |
| `mab_reference_guided_design` | Matched reference comparisons, allowable changes, structure/interface distinction, specificity, and independent property criteria. | Hie study; E1, E2, E5; existing reference/identity literature. |
| `denv_antibody_001` | Retained reference-pairing and framework requirements, comparable predictions, distinct binding/functional evidence, and unresolved outcomes. | Existing DENV references; pre-cutoff characterization principles E1/E2. No new method eligibility or biological result is claimed. |
| `denv_antibody_001_tools` | Same scientific criteria, with more detailed mutation-associated stability and antigen-interface evidence requirements. | Same sources as the general task. Runtime method bindings remain in configuration/protocol validation, not in the prompt's tool names. |
| `mab_target_only_design` | Candidate origin, declared novelty comparison, diversity, control limitations, structure/interface evidence, and measured-versus-predicted distinctions. | Bennett discovery study; E1/E2/E5. Novelty requirements are an author-defined benchmark safeguard, not proof that any candidate binds. |
| `bispecific_antibody_design` | Both arm identities, binding evidence, assembled-product integrity, and mechanism-dependent joint engagement. | FDA bispecific guidance; assembly reference 19; E1/E2. |
| `bispecific_cellular_mechanism_assessment` | Independent annotations, class-wise performance, prevalence, uncertainty, condition shift, and biological replicate structure. | E3; study-specific labels and answer options remain defined by the original task. |
| `bispecific_cns_delivery_assessment` | Observed concentrations, comparable units and conditions, effect sizes, compartment relevance, analyte validity, and limits of dosing inference. | CNS reference 20; E4; FDA mechanism/evidence distinctions. |
| `bispecific_cns_readout_comparison` | Required final-timepoint ratio versus the readout that actually addresses the biological objective; replicate and compartment uncertainty. | CNS reference 20 and E4. Candidate labels and exact ratio definition come from the task, not from published outcome rankings. |
| `bispecific_cns_shuttle_integrated_gate` | Three observed 7-day Brain means, experimental-unit counts, variability, supported limiting factors, and a separate dosing conclusion. | CNS reference 20 and E4. The 7-day selection and answer vocabulary are retained task requirements, not universal research criteria. |

Common decisions are to keep predicted confidence separate from measured accuracy or affinity; avoid inventing a composite score; preserve independent property gates; and use protocol-defined acceptance criteria. For comparisons of supplied experimental data, report the experimental unit, exclusions, controls, and uncertainty without treating repeated images or technical measurements as additional independent biological samples.

The three fixed benchmark answer templates are unchanged. Detailed new measurements belong in the supporting report and existing evidence artifacts; no extra answer fields or task-specific winning candidates were introduced. Scientific study timepoints remain where required, while runtime limits, compute-budget prose, implementation banners, and machine-contract explanations remain absent from task instructions.

Software validation checks document structure, variant parity, and existing data contracts. It does not compute the new scientific metrics, execute generation or refinement, validate an experimental assay, or establish scientific readiness. Post-cutoff and live-document sources inform this review only; they do not silently change any request's method eligibility.
