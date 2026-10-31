# Case study: improve BglB activity without sacrificing functional stability

## Scientific problem and source

Propose up to **five single-amino-acid variants** of Paenibacillus polymyxa BglB
for hydrolysis of 4-nitrophenyl beta-D-glucopyranoside (pNPG). Seek higher
catalytic efficiency while retaining the reference enzyme's functional heat
resistance. Explain the evidence for each proposal and its remaining uncertainty.

This assignment is based on Carlin et al., *PLOS ONE* (2017),
[DOI 10.1371/journal.pone.0176255](https://doi.org/10.1371/journal.pone.0176255),
with source methods/model context from the
[2016 study](https://doi.org/10.1371/journal.pone.0147596).
The papers investigate how mutations affect kinetic constants and functional
stability. This is a real case-study design/reproduction task, not synthetic data.

The assignment's shortlist size, protected sites and resource limits below are
**our project policy**, not thresholds or screening budgets claimed by the paper.

## Inputs and numbering

- [parent.fasta](parent.fasta): 445-residue modelling core, using the authors'
  model numbering. This is P22505 residues 4–448, not the complete tagged assay
  construct. Study position `i` maps to UniProt position `i + 3`.
- Author-provided starting model: member `S1 Code/bagel.pdb` in the 2016 paper's
  [S1 Code archive](https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0147596.s001).
  Despite some download-name ambiguity, its bytes are a ZIP, not a DOCX. Its
  chain A sequence agrees with parent.fasta and the published mutation labels.
  It is a computational, ligand-constrained model, not a new experimental complex.
- Reaction and substrate identity: pNPG hydrolysis to glucose and 4-nitrophenol.
  Resolve the correct beta-D stereochemistry using authoritative records before
  any substrate-conditioned calculation. A substrate analog is not pNPG.
- Published evaluation evidence: 2017
  [S1 Table](https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0176255.s001),
  copied with attribution under [reference results](../../results/bglb-activity-stability/reference/README.md).

Do not silently treat PDB 2O9P as the exact assay parent: it contains expression
tag residues and H376Q/G377R changes in its own numbering. Other structures or
full-length/tagged constructs need an explicit mapping to the study numbering.
The evaluator's mapping anchor is the supplied 445-residue core. Applying its
mutations directly to full UniProt positions would change the wrong residues.

## Reference endpoints and conditions

S1 Table's `BglB` row reports:

| Endpoint | Reference value | Meaning |
| --- | ---: | --- |
| kcat | 880 min^-1 | Reported turnover constant, not s^-1 |
| KM | 5 mM | Reported Michaelis constant, not molar units |
| kcat/KM | 174,000 M^-1 min^-1 | Primary functional objective |
| Functional Tm | 39.93 degrees C | Activity-based response after a 30-minute heat challenge |

The functional Tm is not an equilibrium unfolding free energy, a generic predicted
melting point or an optimum operating temperature. Report the study conditions
and measurement uncertainty; do not compare unlike endpoints as interchangeable.
See the article and S1 methods for assay/construct details. No wet-lab procedure
or execution is requested by this computational assignment.

## Design constraints

1. One standard-amino-acid substitution per candidate; no insertions/deletions,
   terminal/tag additions or combined mutations in the scored 445-residue core.
2. Preserve **E164, Y295 and E353**, using study numbering. These are explicit
   protected functional residues for this task, not universally fixed enzyme sites.
3. Include the unchanged parent as a comparator, never as a designed candidate.
4. Use unique candidate IDs and full sequences. A reported mutation, sequence and
   any structural mapping must agree. Duplicate sequences do not fill the shortlist.
5. Seek kcat/KM above the reference while retaining functional Tm at least equal
   to its reference point estimate. These are the evaluation rule's descriptive
   point comparisons, not evidence of statistically significant improvement.
6. Do not optimize a stability proxy at the expense of reaction requirements.
   A lower energy, favorable docking score or higher structure confidence does
   not establish higher activity or functional Tm.

## Required scientific work

1. Verify the reference inputs, numbering, reaction and available measurements.
2. Establish a comparable parent calculation for the properties being predicted.
3. Choose and explain a design strategy. Propose a small set of variants; using
   literature designs is allowed but must be labelled as rediscovery, not novelty.
4. Evaluate relevant sequence, structural, reaction and property evidence. Choose
   applicable available methods yourself; no molecular tool name is prescribed.
5. Identify failures and uncertainties. Research missing reaction requirements
   using ordinary native search/reading; do not invent geometry tolerances.
6. Revise a bounded batch if useful, rerunning evidence affected by the change.
7. Return a ranked shortlist, limitations and a reference comparison. A shorter
   or empty qualified shortlist is preferable to an unsupported success claim.

The generic process does not mandate an expensive structure/complex calculation
for every early rejected sequence. Missing methods should not block independent
work. Use the native catalogue and existing enzyme input validation; do not build
alternative HTTP callers, tool schemas or input validators.

## Resource limits

For this initial pilot: at most **20 distinct nonparent variants**, **two revision
cycles** and **40 scientific submissions**, within the owning profile's authorized
time/spending allowance. Record actual model/tool usage and remote jobs; failed
submissions still count. These are declared task limits, not a new hard-enforcement
engine. A native child call does not increase the allowance. If a limit cannot be
enforced precisely, disclose that rather than claiming an exact cost cap.

## Exact base-agent prompt

Paste from an SCI chat whose working directory is this environment directory:

> Read ENVIRONMENT_SPEC.md and tasks/bglb-activity-stability/TASK.md. Perform this
> BglB single-variant activity/stability assignment using ordinary Agent-Scientist
> capabilities. Choose your own applicable methods and tool order. Do not invoke
> the enzyme-variant-specialist or use its instructions. Respect the task's
> numbering, protected residues, outputs and resource limits. Use the current
> native catalogue and enzyme input validations, not copied tool schemas. Do not
> use the retired enzyme research/workflow execution plugins for this case. Save
> actual outputs under results/bglb-activity-stability/agent-alone/. Keep published
> measurements, new predictions and missing evidence distinct. Label literature
> rediscovery explicitly. Do not fabricate scientific outputs or replace unknown
> activity with structural scores. Finish with the real achieved result and failures.

## Exact specialist-assisted prompt

After native import/review of the supplied specialist, use a fresh SCI chat:

> Read ENVIRONMENT_SPEC.md and tasks/bglb-activity-stability/TASK.md. Perform the
> same BglB assignment from the original inputs with the same maximum resources.
> Use the saved native enzyme-variant-specialist to diagnose scientific failure
> points or conflicting evidence from this run and propose targeted alternatives.
> The main agent performs scientific tool execution using the current catalogue
> and native input validations. Do not create another runner, catalogue, database
> or child-agent framework. Do not use the retired enzyme research/workflow
> execution plugins. Include specialist usage in the total allowance. Do
> not read the separate base-agent candidate results before finishing this matched
> run. Save actual outputs under results/bglb-activity-stability/agent-with-specialist/.
> Preserve failed attempts, unknown measurements and the original scientific criteria.

For recovery instead of an independent run, explicitly ask the saved specialist
to review the completed base bundle, then follow up within a declared additional
allowance. Label that result **recovery continuation**, record the base bundle as
its input and report cumulative costs. It is not the matched run above.

## Expected outputs

- `candidates.csv`: `candidate_id,rank,mutation,sequence`; ranks start at 1; at
  most five unique designed sequences. Use a header-only CSV if none qualify.
- `report.md`: parent comparison, strategy, methods, results, failures, uncertainty,
  exclusions, achieved count, and whether this is a matched run or continuation.
- `evidence.json`: actual values, units, predicted/measured classification, source
  artifact references and exact candidate/structure identity. No specific tool
  score is silently converted into an experimental endpoint.
- `usage.json`: native session/job references, actual resources/costs where
  available, and explicit unknowns. No credentials or signed download links.
- Supporting structures/sequence files and specialist-run references where used.

## Evaluation and comparison boundary

Run the [task-specific tests](../../tests/bglb-activity-stability/ACCEPTANCE.md).
The small evaluator validates the shortlist and attaches existing published
measurements only to exact, single-mutation matches. Other variants remain
unmeasured. It does not rerank candidates, run molecular tools or manufacture
assay outcomes. Numerical comparison is not a significance test.

The papers and table are public. Both prompts permit ordinary research, so this
is **open-literature retrospective reproduction/design**, not a blinded benchmark.
Record access to known variants; model-training overlap is unknown. A genuinely
new design needs new suitable measurements before claiming experimental superiority.
