# Execution status — task_003 (Boltzmann run)

Updated: 2026-11-10.

## Completed
- Target, framework and epitope verified against primary sources (see provenance.md).
- Stage-0 inputs built and checked (framework.pdb, pd1_target.pdb, epitope JSON).
- Workflow design, evaluation and selection (workflow_design.md): W1 RF-Antibody
  primary, W2 Epitope AbGen comparison, W3/W4 fallback/refinement, W5 flagged.
- Previous local run (CDR-H3-only ProteinMPNN + local Boltz2 confidence) preserved as
  a comparison point (code/legacy_local_run/, results evidence).

## Pending (blocked at user-approval gate)
- Boltzmann upload of framework.pdb returned PARTIAL validation: PDB coordinate
  syntax passed; "chain selection and scientific suitability require input review"
  (inputs were reviewed against the study and match). Connector contract requires
  explicit user approval before retrying with allow_partial_validation. The approval
  dialog timed out; no approval has been given, so no job has been submitted.
- Therefore PENDING: W1/W2 design jobs, candidate filtering, Boltz2/ipSAE,
  Antibody_Prediction, stability-binding-ddg, open-source validation, benchmark
  comparison, final shortlist and results artifacts. None of these are claimed as
  executed.

## Failed
- No executed step failed. (The PMC HTML page was bot-walled; the NCBI eutils efetch
  route succeeded — retrieval, not a task failure.)

## Next action
- On user approval ("proceed"), resume with the reviewed inputs and the exact job
  list in workflow_design.md.
