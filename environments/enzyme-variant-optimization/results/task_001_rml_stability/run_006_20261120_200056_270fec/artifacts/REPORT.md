# RML assisted stability workflow — stopped before candidate qualification

## Result

The workflow is unfinished. The initial generator returned 12 unique sequences, all with lengths different from the frozen 269-residue parent (267–293 residues). All were rejected. No variant was scored, structurally assessed, or selected, and no results-driven revised generation was performed. This is not a finding that RML cannot be improved.

The parent sequence was frozen as supplied. Its polymer matches 3TGL, although coordinates for residues 1–4 are absent and exact study-construct provenance remains unresolved. A separately approved local Biopython alignment was used only for homolog conservation; Boltzmann was used for design and scientific prediction. MLDE and target-study winning mutations/outcome tables were excluded.

## Baseline and context

The frozen primary endpoint, `tmPred_enzymes`, predicted the parent Tm as 46.97819264729818 °C. Replica spread was 1.898791120882475 °C, not a confidence interval. The 1.899 °C operational screen is not an experimental-significance claim. The model does not explicitly parameterize the 50 °C assay context or unknown pH. Parent solubility output was `1`, with undocumented class meaning.

The parent pNPL complex and complete-complex MolProbity were measured. The predicted Ser144 OG–substrate carbonyl distance is 4.9056 Å; it is descriptive and does not establish activity. Ligand identity was compared after template-assigned bond orders, not independently inferred; chemical state, reaction water and restraint limitations remain. MolProbity was measured, not passed. No candidate-specific complex or activity-preservation assessment exists.

## Generation failure and recovery

Random_Controlled_Mutagenesis job `6b0125a40d6c3e1e11b8a595` reported Success but the native CSV failed the fixed-length requirement for every draw. The generator request, all raw draws, lengths and hashes, and the diagnostic audit are preserved. No output was silently repaired. An optional native job-log lookup returned HTTP 404. The worker-level cause and deployed selection-mask semantics remain unresolved; an identical retry was not justified. A possible Solublempnn alternative was not submitted because its deployed fixed-residue syntax and selection semantics were not established. External documentation for a separate service is not evidence of this deployment's contract. A compatible, bounded generation path remains needed.

The completed preliminary stages include the parent endpoint, structural mutation scan, parent pNPL complex, parent complex quality measurement and structural comparison. The ThermoMPNN deployed score sign remains unverified and was not treated as a signed stability prediction. Four homologs were locally aligned; this is limited pairwise evidence, not an MSA. Protected positions and the evidence-intersection mask were frozen in `RUN_PLAN.json`; they do not ensure functional retention.

## Specialist review

Method reviews and recovery consultations are referenced in `decisions.md` and `usage.json`. Independent evaluator receipt `sa-0-12c7894f` reviewed the sealed empty selection and available evidence, confirming the 12 length failures and the absence of a candidate comparison. The evaluator could not independently compute checksums or run the offline comparison helper with its available tools. The coordinator separately verified the selection checksum before review. `evaluation.json` is a coordinator transcription of that review, not an evaluator-created file or helper result.

## Accounting and remaining work

Six scientific submissions completed; execution success does not imply candidate qualification. Counting the parent and all rejected draws conservatively uses 13 of 24 unique sequences, leaving 11. Nine recorded specialist calls account for 348280 input and 12608 output tokens; parent model tokens, complete total cost and wall time are unknown. Scientific billing entries and original unspecified units are in `usage.json`; no currency is inferred. The parent MolProbity submission proceeded under a YOLO policy decision; a specific direct user approval for that call was not recorded.

To complete the requested workflow, establish a compatible constrained generator without exceeding remaining sequence or submission limits; generate and validate candidates, screen properties, model candidate-specific pNPL complexes, execute an evidence-driven revision, re-evaluate, seal a supported selection and obtain a common-protocol independent comparison. The empty selection documents this stopping boundary only; it is not a complete negative result.


## Continuation after ToolUniverse connection

ToolUniverse discovery was queried for constrained protein sequence design and mutagenesis. No accessible matching generator was identified in these searches. The discovered NvidiaNIM_proteinmpnn is gated: its detail request returned missing `NVIDIA_API_KEY`; availability of the key alone would not establish support for the frozen constraints. Recovery review `sa-0-5c4628b4` and method review `sa-0-ed25fdb8` identify the remaining dependency: a documented accessible constrained generator, or the deployed Solublempnn position-control syntax, indexing, chain mapping and inversion semantics. No new scientific submission occurred; the original six jobs and previous evaluator review are unchanged.

The prior specialist usage totals above predate these two continuation reviews; consult the updated `usage.json` for cumulative totals.
