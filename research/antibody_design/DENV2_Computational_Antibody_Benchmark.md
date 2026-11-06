# DENV-2 / DV87.1 Monoclonal-Antibody Benchmark Brief

**Profile:** `denv_antibody_001` — DV87.1-derived paired heavy/light candidates against DENV-2 envelope Domain III (EDIII).

This historical brief records the source situation for two retired task presentations: a
method-neutral task and a tool-specific task. They shared one biological profile, evaluation
protocol, budget and hidden outcome set. See the [current task catalog](../../environments/antibody_design/README.md#tasks-and-benchmarks)
for the published task collection.

## Scenario

The benchmark tests the standard reference-guided monoclonal-antibody workflow in
computational form: given a reference antibody (DV87.1) and a target antigen (DENV-2
envelope EDIII), every candidate pair must be assessed against the general mAb testing
criteria — identity and lineage, physicochemical characterization, framework preservation,
structural confidence, the non-interchangeable binding-endpoint hierarchy (predicted energy,
interface confidence, Kd, kon/koff, ELISA EC50, neutralization potency, ADE risk),
specificity, developability, and immunogenicity — before any candidate may be shortlisted.
The former task-specific criteria and validation files have been retired. Current environment
requirements are described in the [environment specification](../../environments/antibody_design/ENVIRONMENT_SPEC.md).

## Source documents

The profile was assembled from the supplied dengue case files and is summarized in
[science-environments/research/antibody_design/research-notes.md](../antibody_design/research-notes.md),
with per-claim sources in [science-environments/research/antibody_design/references.md](../antibody_design/references.md).

The documents establish:

- the DENV-2 envelope EDIII target and the DV87.1 reference pairing;
- historical predicted binding energies, interface confidences, and ELISA binding entries;
- the method names recorded in the case study, including Stability-Binding DDG (backend job
  `stability-binding-ddg`), PRODIGY, and ipSAE;
- the illustrative limits (up to 10 candidates, 120-minute wall-time budget) and the
  `2024-09-01` knowledge cutoff.

## What the documents do not supply

- The exact antigen sequence/structure, construct boundaries, chain mapping, and residue
  annotation are unresolved until independently verified inputs are staged.
- A reproducible candidate-to-experimental-sample crosswalk is absent.
- No qualified evaluation protocol (thresholds, method revisions, ranking) is supplied;
  historical shortlist values are outcomes, not acceptance thresholds.
- The Stability-Binding DDG sign convention remains unresolved in the returned artifact.
- No antibody–antigen complex generator, docking, developability, or molecular-dynamics
  implementation is named; those capabilities stay unbound.

## Evidence boundary

- Predicted binding energy, measured Kd, ELISA EC50, neutralization potency, and ADE risk
  are separate, non-interchangeable endpoints. None may be inferred from the others.
- Nothing in this benchmark may be cited as experimental binding, neutralization, ADE
  safety, or clinical evidence.
- A method released after the request cutoff is `PROTOCOL_REQUIRED`, never a relaxed
  cutoff.
