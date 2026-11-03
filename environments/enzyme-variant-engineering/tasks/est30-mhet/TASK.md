# Est30 MHET Hydrolysis

## Objective

Design variants of the starting Est30 enzyme with improved predicted MHET
hydrolysis while assessing stability and preserving the catalytic mechanism.
Complete a real computational design, evaluation and optimization workflow.
This is not a readiness check, mutation-scan-only exercise or tool-access pilot.

## Starting inputs

Enzyme: Geobacillus stearothermophilus carboxylesterase Est30.
Experimental starting structure: [PDB 1TQH](https://www.rcsb.org/structure/1TQH).
Retrieve from RCSB using existing scientific tools or its public download service.
Substrate: mono(2-hydroxyethyl) terephthalate (MHET).
Reaction: hydrolysis of MHET to terephthalic acid and ethylene glycol.
Target assay context: pH 7.5 and 50 degrees C. Report when a chosen computational
method does not model those conditions; do not imply that an ordinary prediction
is temperature- or pH-specific when it is not.

Qualify the exact parent sequence and modeling construct, catalytic residues,
residue numbering, relevant assembly, substrate identity and protonation state.
1TQH contains a covalent reaction intermediate; it is not a ready-made MHET reactant
complex. Prepare the intended chemical state explicitly without retaining an
unintended catalytic-residue modification. Keep the actual prepared inputs.

## Allowed research and information boundaries

Use background evidence about WT Est30, serine-hydrolase chemistry, MHET and
applicable computational methods. Resolve scientific questions using existing
search/page-reading tools and primary sources.
Do not read or search published engineered Est30/MHET winning mutations, winning
sequences, target-study design procedures or outcome tables. Do not inspect
operator reference packages, other benchmark-arm outputs or protected evaluation
records. If answers are recalled or exposed, record the exposure and do not claim
independent rediscovery.
These instructions are information boundaries, not an enforced OS sandbox.

## Tool selection and execution

Choose methods from Boltzmann, ToolUniverse or both by relevance to this reaction,
available executable operations, input compatibility and resource requirements.
Use current native discovery, schemas, input validation, authorization and execution.
There is no compulsory sequence of named tools and no requirement to use both
providers. Software descriptions, literature results and deposited structures do
not count as newly executed predictions or simulations.
Do not build another connector, request validator, workflow engine or state database.
Do not modify Agent-Scientist source, settings, installed dependencies or unrelated
GPU/competition work. Native service permissions and approval requirements remain.
The critic's recommendation is scientific advice, not another user-approval gate.

## Assignment limits

Use up to 24 unique sequences including the parent across this arm, at most two
optimization-revision rounds, and at most 60 scientific submission attempts.
Start with approximately 12 distinct, justified variant sequences. These are
planning ceilings for this assignment, not sandbox-enforced spending limits.
All failed attempts and specialist work count within the same arm's allowance.
Do not change the limits after seeing results. Do not reset counts on continuation.
Do not launch an exhaustive large library or consume all host GPU memory. Use
bounded concurrency and leave existing competition workloads undisturbed.
Do not guess a currency cost from provider credits; retain actual billing units.

## Required scientific work

1. Define the objective, protected catalytic positions and allowed mutation scope.
   State and save ranking criteria before inspecting variant prediction results.
   Separate a functional prediction from a stability or docking proxy. Do not
   combine incompatible raw scores without a declared, justified ranking procedure.
2. Generate complete, valid variant sequences with unique candidate IDs, exact
   mutations and a scientific rationale. A list of mutation scores is not a
   generated and evaluated candidate set. De novo scaffold generation is not required.
3. Run relevant functional/property evaluations on the parent and candidate set.
   Select a bounded shortlist for detailed structural work based on real results.
   Use each tool's actual case-sensitive CSV schema, not one assumed universal
   header. Preserve candidate identities across every batch and artifact.
4. Obtain and evaluate structures for the parent and at least five shortlisted
   variants, where scientifically evaluable. Evaluate their MHET interaction in
   an explicitly defined state, structure quality and catalytic-geometry risks.
   Every final candidate requires its own evaluated structure; it cannot inherit
   another candidate's quality or catalytic result. Preserve ligand coordinates
   and sequence/residue mappings for the corresponding candidate.
5. Diagnose actual failure points and conflicting results. Distinguish defective
   designs from bad input preparation, unsuitable predictors, missing evidence
   and execution errors. Do not discard negative evidence to manufacture a winner.
6. Execute at least one justified optimization revision after receiving initial
   scientific results. Produce a revised candidate batch and rerun the affected
   property, structural and catalytic checks. The revision may change mutations,
   search strategy, structure preparation, methods or workflow order, with reasons.
   A proposal or written plan without follow-up execution is not completion.
   If no safe, justified revision exists, report that limitation rather than force
   speculative changes and label the full assignment incomplete where appropriate.
7. Finalize up to five fully supported candidates. Compare them with the parent
   under the same computational protocols, report trade-offs and explain any
   shortfall in the requested final count. Save the ordered selection before
   inspecting any withheld published reference outcomes.

## Chemistry and interpretation

Research reaction-specific geometry and cite the evidence for any acceptance
bounds. Match reactant, intermediate or transition-state geometry to the modeled
state; do not transfer bounds between states without justification. If justified
bounds are unavailable, obtain descriptive measurements with a suitable operation
and report uncertainty; do not invent limits just to satisfy a tool schema.
Continue independent useful analyses when one branch is unavailable, but retain
the missing required result rather than label that branch passed.
Preserve ligand identity, atom mappings and chemistry. Removing the ligand is not
complete protein-ligand quality validation. Check mutation combinations directly;
single-mutation effects need not add up. Predicted folding stability, melting
temperature, thermal half-life, solubility and catalytic activity are different
endpoints. Unknown units or unsupported absolute predictions are descriptive only.
More favorable docking or geometry is not direct proof of a faster reaction.

## Arm specific subagent use

The separate launch instruction selects either agent-alone or specialist-assisted.
Agent-alone: no delegation or specialist consultation of any kind.
Specialist-assisted: use the native enzyme-variant-proposer and enzyme-variant-critic
with actual task/artifact paths, identities and remaining resources. Obtain a
proposal and critique before initial scientific execution. After initial results,
give both roles the actual evidence and failures, obtain a targeted revision and
critique, record the parent's decision and execute justified follow-up. Children
recommend; the parent runs scientific tools. Do not silently substitute generic
agents for either named role. Save native run/session IDs and returned advice.
Do not use the older enzyme-variant-specialist in either arm for this comparison.
The critic is not the independent outcome evaluator.

## Outputs and traceability

Create a new timestamped local run directory under
`.runs/est30-mhet/agent-alone/` or `.runs/est30-mhet/agent-with-specialist/`.
Save its path in the first progress update. These folders are ignored by Git.
Use ordinary native sessions/jobs and checkpoints; no custom background runner.
Retain job IDs immediately. Reconcile uncertain submissions instead of blindly
resending. Existing paid-service safeguards still apply. Do not cancel old jobs.

Save: qualified parent sequence/structure and chemistry; design/ranking/resource
plan; complete candidate FASTA; candidate/mutation table; raw tool outputs;
candidate-specific structures/complexes and mappings; quality/geometry reports;
revision history explaining evidence, changes and effects; final ranked CSV;
job/status/artifact ledger; actual resource/cost records or explicit unavailable
values; and a readable final report distinguishing completed, failed and missing
work. Log a technical execution failure without presenting it as a poor enzyme.

## Comparison rules

Both arms have the same objective, public starting inputs and assignment limits.
The assisted arm sees its own results only, not the agent-alone run. Specialist
usage belongs within the assisted arm's total resources. Save original and revised
results so improvement can be checked rather than asserted.
Published variants are evaluated later, outside both design chats, under the same
declared computational method when available. Historical reproduction and new
common-method rescoring are different comparisons. No new computational result
establishes improved experimental activity or superiority over a published assay.
Independent improvement remains a result to measure, not a required invented outcome.

## Completion

Proceed beyond planning to authorized scientific execution and follow-up. Finish
the required sequence-to-structure-to-evaluation-to-revision workflow or report the
exact unfinished stage and why. Do not replace this assignment with another pilot,
a parent-only analysis, mutation scan, literature recap or integration-only test.

## Launch and evaluation status

Use the two [launch prompts](PROMPTS.md) from this environment's directory.
The parent qualifies inputs as part of the real assignment, not as a replacement
for scientific execution. Subagent implementation is external to this repository.
Completed artifacts will support later case-specific tests and result reports;
none are claimed by this task definition.
